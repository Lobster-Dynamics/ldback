import uuid

from application.parser import ParsingResult
from infrastructure.firebase.persistence import (FileMimeType,
                                                 FirebaseFileStorage)

from .document import DocumentImage, ParsedLLMInput


class DocumentProcessor:
    @staticmethod
    def upload_image_to_bucket(image_data):
        storage = FirebaseFileStorage.create_from_firebase_config("images")
        url = storage.add(image_data, FileMimeType.PNG)
        return url

    def from_sections(self, result: ParsingResult):
        list_text = []
        list_document = []

        combined_sections = result.text_sections + result.image_sections
        combined_sections.sort(key=lambda x: x.index)

        for section in combined_sections:
            if isinstance(section.content, str):
                list_text.append(section.content)
            else:
                url = DocumentProcessor.upload_image_to_bucket(section.content)
                new_uuid = uuid.uuid4()
                doc = DocumentImage(location=str(new_uuid), url=url)
                list_document.append(doc)
                list_text.append(str(url))

        return ParsedLLMInput(content=list_text, imageSections=list_document) 
