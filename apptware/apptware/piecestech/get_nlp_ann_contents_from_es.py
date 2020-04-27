#!/usr/bin/python

"""File to generate the required NLP contents similar to the feature file for the kermit model prediction.
This gets the required data from ElasticSearch ann_index and MySQL DS Prod Replica."""

import pandas as pd
from elasticsearch import Elasticsearch
from application.resources.piecestech import elastic_search_generator as esg
from application.resources.piecestech import global_index_utils as gb_utils


def get_interested_note_type(global_index_address, configuration_index, configuration_index_type):
    """Function to return the primary note types, if not found will return a default set."""
    # This is modified from the function from export relos file
    es = Elasticsearch([global_index_address], timeout=120, max_retries=5, retry_on_timeout=True)
    resp = es.search(index=configuration_index, doc_type=configuration_index_type, body={
        "query": {
            "term": {
                "option_name": "primary.note.type.list"
            }
        }
    })
    if resp['hits']['total'] > 0:
        note_type_list = resp['hits']['hits'][0]['_source']['option_value']
    else:
        # No response from ElasticSearch, so return the default list.
        note_type_list = ["PR", "CN", "CO", "CM", "HP", "DC", "DI", "SW", "CC", "DN", "AP", "EV", "PD", "SO", "PN",
                          "TR", "PP", "CPS", "TD", "PI", "PC", "RB", "AD", "TP", "EDN", "EPD", "APN", "CONS", "DS",
                          "EVENT", "TP", "TRIAGE", "SUBOBJ", "ANPOS", "Anesth", "OP", "TRAN", "PRNO", "PSY", "ORBON",
                          "ANPRE", "ORPRE", "QUERY", "ORPOS", "INHP", "CATH", "CP", "EDHON", "ECMO", "ANES", "NOD",
                          "HPVO", "ADDN", "CODDOC", "PI", "ANTP", "CORR", "SP", "CPR", "DIFAIR", "EDDISP", "TELE",
                          "TPREC", "PROC", "ORS", "ORA", "EDP", "POC", "INTDISP", "Palliative"]
    return note_type_list


def get_adm_disch_data(config, from_date, to_date):
    """Gets the admission date from the relos index specific to the cases which have activity within the
    mentioned time duration and which are not discharged.
    Input: config, from_date,to_date as datetime objects.
    Output: DataFrame with case_id, admission_date and discharge_date as columns."""

    es = Elasticsearch([config.es_address], timeout=120, max_retries=5, retry_on_timeout=True)

    from_date = from_date.strftime("%Y-%m-%d %H:%M:%S")
    to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")

    relos_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "service_date": {
                                "gte": from_date,
                                "lte": to_date,
                                "format": "yyyy-MM-dd HH:mm:ss"
                            }
                        }
                    },
                    {
                        "terms": {
                            "hospital": config.hospital_codes
                        }
                    },
                    {
                        "missing": {
                            "field": "date_of_discharge"
                        }
                    }
                ]
            }
        },
        "_source": ['case_id', 'date_of_admission']

    }

    search_params = {
        'es_object': es,
        'search_index': config.relos_index,
        'scroll_time': '10m',
        'query_body': relos_query,
        'page_size': 50,
        'doc_type': config.relos_index_type,
        'timeout': 60,
        'upto_count': -1
    }

    relos_dicts = []
    for doc_ in esg.es_search_generator(**search_params):
        yield doc_

    # relos_df = pd.DataFrame(relos_dicts)
    # return relos_dicts


def get_ann_data_from_ann_index(config, from_date, to_date):
    """Query the elastic search ann index and get the documents that fall within the given time duration which are from
    primary notes.
    If the config's note_types is an empty list or the variable is missing in config, use the primary note types.
    Input: config, from_date, to_date as datetime objects
    Output: dataframe with all fields from ann_index as columns."""

    es = Elasticsearch([config.es_address], timeout=120, max_retries=5, retry_on_timeout=True)

    try:
        note_types = config.note_types
    except AttributeError:
        note_types = []

    if not note_types:
        # Get Primary note_types if rqd_note_types is missing in config or is an empty list
        note_types = get_interested_note_type(config.global_es_address, config.configuration_index,
                                              config.configuration_index_type)

    event_candidates_by_group = gb_utils.get_ann_candidates(config.global_es_address, config.event_candidate_groups)

    from_date = from_date.strftime("%Y-%m-%d %H:%M:%S")
    to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")

    ann_query = {"query": {
        "bool": {
            "must": [
                {
                    "terms": {
                        "label": event_candidates_by_group
                    }
                },
                {
                    "terms": {
                        "note_type": note_types
                    }
                },
                {
                    "range": {
                        "note_date": {
                            "gte": from_date,
                            "lte": to_date
                        }
                    }
                }
            ]
        }
    },
    }

    search_params = {
        'es_object': es,
        'search_index': config.ann_index,
        'scroll_time': '10m',
        'query_body': ann_query,
        'page_size': 50,
        'doc_type': config.ann_index_type,
        'timeout': 60,
        'upto_count': -1
    }

    ann_dict = {}
    for doc_ in esg.es_search_generator(**search_params):
        ann_dict[doc_['_id']] = doc_['_source']

        # Adding this till WC 1645 is taken care of
        try:
            doc_['_source']['ann_id']
        except KeyError:
            # Copy over the _id into ann_id if missing.
            doc_['_source']['ann_id'] = doc_['_id']

    # ann_df = pd.DataFrame.from_dict(ann_dict, orient='index').reset_index(drop=True)
    return ann_dict


def get_ann_contents(config, from_date, to_date):
    """Gets the required dataframe with same columns as NLP_ann file so that it can be used as input for Kermit.
    Input: config, from_date and to_date as datetime objects.
    Output: dataframe with the required columns and names as the NLP_ann file.
    Updated Output:  List of dict which contain ann_dict and final_dict"""

    mysql_dict = []
    for vaule in get_adm_disch_data(config, from_date, to_date):
    #output:  mysql_dict = list of dictionary contaning case_id, admission_date and discharge_date as keys
    #schema [{'case_id":123,"date_of_addmission":date}]
        mysql_dict.append(vaule)

    ann_dict = get_ann_data_from_ann_index(config, from_date, to_date)
    #List
    final_df = pd.merge(ann_df, mysql_df, on=['case_id'])

    final_dict = mysql_dict.append(ann_dict)

    if 'user_response_type' not in final_df.columns:
        # Will happen if none of the cases have been touched by either kermit or user - shouldn't happen in daily run
        final_df['user_response_type'] = None

    #check code flow before renamoing the  iter
    final_df.rename(columns={'note_id': 'NoteID', 'hospital': 'HosID', 'patient_id': 'PID',
                             'date_of_admission': 'relos.date_of_admission', 'note_date': 'txt.note_date',
                             'note_type': 'txt.note_type',
                             'note_length': 'NoteLength', 'last_modified_by': 'LastModifiedBy',
                             'user_response_type': 'UserResponseType', 'last_modified_date': 'LastModifiedDate',
                             'label': 'ann.label', 'snippet_sentence': 'ann.snippet_sentence',
                             'note_text': 'ann.note_text', 'char_start': 'RELOS_NLP_Feature_startChar',
                             'char_end': 'RELOS_NLP_Feature_endChar', 'sentence_char_start': 'SentenceCharStart',
                             'sentence_char_end': 'SentenceCharEnd', 'encounter_id': 'EnctID',
                             'case_id': 'ann.case_id'}, inplace=True)

    final_df = final_df[['ann_id', 'ann.case_id', 'ann.note_text', 'txt.note_type', 'LastModifiedBy',
                         'UserResponseType', 'txt.note_date', 'relos.date_of_admission', 'ann.snippet_sentence',
                         'ann.label']]
    return final_dict
