from io import BytesIO
from typing import List, Any

from docx2python import docx2python

from application.parser import IParser, ParsingResult
from application.parser.iparser import DocSection


class DOCXParser(IParser):
    """NOTE:
    This parser is not perfect
    It takes into consideration that there are at most 10,000 images in the
    text and that the text does not have matches for the following
    regular expresssion "----media/image[0-99999].jpeg----"
    This is due to the fact that that text is the placeholder for images in the
    text representation of the document
    """

    def parse(self, file: BytesIO) -> ParsingResult:
        text_sections: List[DocSection[str]] = []
        image_sections: List[DocSection[Any]] = []

        with docx2python(file) as docfile:
            img_names_to_bytesio = {}
            for name, img_bytes in docfile.images.items():
                img_names_to_bytesio[f"----media/{name}----"] = BytesIO(img_bytes)

            index = 0
            for tab in docfile.body_runs:
                for table in tab:
                    for row in table:
                        for cell in row:
                            # if an element of the cell is an image key then the whole cell is the image
                            indx = index
                            text_sections_buf: List[DocSection[str]] = []
                            inserted_image = False
                            for str_element in cell:
                                if str_element in img_names_to_bytesio.keys():
                                    image_sections.append(
                                        DocSection[Any](
                                            index=index,
                                            content=img_names_to_bytesio[str_element],
                                        )
                                    )
                                    index += 1
                                    inserted_image = not inserted_image
                                    break
                                text_sections_buf.append(
                                    DocSection[str](index=indx, content=str_element)
                                )
                                indx += 1
                            if not inserted_image:
                                index = indx
                                text_sections = [*text_sections, *text_sections_buf]

        return ParsingResult(text_sections=text_sections, image_sections=image_sections)
