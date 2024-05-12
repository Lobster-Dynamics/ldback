from flask import Blueprint

user_blueprint = Blueprint("user_blueprint", __name__)

# prevent circular imports
from .login_email import *
from .create_account_email import *
from .load_profile import *
from .refresh_token import *