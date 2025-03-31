from pprint import pprint

import httpx
from flask import render_template, flash
# from forms import RequestForm
# from modules.requests.config import reqbp
# from utills.utils import build_request
from datetime import datetime

from flask import flash, redirect, request

from forms import RequestForm, TIME_INTERVALS, VisitorsPassageForm, SearchForm, VisitorSubForm, CarSubForm
from .config import reqbp
from utills.enums import RequestType, RequestStatus
from utills.utils import build_request


@reqbp.route('/creation', methods=['GET'])
def create_get():
    form = RequestForm()
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )
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


@reqbp.route('/creation', methods=['POST'])
def create():
    try:
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

        if ((request_type == RequestType.REUSABLE.value and (to_date - from_date).days != 0)
                or (request_type == RequestType.DISPOSABLE.value and (to_date - from_date).days > 0)
                or (request_type == RequestType.DISPOSABLE.value and (
                        to_date - from_date).days == 0 and from_date.weekday() in [5, 6])):
            # or (request_type == RequestType.DISPOSABLE.value
            #     and (to_date - from_date).days == 0
            # and _check_date(request, from_date))):  #TODO: доделать сервис валидации

            request_status = RequestStatus.APPROVE.value
        else:
            request_status = RequestStatus.CONSIDERATION.value

        status_request = build_request(
            "http://localhost:3002/api/v3/request/status/" + request_status
        )

        if status_request.status_code != 200:
            flash("Не удалось определить статус заявки", "alert-danger")
            return redirect("/requests/creation")

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
                    flash(f"Не удалось создать завку. Сервис API вернул код: {submit_request.status_code}",
                          "alert-danger")
                    return redirect("/requests/creation")

                print(submit_request.json(), "<<-- created_request")

                if form.visitors_list.data:
                    visitors = [
                        {
                            "lastname": v["lastname"].upper(),
                            "name": v["name"].upper(),
                            "patronymic": v["patronymic"].upper() if v['patronymic'] else None,
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
                        flash(
                            f"Не удалось прикрепить посетителей к завке. Сервис API вернул код: {add_visitor_request.status_code}",
                            "alert-danger")
                        return redirect("/requests/creation")

                if form.cars_list.data:

                    car_types_request = build_request(
                        "http://localhost:3002/api/v3/request/car/types"
                    )

                    if car_types_request.status_code != 200:
                        flash(
                            f"Не удалось прикрепить автотранспорт к заявки. Не удалось получить список типов автотранспорта.. Сервис API вернул код: {car_types_request.status_code}",
                            "alert-danger")
                        return redirect("/requests/creation")

                    car_type = \
                    list(filter(lambda x: x['type'] == "По заявке", car_types_request.json()["car_types"]))[0]["id"]

                    cars = [
                        {
                            "govern_num": c["govern_num"].replace(" ", "").upper(),
                            "car_model": c["carmodel"],
                            "passed_status": False,
                            "type_id": car_type,
                            "request_id": submit_request.json()["id"],
                            "visitor_id": None,
                            "is_deleted": False,
                            "on_territory": False,
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
                        flash(
                            f"Не удалось прикрепить автотранспорт к завке. Сервис API вернул код: {add_car_request.status_code}",
                            "alert-danger")
                        return redirect("/requests/creation")

        flash("Заявка успешно отправлена", "alert-success")
        return redirect("/requests/creation")
    except httpx.ConnectError:
        flash("НЕ УДАЛОСЬ СОЗДАТЬ ЗАЯВКУ. API НЕДОСТУПЕН", "alert-danger")
        return redirect("/requests/creation")

@reqbp.route('/', methods=['GET'])
def get_my_requests():
    form = SearchForm()
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )
        if user.status_code != 200:
            return redirect("/auth")

        url = f"http://localhost:3002/api/v3/request/search?&creator={request.cookies.get('id')}"
        print(url)
        requests_ = build_request(
            url
        )


        if requests_.status_code != 200:
            flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {requests_.status_code}", "alert-danger")
            return render_template("pages/creator_requests.html", form=form, requests_data=[], user=user.json())

        return render_template("pages/creator_requests.html", form=form, requests_data=requests_.json()['requests'], user=user.json())

    except httpx.ConnectError:
        flash("НЕ УДАЛОСЬ СОЗДАТЬ ЗАЯВКУ. API НЕДОСТУПЕН", "alert-danger")
        return render_template("pages/creator_requests.html", form=form, requests_data=[], user={"role": None})

@reqbp.route('/edit/<id>', methods=['GET'])
def edit_get(id: int):
    try:
        form = RequestForm()
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

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


        if user.status_code != 200:
            return redirect("/auth")

        request_ = build_request(
            f"http://localhost:3002/api/v3/request/{id}"
        )

        for t in form.type.choices:
            if t[0] == request_.json()["type_id"]:
                form.type.data = t[0]
                break

        for p in form.passage_mode.choices:
            if p[0] == request_.json()["passmode_id"]:
                form.passage_mode.data = p[0]
                break


        interval = f"С {datetime.strptime(request_.json()["from_time"], "%H:%M:%S").strftime("%H:%M")} ДО {datetime.strptime(request_.json()["to_time"], "%H:%M:%S").strftime("%H:%M")}"

        print(interval)

        for i in dict(TIME_INTERVALS):
            print(dict(TIME_INTERVALS)[i])
            if (dict(TIME_INTERVALS)[i] == interval or
                    ((dict(TIME_INTERVALS)[i] == "КРУГЛОСУТОЧНО") and
                    (interval == "С 00:00 ДО 23:59"))):
                form.time_interval.data = i
                break

        form.organization.data = request_.json()["organization"]
        form.comment.data = request_.json()["comment"]
        form.from_date.data = datetime.strptime(request_.json()["from_date"], "%Y-%m-%dT%H:%M:%S")
        form.to_date.data = datetime.strptime(request_.json()["to_date"], "%Y-%m-%dT%H:%M:%S")
        form.contract.data = request_.json()["contract_name"]


        for v in request_.json()["visitors"]:
            if not v["is_deleted"]:
                visitor_form = VisitorSubForm()
                visitor_form.v_id = v["id"]
                visitor_form.lastname = v["lastname"]
                visitor_form.name = v["name"]
                visitor_form.patronymic = v["patronymic"]
                form.visitors_list.append_entry(visitor_form)

        for c in request_.json()["cars"]:
            if not c["is_deleted"]:
                car_form = CarSubForm()
                car_form.c_id = c["id"]
                car_form.car_model = c["car_model"]
                car_form.govern_num = c["govern_num"]
                form.cars_list.append_entry(car_form)


        return render_template("pages/request_editing.html", form=form, id=id, user=user.json(), blocked=False)
    except httpx.ConnectError:
        flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД", "alert-danger")
        return render_template("pages/request_editing.html", form=RequestForm(), id=id, user={"role": None}, blocked=False)

@reqbp.route("/edit/<id>", methods=["POST"])
def edit(id: int):
    form = RequestForm()
    user = build_request(
        f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
    )

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
    get_request = build_request(
        f'http://localhost:3002/api/v3/request/{id}'
    )

    if get_request.status_code != 200:
        flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД", "alert-danger")
        return render_template("pages/request_editing.html", form=RequestForm(), id=id, user={"role": None}, blocked=False)

    request_type = list(filter(lambda x: x['id'] == form.type.data, types_request.json()["types"]))[0]["name"]
    print(request_type, "<<-- type")
    from_date = form.from_date.data
    to_date = form.to_date.data
    if ((request_type == RequestType.REUSABLE.value and (to_date - from_date).days != 0)
            or (request_type == RequestType.DISPOSABLE.value and (to_date - from_date).days > 0)
            or (request_type == RequestType.DISPOSABLE.value and (
                    to_date - from_date).days == 0 and from_date.weekday() in [5, 6])):
        # or (request_type == RequestType.DISPOSABLE.value
        #     and (to_date - from_date).days == 0
        # and _check_date(request, from_date))):  #TODO: доделать сервис валидации

        request_status = RequestStatus.APPROVE.value
    else:
        request_status = RequestStatus.CONSIDERATION.value

    status_request = build_request(
        "http://localhost:3002/api/v3/request/status/" + request_status
    )

    if status_request.status_code != 200:
        flash("Не удалось определить статус заявки", "alert-danger")
        return redirect("/requests/creation")

    if form.time_interval.data == "9":
        from_time = datetime.strptime('00:00', "%H:%M").time().strftime("%H:%M")
        to_time = datetime.strptime('23:59', "%H:%M").time().strftime("%H:%M")
    else:
        interval = dict(TIME_INTERVALS)[form.time_interval.data]
        from_time = datetime.strptime(interval.split()[1], "%H:%M").time().strftime("%H:%M")
        to_time = datetime.strptime(interval.split()[-1], "%H:%M").time().strftime("%H:%M")

    if form.validate_on_submit():

        additional_visitors = []
        additional_cars = []
        updated_visitors = []
        updated_cars = []

        for v in form.visitors_list.data:
            if not v['v_id']:
                del v['v_id']
                additional_visitors.append(v | {"request_id": id,
             "passed_status": False,
             "is_deleted": False,
             "date_deleted": None,
             "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
            else:
                v.update({"id": v["v_id"]})
                del v["v_id"]
                updated_visitors.append(v | {"request_id": id,
                                                "passed_status": False,
                                                "is_deleted": False,
                                                "date_deleted": None,
                                                "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})

        car_types_request = build_request(
            "http://localhost:3002/api/v3/request/car/types"
        )

        if car_types_request.status_code != 200:
            flash(
                f"Не удалось прикрепить автотранспорт к заявки. Не удалось получить список типов автотранспорта.. Сервис API вернул код: {car_types_request.status_code}",
                "alert-danger")
            return redirect("/requests/creation")

        car_type = \
            list(filter(lambda x: x['type'] == "По заявке", car_types_request.json()["car_types"]))[0]["id"]

        for c in form.cars_list.data:
            if not c['c_id']:
                del c['c_id']
                additional_cars.append(c | {
                        "passed_status": False,
                        "type_id": car_type,
                        "request_id": id,
                        "visitor_id": None,
                        "is_deleted": False,
                        "on_territory": False,
                        "date_deleted": None,
                        "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})

            else:
                c.update({"id": c["c_id"]})
                del c["c_id"]

                updated_cars.append(c | {
                        "passed_status": False,
                        "type_id": car_type,
                        "request_id": id,
                        "visitor_id": None,
                        "is_deleted": False,
                        "on_territory": False,
                        "date_deleted": None,
                        "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})


        if additional_visitors:
            add_visitor_request = build_request(
                "http://localhost:3002/api/v3/request/create/visitors",
                method="POST",
                data=additional_visitors
            )

            if add_visitor_request.status_code != 200:
                flash(
                    f"Не удалось прикрепить посетителей к завке. Сервис API вернул код: {add_visitor_request.status_code}",
                    "alert-danger")
                return redirect(f"/requests/edit/{id}")


        if additional_cars:
            add_car_request = build_request(
                "http://localhost:3002/api/v3/request/create/cars",
                method="POST",
                data=additional_cars
            )

            if add_car_request.status_code != 200:
                flash(
                    f"Не удалось прикрепить автотранспорт к завке. Сервис API вернул код: {add_car_request.status_code}",
                    "alert-danger")
                return redirect(f"/requests/edit/{id}")


        deleted_visitors = []
        deleted_cars = []

        visitors_ids = [v_["v_id"] for v_ in form.visitors_list.data]
        cars_ids = [c_["c_id"] for c_ in form.cars_list.data]

        for v in get_request.json()["visitors"]:
            if v['id'] not in visitors_ids:
                deleted_visitors.append(v | {"is_deleted": True, "date_deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})

        for c in get_request.json()["cars"]:
            if c['id'] not in cars_ids:
                del c['driver']
                del c['transport_type']
                deleted_cars.append(c | {"is_deleted": True, "date_deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})



        print(updated_cars + deleted_cars)


        update_request_payload = {
            "request_":{
                "type_id": form.type.data,
                "date_created": get_request.json()["date_created"],
                "contract_name": form.contract.data,
                "organization": form.organization.data,
                "from_date": form.from_date.data,
                "to_date": form.to_date.data,
                "from_time": from_time,
                "to_time": to_time,
                "comment": form.comment.data,
                "request_status_id": status_request.json()["id"],
                "passmode_id": form.passage_mode.data,
                "creator": get_request.json()["creator"],
                "is_deleted": False,
                "id": id
            },
            "visitors_": updated_visitors + deleted_visitors,
            "cars_": updated_cars + deleted_cars
        }

        update_request = build_request(
            f"http://localhost:3002/api/v3/request/update",
            method="PUT",
            data=update_request_payload
        )

        # print(update_request.status_code, update_request.json())

        if update_request.status_code != 204:
            flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД {update_request.status_code}", "alert-danger")
            return render_template("pages/request_editing.html", form=RequestForm(), id=id, user={"role": None},
                                   blocked=False)

    return redirect("/requests")

