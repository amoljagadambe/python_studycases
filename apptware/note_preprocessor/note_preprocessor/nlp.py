"""File to do the pre processing given a note."""
import spacy
import re
import logging
import string

from . import es

logger = logging.getLogger(__name__)


def update_start_end_sentences(doc):
    """Custom sentence detection component to be plugged into the NLP model from Spacy."""
    for token in doc:
        if len(doc) > token.i + 2 and token.text == ":" and doc[token.i + 1].text in ("\t ", "\t"):
            # Bp: 120/80 Stable - No sentence break at / after 120
            doc[token.i + 2].is_sent_start = False
        elif len(doc) > token.i + 1 and token.text in ("\n", "\n ", "\n\t") and doc[token.i + 1].text[0].isupper():
            # Checks the first letter after new line, if upper marks as sent start
            doc[token.i + 1].is_sent_start = True
        elif len(doc) > token.i + 1 and token.text == "Dr.":
            # When there is no space between Dr and .
            doc[token.i + 1].is_sent_start = False
        elif len(doc) > token.i + 1 and token.text == "." and token.i > 1 and doc[token.i - 1].text in ("Dr", "MD"):
            # When there is a space, Checks the sentences with Dr . John or Jane MD .
            doc[token.i + 1].is_sent_start = False
        elif len(doc) > token.i + 3 and token.text == "." and token.i > 1 and doc[token.i - 1].text in ("y") and doc[
            token.i + 1].text == "o":
            # Checks the sentences with 13 y . o .
            doc[token.i + 1].is_sent_start = False
            doc[token.i + 3].is_sent_start = False
    return doc


nlp = spacy.load("en_core_web_sm", disable=['tagger', 'ner'])
nlp.add_pipe(update_start_end_sentences, before="parser")


def process_note(text):
    """Processes the unicode text and returns the tokenized text, token offsets and sentence offsets with respect to the
    tokenized text."""

    text = normalize(text)

    # Get tokenized text
    tokenized_text = get_tokenized_text(text)

    doc = nlp(tokenized_text)
    tokens, token_offsets = get_tokenization_info(doc)
    sentence_offsets = get_sentence_offsets(doc)
    return {'tokenized_text': tokenized_text, 'token_offsets': token_offsets, 'sentence_offsets': sentence_offsets}


def get_tokenization_info(doc):
    """Returns the tokens, token offsets given the spacy processed doc."""
    token_offsets, tokens = [], []
    for token in doc:
        tokenized_text = token.text
        tokens.append(tokenized_text)
        token_offsets.append((token.idx, token.idx + len(tokenized_text)))
    return tokens, token_offsets


def get_sentence_offsets(doc):
    """Returns the sentence offsets given the spacy processed doc."""
    sentence_offsets = []
    for sent in doc.sents:
        sentence_offsets.append((sent.start_char, sent.end_char))
    return sentence_offsets


def get_tokenized_text(text):
    """Takes the unicode text and return the space separated tokens."""
    doc = nlp.make_doc(text)
    return " ".join((token.text for token in doc))


def normalize(text):
    """Normalizes the unicode text. Contains code from old text_processing_utils and also from lexigram tokenizer."""
    #
    text = ''.join(x if x in string.printable else ' ' for x in text)
    # Replace 3 spaces or more with a new line
    text = re.sub(r'\s{3,}', '\n', text)
    # replace multiple \n with single \n
    text = re.sub(r'\n\s*\n', '\n', text)
    text = text.strip()

    # Split the n't words so that models can identify negation easily
    subs = [("isn't", "is not"), ("aren't", "are not"),
            ("wasn't", "was not"), ("weren't", "were not"),
            ("don't", "do not"), ("doesn't", "does not"),
            ("didn't", "did not"), ("haven't", "have not"),
            ("hasn't", "has not"), ("hadn't", "had not"),
            ("won't", "will not")]
    for (a, b) in subs:
        text = text.replace(a, b)

    # punctuation
    # Replaces the groups 1 and 2 with a space before them. group1 is one of colon, comma and period. group2 is
    # group1 followed by not a digit
    text = re.sub(r'([:,\.])([^\d])', r' \1 \2', text)

    # Adds space before and after the ellipsis
    text = re.sub(r'\.\.\.', r' ... ', text)

    # Adds a space before and after any of special characters defined below
    text = re.sub(r'[-\'/\\;@#$%&]', r' \g<0> ', text)

    # Adds a space in front and end of the end-of-line characters ex: hllo.]*' <end of line> becomes hllo .]*',
    # removes extra spaces with a single space, this is done only for the last matching group before end of line.
    text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)\s*$', r'\1 \2\3 ', text)

    # Adds a space before and after the character ? or !
    text = re.sub(r'[?!]', r' \g<0> ', text)

    # Replaces the last slash before end of line with space
    text = re.sub(r'\\$', ' ', text)

    # Replaces the extra slash before the new line with space
    text = text.replace("\\\n", " \n")

    # Replaces the extra slash before the new line with space, resulting in 2 spaces before new line
    text = text.replace("\\ \n", "  \n")

    # Replaces multiple spaces with a single space
    text = re.sub(r' +', ' ', text)

    return text


def preprocess_notes(note_data):
    """Takes the DB data generator and yields Notes from it."""
    for db_row_note in note_data:
        note = es.Note()
        physician_note_row_id = db_row_note['PhysicianNoteRowID']
        note.hospital = db_row_note['HospitalCode']
        note.patient_id = db_row_note['PatientID']
        note.encounter_id = db_row_note['EncounterID']
        note.enterprise_patient_id = note.patient_id
        note.note_date = str(db_row_note['NoteDate'])
        note.note_id = db_row_note['NoteID']
        note.note_type = db_row_note['NoteType']
        note.note_type_raw = db_row_note['RawNoteType']
        note.note_provider_id = db_row_note['NoteProviderID']
        note.raw_text = db_row_note['NoteText']
        note.pti_update_date = str(db_row_note['UpdateDate'])
        note.pti_received_date = str(db_row_note['AddDate'])
        note.case_id = "{}_{}_{}".format(note.hospital, note.patient_id, note.encounter_id)
        try:
            # Tokenize the note text
            processed_text = process_note(note.raw_text)
            note.text, note.token_offsets, note.sentence_offsets = processed_text['tokenized_text'], \
                                                                   processed_text['token_offsets'], \
                                                                   processed_text['sentence_offsets']
            note.note_length = len(note.text)
        except:
            logging.log(logging.ERROR, "Error in processing one of the notes." + str(physician_note_row_id))
            continue
        if note.text == '':
            # Empty file after the tokenization, skipping this
            continue

        yield note
