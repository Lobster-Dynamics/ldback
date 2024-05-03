from io import BytesIO
import os

import pytest

from application.parser.iparser import ParsingResult
from infrastructure.parser.pdf_parser import PDFParser


def _readfile(path: str) -> BytesIO:
    with open(path, "rb") as file:
        return BytesIO(file.read())


@pytest.fixture
def assets_dir() -> str:
    return f"{os.path.dirname(__file__)}/assets"


@pytest.fixture
def parser() -> PDFParser:
    return PDFParser()


def test_returns_correct_type(assets_dir: str, parser: PDFParser):
    file_bytes = _readfile(f"{assets_dir}/pdf1.pdf")
    res = parser.parse(file_bytes)
    assert isinstance(res, ParsingResult)


def test_all_images_extracted_from_pdf1(assets_dir: str, parser: PDFParser):

    file_bytes = _readfile(f"{assets_dir}/pdf1.pdf")
    res = parser.parse(file_bytes)
    assert len(res.image_sections) == 1


def test_correct_indexes_of_sections(assets_dir: str, parser: PDFParser):
    file_bytes = _readfile(f"{assets_dir}/pdf1.pdf")
    res = parser.parse(file_bytes)

    indexes = []

    for image_section in res.image_sections:
        if image_section.index in indexes:
            raise BaseException(
                f"THERE IS AN IMAGE SECTION WITH INDEX {image_section.index} WHEN THAT INDEX HAS ALREADY BEEN USED BY ANOTHER SECTION"
            )
        indexes.append(image_section.index)

    for text_section in res.text_sections:
        if text_section.index in indexes:
            raise BaseException(
                f"THERE IS A TEXT SECTION WITH INDEX {text_section.index} WHEN THAT INDEX HAS ALREADY BEEN USED BY ANOTHER SECTION"
            )
        indexes.append(text_section.index)

    indexes.sort()
    if len(indexes) == 0:
        return
    if indexes[0] != 0:
        raise BaseException(f"INDEX OF SECTIONS MUST START AT 0")
    for i in range(1, len(indexes)):
        if indexes[i] != indexes[i - 1] + 1:
            raise BaseException(
                f"THERE IS A GAP BETWEEN THE INDEXES {indexes[i-1]} AND {indexes[i]}"
            )
