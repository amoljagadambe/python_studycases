FROM python:3.8-slim AS compile-image

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.8-slim AS build-image
COPY --from=compile-image --chown=1000:3000 /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/

ENV PYTHONPATH .

# Copy the code/program
COPY --chown=1000:3000 load_env.py /app/load_env.py
COPY --chown=1000:3000 commands /app/commands
COPY --chown=1000:3000 active_learner /app/active_learner

USER 1000:3000

ENTRYPOINT ["python", "commands/batch_run.py"]

CMD []
