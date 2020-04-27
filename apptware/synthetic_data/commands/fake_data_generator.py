import click
import string
from faker import Faker
import pandas as pd
import datetime
import os
import numpy as np
from pathlib import Path

from elasticsearch import Elasticsearch, helpers

from es_data import factories as es_factories


BASE_PATH = os.path.join(os.path.abspath(
    Path(__file__).parent.as_posix()), "../")
FIXTURES_PATH = os.path.join(BASE_PATH, "fixtures")
SCHEMA_PATH = os.path.join(BASE_PATH, "schema")

SECONDS_LIMIT = 59
MINUTES_LIMIT = 59
HOURS_LIMIT = 23
ADD_DATE_START_MONTH = 4
ADD_DATE_END_MONTH = 7
DAYS_LIMIT = 28
UPDATE_START_MONTH = 8
UPDATE_END_MONTH = 12
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

MYSQL_HOST = 'localhost'
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = 'iamroot'
MYSQL_DB_NAME = 'ptnotes'


fake = Faker()


def hospital_code_gen(gen_values: int, distinct_hosps: int = 10) -> list:
    """
    Returns List of synthetic hospital codes
    Input : Number of values to be generated, Number of distinct hospitals
    Output: List of synthetic hospital codes
    """
    return [
        "{}{}".format("HCST_", str(fake.random.randint(1, distinct_hosps)))
        for _ in range(gen_values)
    ]


def patient_id_gen(gen_values: int, distinct_pats: int = 300) -> list:
    """
    Returns List of synthetic patient ids
    Input : Number of values to be generated, Number of distinct patients
    Output: List of synthetic patient ids
    """
    return [
        "{}{}".format("PATIEND_ID_", str(
            fake.random.randint(1, distinct_pats)))
        for _ in range(gen_values)
    ]


def encounter_id_gen(gen_values: int) -> list:
    """
    Returns List of synthetic encounter ids
    Input : Number of values to be generated
    Output: List of synthetic encounter ids
    """
    return ["{}{}".format("Encounter_ID_", str(value)) for value in range(gen_values)]


def note_id_gen(gen_values: int) -> list:
    """
    Returns List of synthetic note ids
    Input : Number of values to be generated
    Output: List of synthetic note ids
    """
    return ["{}{}".format("Note_ID_", str(value)) for value in range(gen_values)]


def note_type_gen(gen_values: int) -> list:
    """
    Returns List of synthetic note types
    Input : Number of values to be generated
    Output: List of synthetic note types
    """
    note_type_list = [
        "%s%s" % (alphabet, num)
        for alphabet, num in zip(
            string.ascii_uppercase[:10] * 3, list(range(1, 4)) * 10
        )
    ]
    return [
        "NT_" + str(fake.random.choice(note_type_list))
        for _ in range(gen_values)
    ]


def note_provider_id_gen(gen_values: int) -> list:
    """
    Returns List of synthetic note provider ids
    Input : Number of values to be generated
    Output: List of synthetic note provider ids
    """
    provider_list = ["PhysId", "DoctorId"]
    return [
        "{}_{}".format(
            fake.random.choice(provider_list), str(
                fake.random.randint(1, gen_values))
        )
        for _ in range(gen_values)
    ]


def note_status_gen(gen_values: int) -> list:
    """
    Returns List of synthetic note status types
    Input : Number of values to be generated
    Output: List of synthetic note status types
    """
    staus_list = ["Status_1", "Status_2", "Status_3", "Status_4"]
    return [
        "{}{}".format("Note_Status_", str(fake.random.choice(staus_list)))
        for value in range(gen_values)
    ]


def note_text_gen(gen_values: int) -> list:
    """
    Returns List of synthetic note text types
    Input : Number of values to be generated
    Output: List of synthetic note text types
    """
    med_df = pd.read_csv("%s/prescription.csv" % FIXTURES_PATH)
    pres = med_df[med_df["Notes About Confusion "] != "  "]
    note_text_list = pres["Notes About Confusion "].tolist()
    new_note_text_list = [
        text.replace(",", "").replace(";", "") for text in note_text_list
    ]
    return [fake.random.choice(new_note_text_list) for value in range(gen_values)]


def add_source_gen(gen_values: int) -> list:
    """
    Returns List of synthetic add sources
    Input : Number of values to be generated
    Output: List of synthetic add sources
    """
    add_source_list = ["Source_1", "Source_2", "Source_3", "Source_4"]
    return [
        "{}{}".format("Add_", str(fake.random.choice(add_source_list)))
        for _ in range(gen_values)
    ]


def update_source_gen(gen_values: int) -> list:
    """
    Returns List of synthetic update sources
    Input : Number of values to be generated
    Output: List of synthetic update sources
    """
    source_list = ["Source_1", "Source_2", "Source_3", "Source_4"]
    return [
        "{}{}".format("Update_", str(fake.random.choice(source_list)))
        for _ in range(gen_values)
    ]


def raw_note_type_gen(gen_values: int) -> list:
    """
    Returns List of synthetic raw note types
    Input : Number of values to be generated
    Output: List of synthetic raw note types
    """
    raw_note_type_list = [
        "{}{}{}".format("Raw_", alphabet, num)
        for alphabet, num in zip(
            string.ascii_uppercase[:10] * 3, list(range(1, 4)) * 10
        )
    ]

    return [fake.random.choice(raw_note_type_list) for _ in range(gen_values)]


def note_author_type_gen(gen_values: int) -> list:
    """
    Returns List of synthetic note author types
    Input : Number of values to be generated
    Output: List of synthetic note author types
    """
    return [
        "{}{}".format("NoteAuthorType_", str(
            fake.random.randint(1, gen_values)))
        for _ in range(gen_values)
    ]


def id_gen(gen_values: int) -> list:
    """
    Returns List of synthetic ids
    Input : Number of values to be generated
    Output: List of synthetic ids
    """
    return [value for value in range(gen_values)]


def code_id_gen(gen_values: int) -> list:
    """
    Returns List of synthetic code ids
    Input : Number of values to be generated
    Output: List of synthetic code ids
    """
    return ["{}{}".format("code_", str(value)) for value in range(gen_values)]


def name_gen(gen_values: int) -> list:
    """
    Returns List of synthetic names
    Input : Number of values to be generated
    Output: List of synthetic names
    """
    return [str(fake.name()) for _ in range(gen_values)]


def description_gen(gen_values: int) -> list:
    """
    Returns List of synthetic descriptions
    Input : Number of values to be generated
    Output: List of synthetic descriptions
    """
    descr_list = ["Text_1", "Text_2", "Text_3",
                  "Text_4", "Text_5", "Text_6", "Text_7"]
    return [
        "{}{}".format("description", str(fake.random.choice(descr_list)))
        for _ in range(gen_values)
    ]


def timezone_name_gen(gen_values: int) -> list:
    """
    Returns List of synthetic timezone names
    Input : Number of values to be generated
    Output: List of synthetic timezone names
    """
    return [str(fake.timezone()) for _ in range(gen_values)]


def organization(hospital_fk, month_spread, folder: str = "dump"):
    """
    Generates Synthetic Data for Organization table
    hospital_fk : List of Hospital Codes (foreign key)
    """
    file_name_csv = "Organization.csv"
    schema_name = 'create_organization.sql'
    table_name = 'Organization'
    df = pd.DataFrame()

    gen_values = len(set(hospital_fk))
    df["OrgId"] = list(set(hospital_fk))
    df["Name"] = name_gen(gen_values)
    df["TimeZoneName"] = timezone_name_gen(gen_values)
    _, _, update_date = date_gen(gen_values, month_spread)
    df["UpdateDate"] = update_date
    df["UpdateSource"] = update_source_gen(gen_values)
    save_path = os.path.join(BASE_PATH, folder, file_name_csv)
    # Saving CSVs
    df.to_csv(save_path, index=False, encoding="utf8")


def physiciannote(hospital_fk, patient_pk, encounter_pk, note_pk, month_spread, folder: str = "dump"):
    """
    Generates Synthetic Data for physiciannote table
    hospital_fk : List of Hospital Codes (foreign key)
    patient_pk : List of Patient Ids (primary key)
    encounter_pk : List of Encounter Ids (primary key)
    note_pk : List of Note Ids (primary key)
    month_spread : Month Range
    folder: folder to dump data
    Output: Synthetic DataFrame for physiciannote table
    """
    file_name_csv = "STG_PIECES_physiciannote.csv"
    schema_name = 'create_physician_note.sql'
    table_name = 'STG_PIECES_physiciannote'
    df = pd.DataFrame()
    gen_values = len(hospital_fk)
    df["HospitalCode"] = hospital_fk
    df["PatientID"] = patient_pk
    df["EncounterID"] = encounter_pk
    df["NoteID"] = note_pk
    df["NoteType"] = note_type_gen(gen_values)
    df["NoteProviderID"] = note_provider_id_gen(gen_values)
    note_date, add_date, update_date = date_gen(gen_values, month_spread)
    df["NoteDate"] = note_date
    df["NoteStatus"] = note_status_gen(gen_values)
    df["NoteText"] = note_text_gen(gen_values)
    df["AddDate"] = add_date
    df["AddSource"] = add_source_gen(gen_values)
    df["UpdateDate"] = update_date
    df["UpdateSource"] = update_source_gen(gen_values)
    save_path = os.path.join(BASE_PATH, folder, file_name_csv)
    # Saving CSVs
    df.to_csv(save_path, index=False, encoding="utf8")


def physiciannote_properties(hospital_fk, patient_pk, encounter_pk, note_pk, month_spread, folder: str = "dump"):
    """
    Generates Synthetic Data for physiciannote_properties table
    hospital_fk : List of Hospital Codes (foreign key)
    patient_pk : List of Patient Ids (primary key)
    encounter_pk : List of Encounter Ids (primary key)
    note_pk : List of Note Ids (primary key)
    month_spread : Month Range 
    folder: folder to dump data
    Output: Synthetic DataFrame for physiciannote_properties table

    """
    file_name_csv = "physiciannote_properties.csv"
    schema_name = 'create_physician_note_properties.sql'
    table_name = 'physiciannote_properties'
    df = pd.DataFrame()
    gen_values = len(hospital_fk)
    df["HospitalCode"] = hospital_fk
    df["PatientID"] = patient_pk
    df["EncounterID"] = encounter_pk
    df["NoteID"] = note_pk
    df["RawNoteType"] = raw_note_type_gen(gen_values)
    # To support JOIN on provider_type.code
    df["NoteAuthorType"] = code_id_gen(gen_values)
    save_path = os.path.join(BASE_PATH, folder, file_name_csv)
    # Making some rows of RawNoteType and NoteAuthorType as null
    df = add_null_distn(df=df, columns=["RawNoteType", "NoteAuthorType"])
    # Saving CSVs
    df.to_csv(save_path, index=False, encoding="utf8")


def provider_type(param, folder: str = "dump") -> (list, list, list, list, int):
    """
    Generates Synthetic Data for provider_type table
    Input: param(Parameter) to the program (10, 100, 1000)
    folder: folder to dump data
    Output: Synthetic DataFrame for provider_type table
    """
    file_name_csv = "provider_type.csv"
    df = pd.DataFrame()
    hospital_fk, patient_pk, encounter_pk, note_pk, month_spread = get_pk(
        param=param)
    gen_values = len(hospital_fk)
    df["id"] = id_gen(gen_values)
    # OrgID is same as the Hospital code
    df["org_id"] = hospital_fk
    df["code"] = code_id_gen(gen_values)
    df["name"] = name_gen(gen_values)
    df["description"] = description_gen(gen_values)
    _, _, update_date = date_gen(gen_values, month_spread)
    df["update_date"] = update_date
    df["update_source"] = update_source_gen(gen_values)
    save_path = os.path.join(BASE_PATH, folder, file_name_csv)
    # Adding null distribution to some columns which are not primary key
    df = add_null_distn(df=df, columns=["description"])
    df.to_csv(save_path, index=False, encoding="utf8")

    return hospital_fk, patient_pk, encounter_pk, note_pk, month_spread


def date_gen(gen_values: int, month_spread: int, month: str or int = datetime.datetime.now().strftime("%m"),
             year: str or int = datetime.datetime.now().strftime("%Y")) -> list:
    """
    Returns List of synthetic add dates
    Input : Number of values to be generated
    Output: List of synthetic add dates
    """
    month = int(month)
    year = int(year)
    add_date, note_date, update_date = [], [], []
    for _ in range(gen_values):
        # month_delta handles if the value of month is above 12
        month_delta = month + month_spread
        start_date = datetime.datetime(
            year+month_delta//12,
            fake.random.randint(month, month_delta % 12),
            fake.random.randint(1, DAYS_LIMIT),
            fake.random.randint(0, HOURS_LIMIT),
            fake.random.randint(0, MINUTES_LIMIT),
            fake.random.randint(0, SECONDS_LIMIT),
        )

        note_date.append(start_date.strftime(TIMESTAMP_FORMAT))
        add_ = start_date + \
            datetime.timedelta(fake.random.randint(
                1, 60), fake.random.randint(1, 3600))
        add_date.append(add_.strftime(TIMESTAMP_FORMAT))
        update_ = add_ + \
            datetime.timedelta(fake.random.randint(
                1, 60), fake.random.randint(1, 3600))
        update_date.append(update_.strftime(TIMESTAMP_FORMAT))

    return note_date, add_date, update_date


def get_patients_range(param: int or str) -> dict:
    """
    Returns Dictionary with specified constraints
    Input: param(Parameter) to the program (10, 100, 1000)
    Output: Dictionary
    """
    param = int(param)
    dict_patients_count = {
        10: [(100, 500), 2],
        100: [(1000, 3000), 6],
        1000: [(10000, 15000), 12]
    }
    return dict_patients_count.get(param)


def get_pk(param: int or str) -> (list, list, list, list, int):
    """
    Returns Lists of primary keys for the table
    Input: param(Parameter) to the program (10, 100, 1000)
    Output: Lists
    """
    param = int(param)
    patient_spread, month_spread = get_patients_range(param)
    hospital_fk, patient_pk, encounter_pk, note_pk = [], [], [], []
    for hospital in range(fake.random.randint(5, 10)):
        for patient in range(fake.random.randint(*patient_spread)):
            for encounter in range(fake.random.randint(1, 4)):
                for note in range(fake.random.randint(10, 24)):
                    hospital_fk.append("HCST_{}".format(hospital))
                    patient_pk.append("PATIENT_ID_{}".format(patient))
                    encounter_pk.append("Encounter_ID_{}".format(encounter))
                    note_pk.append("Note_ID_{}".format(note))
    return hospital_fk, patient_pk, encounter_pk, note_pk, month_spread


def null_mask(series: pd.Series, true_perc: float = .2, false_perc: float = .8) -> np.array:
    """
    Create mask of boolean with percentage distribution to a series
    series: Pandas Series
    true_perc: True percentage distribution
    false_perc: False percentage distribution
    Output: mask
    """
    mask = np.random.choice([True, False], size=series.shape, p=[
                            true_perc, false_perc])
    return mask


def add_null_distn(df: pd.DataFrame, columns: list):
    """
    Create null distribution to a DataFrame columns
    df: DataFrame
    columns: list of columns where to a null values
    Output: DataFrame after applying null distribution on columns
    """
    for column in columns:
        df[column] = df[column].mask(null_mask(df[column]))
    else:
        # Returning DataFrame after successfully applying null distribution on all columns
        return df


def run_note_preprocessor(param: str or int, folder: str) -> None:
    """
    Exceutes functions provided
    Input: param(Parameter) to the program (10, 100, 1000)
    Output: Exceutes functions provided
    """
    Path(os.path.join(BASE_PATH, folder)).mkdir(parents=True, exist_ok=True)
    param = int(param)
    hospital_fk, patient_pk, encounter_pk, note_pk, month_spread = provider_type(
        param, folder)
    organization(hospital_fk, month_spread, folder)
    physiciannote_properties(hospital_fk, patient_pk,
                             encounter_pk, note_pk, month_spread, folder)
    physiciannote(hospital_fk, patient_pk, encounter_pk,
                  note_pk, month_spread, folder)
    print("Table Size/No of rows :{} for all the table".format(len(hospital_fk)))


def run_active_learner(param: str or int, folder: str) -> None:
    param = int(param)
    ann_batch = es_factories.AnnFactory.create_batch(param)
    relos_batch = es_factories.RelosFactory.create_batch(param)
    relos_ann_batch = es_factories.RelosAnnFactory.create_batch(param)

    client = Elasticsearch(hosts=["localhost"])

    print("Adding Ann items")
    actions = (item.to_dict(True) for item in ann_batch)
    helpers.bulk(client, actions)

    print("Adding Relos items")
    actions = (item.to_dict(True) for item in relos_batch)
    helpers.bulk(client, actions)

    print("Adding RelosAnn items")
    actions = (item.to_dict(True) for item in relos_ann_batch)
    helpers.bulk(client, actions)


def run_kermit(param: str or int, folder: str) -> None:
    param = int(param)
    ann_batch = es_factories.AnnFactory.create_batch(param)
    relos_batch = es_factories.RelosFactory.create_batch(param)

    client = Elasticsearch(hosts=["localhost"])

    print("Adding Ann items")
    actions = (item.to_dict(True) for item in ann_batch)
    helpers.bulk(client, actions)

    print("Adding Relos items")
    actions = (item.to_dict(True) for item in relos_batch)
    helpers.bulk(client, actions)


@click.command()
@click.option(
    "-m",
    "--module_name",
    "module_name",
    help="Name of module to generate data fors",
    required=True,
)
@click.option(
    "-p",
    "--parameter",
    "param",
    help="Number of data rows to generate",
    required=True,
)
@click.option(
    "-f", "--folder", "folder", help="Folder to dump data files into", default="dump"
)
def generate_fake_data(param, module_name, folder: str = "dump"):
    click.echo("Generating fake data for module: %s" % module_name)
    if module_name == "note_preprocessor":
        run_note_preprocessor(param, folder)
    elif module_name == "active_learner":
        run_active_learner(param, folder)
    elif module_name == "kermit":
        run_kermit(param, folder)


if __name__ == "__main__":
    generate_fake_data()
