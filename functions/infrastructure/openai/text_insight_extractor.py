import math
import json
from typing import List
import os

from openai import OpenAI
from domain.document.document import SummarySection
from domain.document.ivector_store import IVectorStore
from domain.document.itext_insight_extractor import (
    ITextInsightExtractor,
    TextInsight,
    BiblioGraphicInfo,
    Summary,
)


class OpenAITextInsightExtractor(ITextInsightExtractor):
    def __init__(self, api_key: str):
        # TODO: parametryze configuration params
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"

    def _fragment_iterator(self, chunks: List[str], k: int): 
        for i in range(math.ceil(len(chunks) / k)):
            text_fragment = ""
            for j in range(i*k, i*k+k):
                if j < len(chunks):
                    text_fragment += chunks[j]
            yield text_fragment

    def _get_response(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant chatbot meant to examinate texts and return reponses based soleley on the informatino contained within the texts",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={"type": "json_object"},
        )

        return completion.choices[0].message.content  # type: ignore

    def _get_json_response(self, prompt: str) -> dict:
        json_string = self._get_response(prompt)
        try:
            return json.loads(json_string)
        except json.decoder.JSONDecodeError as inst:
            raise BaseException("OPENAI MODEL RETURN NON JSON STRING")

    def _extract_bibliographic_info(self, document_id: str, vector_store: IVectorStore) -> BiblioGraphicInfo:
        bibliographic_info_json_schema = json.dumps(
            BiblioGraphicInfo.model_json_schema()
        )
        # get most likeley chunks to get the bibliographic info
        chunks = vector_store.get_similar_chunks(document_id, 4, "Bibliographical info, Authors. Publishment date and details. Publisher")
        
        # merge chunks into text
        
        text = ""
        for chunk in chunks: 
            text += chunk.text
        
        prompt = f"""
        I have a large original text and extracted the fragments that are more likeley\n
        to contain the bibliographic info of the text\n
        Give the following text fragments: "{text}" \n
        please, give the bibliographic info of the text in the form of a json object according to the following json schema  {bibliographic_info_json_schema}. \n
        If you cannot find any author in text please refrain from giving any authors, just set the "authors" parameter to an empty array\n.
        If you cannot find a publisher, set the parameter "publisher" to "Unknown". 
        If you cannot find a publishment date, set the parameter "publishmentDate" to null.
        The title of the text MUST be within the document, if you cannot find a title within the document, then just set the "title" parameter to "Unknown".
        """
        raw_bibliographic_info_obj = self._get_json_response(prompt)
        return BiblioGraphicInfo.model_validate(raw_bibliographic_info_obj)

    def _extract_core_concepts_of_fragment(self, text_fragment: str) -> List[str]:
        prompt = f"""
        Given the following text: "{text_fragment}" \n
        pleasae, give me a list of the core concepts within the text. Give me at least 5 core concepts and at most 10 core concepts. 
        Give me the core concepts in a json object with only one attribute "concepts" which is a list of strings which are the core concepts        
        """
        raw_json_reponse = self._get_json_response(prompt)
        return raw_json_reponse["concepts"]

    def _extract_core_concepts(self, text_chunks: List[str]) -> List[str]:
        concepts = []
        
        # for each four chunks
        for text_fragment in self._fragment_iterator(text_chunks, 4):
            concepts = [
                *concepts, 
                *self._extract_core_concepts_of_fragment(text_fragment)
            ]

        prompt = f"""
        Given the following list of concepts: "{str(concepts)}" \n
        please, give me a list of the most repeated concepts in the list. If two concepts are really 
        similar and can be taken as one, then consider them one \n
        Give me a list of at least 5 elements and at most 10 elements of the most repeated concepts taking into consideration 
        also similar concepts \n. 
        Give me the core concepts in a json object with only one attribute "concepts" which is a list of strings which are the core concepts
        """
        raw_json_reponse = self._get_json_response(prompt)
        return raw_json_reponse["concepts"]

    def _create_summary_from_json(self, data: dict) -> Summary:
        assert isinstance(data["sections"], list)
        sections = []
        for section in data["sections"]:
            assert isinstance(section["title"], str)
            assert isinstance(section["body"], str)
            sections.append(
                SummarySection(title=section["title"], body=section["body"])
            )
        return Summary(secctions=sections)

    def _extract_section_summary(self, text: str) -> List[dict]:
        prompt = f"""
        Given the following text: "{text}" \n
        Please, give me a comprehensive yet not so extense summary of the text by sections. 
        Each section must have a "title"  attribute  and a "body" attribute. The summary must be an object containing a parameter named "sections" 
        that is an array of the sections. Give me summary in the form of the described json object.        
        """
        return self._get_json_response(prompt)

    def _extract_summary(self, text_chunks: List[str]) -> Summary:
        sections = []
        for text_fragment in self._fragment_iterator(text_chunks, 4):
            sections = [*sections, *self._extract_section_summary(text_fragment)["sections"]]
        
        return self._create_summary_from_json({"sections": sections})

    def extract_insight(self, document_id: str, text_chunks: List[str], text_vector_store: IVectorStore) -> TextInsight:
        return TextInsight(
            bibliografic_info=self._extract_bibliographic_info(document_id, text_vector_store),
            key_concepts=self._extract_core_concepts(text_chunks),
            summary=self._extract_summary(text_chunks),
        )
