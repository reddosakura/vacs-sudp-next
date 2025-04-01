import httpx
from flask import Blueprint, render_template, flash, redirect, request
from werkzeug.security import generate_password_hash

from forms import CreateUserForm, UpdateUserForm
from utills.utils import build_request

usersbp = Blueprint('users', __name__)

@usersbp.route('/', methods=['GET'])
def index():
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        users_response = build_request(
            "http://localhost:3001/api/v3/users?show_deleted=false"
        )

        roles_response = build_request(
            "http://localhost:3001/api/v3/users/list/roles"
        )

        if users_response.status_code == 200 and roles_response.status_code == 200:
            if users_response.json()["users"]:
                form = CreateUserForm()
                form.role.choices = [(role['id'], role['name']) for role in roles_response.json()["roles"]]
                return render_template(
                    'pages/users.html',
                    users=users_response.json()["users"],
                    user=user.json(),
                    # roles=roles_response.json()["roles"],
                    form=form,
                )
            else:
                flash("Пользователи не найдены")
        else:
            flash(f"User API вернул код - {users_response.status_code}")


        return render_template(
            'pages/users.html',
            users = [],
            user=user.json(),
            # roles = [],
            form=CreateUserForm()
        )
    except httpx.ConnectError as e:
        flash(f"СЕРВИС НЕДОСТУПЕН, НЕ УДАЛОСЬ СВЯЗАТЬСЯ С API")

        return render_template(
            'pages/users.html',
            users=[],
            user={"role": {"name": None}},
            # roles = [],
            form=CreateUserForm()
        )


@usersbp.route('/<id>', methods=['GET'])
def update_user_get(id: str):
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        users_response = build_request(
            "http://localhost:3001/api/v3/users?show_deleted=false"
        )

        roles_response = build_request(
            "http://localhost:3001/api/v3/users/list/roles"
        )

        if users_response.status_code == 200 and roles_response.status_code == 200:
            if users_response.json()["users"]:
                form = CreateUserForm()
                form.role.choices = [(role['id'], role['name']) for role in roles_response.json()["roles"]]

                form_update = UpdateUserForm()
                form_update.role.choices = [(role['id'], role['name']) for role in roles_response.json()["roles"]]

                updated_user = None
                for u in users_response.json()["users"]:
                    if u["id"] == id:
                        updated_user = u

                form_update.lastname.data = updated_user["lastname"]
                form_update.name.data = updated_user["name"]
                form_update.patronymic.data = updated_user["patronymic"]
                form_update.speciality.data = updated_user["speciality"]
                form_update.id_ = updated_user["id"]

                print(roles_response.json())

                for roles in roles_response.json()["roles"]:
                    if roles["id"] == updated_user["role"]["id"]:
                        form_update.role.data = roles["id"]
                        break

                form_update.login.data = updated_user["login"]

                return render_template(
                    'pages/users.html',
                    users=users_response.json()["users"],
                    user=user.json(),
                    form_update=form_update,
                    # roles=roles_response.json()["roles"],
                    form=form,
                )
            else:
                flash("Пользователи не найдены")
        else:
            flash(f"User API вернул код - {users_response.status_code}")


        return render_template(
            'pages/users.html',
            users = [],
            user=user.json(),
            # roles = [],
            form=CreateUserForm()
        )
    except httpx.ConnectError as e:
        flash(f"СЕРВИС НЕДОСТУПЕН")

        return render_template(
            'pages/users.html',
            users=[],
            user={"role": {"name": None}},
            # roles = [],
            form=CreateUserForm()
        )

@usersbp.route('/', methods=['POST'])
def create_user():
    roles_response = build_request(
        "http://localhost:3001/api/v3/users/list/roles"
    )

    if roles_response.status_code != 200:
        flash("Не удалось получить роли")

    form = CreateUserForm()
    form.role.choices = [(role['id'], role['name']) for role in roles_response.json()["roles"]]
    if form.validate_on_submit():
        body = {
            "lastname": form.lastname.data,
            "name": form.name.data,
            "patronymic": form.patronymic.data,
            "role_id": form.role.data,
            "speciality": form.speciality.data,
            "logged_in": False,
            "is_deleted": False,
            "login": form.login.data,
            "hashed_password": generate_password_hash(
                                    form.password.data,
                                     method="pbkdf2:sha256",
                                     salt_length=8
            )
        }

        create_user_request = build_request(
            "http://localhost:3001/api/v3/users/create",
            method="POST",
            data=body
        )

        if create_user_request.status_code == 200:
            return redirect("/users")

    flash("Пользователь не был создан")
    return render_template("pages/users.html", users=[], form=CreateUserForm())


@usersbp.route('/update/<id>', methods=['POST'])
def update_user(id: str):

    form = UpdateUserForm()
    roles_response = build_request(
        "http://localhost:3001/api/v3/users/list/roles"
    )

    if roles_response.status_code != 200:
        flash("Не удалось получить роли")

    form.role.choices = [(role['id'], role['name']) for role in roles_response.json()["roles"]]
    if form.validate_on_submit():

        body = {}
        if form.edit_btn.data:
            body = {
                "lastname": form.lastname.data,
                "name": form.name.data,
                "patronymic": form.patronymic.data,
                "role_id": form.role.data,
                "speciality": form.speciality.data,
                "logged_in": False,
                "is_deleted": False,
                "login": form.login.data,
            }
            if form.selector.data:
                body = {
                    "lastname": form.lastname.data,
                    "name": form.name.data,
                    "patronymic": form.patronymic.data,
                    "role_id": form.role.data,
                    "speciality": form.speciality.data,
                    "logged_in": False,
                    "is_deleted": False,
                    "login": form.login.data,
                    "hashed_password":generate_password_hash(
                            form.password.data,
                             method="pbkdf2:sha256",
                             salt_length=8
                    ),
                }

        elif form.delete_btn.data:

            user = build_request(
                f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
            )

            if user.status_code != 200:
                flash(
                    f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ПОЛЬЗОВАТЕЛЯ ДЛЯ ДАЛЬНЕЙШЕГО УДАЛЕНИЯ, СЕРВИС USERS API ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {user.status_code}")

                return render_template(
                    'pages/users.html',
                    users=[],
                    user={"role": {"name": None}},
                    form=CreateUserForm()
                )
            user = user.json()

            body = {
                "lastname": user["lastname"],
                "name": user["name"],
                "patronymic": user["patronymic"],
                "role_id": user["role_id"],
                "speciality": user["speciality"],
                "logged_in":  user["logged_in"],
                "is_deleted": True,
                "login": user["login"],
            }
        update_user_request = build_request(
            f"http://localhost:3001/api/v3/users/update/base/{id}",
            method="PUT",
            data=body
        )

        if update_user_request.status_code != 200:
            flash(f"НЕ УДАЛОСЬ СОХРАНИТЬ ИЗМЕНЕНИЯ, СЕРВИС USERS API ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {update_user_request.status_code}")

            return render_template(
                'pages/users.html',
                users=[],
                user={"role": {"name": None}},
                # roles = [],
                form=CreateUserForm()
            )


    return redirect(f"/users/{id}?show=true")

    # roles_response = build_request(
    #     "http://localhost:3001/api/v3/users/list/roles"
    # )
    #
    # if roles_response.status_code != 200:
    #     flash("Не удалось получить роли")
    #
    # form = CreateUserForm()
    # form.role.choices = [(role['id'], role['name']) for role in roles_response.json()["roles"]]
    # if form.validate_on_submit():
    #     body = {
    #         "lastname": form.lastname.data,
    #         "name": form.name.data,
    #         "patronymic": form.patronymic.data,
    #         "role_id": form.role.data,
    #         "speciality": form.speciality.data,
    #         "logged_in": False,
    #         "is_deleted": False,
    #         "login": form.login.data,
    #         "hashed_password": generate_password_hash(
    #                                 form.password.data,
    #                                  method="pbkdf2:sha256",
    #                                  salt_length=8
    #         )
    #     }
    #
    #     create_user_request = build_request(
    #         "http://localhost:3001/api/v3/users/create",
    #         method="POST",
    #         data=body
    #     )
    #
    #     if create_user_request.status_code == 200:
    #         return redirect("/users")
    #
    # flash("Пользователь не был создан")
    # return render_template("pages/users.html", users=[], form=CreateUserForm())
