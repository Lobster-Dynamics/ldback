from io import BytesIO

from .. import celery_app

@celery_app.task # type: ignore
def create_document(creator: str, file: BytesIO):
    """ Entrypoint for the task of creating a document
    Creating a document involves the following actions: 
    1- Parse the document 
    2- Uploading it to persistence 
    3- publishing the event
    """
    ...