import pytest
from kermit.kermit_model_eval import text_processing
from kermit.kermit_model_eval import decision


@pytest.mark.parametrize("text, output",
                         [('f u', 'follow up'), ('c s', 'culture and sensitivity'),
                          ('w o', 'without'), ('e o', 'etiology of')])
def test_text_processing(text, output):
    assert text_processing(text) == output


@pytest.mark.parametrize("dict_iter, expected_dict",
[({'prob':0.2}, {'prob':0.2, 'green': 'False'}),
({'prob' : 0.4}, {'prob': 0.4, 'green': 'False'}),
({'prob' : 0.5}, {'prob': 0.5, 'green': 'True'}),
({'prob' : 0.8}, {'prob': 0.8, 'green': 'True'})
]
)
def test_decision(dict_iter, expected_dict):
    print(type(dict_iter))
    actual_dict = decision(dict_iter)
    assert actual_dict['green']==expected_dict['green']

# def test_similarity_groups_iter():
#
