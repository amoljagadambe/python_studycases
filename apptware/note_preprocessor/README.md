# This repository is used to preprocess notes

Read the notes from MySQL note table and index to ES hospital_txt as they are processed.

## Setup

Download spacy english language model
`pip install -r requirements.txt`
`python -m spacy download en_core_web_sm`

## Local Environment for development (docker)

`docker run -p 3306:3306 -p 9200:9200 <synthetic_data_image> -m <note_preprocessor> -n <number-of-rows>`

## Manage commands

### Run tests

`pytest tests`

### Batch run

Batch run needs mysql and es credentials which can be taken from:

- Environment variables
    This takes data from environment file `.env` file
    To start with copy the `local-sample.env` file in this repo to `.env` file

    ```bash
    cp local-sample.env .env
    ```

    Command: `python commands/batch_run.py -s <start-date> -e <end-date>`
    Date format - `YYYY-MM-DD HH:MM:SS`

- Secrets manager
    This pulls credentials from secrets manager using the secrets name

    Command: `python commands/batch_run.py -s <start-date> -e <end-date> -x <secret-name>`

### Synthetic data creation

Fake data generator script:
Creates the data based on specific table and with its columns properties

As of now 3 csv are generated:
- physiciannote
- physiciannote_properties
- provider_type

**Input**: Number of rows to be generated i.e Table Size, Table Name
**Output**: Creates an csv file based on Table Size, Table Name , Dumps the data into the folder.

## Table schema

### Physiciannote
Columns:
- PhysicianNoteRowID
- HospitalCode
- PatientID
- EncounterID
- NoteID
- NoteType
- NoteProviderID
- NoteDate
- NoteStatus
- NoteText
- AddDate
- AddSource
- UpdateDate
- UpdateSource

### Physiciannote_properties
Columns:
- HospitalCode
- PatientID
- EncounterID
- NoteID
- RawNoteType
- NoteAuthorType

**Primary key**: (PatientID, EncounterID, HospitalCode, NoteID)
**Foreign keys**: RawNoteType -> NoteType

### Provider_type
Columns:
- id (Auto-incremented primary key)
- org_id (The organization to which this provider type applies)
- code (A short code representing the provider type.  This is typically the value received from the client organization)
- name (The common name for the provider type)
- description (A more detailed description for the provider type)
- update_date (The date/time this record was created or last updated (based on the database server clock)
- update_source (The identity of the person or process that last updated this record)

**Unique constraint**: (org_id, code)
**Foreign keys**: org_id -> Organization
