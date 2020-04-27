# About

This repository is used to generate synthetic data for local development and tests

The docker image built from this repository contains:

- MySQL v5.7.18 with appropriate schema - exposed on port 3306
- Elasticsearch v7.1.1 with appropriate schema - exposed on port 9200
- python code to generate fake/synthetic data - exposed as entrypoint, accepts extra arguments

On running the docker image (with `module_name` and `extra_args` as arguments):

- it spins up MySQL & Elasticsearch
- executes a python script to generate fake data (based on `module_name` and `extra_args`) and writes it to a csv (inside the container itself)
- loads the csv to MySQL and/or Elasticsearch (basesd on `module_name`)

## How to run

```bash
docker run --name $CONTAINER_NAME -p $MYSQL_PORT:3306 -p $ELASTICSEARCH_PORT:9200 $IMAGE:$TAG

docker exec -it $CONTAINER_NAME /app/scripts/gen_data.sh $MODULE_NAME $MODULE_PARAMS
```

Here, `MODULE_NAME` is the module we want to generate fake data for. Example: "note_preprocessor"

## Synthetic data creation (Python script)

Fake data generator script:
Creates the data based on specific table and with its columns properties

As of now 3 csv are generated:

- physiciannote
- physiciannote_properties
- provider_type

**Input**: Number of rows to be generated i.e Table Size, Table Name
**Output**: Creates an csv file based on Table Size, Table Name , Dumps the data into the folder.

### Table schema

#### Physiciannote

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

#### Physiciannote_properties

Columns:

- HospitalCode
- PatientID
- EncounterID
- NoteID
- RawNoteType
- NoteAuthorType

**Primary key**: (PatientID, EncounterID, HospitalCode, NoteID)
**Foreign keys**: RawNoteType -> NoteType

#### Provider_type

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
