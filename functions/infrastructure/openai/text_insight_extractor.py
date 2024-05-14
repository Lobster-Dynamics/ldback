import json
from typing import List
import os

from openai import OpenAI
from domain.document.document import SummarySection
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

    def _extract_bibliographic_info(self, text_body: str) -> BiblioGraphicInfo:
        bibliographic_info_json_schema = json.dumps(
            BiblioGraphicInfo.model_json_schema()
        )
        prompt = f"""
        Give the following text: "{text_body}" \n
        please, give the bibliographic info of the text in the form of a json object according to the following json schema  {bibliographic_info_json_schema}. \n
        If you cannot find any author in text please refrain from giving any authors, just set the "authors" parameter to an empty array\n.
        If you cannot find a publisher, set the parameter "publisher" to "Unknown". 
        If you cannot find a publishment date, set the parameter "publishmentDate" to null.
        The title of the text MUST be within the document, if you cannot find a title within the document, then just set the "title" parameter to "Unknown".
        """
        raw_bibliographic_info_obj = self._get_json_response(prompt)
        return BiblioGraphicInfo.model_validate(raw_bibliographic_info_obj)

    def _extract_core_concepts(self, text_body: str) -> List[str]:
        prompt = f"""
        Given the following text: "{text_body}" \n
        pleasae, give me a list of the core concepts within the text. Give me at least 5 core concepts and at most 10 core concepts. 
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

    def _extract_summary(self, text_body: str) -> Summary:
        prompt = f"""
        Given the following text: "{text_body}" \n
        Please, give me a comprehensive yet not so extense summary of the text by sections. 
        Each section must have a "title"  attribute  and a "body" attribute. The summary must be an object containing a parameter named "sections" 
        that is an array of the sections. Give me summary in the form of the described json object.        
        """
        raw_json_summary = self._get_json_response(prompt)
        return self._create_summary_from_json(raw_json_summary)

    def extract_insight(self, text_body: str) -> TextInsight:
        return TextInsight(
            bibliografic_info=self._extract_bibliographic_info(text_body),
            key_concepts=self._extract_core_concepts(text_body),
            summary=self._extract_summary(text_body),
        )
