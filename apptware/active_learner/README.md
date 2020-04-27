# README

This repository is used to apply active learner on annotations. For detailed documentation, see [Confluence](https://piecestech.atlassian.net/wiki/spaces/AE/pages/97157158/Active+Learner+Module)

## Setup

`pip install -r requirements.txt`

## Local Environment for development (docker)

```bash
docker run --name sd-local -p 3306:3306 -p 9200:9200 $SYNTHETIC_DATA_IMAGE

docker exec $CONTAINER_NAME /app/scripts/gen_data.sh active_learner $PARAMS
```

Here, $PARAMS can be any positive integer value. The synthetic data image will generate that many number of rows of synthetic data for this module.

## Manage commands

### Run tests

`pytest tests`

### Batch run

Batch run needs mysql and es credentials which can be taken from:

- Environment vriables
  This takes data from environment file `.env` file
    To start with copy the `local-sample.env` file in this repo to `.env` file

    ```bash
    cp local-sample.env .env
    ```

    Command: `python commands/batch_run.py -s <start-date> -e <end-date> --is-local`
    Date format - `YYYY-MM-DD HH:MM:SS`

- Secrets manager
  This pulls credentials from secrets manager using the secrets name

  Command: `python commands/batch_run.py -s <start-date> -e <end-date> -x <secret-name>`
