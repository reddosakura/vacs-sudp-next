import httpx
from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import ProcessRequestForm
from modules.requests.exceptions import FailWhileProcessing
from utills.enums import RequestStatus, Scopes
from utills.utils import build_request

monbp = Blueprint('monbp', __name__)

@monbp.route('/')
def index():

    user_role = request.cookies.get("role")
    request_id = request.args.get("id")
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        is_admin = False
        if not (check_password_hash(user_role, Scopes.MONITORING.value) or
                check_password_hash(user_role, Scopes.REQUESTER.value)):
            is_admin = True

        requests_response = build_request(
            "http://localhost:3002/api/v3/requests/list/?monitoring=true",
        )

        if requests_response.status_code != 200:
            flash(f"СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {requests_response.status_code}")
            return render_template("pages/monitoring.html")

        requests = requests_response.json()['requests']

        for req in requests:
            req.update(req | {"approval": build_request(f"http://localhost:3003/api/v3/approval/request/{req['id']}").json()})

        return render_template(
            "pages/monitoring.html",
            is_admin=is_admin,
            user=user.json(),
            requests=requests,
        )

    except httpx.ConnectError:
        flash("СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН")
        return render_template("pages/monitoring.html")
