from flask import Flask

from flask_cors import CORS

cors = CORS()


def create_app() -> Flask:
    app = Flask(__name__)
    cors.init_app(app)
    from .user import user_blueprint
    from .documentos import documentos_blueprint
    from .document import document_blueprint
    from .directory import directory_blueprint
    from .middleware import middleware_blueprint

    app.register_blueprint(user_blueprint, url_prefix="/user")
    app.register_blueprint(documentos_blueprint, url_prefix="/documentos")
    app.register_blueprint(document_blueprint, url_prefix="/document")
    app.register_blueprint(directory_blueprint, url_prefix="/directory")
    app.register_blueprint(middleware_blueprint)

    return app
