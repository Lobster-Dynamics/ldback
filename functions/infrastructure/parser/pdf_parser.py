from application.parser import IParser, ParsingResult
from application.parser.iparser import DocSection
from PyPDF2 import PdfReader
from typing import List, Any
from io import BytesIO

class PDFParser(IParser):
   def parse(self, file: BytesIO) -> ParsingResult:
        # Initialize a PDF file reader
        pdf = PdfReader(file)
        
        # Initialize the text and images list
        paragraphs = List[DocSection[str]] = []
        imagesAll = List[DocSection[Any]] = []
        counter = 0
        
        # Extract text from each page
        for page in range(len(pdf.pages)):
            page_text = pdf.pages[page].extract_text()

            lines = page_text.split('\n')
            
            paragraph = ""

            for line in lines:
                if line.strip() != "":
                    paragraph += " " + line.strip()
                elif paragraph != "":
                    paragraphs.append(DocSection[str](index = counter,content = paragraph.strip()))
                    paragraph = ""
                    counter += 1
            if paragraph != "":
                paragraphs.append(DocSection[str](index = counter,content = paragraph.strip()))
                counter += 1

            for image_file_object in page.images:
                imagesAll += (DocSection(counter, image_file_object.data))
                counter += 1

        return ParsingResult(text_sections=paragraphs, image_sections=imagesAll)
