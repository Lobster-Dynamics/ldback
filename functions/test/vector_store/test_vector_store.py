import os
import pytest

from domain.document.ivector_store import ResultingChunk
from infrastructure.vector_store.vector_store import VectorStore

def test_insert():
    test_prompt="Hello, this is a test to test in the test about testing the vector test give me tests test I love tests tests are great I am normal and I love tests."
    testing_vector = VectorStore(os.environ["OPENAI_API_KEY"], os.environ["PINECONE_API_KEY"])
    testing_vector.insert(document_id="1", text=test_prompt)
    assert True
    