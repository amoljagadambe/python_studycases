# Model related imports
from gensim.models import KeyedVectors
from numpy import asarray
from numpy.linalg import norm
from pandas import DataFrame, read_pickle
from re import sub
from sklearn.externals.joblib import load

def apply_w2v(word_list, w2v, w2v_vocab, extract=['add'], new_keys=True):
    """Convert word_list into matrix of vectors for each word.
    extract=['first', 'last', 'add'] returns the given normalized vectors
    new_keys=True will make key/value 1-to-1.
    """

    # Build extractors that extract normalized vectors from the matrix
    def matrix2(matrix):
        return matrix

    def first(matrix):
        vec = matrix[0, :]
        return vec / norm(vec)

    def last(matrix):
        vec = matrix[-1, :]
        return vec / norm(vec)

    def add(matrix):
        vec = matrix.sum(axis=0)
        return vec / norm(vec)

    def new_key(result_dict):
        new_dict = {}
        for k, v in result_dict.items():
            for i in range(len(v)):
                k2 = '0' * (3 - len(str(i + 1))) + str(i + 1)
                new_dict[k + k2] = v[i]
        return new_dict

    extractors = {'matrix': matrix2, 'first': first, 'last': last, 'add': add}
    matrix = asarray([w2v[_] for _ in word_list if _ in w2v_vocab])
    # result_dict = extract: vector
    if matrix.shape == (0,):
        result_dict = {_: [None] * 300 for _ in extract}
    else:
        result_dict = {_: extractors[_](matrix) for _ in extract}
    if new_keys:
        result_dict = new_key(result_dict)
    return result_dict

def text_processing(text):
    def find_replace(text, find_and_replace):
        for find, replace in find_and_replace:
            text = text.replace(' ' + find + ' ', ' ' + replace + ' ')
            if text == find:  # if the whole text matches find
                text = replace
            if text.startswith(find + ' '):  # if it startswith (replace 1)
                text = text.replace(find + ' ', replace + ' ', 1)
            if text[::-1].startswith(find[::-1] + ' '):  # if it endswith (replace 1)
                text = text[::-1].replace(find[::-1] + ' ', replace[::-1] + ' ', 1)[::-1]
        return text

    # lowercase
    text = text.lower()
    # \n issue in text
    text = text.replace('\\n', ' ')
    # find and replace with numbers and punctuation
    find_and_replace = [('o2', 'oxygen'),
                        ('a1c', 'hemoglobinac'),
                        ('hba1c', 'hemoglobinac'),
                        ('c1', 'clab'),
                        ('c2', 'clab'),
                        ('c3', 'clab'),
                        ('c4', 'clab')]
    text = find_replace(text, find_and_replace)
    # drop numbers and punctuation
    text = sub("[^A-Za-z]", " ", text)
    # get rid of extra whitespace between words
    text = sub("\s+", " ", text)
    # find and replace without numbers and punctuation
    find_and_replace = [('f u', 'follow up'),
                        ('d c', 'dc'),
                        ('h o', 'history of'),
                        ('i o', 'intake and output'),
                        ('i os', 'intake and output'),
                        ('h h', 'hemoglobin and hematocrit'),
                        ('c s', 'culture and sensitivity'),
                        ('c diff', 'clostridium difficile'),
                        ('i d', 'incision and drainage'),
                        ('q hr', 'every hour'),
                        ('q h', 'every hour'),
                        ('q hour', 'every hour'),
                        ('q hours', 'every hours'),
                        ('c c e', 'clubbing cyanosis edema'),
                        ('w u', 'work up'),
                        ('d w', 'discuss with'),
                        ('o p', 'ova parasites'),
                        ('m w f', 'monday wednesday friday'),
                        ('w o', 'without'),
                        ('r o', 'rule out'),
                        ('s p', 'status post'),
                        ('u s', 'ultrasound'),
                        ('w c', 'wheelchair'),
                        ('c o', 'complains'),
                        ('g q h', 'grams per hour'),
                        ('b l', 'bilateral'),
                        ('a p', 'anterior posterior'),
                        ('c w', 'cw'),
                        ('b c', 'bc'),
                        ('n v', 'nausea vomiting'),
                        ('d t', 'due to'),
                        ('e o', 'etiology of')
                        ]
    text = find_replace(text, find_and_replace)
    # strip extra whitespace
    text = text.strip()
    return text


def apply_w2v_dict(dict_vaule, key , w2v, w2v_vocab, extract=['add'], label=None):
    """df is a dataframe, column contains a word_list in each entry.
    extract=['first', 'last', 'add'] adds the given normalized vectors.
    label is an optional label to add to the beginning of each result col name.
    """
    # start_time = time.time()

    extracted = apply_w2v(dict_vaule[key], w2v, w2v_vocab, extract, new_keys=True)
    if label:
        for keys in list(extracted.keys()):
            extracted[label + '_' + keys] = extracted[keys]
            del extracted[keys]
        dict_vaule.update(extracted)
    # end_time = time.time()
    return dict_vaule


def kermit_similarity_groups(dict_vaule, X_cols, threshold):

    return similarity_groups_iter(dict_vaule, X_cols, threshold)


def similarity_groups(matrix, threshold):
    """ Group similiar rows based on cosine similarity
    Input Matrix: Each row is an observation
    Output Vector: The group for each observation
    """

    def _similarity(key_vector_dict, keys, remaining_keys, threshold):
        """recursively find all keys meeting similarity threshold"""

        def _similarity2(key_vector_dict, keys, remaining_keys, similar_keys, threshold):
            if len(keys) == 0:
                return similar_keys
            keyslist = list(keys)
            key = keyslist[0]
            keys = set(keyslist[1:])
            for r in remaining_keys:
                if key_vector_dict[key].dot(key_vector_dict[r]) >= threshold:
                    remaining_keys = remaining_keys.difference(set([r]))
                    similar_keys = similar_keys.union(set([r]))
                    keys = keys.union(set([r]))
            return _similarity2(key_vector_dict, keys, remaining_keys, similar_keys, threshold)

        similar_keys = set()
        similar_keys = _similarity2(key_vector_dict, keys, remaining_keys, similar_keys, threshold)
        return similar_keys

    key_vector_dict = {key: vector for key, vector in enumerate(matrix)}
    remaining_keys = set(key_vector_dict.keys())
    group = 1
    groups = []
    while len(remaining_keys) > 0:
        keys = set([list(remaining_keys)[0]])
        similar_keys = _similarity(key_vector_dict, keys, remaining_keys, threshold)
        union = keys.union(similar_keys)
        for k in list(union):
            groups.append([k, group])
            remaining_keys = remaining_keys.difference(union)
        group += 1
    return asarray([_[1] for _ in sorted(groups)])


def similarity_groups_iter(dict_vaule, x_col, threshold, new_col='sim_grp'):
    """Apply similarity groups algorithm to a dict"""
    final_dict = {your_key: dict_vaule[your_key] for your_key in x_col}
    np_array = asarray.array(list(final_dict.values()))
    dict_vaule[new_col] = similarity_groups(np_array, threshold)
    return dict_vaule


def determine_prob(dict_iter, X_cols, lookup, model):
    # If live annotation, use 0 or 1.
    if dict_iter['last_modified_by'] not in ['', 'pieces']:
        if dict_iter['user_response_type'] == 'relos_relavent':  # relavent is mis-spelled in system.
            return 1.0
        else:
            return 0.0
    # Check Corpus (True is 0.9999 so live annotation takes priority)
    exact = lookup[lookup['ann.note_text'] == dict_iter['note_text']]
    if len(exact) > 0:
        return min(exact['Label'].mean(), .9999)
    processed = lookup[lookup['ann.note_textR1'] == dict_iter['note_textP']]
    if len(processed) > 0:
        return min(processed['Label'].mean(), .9999)
    # if X_cols are NaN, return 0
    for key in X_cols:
        if dict[key]:
            return 0
    final_dict = {your_key: dict_iter[your_key] for your_key in X_cols}
    np_array = asarray.array(list(final_dict.values()))
    # Return Model Prediction (True is 0.9998 so live annotation and corpus takes priority)
    return min(model.predict_proba(np_array.reshape(1, 300))[0][1], .9998)


def decision(dict_iter, prob_threshold=0.5, max_green=6):
    #this will check the probabilty if the vaule range below to 0.5 this will set the flasg to fals
    dict_iter['green'] = 'True' if dict_iter['prob'] >= prob_threshold else 'False'
    return dict_iter


def evaluate(dict_iterater, kermit_w2v_path, lookup_path, model_path,
             sim_threshold, prob_threshold, max_green):
    # Load resources
    kermit_w2v = KeyedVectors.load_word2vec_format(kermit_w2v_path, binary=True)
    kermit_w2v_vocab = set(kermit_w2v.wv.vocab.keys())
    #print(lookup_path)
    lookup = read_pickle(lookup_path)
    model = load(model_path)

    updated_dict_list = []
    for dict_vaule in dict_iterater:
        note_text_values = dict_vaule['note_text']
        # process text
        dict_vaule['note_textP'] = text_processing(note_text_values)
        dict_vaule['note_textL'] = dict_vaule['note_textP'].split()
        dict_vaule = apply_w2v_dict(dict_vaule, 'note_textL', kermit_w2v, kermit_w2v_vocab, extract=['add'], label='snip')
        x_col = [k for k in dict_vaule.keys() if k.startswith('snip_add')]
        dict_vaule = kermit_similarity_groups(dict_vaule, x_col, sim_threshold)
        dict_vaule['prob'] = determine_prob(dict_vaule, x_col, lookup, model)
        dict_vaule = decision(dict_vaule, prob_threshold, max_green)
        updated_dict_list.append(dict_vaule)

    return updated_dict_list

"""
# Sample usage
df = evaluate(dict_iter,
              kermit_w2v_path='/home/local/COMMON-PHI/michael.seeber/seeber/kermit_spark/w2v/kermitW2V',
              lookup_path='resources/lookup.pkl',
              model_path='resources/model.pkl',
              sim_threshold=0.80,
              prob_threshold=0.5,
              max_green=6)
"""
