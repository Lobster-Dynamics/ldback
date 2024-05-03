from io import BytesIO
from typing import Tuple
from uuid import uuid1
from firebase_admin import App, storage
from google.cloud.storage import Bucket

from application.persistence import IFileStorage, FileMimeType, mimetypes_to_extensions

from .. import FIREBASE_APP, FIREBASE_CONFIG


class FirebaseFileStorage(IFileStorage):
    def __init__(
        self, firebase_app: App, firebase_bucket_name: str, base_directory: str
    ):
        """
        Pass already initialized firebase_app. name of the bucket and the base_directory
        on the bucket where the files will be stored
        """
        self.bucket_name = firebase_bucket_name
        self.bucket: Bucket = storage.bucket(
            app=firebase_app, name=firebase_bucket_name
        )
        self.base_directory = base_directory

    def _get_filename_from_url(self, file_url: str) -> str:
        parts = file_url.split("/")

        # check that url is valid for this bucket
        assert parts[0] == "gs:"
        assert parts[2] == self.bucket_name
        assert parts[3] == self.base_directory

        return parts[4]

    def _file_exists(self, file_url: str) -> bool:
        filename = self._get_filename_from_url(file_url)
        blob_path = f"{self.base_directory}/{filename}"
        return self.bucket.blob(blob_path).exists()

    def add(self, file: BytesIO, mimetype: FileMimeType) -> str:
        document_name = (
            self.base_directory + "/" + str(uuid1()) + mimetypes_to_extensions[mimetype]
        )
        # final_file is ensured to be at the beggining of the stream
        final_file = BytesIO(file.getbuffer())
        blob = self.bucket.blob(document_name)
        blob.upload_from_file(final_file, content_type=mimetype.value, num_retries=2)
        return f"gs://{self.bucket_name}/{document_name}"

    def get(self, file_url: str) -> Tuple[BytesIO, FileMimeType]:
        assert self._file_exists(file_url)
        filename = self._get_filename_from_url(file_url)
        payload = BytesIO()
        blob = self.bucket.blob(filename)
        blob.download_to_file(payload)
        file_mime_type = FileMimeType(blob.content_type)
        return (payload, file_mime_type)

    def delete(self, file_url: str):
        assert self._file_exists(file_url)
        try:
            # Obtain filename from URL
            filename = self._get_filename_from_url(file_url)
            
            blob_path = f"{self.base_directory}/{filename}"
            # Delete the blob using the filename
            self.bucket.blob(blob_path).delete()
            
            print("File deleted successfully")
        except Exception as e:
            print(f"Error deleting file: {e}")

    @classmethod
    def create_from_firebase_config(cls, base_directory: str) -> "FirebaseFileStorage":
        return cls(
            firebase_app=FIREBASE_APP,
            firebase_bucket_name=FIREBASE_CONFIG["storageBucket"],  # type: ignore
            base_directory=base_directory,
        )
