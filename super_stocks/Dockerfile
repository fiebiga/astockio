FROM python:3.10-slim-buster

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./src .

ENV PYTHONPATH "${PYTHONPATH}:."

RUN chmod 755 entrypoint.sh