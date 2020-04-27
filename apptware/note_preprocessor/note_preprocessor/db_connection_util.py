"""This file has the functions to connect to MySQL and get the required data. Based this from
https://stackoverflow.com/a/38078544/8133596 """
import pymysql

# Unused constant currently, this query is retrieved from the secrets manager.
NOTE_QUERY = """
SELECT
    pn.PhysicianNoteRowID AS PhysicianNoteRowID,
    pn.HospitalCode AS HospitalCode,
    pn.PatientID AS PatientID,
    pn.EncounterID AS EncounterID,
    pn.NoteType AS NoteType,
    pnp.RawNoteType AS RawNoteType,
    pn.NoteID AS NoteID,
    pn.NoteProviderID AS NoteProviderID,
    pn.NoteDate AS NoteDate,
    pn.NoteStatus AS NoteStatus,
    pn.NoteText AS NoteText,
    pn.UpdateDate AS UpdateDate,
    pn.AddDate AS AddDate,
    ptype.name AS NoteProviderType
FROM
    STG_PIECES_physiciannote pn
        LEFT JOIN
    physiciannote_properties pnp ON pn.PatientID = pnp.PatientID
        AND pn.EncounterID = pnp.EncounterID
        AND pn.NoteID = pnp.NoteID
        LEFT JOIN
    pieces_common.provider_type AS ptype ON ptype.code = pnp.NoteAuthorType
        AND ptype.org_id = '{}'
WHERE
     pn.UpdateDate > '{}' and pn.UpdateDate < '{}';
"""


class Database:
    def __init__(self, host=None, port=None, user=None, password=None, database=None):
        """Sets the Db connection."""
        self._conn = pymysql.connect(
            host=host,
            user=user,
            port=int(port) if port else port,
            password=password,
            database=database,
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.connection.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchmany(self, count=1000):
        return self.cursor.fetchmany(count)

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def iquery(self, sql, params=None):
        # TODO: modify this to be a generator which uses fetchmany
        self.cursor.execute(sql, params or ())
        return self.fetchall()


def get_data(db_config, org_id, start_time, end_time):
    """This connects to DB, gets the notes based on the connection, query and returns list of db rows.
    The config should have db details, query_string"""

    query_note_table = NOTE_QUERY.format(org_id, start_time, end_time)

    with Database(**db_config) as conn:
        db_data = conn.query(query_note_table)
    return db_data


def yield_data(config, start_time, end_time):
    """TODO: This is the generator version of get_data. Uses the iquery method of DB."""
