from flask import jsonify, request, current_app, g
from firebase_admin.auth import verify_id_token, RevokedIdTokenError, CertificateFetchError, UserDisabledError, ExpiredIdTokenError, InvalidIdTokenError

from . import middleware_blueprint


@middleware_blueprint.before_app_request
def verify_jwt():
    # Check whether the endpoint is excluded from the middleware
    verify_jwt_middleware = True
    
    if request.endpoint in current_app.view_functions:
        view_func = current_app.view_functions[request.endpoint]
        verify_jwt_middleware = not hasattr(view_func, '_exclude_verify_token')
    if not verify_jwt_middleware or request.method == "OPTIONS": return

    auth_header = request.headers.get('Authorization')    
    if not auth_header:
        return jsonify(msg="Authorization header is required"), 400

    token = auth_header.replace('Bearer ', '')
    if not token:
        return jsonify(msg="Token must be set"), 400


    try:
        payload = verify_id_token(token)
        request.token = payload
    except ValueError:
        return jsonify(msg="Token must be set and be a string"), 400
    except RevokedIdTokenError:
        return jsonify(msg="Token has been revoked"), 401
    except CertificateFetchError:
        return jsonify(msg="An error occurred while decoding token"), 401
    except UserDisabledError:
        return jsonify(msg="User disabled"), 401
    except ExpiredIdTokenError:
        return jsonify(msg="Token has expired"), 403
    except InvalidIdTokenError:
        return jsonify(msg="Invalid Token"), 401
    
