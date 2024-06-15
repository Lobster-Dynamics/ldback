from flask import Flask
from flask_cors import CORS
from infrastructure.mail.email_service import EmailService

cors = CORS()


def create_app() -> Flask:
    app = Flask(__name__)
    cors.init_app(app)
    from .directory import directory_blueprint
    from .document import document_blueprint
    from .documentos import documentos_blueprint
    from .middleware import middleware_blueprint
    from .user import user_blueprint

    email_service = EmailService()

    # Inicializa el servicio para mandar correos
    app.email_service = email_service

    app.register_blueprint(user_blueprint, url_prefix="/user")
    app.register_blueprint(documentos_blueprint, url_prefix="/documentos")
    app.register_blueprint(document_blueprint, url_prefix="/document")
    app.register_blueprint(directory_blueprint, url_prefix="/directory")
    app.register_blueprint(middleware_blueprint)

    return app
