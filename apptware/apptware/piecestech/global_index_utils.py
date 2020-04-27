"""File to store the global configuration related functions/methods in whiteCoat platform."""

from elasticsearch import Elasticsearch


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


def get_ann_candidates(global_index_address, groups):
    """Function to return the categories give the use cases. Example categories for relos and general."""
    es = Elasticsearch([global_index_address], timeout=120, max_retries=5, retry_on_timeout=True)
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "terms": {
                            "group": groups
                        }
                    },
                    {
                        "term": {
                            "unused": False
                        }
                    }
                ]
            }
        }
    }

    resp = es.search(index="ann_conf", doc_type="info", body=query_body, scroll='5m')
    ann_candidates = []
    scroll_id = resp.get('_scroll_id')
    if scroll_id:
        first_run = True
        while True:
            if first_run:
                first_run = False
            else:
                resp = es.scroll(scroll_id, scroll='5m')
            if resp.get('hits').get('hits'):
                for doc in resp.get('hits').get('hits'):
                    ann_candidates.append(doc['_source']['type'])
            scroll_id = resp.get('_scroll_id')
            if scroll_id is None or not resp['hits']['hits']:
                break

    return ann_candidates
