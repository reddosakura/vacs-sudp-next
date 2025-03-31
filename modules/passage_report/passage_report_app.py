import datetime

import httpx
from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash
from forms import PassagesFilterSearchForm
from utills.enums import Scopes
from utills.utils import build_request

passagebp = Blueprint('passagebp', __name__)


@passagebp.route('/')
def index():
    user_role = request.cookies.get("role")
    form = PassagesFilterSearchForm()
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


        all_car_passages_actual = build_request(
            f"http://localhost:3004/api/v3/passage/list?ftime=00%3A00%3A00&ttime=23%3A59%3A59&fdate={datetime.datetime.now().date()}&tdate={datetime.datetime.now().date()}"
        )

        if all_car_passages_actual.status_code != 200:
            flash(f"СЕРВИС ОТЧЕТОВ НЕДОСТУПЕН, СЕРВИС РЕГИСТРАЦИИ ПРОХОДОВ АВТОТРАНСПОРТА ВЕРНУЛ КОД: {all_car_passages_actual.status_code}")
            return render_template("pages/passages.html", user={"role": None})

        print(all_car_passages_actual.json())

        car_passages = [
            car for car in all_car_passages_actual.json()["c_passages"] if car['car']['transport_type']['type'] == 'По заявке'
        ]

        spec_passages = [
            car for car in all_car_passages_actual.json()["c_passages"] if car['car']['transport_type']['type'] != 'По заявке'
        ]

        visitor_passages_actual = build_request(
            f"http://localhost:3005/api/v3/passage/list?ftime=00%3A00%3A00&ttime=23%3A59%3A59&fdate={datetime.datetime.now().date()}&tdate={datetime.datetime.now().date()}"
        )

        if visitor_passages_actual.status_code != 200:
            flash(f"СЕРВИС ОТЧЕТОВ НЕДОСТУПЕН, СЕРВИС РЕГИСТРАЦИИ ПРОХОДОВ ПОСЕТИТЕЛЕЙ ВЕРНУЛ КОД: {visitor_passages_actual.status_code}")
            return render_template("pages/passages.html", user={"role": None})

        return render_template(
            "pages/passages.html",
            user=user.json(),
            v_passages=visitor_passages_actual.json()["v_passages"],
            c_passages=car_passages,
            s_passages=spec_passages,
            is_admin=is_admin,
            form=form,
        )

    except httpx.ConnectError as e:
        flash("СЕРВИС ОТЧЕТОВ НЕДОСТУПЕН, НЕ УДАЛОСЬ СВЯЗАТЬТСЯ С API")
        return render_template("pages/passages.html", user={"role": None}, form=form)

@passagebp.route('/search')
def filtered():
    user_role = request.cookies.get("role")
    user = build_request(
        f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
    )

    if user.status_code != 200:
        return redirect("/auth")

    is_admin = False
    if not (check_password_hash(user_role, Scopes.MONITORING.value) or
            check_password_hash(user_role, Scopes.REQUESTER.value)):
        is_admin = True

    form = PassagesFilterSearchForm(request.args)

    if form.search_field.data:
        # url_cars = f"http://localhost:3004/api/v3/passage/list?ftime={form.filter_ftime.data}&ttime={form.filter_ttime.data}&fdate={form.filter_fdate.data}&tdate={form.filter_tdate.data}"
        url_visitors = f"http://localhost:3005/api/v3/passage/search?value={form.search_field.data}&ftime={form.filter_ftime.data}&ttime={form.filter_ttime.data}&fdate={form.filter_fdate.data}&tdate={form.filter_tdate.data}"
        url_cars = f"http://localhost:3004/api/v3/passage/search?value={form.search_field.data}&ftime={form.filter_ftime.data}&ttime={form.filter_ttime.data}&fdate={form.filter_fdate.data}&tdate={form.filter_tdate.data}"
    else:
        url_visitors = f"http://localhost:3005/api/v3/passage/list?ftime={form.filter_ftime.data}&ttime={form.filter_ttime.data}&fdate={form.filter_fdate.data}&tdate={form.filter_tdate.data}"
        url_cars = f"http://localhost:3004/api/v3/passage/list?ftime={form.filter_ftime.data}&ttime={form.filter_ttime.data}&fdate={form.filter_fdate.data}&tdate={form.filter_tdate.data}"

    all_car_passages_actual = build_request(
        url_cars
    )

    if all_car_passages_actual.status_code != 200:
        flash(
            f"СЕРВИС ОТЧЕТОВ НЕДОСТУПЕН, СЕРВИС РЕГИСТРАЦИИ ПРОХОДОВ АВТОТРАНСПОРТА ВЕРНУЛ КОД: {all_car_passages_actual.status_code}")
        return render_template("pages/passages.html", user={"role": None})

    print(all_car_passages_actual.json())

    car_passages = [
        car for car in all_car_passages_actual.json()["c_passages"] if
        car['car']['transport_type']['type'] == 'По заявке'
    ]

    spec_passages = [
        car for car in all_car_passages_actual.json()["c_passages"] if
        car['car']['transport_type']['type'] != 'По заявке'
    ]

    visitor_passages_actual = build_request(
        url_visitors
    )

    if visitor_passages_actual.status_code != 200:
        flash(
            f"СЕРВИС ОТЧЕТОВ НЕДОСТУПЕН, СЕРВИС РЕГИСТРАЦИИ ПРОХОДОВ ПОСЕТИТЕЛЕЙ ВЕРНУЛ КОД: {visitor_passages_actual.status_code}")
        return render_template("pages/passages.html", user={"role": None})

    return render_template(
        "pages/passages.html",
        user=user.json(),
        v_passages=visitor_passages_actual.json()["v_passages"],
        c_passages=car_passages,
        s_passages=spec_passages,
        is_admin=is_admin,
        form=form,
    )