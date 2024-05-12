from flask import Blueprint

middleware_blueprint = Blueprint("middleware_blueprint", __name__)

# prevent circular imports
from .middleware import *