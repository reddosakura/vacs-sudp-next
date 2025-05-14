import httpx
from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash

from forms import CameraManagementForm
from utills.enums import Scopes
from utills.utils import build_request

cambp = Blueprint('cambp', __name__)


@cambp.route('/')
def index():
    form = CameraManagementForm()
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

    print(is_admin)

    elements = []
    try:

        cameras = build_request(
            "http://192.168.1.105:8000/connections/list"
        )

        print(cameras.json())
        elements= cameras.json()['endpoints']
    except (httpx.ConnectError,httpx.ConnectTimeout):
        print("Не удалось связаться с сервисом обработки камер")
    # if is_admin:

    return render_template(
        "pages/camera.html",
        user=user.json(),
        camera_status=True,
        is_admin=is_admin,
        form=form,
        elements=elements,
    )


@cambp.route('/', methods=['POST'])
def cemera_add_connection():
    form = CameraManagementForm()
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

    if form.validate_on_submit():
        print(form.data)
    # if is_admin:

    return render_template(
        "pages/camera.html",
        user=user.json(),
        camera_status=True,
        is_admin=is_admin,
        form=form
    )

# @cambp.route('/test')
# def test():
#     form = CameraManagementForm()
#     elements = [
#         'First',
#         'Second',
#         'Third',
#         'Fourth',
#         'Fifth',
#         'Sixth',
#         'Seventh',
#         'Eighth',
#         'Ninth',
#     ]
#     return render_template('pages/camera.html', elements=elements, form=form)
