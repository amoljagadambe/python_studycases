from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers




def connect_es(host, region='es-east-1'):
    """Connects to ElasticSearch by using the secret key and access key from AWS. Returns the ES Connection Object."""

    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    return es
