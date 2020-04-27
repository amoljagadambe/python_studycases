FROM python:3.5-slim AS compile-image

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.0/en_core_web_sm-2.2.0.tar.gz

FROM python:3.5-slim AS build-image
COPY --from=compile-image --chown=1000:3000 /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

# Copy the code/program
COPY --chown=1000:3000 batch_run.py /app/batch_run.py
COPY --chown=1000:3000 note_preprocessor /app/note_preprocessor
COPY --chown=1000:3000 README /app/README

USER 1000:3000

ENTRYPOINT ["python", "/app/batch_run.py"]

CMD []
