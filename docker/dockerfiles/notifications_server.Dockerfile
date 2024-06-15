FROM python:3.11-alpine


# here is where the api will be served
WORKDIR /notsser 

EXPOSE 8000

COPY ./functions/cert ./cert
COPY ./functions/application ./application
COPY ./functions/domain ./domain
COPY ./functions/infrastructure ./infrastructure
COPY ./functions/__init__.py ./__init__.py
COPY ./functions/requirements.txt ./requirements.txt
COPY ./functions/notifications_server ./notifications_server
COPY ./functions/notifications_entrypoint.py ./notifications_entrypoint.py
COPY ./functions/.api.env ./.api.env


RUN python3 -m venv ./venv 
RUN . ./venv/bin/activate 
RUN pip install -r requirements.txt
RUN pip install fastapi

CMD python ./notifications_entrypoint.py
