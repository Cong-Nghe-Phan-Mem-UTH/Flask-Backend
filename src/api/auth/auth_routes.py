from flask import Blueprint, request
from services.auth_service import (
    login_service,
    logout_service,
    refresh_token_service,
    login_google_service
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    return login_service(request.json)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return logout_service(request.json)

@auth_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    return refresh_token_service(request.json)

@auth_bp.route("/login/google", methods=["GET"])
def login_google():
    code = request.args.get("code")
    return login_google_service(code)

