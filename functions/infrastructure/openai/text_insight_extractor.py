import math
import uuid
import json
from typing import Dict, List

from openai import OpenAI
from domain.document.document import SummarySection
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

    def _extract_raw_key_concepts_of_fragment(self, text_fragment: str) -> List[str]:
        prompt = f"""
        Given the following text: "{text_fragment}" \n
        pleasae, give me a list of the core concepts within the text. Give me at least 5 core concepts and at most 10 core concepts. 
        Give me the core concepts in a json object with only one attribute "concepts" which is a list of strings which are the core concepts        
        """
        raw_json_reponse = self._get_json_response(prompt)
        return raw_json_reponse["concepts"]

    def _create_key_concept(
        self, document_id: str, key_concept_name: str, vector_store: IVectorStore
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
        Your response should be just raw text.
        """
        description = self._get_response(prompt)
        return KeyConcept(
            id=str(uuid.uuid1()), 
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
        for concept_name in concept_names:
            concepts.append(
                self._create_key_concept(
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
        father_key_concept_json_string = json.dumps(key_concept.model_dump_json())
        key_concepts_strings = ""
        for key_concept in key_concepts:
            key_concepts_strings += json.dumps(key_concept.model_dump_json()) + "\n"
        
        chunks_likeley_to_define_key_concept = vector_store.get_similar_chunks(
            document_id=document_id, text=key_concept.name, k=4
        )
        likeley_to_define_text = ""
        for chunk in chunks_likeley_to_define_key_concept:
            likeley_to_define_text += chunk.text + " "
        
        prompt = f"""
        Consider the following FATHER CONCEPT: {father_key_concept_json_string} \n
        Also consider the following information about that key concept: \n 
        {likeley_to_define_text}
        Also consider the following key concepts: 
        {key_concepts_strings} \n
        Given all the information that I just provided you, please give me a json list of the 
        all the relationships in which the concept that I first gave you: "{key_concept.name}", is the 
        FATHER CONCEPT or a concept in which another concept of all the concepts that I gave you depends.
        Every item of the json list that you provide must follow the following json schema: 
        {r'{"child_concept_id": "Id of the concept dependent in father concept", "description": "description of the relationship"}'}
        """
        raw_relationships = self._get_json_response(prompt)
        relations = json.loads(raw_relationships)
        for relation in relations: 
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
        for key_concept in key_concepts:
            # get concepts in which key concept is father
            relationships_in_which_key_is_father = self._extract_relationships_in_which_concept_is_father(
                key_concept=key_concept, 
                key_concepts=key_concepts, 
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
