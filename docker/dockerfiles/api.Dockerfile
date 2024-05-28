# Dockerfile for development api
FROM python:3.11-alpine

WORKDIR /api 

# here is where the api will be served
EXPOSE 5000 


COPY ./functions/app ./app
COPY ./functions/application ./application
COPY ./functions/cert ./cert
COPY ./functions/domain ./domain
COPY ./functions/infrastructure ./infrastructure
COPY ./functions/__init__.py ./__init__.py
COPY ./functions/dev_app.py ./dev_app.py
COPY ./functions/requirements.txt ./requirements.txt

RUN python3 -m venv ./venv 
RUN . ./venv/bin/activate 
RUN pip install -r requirements.txt
RUN pip uninstall watchdog -y

CMD python ./dev_app.py
