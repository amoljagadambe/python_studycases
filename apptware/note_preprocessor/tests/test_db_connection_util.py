import sqlalchemy
import pytest

from note_preprocessor import db_connection_util as db_util
from tests import db_queries


DB_CONFIG = {
    "user": "test",
    "password": "test",
    "database": "pieces_common"
}

DB_TABLES = {
    "Organization": db_queries.CREATE_ORGANIZATION_QUERY,
    "provider_type": db_queries.CREATE_PROVIDER_TYPE_QUERY,
    "STG_PIECES_physiciannote": db_queries.CREATE_PHYSICIANNOTE_QUERY,
    "physiciannote_properties": db_queries.CREATE_PHYSIANNOTE_PROPERTIES_QUERY
}

@pytest.fixture(scope="session")
def db_engine(mysql_db):
    with mysql_db as mysql:
        url = mysql.get_connection_url() + "?local_infile=1"
        yield sqlalchemy.create_engine(url)


@pytest.fixture(scope="session")
def load_tables(db_engine):
    for query in DB_TABLES.values():
        db_engine.execute(query)


@pytest.fixture(scope="session")
def load_data(db_engine, load_tables):
    for table_name in DB_TABLES:
        db_engine.execute(db_queries.LOAD_DATA_QUERY.format(table_name=table_name))
    

@pytest.mark.parametrize(
    "org_id,start_time,end_time,output_count",
    [
        ("HCST_0", "2021-01-28 05:34:33", "2021-04-15 05:34:33", 11,),
        ("DOES_NOT_EXIST", "2021-01-28 05:34:33", "2021-04-15 05:34:33", 11,),
        ("HCST_0", "2021-02-01 05:34:33", "2021-04-30 05:34:33", 13,),
        ("DOES_NOT_EXIST", "2021-02-01 05:34:33", "2021-04-30 05:34:33", 13,),
        ("HCST_0", "2021-02-01 05:34:33", "2021-05-31 05:34:33", 36,),
        ("DOES_NOT_EXIST", "2021-02-01 05:34:33", "2021-05-31 05:34:33", 36,),
        ("HCST_0", "2021-03-15 05:34:33", "2021-06-24 05:34:33", 44,),
        ("DOES_NOT_EXIST", "2021-03-15 05:34:33", "2021-06-24 05:34:33", 44,),
        ("HCST_0", "2021-03-15 05:34:33", "2021-06-25 05:34:33", 46,),
        ("DOES_NOT_EXIST", "2021-03-15 05:34:33", "2021-06-25 05:34:33", 46,),
    ]
)
def test_note_query(org_id, start_time, end_time, output_count, db_engine, load_data):
    query_note_table = db_util.NOTE_QUERY.format(org_id, start_time, end_time)
    result = db_engine.execute(query_note_table)
    assert output_count == result.rowcount
