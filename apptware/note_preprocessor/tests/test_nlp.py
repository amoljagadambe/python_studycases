import pytest
import json
import spacy

from note_preprocessor import nlp


@pytest.fixture(scope="session")
def spacy_module():
    return spacy.load("en_core_web_sm", disable=['tagger', 'ner'])


def test_normalize(normalize_test_file):
    with open(normalize_test_file) as json_file:
        _data = json.load(json_file)
        for item in _data["items"]:
            input_text = item["input"]
            output = nlp.normalize(input_text)
            assert item["output"] == output


def test_update_start_end_sentences(spacy_module, updatesentences_test_file):
    with open(updatesentences_test_file) as json_file:
        _data = json.load(json_file)
        for item in _data["items"]:
            input_text = item["input"]
            _doc = spacy_module(input_text)  # convert to spacy doc
            output = nlp.update_start_end_sentences(_doc)
            assert item["output"] == output.text


@pytest.mark.parametrize(
    "input_text,o_token_offsets",
    [
        (
            "Google Facebook are Tech companies",
            [(0, 6), (7, 15), (16, 19), (20, 24), (25, 34)]
        ),
        (
            "All you need is coffee!",
            [(0, 3), (4, 7), (8, 12), (13, 15), (16, 22), (22, 23)]
        ),
        (
            "May the force be with you",
            [(0, 3), (4, 7), (8, 13), (14, 16), (17, 21), (22, 25)]
        )
    ]
)
def test_get_tokenization_info(input_text, o_token_offsets, spacy_module):
    doc = spacy_module(input_text)
    _, token_offsets = nlp.get_tokenization_info(doc)
    assert token_offsets == o_token_offsets


@pytest.mark.parametrize(
    "input_text,o_sent_offsets",
    [
        (
            "Google Facebook are Tech companies",
            [(0, 34)]
        ),
        (
            "All you need is coffee!",
            [(0, 23)]
        ),
        (
            "May the force be with you",
            [(0, 25)]
        )
    ]
)
def test_get_sentence_offsets(input_text, o_sent_offsets, spacy_module):
    doc = spacy_module(input_text)
    s_offsets = nlp.get_sentence_offsets(doc)
    assert s_offsets == o_sent_offsets
