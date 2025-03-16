from flask import Blueprint, render_template, flash, redirect
from werkzeug.security import generate_password_hash

from forms import CreateUserForm
from utills.utils import build_request

usersbp = Blueprint('users', __name__)

@usersbp.route('/', methods=['GET'])
def index():
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
