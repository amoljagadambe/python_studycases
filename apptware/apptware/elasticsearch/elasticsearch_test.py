import datetime
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Search
from elasticsearch_dsl.connections import connections
import factory.fuzzy
from faker import Faker

fake = Faker()
Faker.seed(4321)

# Define a default Elasticsearch client
connections.create_connection(alias='my_new_connection', hosts=['localhost'], timeout=60)


def store_data():
    article_object = Article()
    artical_factory = Annfactory()
    article_object.title = artical_factory.title
    article_object.body = artical_factory.body
    article_object.tags = artical_factory.tags
    return article_object.save()


def data_retrival_genrater():
    s = Search(using='my_new_connection').sort(
        'category',
        '-title',
        {"lines": {"order": "asc", "mode": "avg"}}
    )
    for hit in s.scan():
        print(hit.title)
        yield hit


class Article(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tags = Keyword()
    published_from = Date()
    lines = Integer()


# create and save and article
class Annfactory(factory.Factory):
    class Meta:
        model = Article

    title = fake.text(max_nb_chars=200)
    body = fake.text(max_nb_chars=200)
    tags = fake.name()
    published_from = fake.date_time(tzinfo=datetime.timezone.utc, end_datetime=None)
    lines = factory.fuzzy.FuzzyInteger(42)


# create the mappings in elasticsearch
Article.init()

# Genrate data from faker and store the data into elasticsearch
if store_data():
    print("data stored sucessfully")

# data retrival and preprocessing

def preprocess():

    out_list = []
    for value in data_retrival_genrater():
        out_list.append(value)


    #TODO: Doing Some Preprocessing operation on the data which will be discussed by 7 PM call


# Display cluster health
print(connections.get_connection().cluster.health())
