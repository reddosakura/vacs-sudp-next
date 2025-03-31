from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash

from utills.enums import Scopes
from utills.utils import build_request

cambp = Blueprint('cambp', __name__)


@cambp.route('/')
def index():
    user = build_request(
        f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
    )
    user_role = request.cookies.get("role")
    if user.status_code != 200:
        return redirect("/auth")

    is_admin = False
    if not (check_password_hash(user_role, Scopes.MONITORING.value) or
            check_password_hash(user_role, Scopes.REQUESTER.value)):
        is_admin = True

    return render_template("pages/camera.html", user=user.json(), camera_status=True, is_admin=is_admin)
