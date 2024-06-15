import json

from flask import jsonify
from infrastructure.firebase.persistence.repos.document_repo import FirebaseDocumentRepo
from infrastructure.counter.TextCounter import TextAnalyzer
from . import document_blueprint
from domain.document.document import WordCloud

@document_blueprint.route("/generate_word_cloud/<id>", methods=["GET"])
def get_word_cloud_handle(id):
    # Se manda a llamar la clase de firebasedocumentsrepo
    repo = FirebaseDocumentRepo()
    filter = TextAnalyzer()

    # Se consigue la respuesta
    document = repo.get(str(id))

    if document:

        wordcloud = document.wordcloudinfo
        
        # filtered_text = filter.remove_stopwords(document.parsed_llm_input)

        # response = filter.word_cloud_filter(filtered_text)

        # word_cloud_list = []

        # for word, value in response.items():
        #     # Append new WordCloud instances to the list with text and value
        #     word_cloud_list.append(WordCloud(text=word, value=value).model_dump())

         # Ensure wordcloud is a list of WordCloud objects
        if isinstance(wordcloud, list) and all(isinstance(wc, WordCloud) for wc in wordcloud):
            # Serialize each WordCloud object in the list
            wordcloud = [wc.model_dump() for wc in wordcloud]


                
        return jsonify(wordcloud), 200
    else:
        return jsonify({"error": "Document not found"}), 400
