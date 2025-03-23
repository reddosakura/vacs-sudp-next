import httpx
from flask import render_template, flash
# from forms import RequestForm
# from modules.requests.config import reqbp
# from utills.utils import build_request
from datetime import datetime

from flask import flash, redirect, request

from forms import RequestForm, TIME_INTERVALS
from .config import reqbp
from utills.enums import RequestType, RequestStatus
from utills.utils import build_request


@reqbp.route('/', methods=['GET'])
def index():
    form = RequestForm()
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        print(user)

        if user.status_code != 200:
            return redirect("/auth")

        passmodes_request = build_request(
            "http://localhost:3002/api/v3/req/passmodes"
        )

        types_request = build_request(
            "http://localhost:3002/api/v3/req/types"
        )

        if passmodes_request.status_code == 200 and types_request.status_code == 200:

            form.type.choices = [(type['id'], type['name']) for type in types_request.json()['types']]
            form.passage_mode.choices = [(type['id'], type['name']) for type in passmodes_request.json()['passage_modes']]

            return render_template(
                "pages/request_creation.html",
                form=form,
                passmodes=passmodes_request.json()['passage_modes'],
                user=user.json(),
                types=types_request.json()['types'],
                blocked=False
            )

        flash("Не удалось получить типы заявок и режимы прохода", "alert-danger")
        return render_template(
            "pages/request_creation.html",
            form=form,
            passmodes=[],
            types=[],
            user=user.json(),
            blocked=True
        )
    except httpx.ConnectError as e:
        flash("Ошибка при подключении к сервису заявок", "alert-danger")
        return render_template(
            "pages/request_creation.html",
            form=form,
            passmodes=[],
            types=[],
            user={"role": {"name": None}},
            blocked=True
        )


@reqbp.route('/', methods=['POST'])
def create():
    form = RequestForm()
    passmodes_request = build_request(
        "http://localhost:3002/api/v3/req/passmodes"
    )

    types_request = build_request(
        "http://localhost:3002/api/v3/req/types"
    )

    if passmodes_request.status_code != 200 and types_request.status_code != 200:
        flash("Не удалось получить типы заявок и режимы прохода", "alert-danger")

    form.type.choices = [(type['id'], type['name']) for type in types_request.json()['types']]
    form.passage_mode.choices = [(type['id'], type['name']) for type in passmodes_request.json()['passage_modes']]

    if form.time_interval.data == "9":
        from_time = datetime.strptime('00:00', "%H:%M").time().strftime("%H:%M")
        to_time = datetime.strptime('23:59', "%H:%M").time().strftime("%H:%M")
    else:
        interval = dict(TIME_INTERVALS)[form.time_interval.data]
        from_time = datetime.strptime(interval.split()[1], "%H:%M").time().strftime("%H:%M")
        to_time = datetime.strptime(interval.split()[-1], "%H:%M").time().strftime("%H:%M")

    from_date = form.from_date.data
    to_date = form.to_date.data
    request_type = list(filter(lambda x: x['id'] == form.type.data, types_request.json()["types"]))[0]["name"]
    print(request_type, "<<-- type")


    if ((request_type.upper() == RequestType.REUSABLE.value.upper() and (to_date - from_date).days != 0)
            or (request_type.upper() == RequestType.DISPOSABLE.value.upper() and (to_date - from_date).days > 0)
            or (request_type.upper() == RequestType.DISPOSABLE.value.upper() and (to_date - from_date).days == 0
                and from_date.weekday() in [5, 6])
            or (request_type.upper() == RequestType.DISPOSABLE.value.upper()
                and (to_date - from_date).days == 0
                and (to_date - from_date).days == 0)):
            # and _check_date(request, from_date))):  #TODO: доделать сервис валидации
        request_status = RequestStatus.APPROVE.value
    else:
        request_status = RequestStatus.CONSIDERATION.value

    status_request = build_request(
        "http://localhost:3002/api/v3/request/status/" + request_status
    )

    if status_request.status_code != 200:
        flash("Не удалось определить статус заявки", "alert-danger")
        return redirect("/requests/")


    if form.validate_on_submit():
        if form.create_btn.data:
            body = {
                "request_": {
                    "type_id": form.type.data,
                    "date_created": datetime.now(),
                    "contract_name": form.contract.data,
                    "organization": form.organization.data,
                    "from_date": from_date,
                    "to_date": to_date,
                    "from_time": from_time,
                    "to_time": to_time,
                    "comment": form.comment.data,
                    "request_status_id": status_request.json()['id'],
                    "passmode_id": form.passage_mode.data,
                    "creator": request.cookies.get("id"),
                    "is_deleted": False
                }
            }

            submit_request = build_request(
                 "http://localhost:3002/api/v3/request/create",
                method="POST",
                data=body
            )

            if submit_request.status_code != 200:
                flash(f"Не удалось создать завку. Сервис API вернул код: {submit_request.status_code}", "alert-danger")
                return redirect("/requests/")

            print(submit_request.json(), "<<-- created_request")

            if form.visitors_list.data:
                visitors = [
                    {
                        "lastname": v["lastname"],
                        "name": v["name"],
                        "patronymic": v["patronymic"],
                        "request_id": submit_request.json()["id"],
                        "passed_status": False,
                        "is_deleted": False,
                        "date_deleted": None,
                        "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),

                    } for v in form.visitors_list.data
                ]

                add_visitor_request = build_request(
                    "http://localhost:3002/api/v3/request/create/visitors",
                    method="POST",
                    data=visitors
                )

                if add_visitor_request.status_code != 200:
                    flash(f"Не удалось прикрепить посетителей к завке. Сервис API вернул код: {add_visitor_request.status_code}", "alert-danger")
                    return redirect("/requests/")

            if form.cars_list.data:

                car_types_request = build_request(
                    "http://localhost:3002/api/v3/request/car/types"
                )

                if car_types_request.status_code != 200:
                    flash(f"Не удалось прикрепить автотранспорт к заявки. Не удалось получить список типов автотранспорта.. Сервис API вернул код: {car_types_request.status_code}", "alert-danger")
                    return redirect("/requests/")

                print(car_types_request.json(), "<<-- car_types_request")

                car_type = list(filter(lambda x: x['type'] == "По заявке", car_types_request.json()["car_types"]))[0]["id"]

                cars = [
                    {
                        "govern_num": c["govern_num"].replace(" ", "").upper(),
                        "car_model": c["carmodel"],
                        "passed_status": False,
                        "type_id": car_type,
                        "request_id": submit_request.json()["id"],
                        "visitor_id": None,
                        "is_deleted": False,
                        "date_deleted": None,
                        "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    } for c in form.cars_list.data
                ]

                add_car_request = build_request(
                    "http://localhost:3002/api/v3/request/create/cars",
                    method="POST",
                    data=cars
                )

                if add_car_request.status_code != 200:
                    flash(f"Не удалось прикрепить автотранспорт к завке. Сервис API вернул код: {add_car_request.status_code}", "alert-danger")
                    return redirect("/requests/")


    flash("Заявка успешно отправлена", "alert-success")
    return redirect("/requests/")
