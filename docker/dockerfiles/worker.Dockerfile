# Dockerfile for development api
FROM python:3.11-alpine

WORKDIR /api 

# here is where the api will be served

COPY ./functions/app ./app
COPY ./functions/application ./application
COPY ./functions/cert ./cert
COPY ./functions/domain ./domain
COPY ./functions/infrastructure ./infrastructure
COPY ./functions/__init__.py ./__init__.py
COPY ./functions/celery_entrypoint.py ./celery_entrypoint.py
COPY ./functions/requirements.txt ./requirements.txt
COPY ./functions/.api.env ./.api.env

RUN python3 -m venv ./venv 
RUN . ./venv/bin/activate 
RUN pip install -r requirements.txt

CMD celery -A celery_entrypoint worker --loglevel=INFO
