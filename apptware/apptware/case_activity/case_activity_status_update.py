from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q
from application.resources.case_activity.WhiteCoatException import WhiteCoatException
import logging
import os
import pandas as pd
import datetime
import imp
import sys


def get_note_count(case_ids, dormant_time, config):
    note_count_list = []
    for case_id in case_ids:
        q = Q('term', case_id=case_id) & Q('range', modified_date={"gte": dormant_time})
        s = Search(index=config.note_index, doc_type=config.note_index_type).query(q).using(es)
        response = s.count()
        tmp = dict()
        tmp['case_id'] = case_id
        tmp['has_notes'] = response > 0
        note_count_list.append(tmp)
    return pd.DataFrame(note_count_list)


def get_share_bed(df):
    df = df[(df['bed'] != '') & (df['room'] != '')]
    share_bed = []
    for _, group in df.groupby(['bed', 'room']):
        if len(group['case_id']) > 1:
            share_bed.extend(list(group['case_id']))
    res = pd.DataFrame(share_bed, columns=['case_id'])
    res['share_bed'] = True

    return res


# change case_activity_status of cases that are not discharged
def update_active_zombie_status(es, actions, config):
    curr_runtime = datetime.datetime.now()

    q = Q('missing', field="date_of_discharge")
    s = Search(index=config.relos_index, doc_type=config.relos_index_type) \
        .source(include=['case_id', 'room', 'bed', 'date_of_admission']) \
        .query(q).params(scroll='10m', size=5000).using(es)
    df = pd.DataFrame([doc.to_dict() for doc in s.scan()])

    if df.empty:
        return

    df['case_activity_status'] = 'Active'
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'])
    df['los'] = df.apply(lambda row: curr_runtime - row['date_of_admission'], axis=1) \
        .astype('timedelta64[D]').astype('int64')
    df['prolonged_los'] = df['los'].map(lambda x: x >= config.patient_dormant_day)
    df['future_admission'] = df['date_of_admission'].map(lambda x: x > curr_runtime)

    note_dormant_day = (curr_runtime - datetime.timedelta(days=config.note_dormant_day)).strftime(TIME_FORMAT)
    df = pd.merge(df, get_note_count(df.case_id.values.tolist(), note_dormant_day, config), on='case_id', how='left')
    df.loc[(df['prolonged_los'] == True) & (df['has_notes'] == False), 'case_activity_status'] = 'Zombie'

    df = pd.merge(df, get_share_bed(df[df['case_activity_status'] != 'Zombie']), on='case_id', how='left')
    df.loc[(df['share_bed'] == True) & (df['has_notes'] == False), 'case_activity_status'] = 'Zombie'
    service_date = curr_runtime.strftime(TIME_FORMAT)
    for _, row in df.iterrows():
        action = {
            "_id": row.case_id,
            "_index": config.relos_index,
            "_op_type": 'update',
            "_type": config.relos_index_type,
            "_source": {
                "doc": {
                    "length_of_stay": row.los,
                    "current_hours_of_stay": row.los,
                    "case_activity_status": row.case_activity_status,
                    "service_date": service_date
                }}
        }
        actions.append(action)


# change case_activity_status of cases that are discharged
def update_discharged_status(es, actions, config):
    curr_runtime = datetime.datetime.now()

    q = ~Q('missing', field="date_of_discharge") & ~Q('term', case_activity_status="Discharged")  #vaule of case_activity_status is set to not discharged
    s = Search(index=config.relos_index, doc_type=config.relos_index_type) \
        .source(include=['case_id', 'date_of_admission', 'date_of_discharge']) \
        .query(q).params(scroll='10m', size=5000).using(es)
    df = pd.DataFrame([doc.to_dict() for doc in s.scan()])

    if df.empty:
        return

    service_date = (curr_runtime - datetime.timedelta(hours=1)).strftime(TIME_FORMAT)
    df['case_activity_status'] = 'Discharged'
    df['date_of_admission'] = pd.to_datetime(df['date_of_admission'])
    df['date_of_discharge'] = pd.to_datetime(df['date_of_discharge'])
    df['los'] = df.apply(lambda row: row['date_of_discharge'] - row['date_of_admission'], axis=1) \
        .astype('timedelta64[D]').astype('int64')
    for _, row in df.iterrows():
        action = {
            "_id": row.case_id,
            "_index": config.relos_index,
            "_op_type": 'update',
            "_type": config.relos_index_type,
            "_source": {
                "doc": {
                    "length_of_stay": row.los,
                    "current_hours_of_stay": row.los,
                    "case_activity_status": row.case_activity_status,
                    "service_date": service_date
                }}
        }
        actions.append(action)


if __name__ == "__main__":
    config_file_path = sys.argv[1]
    config = imp.load_source('config', config_file_path)

    # Setup the pagerDuty Logger
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    logger_nonphi = logging.getLogger(os.path.basename(__file__))
    logger_nonphi.info("Started the {}".format(os.path.basename(__file__)))

    # Setup the program output logger
    logger_program_output = logging.getLogger('main')
    logger_program_output.propagate = False
    log_filename = os.path.join(config.log_folder,
                                os.path.basename(__file__)[:-3] + datetime.datetime.now().strftime("%Y%m%d") + '.log')
    file_handler = logging.FileHandler(log_filename)
    logger_program_output.addHandler(file_handler)

    tracer = logging.getLogger('elasticsearch')
    tracer.setLevel(logging.CRITICAL)
    tracer.addHandler(file_handler)

    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    try:
        es = Elasticsearch([config.es_address], timeout=120, max_retries=5, retry_on_timeout=True)
        actions = []
        update_active_zombie_status(es, actions, config)
        update_discharged_status(es, actions, config)
        logger_program_output.info(helpers.bulk(es, actions, raise_on_error=False, stats_only=True))
    except Exception as e:
        # Capturing broad exception, AGAINST recommended practises - this is meant to capture the error/exception and
        # raise a pagerduty alert, to be refined/replaced once we move to the new modules
        logger_program_output.exception(
            'Exception occurred in the Program at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        raise WhiteCoatException(config.hospital_system + "'s " + os.path.basename(__file__) + " Failed at " +
                                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    else:
        logger_nonphi.info("Completed the {}".format(os.path.basename(__file__)))
