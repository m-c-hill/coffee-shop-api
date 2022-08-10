import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

ALGORITHMS = ["RS256"]  # RSA using SHA256
API_AUDIENCE = "coffee"
AUTH0_DOMAIN = "dev-t-0la1ih.us.auth0.com"


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """
    Retrieve the token from the request auth header
    """
    if "Authorization" not in request.headers:
        raise AuthError(
            {
                "code": "auth_header_missing",
                "description": "Authorization header is expected.",
            },
            401,
        )

    auth_header = request.headers["Authorization"]
    _validate_bearer_token(auth_header)

    return auth_header.split(" ")[1]


def _validate_bearer_token(header):
    """
    Helper function to check if the string 'bearer' preceeds the auth token
    """
    header_parts = header.split(" ")

    if len(header_parts) != 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must have the format 'Bearer {{bearer_token}}'.",
            },
            401,
        )

    if header_parts[0].lower() != "bearer":
        raise AuthError(
            {"code": "invalid_header", "description": "The prefix has to be 'Bearer'."},
            401,
        )


def check_permissions(permission, payload):
    """
    Check the permissions list in the JWT payload contains the required permission.
    """
    if "permissions" not in payload:
        raise AuthError(
            {
                "code": "empty_claims",
                "description": "Permissions list not included in JWT",
            },
            401,
        )

    if permission not in payload["permissions"]:
        raise AuthError(
            {"code": "unauthorized", "description": "Permission not found"}, 403
        )


def verify_decode_jwt(token):
    """
    Decode the jwt token using RSA with SHA256 algorithm
    """
    # auth0 jwks docs: https://auth0.com/docs/secure/tokens/json-web-tokens/json-web-key-sets
    jwks_url = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jwks_url.read())  # json web key set

    # jwt lib docs: https://pyjwt.readthedocs.io/en/stable/usage.html
    unverified_header = jwt.get_unverified_header(token)

    if "kid" not in unverified_header:
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization malformed."}, 401
        )

    # retrieve rsa key used for jtw signature
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "e": key["e"],
                "kid": key["kid"],
                "kty": key["kty"],
                "n": key["n"],
                "use": key["use"],
            }

    # decode the jwt using the rsa key and return the payload
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )

            return payload

        except jwt.JWTClaimsError:
            raise AuthError(
                {"code": "invalid_claims", "description": "Invalid claims"}, 401
            )

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token has expired"}, 401
            )

        except Exception:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token",
                },
                400,
            )

    raise AuthError(
        {"code": "invalid_header", "description": "Unable to find rsa key"}, 400
    )


def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
