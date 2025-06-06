import _io
import os
import uuid
# from pprint import pprint

import httpx
from flask import render_template, send_file
# from forms import RequestForm
# from modules.requests.config import reqbp
# from utills.utils import build_request
from datetime import datetime

from flask import flash, redirect, request
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from forms import RequestForm, TIME_INTERVALS, SearchForm, VisitorSubForm, CarSubForm
from .config import reqbp, UPLOAD_FOLDER
from utills.enums import RequestType, RequestStatus, Scopes
from utills.utils import build_request


@reqbp.route('/file/<filename>', methods=['GET'])
def files(filename: str):
    return send_file(
        UPLOAD_FOLDER + filename, mimetype='application/pdf'
    )

@reqbp.route('/creation', methods=['GET'])
def create_get():

    search_form = SearchForm(request.args)
    from_request = request.args.get('from_request')
    # print(, "<-- req args")
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

        url = f"http://localhost:3002/api/v3/request/search?&creator={request.cookies.get('id')}"


        if search_form.search_submit.data:
            url = f"{url}&value={search_form.search_field.data}"

        user_requests = build_request(
            url
        )


        if passmodes_request.status_code == 200 and types_request.status_code == 200 and user_requests.status_code == 200:
            form = RequestForm()
            form.type.choices = [(type['id'], type['name']) for type in types_request.json()['types']]
            form.passage_mode.choices = [(type['id'], type['name']) for type in passmodes_request.json()['passage_modes']]

            if from_request:
                print("from request spotted")
                request_ = build_request(
                    f"http://localhost:3002/api/v3/request/{from_request}"
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

                for i in dict(TIME_INTERVALS):
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

                if request_.json()["visitors"]:
                    for v in request_.json()["visitors"]:
                        if not v["is_deleted"]:
                            visitor_form = VisitorSubForm()
                            visitor_form.v_id = v["id"]
                            visitor_form.lastname = v["lastname"]
                            visitor_form.name = v["name"]
                            visitor_form.patronymic = v["patronymic"]
                            form.visitors_list.append_entry(visitor_form)
                if request_.json()["cars"]:
                    for c in request_.json()["cars"]:
                        if not c["is_deleted"]:
                            car_form = CarSubForm()
                            car_form.c_id = c["id"]
                            car_form.car_model = c["car_model"]
                            car_form.govern_num = c["govern_num"]
                            form.cars_list.append_entry(car_form)

            return render_template(
                "pages/request_creation.html",
                form=form,
                search_form=search_form,
                search_value=search_form.search_field.data,
                passmodes=passmodes_request.json()['passage_modes'],
                user=user.json(),
                types=types_request.json()['types'],
                user_requests=user_requests.json()['requests'],
                blocked=False
            )

        flash("Не удалось получить типы заявок и режимы прохода", "alert-danger")
        return render_template(
            "pages/request_creation.html",
            form=RequestForm(),
            search_form=search_form,
            passmodes=[],
            types=[],
            user=user.json(),
            user_requests=[],
            blocked=True
        )
    except httpx.ConnectError as e:
        flash("Ошибка при подключении к сервису заявок", "alert-danger")
        return render_template(
            "pages/request_creation.html",
            form=RequestForm(),
            search_form=search_form,
            passmodes=[],
            types=[],
            user={"role": {"name": None}},
            user_requests=[],
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

        print(form.data)


        # print(form.errors, "<<-- error")
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

                if form.add_files_btn.data:
                    files = []
                    for file in form.add_files_btn.data:
                        if file.filename:
                            filename = str(uuid.uuid4().time) + "." + secure_filename(file.filename)

                            file.save(os.path.join(UPLOAD_FOLDER, filename))
                            files.append({
                                'path': filename,
                                "request_id": submit_request.json()["id"]
                            })

                    print(files, "<<-- files")
                    if files:
                        add_files = build_request(
                            "http://localhost:3002/api/v3/request/create/files",
                            method="POST",
                            data=files
                        )

                        if add_files.status_code != 200:
                            flash(
                                f"Не удалось прикрепить файлы к завке. Сервис API вернул код: {add_files.status_code}",
                                "alert-danger")
                            return redirect("/requests/creation")

                list_visitor_ids = []
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

                    print(add_visitor_request.json(), "<-- add_visitor")
                    list_visitor_ids = [v['id'] for v in add_visitor_request.json()]


                if form.cars_list.data:
                    print(form.cars_list.data, "<-- cars_list data")
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
                            "car_model": c["car_model"],
                            "passed_status": False,
                            "type_id": car_type,
                            "request_id": submit_request.json()["id"],
                            "visitor_id": list_visitor_ids[int(c['visitor'])] if c['visitor'] else None,
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
    form = SearchForm(request.args)
    try:
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

        url = f"http://localhost:3002/api/v3/request/search?&creator={request.cookies.get('id')}"

        if form.search_field.data:
            url = f"{url}&value={form.search_field.data}"

        if request.args.get("show_archive"):
            url = f"http://localhost:3002/api/v3/requests/list/?&is_archived=true&creator={request.cookies.get('id')}"

        requests_ = build_request(
            url
        )

        if requests_.status_code != 200:
            flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {requests_.status_code}", "alert-danger")
            return render_template("pages/creator_requests.html", form=form, requests_data=[], user=user.json())

        return render_template("pages/creator_requests.html", form=form, requests_data=requests_.json()['requests'], user=user.json(), is_admin=is_admin)

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

        for i in dict(TIME_INTERVALS):
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


        if request_.json()["visitors"]:
            for v in request_.json()["visitors"]:
                if not v["is_deleted"]:
                    visitor_form = VisitorSubForm()
                    visitor_form.v_id = v["id"]
                    visitor_form.lastname = v["lastname"]
                    visitor_form.name = v["name"]
                    visitor_form.patronymic = v["patronymic"]
                    form.visitors_list.append_entry(visitor_form)
        if request_.json()["cars"]:
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
    if user.status_code != 200:
        return redirect("/auth")

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
    from_date = form.from_date.data
    to_date = form.to_date.data

    if ((request_type == RequestType.REUSABLE.value and (to_date - from_date).days != 0)
            or (request_type == RequestType.DISPOSABLE.value and (to_date - from_date).days > 0)
            or (request_type == RequestType.DISPOSABLE.value and (
                    to_date - from_date).days == 0 and from_date.weekday() in [5, 6])):
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
                        # "visitor_id": None,
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

        if get_request.json()["visitors"]:
            for v in get_request.json()["visitors"]:
                if v['id'] not in visitors_ids:
                    deleted_visitors.append(v | {"is_deleted": True, "date_deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
        if get_request.json()["cars"]:
            for c in get_request.json()["cars"]:
                if c['id'] not in cars_ids:
                    del c['driver']
                    del c['transport_type']
                    deleted_cars.append(c | {"is_deleted": True, "date_deleted": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})


        files = []
        if form.add_files_btn.data:
            for file in form.add_files_btn.data:
                if file.filename:
                    filename = str(uuid.uuid4().time) + "." + secure_filename(file.filename)

                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    files.append({
                        'path': filename,
                        "request_id": id
                    })

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
            "cars_": updated_cars + deleted_cars,
            "files_": files
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


@reqbp.route("/withdraw/<id>", methods=["POST"])
def withdraw(id: str):
    get_request = build_request(
        f'http://localhost:3002/api/v3/request/{id}'
    )

    if get_request.status_code != 200:
        flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {get_request.status_code}", "alert-danger")
        return render_template("pages/creator_requests.html", form=SearchForm(), requests_data=[], user={"role": None})

    status = build_request(
        f"http://localhost:3002/api/v3/request/status/{RequestStatus.WITHDRAWN.value}"
    )

    update_request_payload = {
        "request_": {
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
            "is_deleted": get_request.json()["is_deleted"],
            "id": get_request.json()["id"]
        },
        "visitors_": get_request.json()["visitors"],
        "cars_": get_request.json()["cars"],
        "files_": get_request.json()["files"],
    }

    print(update_request_payload)

    update_request = build_request(
        f"http://localhost:3002/api/v3/request/update",
        method="PUT",
        data=update_request_payload
    )

    if update_request.status_code != 204:
        print(update_request.status_code)
        flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {update_request.status_code}, ПРИ ПОПЫТКЕ ОТОЗВАТЬ ЗАЯВКУ", "alert-danger")
        return render_template("pages/creator_requests.html", form=SearchForm(), requests_data=[], user={"role": None})

    print(request.url)

    if 'reports' in request.url:
        return redirect("/reports/")

    return redirect("/requests/")


@reqbp.route("/delete/<id>", methods=["POST"])
def delete(id: str):
    get_request = build_request(
        f'http://localhost:3002/api/v3/request/{id}'
    )

    if get_request.status_code != 200:
        flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {get_request.status_code}", "alert-danger")
        return render_template("pages/creator_requests.html", form=SearchForm(), requests_data=[], user={"role": None})

    print(get_request.json())
    update_request_payload = {
        "request_": {
            "type_id": get_request.json()["type_id"],
            "date_created": get_request.json()["date_created"],
            "contract_name": get_request.json()["contract_name"],
            "organization": get_request.json()["organization"],
            "from_date": get_request.json()["from_date"],
            "to_date": get_request.json()["to_date"],
            "from_time": get_request.json()["from_time"],
            "to_time": get_request.json()["to_time"],
            "comment": get_request.json()["comment"],
            "request_status_id": get_request.json()["request_status_id"],
            "passmode_id": get_request.json()["passmode_id"],
            "creator": get_request.json()["creator"],
            "is_deleted": True,
            "id": get_request.json()["id"]
        },
        "visitors_": get_request.json()["visitors"],
        "cars_": get_request.json()["cars"],
        "files_": get_request.json()["files"],
    }

    update_request = build_request(
        f"http://localhost:3002/api/v3/request/update",
        method="PUT",
        data=update_request_payload
    )

    if update_request.status_code != 204:
        print(update_request.status_code)
        flash(f"СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {update_request.status_code}, ПРИ ПОПЫТКЕ ОТОЗВАТЬ ЗАЯВКУ", "alert-danger")
        return render_template("pages/creator_requests.html", form=SearchForm(), requests_data=[], user={"role": None})

    print(request.url)

    if 'reports' in request.url:
        return redirect("/reports/")

    return redirect("/requests/")
