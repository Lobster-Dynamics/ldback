from flask import Blueprint

directory_blueprint = Blueprint('directory_blueprint', __name__)

# prevent circular imports
from .get_directory import *