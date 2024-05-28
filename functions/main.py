import json

from flask import Request, Response, Flask, request, jsonify, session

from firebase_functions import https_fn

from app import create_app

# NOTE: if "max_instances" parameter is changed to be something different from int(1),
#       the "session" object of "flask" will stop working, making the whole app
#       fail
@https_fn.on_request(max_instances=1)
def main_func(req: Request) -> Response:
    _app = create_app()
    with _app.request_context(req.environ):
        return _app.full_dispatch_request()
