from elasticsearch_dsl import Document, Keyword, Boolean, Date, Integer, Text, Index
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers

from datetime import datetime


class Note(Document):
    """Mapping for note Index Documents."""
    case_id = Keyword()
    de_id = Boolean()
    hospital = Keyword()
    patient_id = Keyword()
    encounter_id = Keyword()
    enterprise_patient_id = Keyword()
    note_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    note_id = Keyword()
    note_length = Integer()
    note_type = Keyword()
    note_type_raw = Keyword()
    note_provider_id = Keyword()
    note_provider_service = Keyword()
    note_provider_type = Keyword()
    note_provider_name = Keyword(multi=True)
    update_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    add_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    ds_add_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    ds_update_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')
    sentence_offsets = Integer(multi=True, index=False)
    text = Text()
    raw_text = Text()
    sentences = Text(multi=True)
    token_offsets = Integer(multi=True, index=False)

    def save(self, **kwargs):
        if not self.add_date:
            self.add_date = datetime.now().strftime("yyyy-MM-dd HH:mm:ss")
        self.update_date = datetime.now().strftime("yyyy-MM-dd HH:mm:ss")
        return super(Note, self).save(**kwargs)

    def to_dict(self, include_meta=False, skip_empty=True):
        self.meta.id = "{}_{}".format(self.case_id, self.note_id)
        if not self.add_date:
            self.add_date = datetime.now().strftime("yyyy-MM-dd HH:mm:ss")
        self.update_date = datetime.now().strftime("yyyy-MM-dd HH:mm:ss")
        return super(Note, self).to_dict(include_meta=include_meta, skip_empty=skip_empty)


def index_notes(es_conn, notes, index_name):
    """Indexes the note documents via bulk indexing. The notes are provided as list of Note objects."""
    index = Index(index_name, using=es_conn)
    index.document(Note)

    actions = (note.to_dict(True) for note in notes)
    helpers.bulk(es_conn, actions)


def connect_es(host, port, from_cloud=False):
    """Connects to ElasticSearch
    if from_cloud: by using the secret key and access key from AWS.
    else: Elasticsearch-Py connection

    Returns the ES Connection Object.
    """
    if from_cloud:
        return Elasticsearch(
            hosts=[{'host': host, 'port': port}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    return Elasticsearch(hosts=[{"host": host, "port": port}])
