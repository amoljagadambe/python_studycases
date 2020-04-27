import datetime
import typing
import random
import factory
import math
from factory import fuzzy
from faker import Faker
from scipy import stats as sp_stats

from elasticsearch import Elasticsearch

from es_data import models as es_models

# factory.Faker.seed(4321)
RANDOM_SEED = "4321"
fake = Faker()

# Explicitly seed factory and faker
factory.random.reseed_random(RANDOM_SEED)
Faker.seed(RANDOM_SEED)

PATIENT_ID_RANGE = (1, 100)
ENCOUNTER_ID_RANGE = (1, 300)

# TODO: Will get this, hardcoded with random words for now
SNIPPET_BUILDERS = [
    "ahead",
    "should",
    "him",
    "admit",
    "good",
    "score",
    "ok",
    "voice",
    "personal",
    "much",
    "go",
    "list",
    "upon",
    "agreement",
    "strong",
    "worry",
    "task",
    "he",
    "training",
    "federal",
]

# TODO: Ask, added the first; from encounter_class table in dev
ENCOUNTER_CLASSES = [
    "Discharged",
    "Emergency",
    "Inpatient",
    "Outpatient",
    "Observation",
    "Surgery Admit",
    "Preadmit",
    "Recurring",
    "Specimen",
    "Pre-surgery Assessment",
    "Hospital Ambulatory Surgery",
    "Transport",
    "Psych Recurring",
    "Preregister",
    "Home Care Agency",
    "Home Medical Equipment",
    "Admitted",
    "Oasis",
    "Lab Vendor (Corporate)",
    "Lab Hospital Specimen (Paper Patient)",
    "Lab Vendor Outpatient (Outpatient)",
    "Lab Only (Reference)",
    "Outpatient with Observation Services",
    "Series",
    "Clinical",
    "PRE-CLINIC",
    "Provider Office Visit",
    "Provider Practice Record",
    "Referred",
    "Surgical Day Care",
    "103 - Emergency",
    "101 - Inpatient",
    "102 - Outpatient",
]


def get_substring_indices(total_length: int) -> typing.Tuple[int, int]:
    x = random.randint(0, total_length)
    if x > total_length / 2:
        return random.randint(0, x - 1), x
    else:
        return x, random.randint(x + 1, total_length)


class RelosAnnFactory(factory.Factory):

    class Meta:
        model = es_models.RelosAnn

    # {hospital_id}_{patient_id}_{encounter_id}
    case_id = factory.LazyAttribute(lambda item: "HP_{hid}_PATIENT_ID_{pid}_ENCOUNTER_ID_{eid}".format(
        hid=fake.random_int(min=1, max=5),
        pid=fake.random_int(min=PATIENT_ID_RANGE[0], max=PATIENT_ID_RANGE[1]),
        eid=fake.random_int(
            min=ENCOUNTER_ID_RANGE[0], max=ENCOUNTER_ID_RANGE[1])
    ))

    # choice of action
    ACTION_CHOICES = ["dismiss", "review", "submit", "audit", "no decision"]
    review_action = fuzzy.FuzzyChoice(ACTION_CHOICES)

    # Date
    @factory.lazy_attribute
    def review_action_time(self):
        return fake.date_time(tzinfo=datetime.timezone.utc, end_datetime=None)

    review_comment = fuzzy.FuzzyText()
    review_confidence = fuzzy.FuzzyInteger(0, 1)

    # duration_in_sec: 1 - 4000 seconds
    review_duration_in_sec = fuzzy.FuzzyInteger(low=1, high=4000)

    # Choice deep, quick, testing
    review_mode = fuzzy.FuzzyChoice(["deep", "quick", "testing"])

    # one of the names is pieces - 50-60%
    reviewer = factory.LazyFunction(
        lambda: "pieces" if fake.random.random() < 0.55 else fake.name())


class AnnFactory(factory.Factory):
    class Meta:
        model = es_models.Ann

    # {hospital_id}_{patient_id}_{encounter_id}
    case_id = factory.LazyAttribute(lambda item: "{hid}_{pid}_{eid}".format(
        hid=item.hospital,
        pid=item.patient_id,
        eid=item.encounter_id
    ))

    patient_id = factory.LazyFunction(lambda: "PATIENT_ID_%s" % fake.random_int(
        min=PATIENT_ID_RANGE[0], max=PATIENT_ID_RANGE[1]))

    # note_preprocessor
    encounter_id = factory.LazyFunction(lambda: "ENCOUNTER_ID_%s" % fake.random_int(
        min=PATIENT_ID_RANGE[0], max=PATIENT_ID_RANGE[1]))

    # note_preprocessor
    enterprise_patient_id = "ENT_PAT_ID_%s" % fake.random_int(min=1, max=10000)

    # choice of hospitals from a list
    HOSPITAL_CHOICES = ["HP_1", "HP_2", "HP_3", "HP_4", "HP_5"]
    hospital = fuzzy.FuzzyChoice(HOSPITAL_CHOICES)
    # {case_id}_{note_id}_{snippet_label}_{snippet_text}_{sentence_char_start}_{sentence_char_end}_{model_id}
    @factory.lazy_attribute
    def ann_id(self):
        return "{case_id}_{note_id}_{snippet_label}_{snippet_text}_{scs}_{sce}_{model_id}".format(
            case_id=self.case_id,
            note_id=self.note_id,
            snippet_label=self.snippet_label,
            snippet_text=self.snippet_text,
            scs=self.sentence_char_start,
            sce=self.sentence_char_end,
            model_id=self.model_id
        )

    # make this empty
    event_trigger = ""

    # if last_annotated_date exists, th is is non-empty
    @factory.lazy_attribute
    def last_annotator(self):
        if self.last_annotator_date:
            return ""
        return fake.name()

    # between 10 and 300
    note_length = fuzzy.FuzzyInteger(low=10, high=300)

    # TODO
    # depends on snippet_sentence - HAS to be less than note_length
    sentence_char_start = fuzzy.FuzzyInteger(78)
    sentence_char_end = fuzzy.FuzzyInteger(56)

    # get from a list of 30/50 constant note_types
    note_length = fuzzy.FuzzyInteger(low=10, high=300)

    # TODO
    # depends on snippet_sentence - HAS to be less than note_length
    sentence_char_start = fuzzy.FuzzyInteger(78)
    sentence_char_end = fuzzy.FuzzyInteger(56)

    # get from a list of 30/50 constant note_types
    @factory.lazy_attribute
    def note_type(self):
        return "NT_%s" % fake.random_int(min=1, max=50)

    # similar to note_type
    @factory.lazy_attribute
    def note_type_raw(self):
        return "NOTE_TYPE_RAW_%s" % self.note_type.split("_")[1]

    # random int between 8000 - 20000
    note_id = fuzzy.FuzzyInteger(low=8000, high=20000)

    # TODO: discuss later
    char_start = fuzzy.FuzzyInteger(60)
    char_end = fuzzy.FuzzyInteger(60)

    @factory.lazy_attribute
    def note_provider_type(self):
        return "NPT_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def note_provider_service(self):
        return "NPS_%s" % fake.random_int(min=1, max=10)

    # random slice from snippet_sentence
    @factory.lazy_attribute
    def snippet_text(self):
        _start, _end = get_substring_indices(len(self.snippet_sentence))
        return self.snippet_sentence[_start:_end]

    # choice of label_type from a list
    label_type = "LTYPE_%s" % fake.random_int(min=1, max=10)

    # will get a set of words - hard code it for now.
    # build a sentence from those words
    snippet_sentence = factory.Faker(
        "sentence", ext_word_list=SNIPPET_BUILDERS)

    # make this empty
    comment_text = ""

    # choice of label from a list
    snippet_label = factory.LazyFunction(
        lambda: "SL_%s" % fake.random_int(min=1, max=10))

    # choice from a list, same till attribute_value_units

    @factory.lazy_attribute
    def user_response_type(self):
        return "URT_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def code_umls(self):
        return "CODE_UMLS_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def code_snomed(self):
        return "CODE_SNOMED_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def code_rxnorm(self):
        return "CODE_RXNORM_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def code_loinc(self):
        return "CODE_LOINC_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def attribute_hypothetical(self):
        return "ATT_HYP_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def attribute_bodysite(self):
        return "ATT_BSITE_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def attribute_possible(self):
        return "ATT_POSS_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def attribute_negation(self):
        return "ATT_NEG_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def attribute_section(self):
        return "ATT_SEC_%s" % fake.random_int(min=1, max=10)

    @factory.lazy_attribute
    def attribute(self):
        return "ATT_VAL_%s" % fake.random_int(min=1, max=10)

    # TODO: clarify
    attribute_num = fuzzy.FuzzyFloat(0, 100)

    @factory.lazy_attribute
    def attribute_units(self):
        return "ATT_VAL_UNITS_%s" % fake.random_int(min=1, max=10)

    # choice of ["user", "machine"]. 95% times it'll be machine
    snippet_source = factory.LazyFunction(
        lambda: "user" if fake.random.random() < 0.05 else "machine")

    # generate this value on the basis of kermit_probability
    snippet_entropy = factory.LazyAttribute(lambda item: sp_stats.entropy(
        [item.kermit_probability, 1 - item.kermit_probability]))

    # unitex or clamp
    @factory.lazy_attribute
    def machine_type(self):
        if self.snippet_source == "user":
            return ""
        else:
            return factory.random.randgen.choice(["unitex", "clamp"])

    model_id = factory.LazyAttribute(lambda item: item.machine_type)

    # choice of green and yellow
    kermit_label = fuzzy.FuzzyChoice(["green", "yellow"])

    # int between 1 and 6
    similarity_group = fuzzy.FuzzyInteger(low=1, high=6)

    # make this empty
    CRF_probability = None

    # between 0 and 1
    kermit_probability = fuzzy.FuzzyFloat(low=0, high=1)

    # make this empty
    duplicate_status = ""

    # make this empty
    concept_probability = None

    # make this empty
    sentence_probability = None

    # kermit_date == update_date
    kermit_date = update_date = factory.Faker(
        "date_time", tzinfo=datetime.timezone.utc, end_datetime=None)

    # note_date, add_date should be within 24 hours before kermit/update (kermit looks at last 24 hour data)
    # add_date to be 2-3 hours after note_date
    @factory.lazy_attribute
    def note_date(self):
        # _ed = self.add_date - datetime.timedelta(hours=2)
        return fake.date_time_between(
            tzinfo=datetime.timezone.utc,
            start_date="-3h",
            end_date=self.add_date
        )

    @factory.lazy_attribute
    def add_date(self):
        return fake.date_time_between(
            tzinfo=datetime.timezone.utc,
            start_date="-21h",
            end_date=self.kermit_date
        )

    # will only exist if snippet_source == "user"
    @factory.lazy_attribute
    def last_annotator_date(self):
        if self.snippet_source == "user":
            return fake.date_time(tzinfo=datetime.timezone.utc, end_datetime=None)
        else:
            return None


class RelosFactory(factory.Factory):
    class Meta:
        model = es_models.Relos

    # {hospital_id}_{patient_id}_{encounter_id}
    case_id = factory.LazyAttribute(lambda item: "HP_{hid}_{pid}_{eid}".format(
        hid=fake.random_int(min=1, max=5),
        pid=item.patient_id,
        eid=item.encounter_id
    ))

    patient_id = factory.LazyFunction(lambda: "PATIENT_ID_%s" % fake.random_int(
        min=PATIENT_ID_RANGE[0], max=PATIENT_ID_RANGE[1]))
    encounter_id = factory.LazyFunction(lambda: "ENCOUNTER_ID_%s" % fake.random_int(
        min=PATIENT_ID_RANGE[0], max=PATIENT_ID_RANGE[1]))

    acrr_rating = factory.LazyFunction(
        lambda: "ACRR_RATING_%s" % fake.random_int(min=1, max=10))

    # TODO: Ask if score between 0 and 1 or more?
    acrr_score = fuzzy.FuzzyFloat(low=0, high=1)

    add_source = fuzzy.FuzzyText()

    admission_diagnosis_text = fuzzy.FuzzyText()

    admission_type = fuzzy.FuzzyText()
    admission_diagnosis = fuzzy.FuzzyText()
    admit_source = fuzzy.FuzzyText()

    # TODO: Ask Age limits?
    age = fuzzy.FuzzyInteger(low=1, high=100)

    @factory.lazy_attribute
    def age_group(self):
        _age_f = self.age/10
        return "{floor}-{ceil}".format(
            floor=math.floor(_age_f)*10,
            ceil=math.ceil(_age_f)*10
        )

    attending_doctor_id = fuzzy.FuzzyText()
    attending_doctor_name = fuzzy.FuzzyText()
    bed = fuzzy.FuzzyText()
    benefit_plan_name = fuzzy.FuzzyText()

    # case_activity_status is Active, Discharged, Zombie
    # TODO: Ask if this depends on patient_class if it is "discharged"
    case_activity_status = fuzzy.FuzzyChoice(
        ["Activity", "Discharged", "Zombie"])

    case_entropy = fuzzy.FuzzyFloat(low=0, high=1)

    # now - date_of_admission in days
    length_of_stay = factory.LazyAttribute(lambda item: (
        datetime.datetime.now(tz=datetime.timezone.utc) - item.date_of_admission).days)

    # now - date_of_admission in hours
    current_hours_of_stay = factory.LazyAttribute(lambda item: (
        datetime.datetime.now(tz=datetime.timezone.utc) - item.date_of_admission).total_seconds()/3600)

    current_reviewer = fuzzy.FuzzyText()

    death_ind = fuzzy.FuzzyText()
    department_abbreviation = fuzzy.FuzzyText()
    department_name = fuzzy.FuzzyText()
    diagnosis_this_visit = fuzzy.FuzzyText()
    discharge_location = fuzzy.FuzzyText()

    discharge_probability = fuzzy.FuzzyFloat(low=0, high=20)
    discharge_probability_24hr = fuzzy.FuzzyFloat(low=0, high=20)
    discharge_probability_48hr = fuzzy.FuzzyFloat(low=0, high=20)
    discharge_probability_72hr = fuzzy.FuzzyFloat(low=0, high=20)

    # TODO: Ask, implement
    discharge_status = fuzzy.FuzzyText()

    financial_class = fuzzy.FuzzyText()
    first_name = factory.Faker("name")

    # TODO: Ask choices?
    gender = fuzzy.FuzzyChoice(["M", "F", "NA"])

    # choice of hospitals from a list
    HOSPITAL_CHOICES = ["HP_1", "HP_2", "HP_3", "HP_4", "HP_5"]
    hospital = fuzzy.FuzzyChoice(HOSPITAL_CHOICES)
    hospital_account = fuzzy.FuzzyText()
    hospital_service = fuzzy.FuzzyText()

    intervention_categories = fuzzy.FuzzyText()
    language = fuzzy.FuzzyText()
    last_name = fuzzy.FuzzyText()

    last_confidence = fuzzy.FuzzyInteger(low=0, high=20)

    last_decision = fuzzy.FuzzyText()
    last_decision_comment = fuzzy.FuzzyText()

    last_decision_duration_in_sec = fuzzy.FuzzyInteger(low=0, high=20)

    last_decision_maker = fuzzy.FuzzyText()

    latest_complexity_index = fuzzy.FuzzyInteger(low=0, high=20)
    latest_confidence = fuzzy.FuzzyInteger(low=0, high=20)

    latest_decision = fuzzy.FuzzyText()

    latest_decision_comment = fuzzy.FuzzyText()

    latest_decision_maker = fuzzy.FuzzyText()

    # latest_review_status - audit, submit, dismiss, review
    latest_review_status = fuzzy.FuzzyChoice(
        ["audit", "submit", "dismiss", "review"])

    marital_status = fuzzy.FuzzyText()
    middle_name = fuzzy.FuzzyText()

    patient_class = fuzzy.FuzzyChoice(ENCOUNTER_CLASSES)

    patient_locations = fuzzy.FuzzyText()

    patient_type = fuzzy.FuzzyText()

    point_of_care = fuzzy.FuzzyText()

    # TODO: implement after confirmation on use of Nested
    # predictions_discharge_probability = Nested(PredictionsDischargeProbability)

    prelos = fuzzy.FuzzyText()

    prev_discharge_probabilities = fuzzy.FuzzyFloat(low=0, high=1)
    prev_discharge_probability_24hr = fuzzy.FuzzyFloat(low=0, high=1)
    prev_discharge_probability_48hr = fuzzy.FuzzyFloat(low=0, high=1)
    prev_discharge_probability_72hr = fuzzy.FuzzyFloat(low=0, high=1)

    #  int value between 1 and 7, mostly between 1 and 5
    # TODO: mostly between 1 and 5
    prev_prelos = fuzzy.FuzzyInteger(low=1, high=7)
    prev_rlos = fuzzy.FuzzyFloat(low=0, high=7)

    primary_admission_diagnosis = fuzzy.FuzzyText()

    # TODO: implement
    # primary_icd10 = Keyword(fields={"analyzed": Keyword()})

    prior_bed = fuzzy.FuzzyText()
    prior_point_of_care = fuzzy.FuzzyText()
    prior_room = fuzzy.FuzzyText()

    race = fuzzy.FuzzyText()
    reason_for_visit = fuzzy.FuzzyText()
    rlos = fuzzy.FuzzyFloat(low=0, high=20)
    room = fuzzy.FuzzyText()

    # TODO: implement
    secondary_icd10 = fuzzy.FuzzyText()
    secondary_icd10_analyzed = fuzzy.FuzzyText()

    treatment_teams = factory.LazyFunction(
        lambda: "TREATMENT_TEAM_%s" % fake.random_int(min=1, max=100))

    update_source = fuzzy.FuzzyText()
    user_confidence = fuzzy.FuzzyInteger(low=0, high=20)

    date_of_admission = factory.Faker(
        "date_time_between", tzinfo=datetime.timezone.utc, start_date="-10d", end_date="now")

    # if the patient is discharged - set a discharge date later than all other dates,
    @factory.lazy_attribute
    def date_of_discharge(self):
        if self.patient_class == "Discharged":
            return fake.date_time_between(
                tzinfo=datetime.timezone.utc,
                start_date=self.date_of_admission,
                end_date="now"
            )
        return None

    # last date is same as discharge_date if it exists
    last_review_decision_time = factory.LazyAttribute(lambda item: item.date_of_discharge or fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission))
    last_review_start_time = factory.LazyAttribute(lambda item: item.date_of_discharge or fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission))

    # All other dates between date_of_admission and date_of_discharge
    acrr_evaluation_date = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    service_date = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    service_date_history = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    latest_review_decision_time = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    latest_review_start_time = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))

    date_of_add_instance = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    date_of_death = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    date_of_point_of_care_effective = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
    date_of_update_instance = factory.LazyAttribute(lambda item: fake.date_time_between(
        tzinfo=datetime.timezone.utc, start_date=item.date_of_admission, end_date=item.date_of_discharge or "now"))
