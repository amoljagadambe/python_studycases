import logging
import datetime
import warnings
import itertools
from typing import Iterator, List, Tuple, Dict, Mapping, Optional
from dataclasses import dataclass, asdict

from elasticsearch_dsl import Search, Q
from dateutil import parser as dateutil_parser
from scipy import stats as sp_stats

from active_learner import models as al_models
from active_learner.ai_engine_exception import AiEngineWarning


logger = logging.getLogger(__name__)


@dataclass
class CaseInfo:
    case_id: str
    review_action_time: Optional[datetime.datetime] = None


@dataclass
class CaseSnippetInfo:
    case_id: str
    ann_id: str = ""
    kermit_probability: float = 0.0
    similarity_group: int = 0
    kermit_label: str = ""

    @property
    def green_tag(self) -> bool:
        return True if self.kermit_label == "green" else False

    @property
    def entropy(self) -> float:
        return sp_stats.entropy(
            [float(self.kermit_probability),
             (1 - float(self.kermit_probability))],
            base=2
        )


def imerge(a, b):
    for i, j in zip(a, b):
        yield i
        yield j


def get_all_non_discharge_cases_iter(es_conn, hospital_codes, relos_index, from_date_obj, to_date_obj) -> Iterator[CaseInfo]:
    """Returns an iterator of CaseInfo objects for cases which are not discharged."""
    q = Q(
        "bool",
        must=[
            Q("terms", hospital__keyword=hospital_codes),
            Q('range', service_date={"gte": from_date_obj, "lte": to_date_obj})
        ],
        must_not=[
            Q("exists", field="date_of_discharge"),
            Q("term", latest_review_status__keyword="dismiss")
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_index) \
        .doc_type(al_models.Relos) \
        .query(q) \
        .source(False)

    for res in s.scan():
        yield CaseInfo(case_id=res.meta.id)


def get_submitted_in_relos_ann_sobj(es_conn, relos_ann_index, from_date_obj, to_date_obj) -> Search:
    """
    Returns the elasticsearch_dsl.Search object with source=["case_id", "review_action_time"]
    for cases which have been annotated between from_date_obj and to_date_obj.
    """
    q = Q(
        "bool",
        must=[
            Q("term", review_action__keyword="submit"),
            Q('range', review_action_time={
              "gte": from_date_obj, "lte": to_date_obj})
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_ann_index) \
        .doc_type(al_models.RelosAnn) \
        .query(q) \
        .source(["case_id", "review_action_time"])
    return s


def get_case_info_from_relos_ann_sobj_iter(sobj: Search) -> Iterator[CaseInfo]:
    """
    Returns an Iterator of CaseInfo objects for cases
    which have been annotated between from_date_obj and to_date_obj.
    """
    for res in sobj.scan():
        yield CaseInfo(case_id=res.case_id, review_action_time=res.review_action_time)


def get_case_last_decision_iter(es_conn, hospital_codes, relos_index, relos_ann_index, from_date_obj, to_date_obj) -> Iterator[CaseInfo]:
    """Returns the cases (Iterator of CaseInfo objects) which are not discharged.
    The entropy is then re-calculated and updated for the cases returned from this iterator."""

    all_non_discharge_cases_info_iter = get_all_non_discharge_cases_iter(
        es_conn, hospital_codes, relos_index, from_date_obj, to_date_obj)

    relos_ann_submitted_sobj = get_submitted_in_relos_ann_sobj(
        es_conn, relos_ann_index, from_date_obj, to_date_obj)

    # If not reviewed in last 24 hours
    if relos_ann_submitted_sobj.count() == 0:
        logging.log(logging.INFO, "No reviewed cases found between {} and {}.".format(
            from_date_obj,
            to_date_obj
        ))
        return all_non_discharge_cases_info_iter

    relos_ann_submitted_cases_info_iter = get_case_info_from_relos_ann_sobj_iter(
        relos_ann_submitted_sobj)

    # Group & Merge all_non_discharge_cases_info_iter and ann_submitted_cases_info_iter by case_id
    relos_ann_submitted_grouped_by_case_id = itertools.groupby(
        relos_ann_submitted_cases_info_iter, lambda item: item.case_id)
    all_non_discharge_grouped_by_case_id = itertools.groupby(
        all_non_discharge_cases_info_iter, lambda item: item.case_id)
    merged_iter = imerge(relos_ann_submitted_grouped_by_case_id,
                         all_non_discharge_grouped_by_case_id)

    for case_id, group_obj in merged_iter:
        yield max(group_obj, key=lambda item: item.review_action_time)


def get_snippet_info_for_case_info_iter(case_info: CaseInfo, from_date_obj: datetime.datetime, es_conn, ann_index, primary_note_types, event_candidates) -> Iterator[CaseSnippetInfo]:
    """
    Queries the ann index for snippets with specific case_id, from primary note_types, with label green and
    note_date greater than service_date.

    Returns an Iterator of CaseSnippetInfo objects
    """

    # Compute the time from which each case's snippets have to be considered.
    # This is done by comparing the review_action_time for each CaseInfo and the x hour limit
    case_consideration_time = max(from_date_obj, case_info.review_action_time) if case_info.review_action_time else from_date_obj

    q = Q(
        "bool",
        must=[
            Q("term", case_id__keyword=case_info.case_id),
            Q("terms", snippet_label__keyword=event_candidates),
            Q("terms", note_type__keyword=primary_note_types),
            Q('range', note_date={"gte": case_consideration_time})
        ])
    s = Search(using=es_conn) \
        .index(ann_index) \
        .doc_type(al_models.Ann) \
        .query(q) \
        .source(["case_id", "ann_id", "kermit_probability", "similarity_group", "kermit_label"])

    if s.count() == 0:
        yield CaseSnippetInfo(case_id=case_info.case_id)

    for res in s.scan():
        yield CaseSnippetInfo(
            case_id=case_info.case_id,
            ann_id=res.ann_id,
            kermit_probability=res.kermit_probability,
            similarity_group=res.similarity_group,
            kermit_label=res.kermit_label
        )


def get_representative_snippet_for_each_similarity_group_iter(sinfo_iter: Iterator[CaseSnippetInfo]):
    """
    Filters the Iterator of CaseSnippetInfo objects based on similarity groups.

    Returns an iterator of CaseSnippetInfo objects
    """
    sinfo_grouped_by_sg = itertools.groupby(
        sinfo_iter, lambda item: item.similarity_group)
    for sg, sinfo_grouped_obj in sinfo_grouped_by_sg:
        yield max(sinfo_grouped_obj, key=lambda item: item.kermit_probability)


def get_cases_under_review(relos_index, from_date_obj, es_conn) -> List[str]:
    """Returns the List of case_ids which are under review from the last 24 hours."""
    q = Q(
        "bool",
        must=[
            Q("term", latest_review_status__keyword="review"),
            Q('range', latest_review_start_time={"gte": from_date_obj})
        ]
    )
    s = Search(using=es_conn) \
        .index(relos_index) \
        .doc_type(al_models.Relos) \
        .query(q) \
        .source(["case_id"])

    cases_under_review = []
    for res in s.scan():
        cases_under_review.append(res.case_id)

    return cases_under_review
