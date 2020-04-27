from elasticsearch_dsl import Document, Date, Keyword, Text, Integer, Float
import factory
import datetime
import factory.random
from faker import Faker


fake = Faker()
Faker.seed(4321)

class User(Document):
    """Mapping for the ann index documents."""
    username = Keyword()
    email = Keyword()
    last_annotator_date = Date(format='yyyy-MM-dd HH:mm:ss', default_timezone='UTC')


class UserFactory(factory.Factory):
    class Meta:
        model = User


    @factory.lazy_attribute
    def username(self):
        return factory.random.randgen.choice(["unitex", "clamp"])

    patient_id = "PATIENT_ID_%s" % fake.random_int(min=1000, max=10000)
    HOSPITAL_CHOICES = ["HP_1", "HP_2", "HP_3", "HP_4", "HP_5"]
    case_id = factory.LazyAttribute(lambda item: "HP_{hid}_PATIENT_ID_{pid}".format(
        hid=fake.random_int(min=1, max=5),
        pid=fake.random_int(min=1000, max=10000)
                            ))

    @factory.lazy_attribute
    def email(self):
        return '%s@example.com' % fake.first_name().lower()

    @factory.lazy_attribute
    def last_annotator_date(self):
            return fake.date_time(tzinfo=datetime.timezone.utc, end_datetime=None)

    my_name = factory.Faker('date_time',tzinfo=datetime.timezone.utc, end_datetime=None)

    @factory.lazy_attribute
    def review_duration_in_sec(self):
        return "%s seconds" % fake.random_int(min=0, max=4000)



obj = UserFactory()
print(obj.email)
print(obj.case_id)
