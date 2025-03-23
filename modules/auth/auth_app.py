import httpx
from flask import Blueprint, render_template, make_response, flash, redirect
from utills.utils import build_request
from forms import AuthForm
from werkzeug.security import generate_password_hash

authbp = Blueprint('auth_app', __name__, template_folder='templates')


@authbp.route('/', methods=['GET'])
def index():
    form = AuthForm()
    return render_template("pages/auth.html", form=form)


@authbp.route('/', methods=['POST'])
def login():
    form = AuthForm()
    if form.validate_on_submit():
        try:
            body = {
                "login": form.login.data,
                "password": form.password.data
            }
            auth_response = build_request(
                "http://localhost:3001/api/v3/auth",
                method="POST",
                data=body,
            )

            if auth_response.status_code == 200:
                if auth_response.json()["authenticated"]:
                    role = auth_response.json()["role"]
                    match role:
                        case "Администратор": page = "/processing/consider"
                        case "Ограниченное администрирование": page = "/processing/approval"
                        case "Суперпользователь": page = "/users"
                        case "Заявитель": page = "/requests"
                        case "Охрана": page = "/monitoring"
                        case _: page = "/404"

                    res = make_response(redirect(page))
                    res.set_cookie("role", value=generate_password_hash(role))
                    res.set_cookie("lnp", value=auth_response.json()["lnp"])
                    res.set_cookie("id", value=auth_response.json()["id"])
                    return res

                flash('Неверный логин или пароль')
                return render_template("pages/auth.html", form=form)

        except httpx.ConnectError as e:
            flash('Не удалось подключиться к сервису авторизации')
            return render_template("pages/auth.html", form=form)

    flash('Неверный логин или пароль')
    return render_template("pages/auth.html", form=form)
