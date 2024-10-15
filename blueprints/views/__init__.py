from flask import Blueprint
from flask_login import login_required
from ext.core import send_form
from ext.auth import login, logout
# from ext.api import api_data
from .views import home, cadastrar_os, pesquisar, serve_file, health_check

bp = Blueprint("views", __name__)


bp.add_url_rule("/", view_func=login_required(home), endpoint="default")
bp.add_url_rule("/home", view_func=login_required(home))
bp.add_url_rule("/cadastrar_os", view_func=login_required(cadastrar_os))
bp.add_url_rule("/pesquisar", view_func=login_required(pesquisar))
# bp.add_url_rule("/api/<path:data>", view_func=login_required(api_data))
bp.add_url_rule("/process_form/send", view_func=login_required(send_form), methods=["POST"])
bp.add_url_rule("/login", view_func=login, methods=["POST", "GET"])
bp.add_url_rule("/logout/", view_func=login_required(logout), methods=["POST", "GET"])
bp.add_url_rule("/<path:filename>", view_func=login_required(serve_file))
bp.add_url_rule("/ping", view_func=health_check)


def init_app(app):
    app.register_blueprint(bp)
