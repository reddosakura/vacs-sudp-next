# from datetime import datetime
# from pprint import pprint

import httpx
from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import ProcessRequestForm
from modules.requests.exceptions import FailWhileProcessing
from utills.enums import RequestStatus, Scopes
from utills.utils import build_request

procbp = Blueprint('procbp', __name__)





@procbp.route('/consider', methods=['GET'])
def consider():
    user_role = request.cookies.get("role")
    request_id = request.args.get("id")

    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        is_admin = False
        if (check_password_hash(user_role, Scopes.SUPERUSER.value) or
                check_password_hash(user_role, Scopes.ADMIN.value)):
            is_admin = True

        response = build_request(
            "http://localhost:3002/api/v3/requests/list/?is_consideration=true"
        )


        if response.status_code != 200:
            flash(f"Сервис заявок вернул некорректный код: {response.status_code}")
            return render_template("pages/processing.html",
                                   requests=[],
                                   mode="consider",
                                   request_id=None,
                                   is_admin=is_admin,
                                   blocked=True,
                                   user=user.json(),
                                   form=ProcessRequestForm()
                                   )

        if not response.json()['requests']:
            return render_template("pages/processing.html",
                                   requests=[],
                                   mode="consider",
                                   request_id=None,
                                   is_admin=is_admin,
                                   blocked=True,
                                   user=user.json(),
                                   form=ProcessRequestForm()
                                   )
        content = build_request(
            f"http://localhost:3002/api/v3/request/{request_id if request_id else response.json()['requests'][0]['id']}"
        )



        if content.status_code != 200:
            flash(f"Сервис заявок вернул некорректный код: {content.status_code}")
            return render_template("pages/processing.html",
                                   requests=[],
                                   mode="consider",
                                   request_id=None,
                                   is_admin=is_admin,
                                   content=None,
                                   blocked=True,
                                   user=user.json(),
                                   form=ProcessRequestForm()
                                   )
        # pprint(response.json()['requests'], sort_dicts=False)

        return render_template("pages/processing.html",
                               requests=response.json()['requests'],
                               mode="consider",
                               request_id=int(request_id) if request_id else response.json()['requests'][0]['id'],
                               blocked=False,
                               content=content.json(),
                               is_admin=is_admin,
                               user=user.json(),
                               form=ProcessRequestForm(request_id=request_id if request_id else response.json()['requests'][0]['id'])
                               )
    except httpx.ConnectError:
        flash("СЕРВИС ОБРАБОТКИ НЕДОСТУПЕН. ПОПЫТКА СОЕДИНЕНИЯ НЕ УДАЛАСЬ")
        return render_template("pages/processing.html",
                               requests=[],
                               mode="consider",
                               request_id=None,
                               is_admin=False,
                               content=None,
                               blocked=True,
                               user={"role":{"name": None}},
                               form=ProcessRequestForm()
                               )


@procbp.route('/approval', methods=['GET'])
def approval():
    user_role = request.cookies.get("role")
    request_id = request.args.get("id")

    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        is_admin = False
        if (check_password_hash(user_role, "Суперпользователь") or
                check_password_hash(user_role, "Администратор")):
            is_admin = True

        if is_admin:
            response = build_request(
                "http://localhost:3002/api/v3/requests/list/?is_admin=true"
            )
        else:
            response = build_request(
                "http://localhost:3002/api/v3/requests/list/?is_approval=true"
            )

        if response.status_code != 200:
            flash(f"Сервис заявок вернул некорректный код: {response.status_code}")
            return render_template("pages/processing.html",
                                   requests=[],
                                   mode="approval",
                                   request_id=None,
                                   is_admin=is_admin,
                                   blocked=True,
                                   user=user.json(),
                                   form=ProcessRequestForm()
                                   )

        if not response.json()['requests']:
            return render_template("pages/processing.html",
                                   requests=[],
                                   mode="approval",
                                   request_id=None,
                                   is_admin=is_admin,
                                   blocked=True,
                                   user=user.json(),
                                   form=ProcessRequestForm()
                                   )
        content = build_request(
            f"http://localhost:3002/api/v3/request/{request_id if request_id else response.json()['requests'][0]['id']}"
        )

        if content.status_code != 200:
            flash(f"Сервис заявок вернул некорректный код: {content.status_code}")
            return render_template("pages/processing.html",
                                   requests=[],
                                   mode="approval",
                                   request_id=None,
                                   is_admin=is_admin,
                                   content=None,
                                   blocked=True,
                                   user=user.json(),
                                   form=ProcessRequestForm()
                                   )
        # pprint(response.json()['requests'], sort_dicts=False)

        return render_template("pages/processing.html",
                               requests=response.json()['requests'],
                               mode="approval",
                               request_id=int(request_id) if request_id else response.json()['requests'][0]['id'],
                               blocked=False,
                               content=content.json(),
                               is_admin=is_admin,
                               user=user.json(),
                               form=ProcessRequestForm(request_id=request_id if request_id else response.json()['requests'][0]['id'])
                               )
    except httpx.ConnectError:
        flash(f"СЕРВИС ОБРАБОТКИ НЕДОСТУПЕН. ПОПЫТКА СОЕДИНЕНИЯ НЕ УДАЛАСЬ")
        return render_template("pages/processing.html",
                               requests=[],
                               mode="approval",
                               request_id=None,
                               is_admin=False,
                               content=None,
                               blocked=True,
                               user={"role": {"name": None}},
                               form=ProcessRequestForm()
                               )


@procbp.route('/consider', methods=['POST'])
def post_consider():
    try:
        user_role = request.cookies.get("role")
        form = ProcessRequestForm()
        _process_request(form, "consider", user_role)
        return redirect("consider")

    except FailWhileProcessing as e:
        flash(f"{e}")
        return redirect("consider")

    except httpx.ConnectError:
        flash("СЕРВИС НЕДОСТУПЕН. ПОПЫТКА СОЕДИНЕНИЯ НЕ УДАЛАСЬ")
        return redirect("consider")


@procbp.route('/approval', methods=['POST'])
def post_approval():
    user_role = request.cookies.get("role")
    form = ProcessRequestForm()
    _process_request(form, "approval", user_role)
    return redirect("approval")


def _process_request(form: ProcessRequestForm, mode: str, user_role: str):
    global status
    if form.validate_on_submit():

        get_request = build_request(
            f'http://localhost:3002/api/v3/request/{form.request_id.data}'
        )

        if get_request.status_code != 200:
            raise FailWhileProcessing("НЕ УДАЛОСЬ ПОЛУЧИТЬ ДАННЫЕ ЗАЯВКИ")

        match mode:
            case "approval":
                if form.allow.data:
                    status = build_request(
                        f"http://localhost:3002/api/v3/request/status/{RequestStatus.ALLOWED.value}"
                    )
                elif form.approve.data:
                    status = build_request(
                        f"http://localhost:3002/api/v3/request/status/{RequestStatus.PASSAPPROVAL.value}"
                    )
                elif form.deny.data:
                    if user_role != generate_password_hash("Ограниченное администрирование"):
                        status = build_request(
                            f"http://localhost:3002/api/v3/request/status/{RequestStatus.UNPASSAPPROVAL.value}"
                        )
                    else:
                        status = build_request(
                            f"http://localhost:3002/api/v3/request/status/{RequestStatus.REJECTED.value}"
                        )
            case "consider":
                if form.allow.data:
                    status = build_request(
                        f"http://localhost:3002/api/v3/request/status/{RequestStatus.ALLOWED.value}"
                    )
                elif form.approve.data:
                    status = build_request(
                        f"http://localhost:3002/api/v3/request/status/{RequestStatus.PASSAPPROVAL.value}"
                    )
                elif form.deny.data:
                    status = build_request(
                        f"http://localhost:3002/api/v3/request/status/{RequestStatus.REJECTED.value}"
                    )

        if status.status_code != 200:
            raise FailWhileProcessing("СЕРВИС ОБРАБОТКИ НЕДОСТУПЕН")

        data = {
            "request_id": form.request_id.data,
            "user_id": request.cookies.get("id"),
            "request_status_id": status.json()["id"],
            "comment": form.comment.data,
        }

        pool_request = build_request(
            'http://localhost:3003/api/v3/approval/create/',
            method="POST",
            data=data
        )

        if pool_request.status_code != 200:
            raise FailWhileProcessing("НЕ УДАЛОСЬ СВЯЗАТЬСЯ С ПУЛОМ СОГЛАСОВАНИЯ")

        update_request_payload = {
            "request_":{
                "type_id": get_request.json()["type_id"],
                "date_created": get_request.json()["date_created"],
                "contract_name": get_request.json()["contract_name"],
                "organization": get_request.json()["organization"],
                "from_date": get_request.json()["from_date"],
                "to_date": get_request.json()["to_date"],
                "from_time": get_request.json()["from_time"],
                "to_time": get_request.json()["to_time"],
                "comment": get_request.json()["comment"],
                "request_status_id": status.json()["id"],
                "passmode_id": get_request.json()["passmode_id"],
                "creator": get_request.json()["creator"],
                "is_deleted": get_request.json()["is_deleted"]
            },
            "visitors_": get_request.json()["visitors"],
            "cars_": get_request.json()["cars"]
        }

        update_request = build_request(
            f"http://localhost:3002/api/v3/request/update/{form.request_id.data}",
            method="PUT",
            data=update_request_payload
        )

        if update_request.status_code != 204:
            raise FailWhileProcessing(f"НЕ УДАЛОСЬ ОБРАБОТАТЬ ЗАЯВКУ. ПУЛ СОГЛАСОВАНИЯ ВЕРНУЛ КОД: {update_request.status_code}")
        return

# @procbp.route("/", methods=["GET"])
# def index():
#     user_role = request.cookies.get("role")
#     if (check_password_hash(user_role, "Суперпользователь") or
#             check_password_hash(user_role, "Администратор")):
#         mode = True
#     else:
#         mode = False
#     requests = build_request(
#         "http://localhost:3002/api/v3/requests/list/?is_consideration=false"
#     )
#
#     return render_template("pages/processing.html", requests=requests, mode=mode)
