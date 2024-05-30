from flask import Blueprint

document_blueprint = Blueprint("document_blueprint", __name__)

# prevent circular imports
from .upload_document import *
from .get_document import *
from .get_documents import *
from .delete_document import *
from .rename_document import *
from .generate_word_cloud import *
from .get_message import *
from .search_document import *
from .delete_key_concept import *
from .get_all_messages import *
from .get_explanation import *
from .share_document import *
from .get_explanations import *
