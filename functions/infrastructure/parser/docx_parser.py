from application.parser import IParser, ParsingResult
from docx import Document
from io import BytesIO


class DOCXParser(IParser):
    ...

    def parse(self, file: BytesIO) -> ParsingResult:
        doc = Document(file)
        parse_list = [para.text for para in doc.paragraphs]
        ...
        # return ParsingResult(text=parse_list,images=None)
