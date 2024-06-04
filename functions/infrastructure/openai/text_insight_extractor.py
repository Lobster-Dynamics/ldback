import logging
logger = logging.getLogger(__name__)
import math
import uuid
import json
from typing import Dict, List

from openai import OpenAI
from domain.document.document import SummarySection, Relationship
from domain.document.ivector_store import IVectorStore
from domain.document.itext_insight_extractor import (
    ITextInsightExtractor,
    TextInsight,
    BiblioGraphicInfo,
    Summary,
    KeyConcept, 
    Relationship
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

    def _get_json_response(self, prompt: str) -> dict | list:
        json_string = self._get_response(prompt)
        try:
            return json.loads(json_string)
        except json.decoder.JSONDecodeError as inst:
            raise BaseException("OPENAI MODEL RETURN NON JSON STRING")

    def _extract_bibliographic_info(self, document_id: str, vector_store: IVectorStore) -> BiblioGraphicInfo | None:
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
        try: 
            return BiblioGraphicInfo.model_validate(raw_bibliographic_info_obj)
        except BaseException as inst:
            return None

    def _extract_raw_key_concepts_of_fragment(self, text_fragment: str) -> List[str]:
        prompt = f"""
        Given the following text: "{text_fragment}" \n
        pleasae, give me a list of the core concepts within the text. Give me at least 5 core concepts and at most 10 core concepts. 
        Give me the core concepts in a json object with only one attribute "concepts" which is a list of strings which are the core concepts        
        """
        raw_json_reponse = self._get_json_response(prompt)
        return raw_json_reponse["concepts"]

    def _create_key_concept(
        self, concept_id: str, document_id: str, key_concept_name: str, vector_store: IVectorStore
    ) -> KeyConcept:
        """ Creates key concepts without its relationships """
        chunks_likeley_to_define_key_concept = vector_store.get_similar_chunks(
            document_id=document_id, text=key_concept_name, k=4
        )
        likeley_to_define_text = ""
        for chunk in chunks_likeley_to_define_key_concept:
            likeley_to_define_text += chunk.text + " "
        prompt = f"""
        Given the following text:"{likeley_to_define_text}" \n
        try to briefly and concisely define the following concept: "{key_concept_name}".
        Your response should be a json object with an attrbute called "definition"
        """
        description = self._get_json_response(prompt)["definition"]
        return KeyConcept(
            id=concept_id, 
            name=key_concept_name, 
            description=description, 
            relationships=[]
        )

    def _extract_key_concepts(
        self, 
        document_id: str, 
        vector_store: IVectorStore, 
        text_chunks: List[str]
    ) -> List[KeyConcept]:
        concepts = []
        
        # for each four chunks
        for text_fragment in self._fragment_iterator(text_chunks, 4):
            concepts = [
                *concepts, 
                *self._extract_raw_key_concepts_of_fragment(text_fragment)
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
        
        concept_names = raw_json_reponse["concepts"]
        concepts = []
        for i, concept_name in enumerate(concept_names):
            concepts.append(
                self._create_key_concept(
                    concept_id=str(i),
                    document_id=document_id, 
                    key_concept_name=concept_name, 
                    vector_store=vector_store
                )
            )

        return concepts

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


    def _extract_relationships_in_which_concept_is_father(
        self, 
        key_concept: KeyConcept, 
        key_concepts: List[KeyConcept],
        vector_store: IVectorStore,
        document_id: str,     
    ) -> List[Relationship]:
        relationships = []
        
        # dont give the model a lot of ids or it will get confused
        father_key_concept_json  = key_concept.model_dump()
        father_key_concept_json["relationships"] = []
        father_key_concept_json_string = json.dumps(father_key_concept_json, indent=3)
        
        key_concepts_strings = ""
        for kkey_concept in key_concepts:
            if kkey_concept.id != key_concept.id:
                key_concept_json = kkey_concept.model_dump()
                key_concept_json["relationships"] = []
                key_concepts_strings += json.dumps(key_concept_json, indent=3) + "\n"
        
        chunks_likeley_to_define_key_concept = vector_store.get_similar_chunks(
            document_id=document_id, text=key_concept.name, k=4
        )
        likeley_to_define_text = ""
        for chunk in chunks_likeley_to_define_key_concept:
            likeley_to_define_text += chunk.text + " "
        

        prompt = f"""
        The task that you should perform is the following.\n 
        I am going to give you a MAIN CONCEPT and a list of other concepts. \n
        If there is a necessity to understand the MAIN CONCEPT to also understand \n 
        a concept of the list of other concepts, then those concepts are related. \n
        This is the MAIN CONCEPT: {father_key_concept_json_string} \n
        
        The following text should give you more information about the meaning of the MAIN CONCEPT: \n 
        "{likeley_to_define_text}"
        
        The list of the other concepts is the following: 
        {key_concepts_strings} \n
        
        Given all the information that I just provided you, please give me a json object that has \n
        an attribute called "relationships", this attribute is a list of json objects which represent relationships \n 
        . Each relationship is an association between the MAIN CONCEPT and another concept from the list of other concepts that I gave you.
        In each relationship it is necesarry that the MAIN CONCEPT is necesarry to understand the other concept of the relationship.\n
        Only provide the realationships that you consider to be true and do not add extra unecessary relationships. \n
        Also, the MAIN CONCEPT can have AT MOST ONE relationship with each other concept of the list that I gave you. \n 
        Every item of the attribute "relationships" that you provide must follow the following json schema: 
        {r'{"child_concept_id": "Id of the concept dependent in father concept", "description": "description of the relationship and how the father concept relates to the child concept. a description of the interaction of both concepts"}'} \n
        The description of the relationships should be in the same language as the text that gives you more information about the MAIN CONCEPT. \n
        """

        raw_relationships = self._get_json_response(prompt)

        for relation in raw_relationships["relationships"]: 
            relationships.append(
                Relationship(
                    id=str(uuid.uuid1()), 
                    fatherConceptId=key_concept.id, 
                    childConceptId=relation["child_concept_id"], 
                    description=relation["description"]
                )
            )
        return relationships

    def extract_insight(self, document_id: str, text_chunks: List[str], text_vector_store: IVectorStore) -> TextInsight:
        key_concepts = self._extract_key_concepts(
            document_id=document_id,
            vector_store=text_vector_store, 
            text_chunks=text_chunks
        )
        ids_to_key_concepts: Dict[str, KeyConcept] = \
            {key_concept.id: key_concept for key_concept in key_concepts}

        relationships = []
        for i, key_concept in enumerate(key_concepts):
            if i == len(key_concepts) - 1:
                continue
            # get concepts in which key concept is father
            relationships_in_which_key_is_father = self._extract_relationships_in_which_concept_is_father(
                key_concept=key_concept, 
                key_concepts=key_concepts[i+1:], 
                vector_store=text_vector_store, 
                document_id=document_id
            )
            # add each concept to a father and child concept
            for relationship in relationships_in_which_key_is_father:
                ids_to_key_concepts[relationship.father_concept_id].relationships.append(relationship.id)
                ids_to_key_concepts[relationship.child_concept_id].relationships.append(relationship.id)
            relationships = [*relationships, *relationships_in_which_key_is_father]
        
        return TextInsight(
            bibliografic_info=self._extract_bibliographic_info(document_id, text_vector_store),
            key_concepts=key_concepts,
            summary=self._extract_summary(text_chunks),
            relationships=relationships
        )
