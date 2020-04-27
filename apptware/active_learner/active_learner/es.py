from elasticsearch_dsl import Document, Keyword, Boolean, Date, Integer, Text, Index
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers

from datetime import datetime


def connect_es(host, port, from_cloud=False):
    if from_cloud:
        return Elasticsearch(
            hosts=[{'host': host, 'port': port}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    return Elasticsearch(hosts=[{"host": host, "port": port}])
