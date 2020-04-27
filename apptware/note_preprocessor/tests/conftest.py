import pytest

from testcontainers.elasticsearch import ElasticsearchContainer
from testcontainers.mysql import MySqlContainer
import sqlalchemy


def pytest_addoption(parser):
    parser.addoption(
        "--normalize-test-file", action="store",
        default="fixtures/test_normalize.json",
        help="Input/Output file to test normalize"
    )
    parser.addoption(
        "--updatesentences-test-file", action="store",
        default="fixtures/test_update_start_end_sentences.json",
        help="Input/Output file to test update_start_end_sentences"
    )


@pytest.fixture
def normalize_test_file(request):
    return request.config.getoption("--normalize-test-file")


@pytest.fixture
def updatesentences_test_file(request):
    return request.config.getoption("--updatesentences-test-file")


@pytest.fixture(scope="session")
def mysql_db():
    return MySqlContainer(
        'mysql:5.7.18',
        MYSQL_DATABASE="pieces_common"
    )
