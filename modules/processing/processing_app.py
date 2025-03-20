from datetime import datetime
from pprint import pprint

from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash

from forms import ProcessRequestForm
from utills.utils import build_request

procbp = Blueprint('procbp', __name__)





@procbp.route('/consider', methods=['GET'])
def index():
    user_role = request.cookies.get("role")
    request_id = request.args.get("id")

    is_admin = False
    if (check_password_hash(user_role, "Суперпользователь") or
            check_password_hash(user_role, "Администратор")):
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
                               form=ProcessRequestForm()
                               )

    print(response.json()['requests'][0]['id'], "<<-- id")

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
                               form=ProcessRequestForm()
                               )

    return render_template("pages/processing.html",
                           requests=response.json()['requests'],
                           mode="consider",
                           request_id=request_id if request_id else response.json()['requests'][0]['id'],
                           blocked=False,
                           content=content.json(),
                           is_admin=is_admin,
                           form=ProcessRequestForm(request_id=request_id if request_id else response.json()['requests'][0]['id'])
                           )


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
