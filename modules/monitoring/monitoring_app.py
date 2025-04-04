from datetime import datetime

import httpx
from flask import Blueprint, render_template, request, flash, redirect
from werkzeug.security import check_password_hash
from forms import  VisitorsPassageForm, CarsPassageForm, SpecTransportForm
from utills.enums import RequestStatus, Scopes, RequestType
from utills.utils import build_request

monbp = Blueprint('monbp', __name__)


def _get_content(visitors_form, cars_form, spec_form, request_id):
    user_role = request.cookies.get("role")
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

        requests_response = build_request(
            "http://localhost:3002/api/v3/requests/list/?monitoring=true",
        )

        if requests_response.status_code != 200:
            flash(f"СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {requests_response.status_code}")
            return render_template("pages/monitoring.html",
                                   cars_form=CarsPassageForm(),
                                   spec_form=SpecTransportForm(),
                                   visitors_form=VisitorsPassageForm())

        requests = requests_response.json()['requests']

        for req in requests:
            req.update(req | {"approval": build_request(f"http://localhost:3003/api/v3/approval/request/{req['id']}").json()})

        cars_on_territory_response = build_request(
            "http://localhost:3002/api/v3/request/cars/on_territory"
        )

        if cars_on_territory_response.status_code != 200:
            flash(f"НЕ УДАЛОСЬ ПОЛУЧИТЬ АВТОМОБИЛИ НА ТЕРРИТОРИИ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {cars_on_territory_response.status_code}")
            return render_template("pages/monitoring.html",
                                   cars_form=CarsPassageForm(),
                                   spec_form=SpecTransportForm(),
                                   visitors_form=VisitorsPassageForm())

        return render_template(
            "pages/monitoring.html",
            is_admin=is_admin,
            user=user.json(),
            requests=requests,
            cars_form=cars_form,
            spec_form=spec_form,
            cars_on_territory=cars_on_territory_response.json(),
            visitors_form=visitors_form,
            request_id=request_id,
        )

    except httpx.ConnectError:
        flash("СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН")
        return render_template("pages/monitoring.html", cars_form=cars_form,
            visitors_form=visitors_form)


def _close_request(request_id) -> bool | str:
    get_request = build_request(
        f"http://localhost:3002/api/v3/request/{request_id}"
    )

    if get_request.status_code != 200:
        flash(f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ЗАЯВКУ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {get_request.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())

    if get_request.json()["type"]['name'] == RequestType.DISPOSABLE.value:
        passage_counter = 0
        if get_request.json()["visitors"]:
            for v in get_request.json()["visitors"]:
                if v["passed_status"]: passage_counter += 1
        if get_request.json()["cars"]:
            for c in get_request.json()["cars"]:
                if c["passed_status"]: passage_counter += 1

        if passage_counter == (len(get_request.json()["visitors"]) + len(get_request.json()["cars"] if get_request.json()["cars"] else [])):

            status = build_request(
                f"http://localhost:3002/api/v3/request/status/{RequestStatus.CLOSED.value}"
            )

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
                    "is_deleted": get_request.json()["is_deleted"],
                    "id": get_request.json()["id"]
                },
                "visitors_": None,
                "cars_": None
            }

            update_request = build_request(
                f"http://localhost:3002/api/v3/request/update",
                method="PUT",
                data=update_request_payload
            )
            if update_request.status_code != 200:
                flash(
                    f"НЕ УДАЛОСЬ ЗАКРЫТЬ ОДНОРАЗОВУЮ ЗАЯВКУ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {update_request.status_code}")
                return render_template("pages/monitoring.html",
                                       cars_form=CarsPassageForm(),
                                       spec_form=SpecTransportForm(),
                                       visitors_form=VisitorsPassageForm())

            print("CLOSED REQUEST ID:", get_request.json()["id"])

            return True
        else:
            return False
    else:
        return False


def _update_passage_status(form):
    data = []
    update_payload = []
    url = ""
    if isinstance(form, VisitorsPassageForm):
        data = [
            {
                "pass_date": datetime.now(),
                "status": True,
                "visitor_id": choice
            } for choice in form.visitors_check_group.data
        ]
        ids_payload = {
            "ids": [choice for choice in form.visitors_check_group.data]
        }

        get_visitors = build_request(
            "http://localhost:3002/api/v3/request/visitors/ids",
            data=ids_payload,
            method="POST"
        )

        if get_visitors.status_code != 200:
            flash(
                f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ПОСЕТИТЕЛЯХ ДЛЯ ОБНОВЛЕНИЯ СТАТУСА ПРОХОДА, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {get_visitors.status_code}")
            return render_template("pages/monitoring.html",
                                   cars_form=CarsPassageForm(),
                                   spec_form=SpecTransportForm(),
                                   visitors_form=VisitorsPassageForm())
        update_payload = {
            "request_": None,
            "visitors_": [visitor | {"passed_status": True} for visitor in get_visitors.json()["visitors"]],
            "cars_": None
        }

        url = "http://localhost:3005/api/v3/passage/create"

    elif isinstance(form, CarsPassageForm):
        print("CARS PASSAGE")
        data = [
            {
                "pass_date": datetime.now(),
                "status": True,
                "car_id": choice
            } for choice in form.cars_check_group.data
        ]

        ids_payload = {
            "ids": [choice for choice in form.cars_check_group.data]
        }

        get_cars = build_request(
            "http://localhost:3002/api/v3/request/cars/ids",
            data=ids_payload,
            method="POST"
        )

        print(get_cars.status_code, "<-- status")

        if get_cars.status_code != 200:
            flash(
                f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ ОБ АВТОТРАНСПОРТЕ ДЛЯ ОБНОВЛЕНИЯ СТАТУСА ПРОХОДА, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {get_cars.status_code}")
            return render_template("pages/monitoring.html",
                                   cars_form=CarsPassageForm(),
                                   spec_form=SpecTransportForm(),
                                   visitors_form=VisitorsPassageForm())

        update_payload = {
            "request_": None,
            "visitors_": None,
            "cars_": [car | {"passed_status": True, "on_territory": True} for car in get_cars.json()["cars"]]
        }

        url = "http://localhost:3004/api/v3/passage/create"

    create_passages = build_request(
        url,
        data=data,
        method="POST"
    )

    print(create_passages.status_code != 200, "<-- status")

    if create_passages.status_code != 200:
        flash(
            f"СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН, СЕРВИС ПРОХОДОВ ПОСЕТИТЕЛЕЙ ВЕРНУЛ КОД: {create_passages.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())

    update_passage = build_request(
        f"http://localhost:3002/api/v3/request/update",
        method="PUT",
        data=update_payload
    )

    if update_passage.status_code != 204:
        flash(f"НЕ УДАЛОСЬ ОБНОВИТЬ СТАТУС ПРОХОДА, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {update_passage.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())
    return


@monbp.route('/')
def index():
    visitors_form = VisitorsPassageForm()
    cars_form = CarsPassageForm()
    spec_form = SpecTransportForm()

    try:
        car_types = build_request(
            "http://localhost:3002/api/v3/request/car/types",
        )

        if car_types.status_code != 200:
            flash(
            f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ЗАЯВКЕ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {car_types.status_code}")
            return render_template("pages/monitoring.html",
                                   cars_form=CarsPassageForm(),
                                   spec_form=SpecTransportForm(),
                                   visitors_form=VisitorsPassageForm())

        spec_form.type_field.choices = [(car_type['id'], f'{car_type['type']}') for car_type in car_types.json()["car_types"] if car_type["type"] != "По заявке"]

        return _get_content(visitors_form, cars_form, spec_form, None)
    except httpx.ConnectError as e:
        flash(
            f"МОНИТОРИНГ НЕДОСТУПЕН, НЕ УДАЛОСЬ СВЯЗАТЬСЯ С СЕРВИСОМ ЗАЯВОК")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())


@monbp.route('/<request_id>')
def passage(request_id: int):
    visitors_form = VisitorsPassageForm()
    cars_form = CarsPassageForm()
    spec_form = SpecTransportForm()

    car_types = build_request(
        "http://localhost:3002/api/v3/request/car/types",
    )

    if car_types.status_code != 200:
        flash(
        f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ЗАЯВКЕ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {car_types.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())

    spec_form.type_field.choices = [(car_type['id'], f'{car_type['type']}') for car_type in car_types.json()["car_types"] if car_type["type"] != "По заявке"]

    get_request = build_request(f"http://localhost:3002/api/v3/request/{request_id}")

    if get_request.status_code != 200:
        flash(
        f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ЗАЯВКЕ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {get_request.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())

    cars_choices, visitors_choices = [], []
    if get_request.json()["visitors"]:
        for visitor in get_request.json()["visitors"]:
            if get_request.json()["type"]["name"] == RequestType.DISPOSABLE.value and visitor["passed_status"]:
                continue
            visitors_choices.append((visitor['id'], f'{visitor['lastname']} {visitor['name']} {visitor['patronymic']}'))

    if get_request.json()["cars"]:
        for car in get_request.json()["cars"]:
            if get_request.json()["type"]["name"] == RequestType.DISPOSABLE.value and car["passed_status"]:
                continue
            cars_choices.append((car['id'], f'{car['govern_num']} {car['car_model']}'))

    visitors_form.visitors_check_group.choices = visitors_choices
    cars_form.cars_check_group.choices = cars_choices

    return _get_content(visitors_form, cars_form, spec_form, request_id)


@monbp.route('/visitors/passage', methods=['POST'])
def process_visitors_passage():
    visitors_form = VisitorsPassageForm()
    request_id = request.args.get("request")
    if visitors_form.validate_on_submit():
        if visitors_form.pass_submit.data:

            _update_passage_status(visitors_form)

            _closed_status = _close_request(request_id)

            if _closed_status:
                return redirect(f"/monitoring")

            return redirect(f"/monitoring/{request_id}?show=true")


@monbp.route('/cars/passage', methods=['POST'])
def process_cars_passage():
    cars_form = CarsPassageForm()
    request_id = request.args.get("request")
    if cars_form.validate_on_submit():
        if cars_form.pass_submit.data:

            _update_passage_status(cars_form)

            _closed_status = _close_request(request_id)

            if _closed_status:
                return redirect(f"/monitoring")

            return redirect(f"/monitoring/{request_id}?show=true")


@monbp.route('/spec/passage', methods=['POST'])
def process_spec_passage():
    spec_form = SpecTransportForm()
    car_types = build_request(
        "http://localhost:3002/api/v3/request/car/types",
    )

    if car_types.status_code != 200:
        flash(
        f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ О ЗАЯВКЕ, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {car_types.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())

    spec_form.type_field.choices = [(car_type['id'], f'{car_type['type']}') for car_type in car_types.json()["car_types"] if car_type["type"] != "По заявке"]
    if spec_form.validate_on_submit():
        if spec_form.pass_spec_submit.data:

            cars = [
                {
                    "govern_num": spec_form.govern_num_field.data.replace(" ", "").upper(),
                    "car_model": spec_form.model_field.data.upper(),
                    "passed_status": False,
                    "type_id": spec_form.type_field.data,
                    "request_id": None,
                    "visitor_id": None,
                    "is_deleted": False,
                    "on_territory": True,
                    "date_deleted": None,
                    "date_created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                }
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
                return redirect("/requests/")

            print(add_car_request.json(), "<- created_car")

            data = [
                {
                    "pass_date": datetime.now(),
                    "status": True,
                    "car_id": add_car_request.json()[0]["id"]
                }
            ]

            create_passages = build_request(
                "http://localhost:3004/api/v3/passage/create",
                data=data,
                method="POST"
            )

            print(create_passages.status_code != 200, "<-- status")

            if create_passages.status_code != 200:
                flash(
                    f"СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН, СЕРВИС ПРОХОДОВ ПОСЕТИТЕЛЕЙ ВЕРНУЛ КОД: {create_passages.status_code}")
                return render_template("pages/monitoring.html",
                                       cars_form=CarsPassageForm(),
                                       spec_form=SpecTransportForm(),
                                       visitors_form=VisitorsPassageForm())

    return redirect(f"/monitoring")


@monbp.route('/car/out/<car_id>', methods=['GET'])
def process_cars_out(car_id):
    print(car_id)

    ids_payload = {
        "ids": [car_id],
    }

    get_cars = build_request(
        "http://localhost:3002/api/v3/request/cars/ids",
        data=ids_payload,
        method="POST"
    )

    data = [
        {
            "pass_date": datetime.now(),
            "status": False,
            "car_id": car_id
        }
    ]

    create_passages = build_request(
        "http://localhost:3004/api/v3/passage/create",
        data=data,
        method="POST"
    )

    print(create_passages.status_code != 200, "<-- status")

    if create_passages.status_code != 200:
        flash(
            f"СЕРВИС МОНИТОРИНГА НЕДОСТУПЕН, СЕРВИС ПРОХОДОВ ПОСЕТИТЕЛЕЙ ВЕРНУЛ КОД: {create_passages.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())


    if get_cars.status_code != 200:
        flash(
            f"НЕ УДАЛОСЬ ПОЛУЧИТЬ ИНФОРМАЦИЮ ОБ АВТОТРАНСПОРТЕ ДЛЯ ОБНОВЛЕНИЯ СТАТУСА ПРОХОДА, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {get_cars.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())

    update_payload = {
        "request_": None,
        "visitors_": None,
        "cars_": [car | {"passed_status": True, "on_territory": False} for car in get_cars.json()["cars"]]
    }

    update_passage = build_request(
        f"http://localhost:3002/api/v3/request/update",
        method="PUT",
        data=update_payload
    )

    if update_passage.status_code != 204:
        flash(f"НЕ УДАЛОСЬ ОБНОВИТЬ СТАТУС ПРОХОДА, СЕРВИС ЗАЯВОК ВЕРНУЛ КОД: {update_passage.status_code}")
        return render_template("pages/monitoring.html",
                               cars_form=CarsPassageForm(),
                               spec_form=SpecTransportForm(),
                               visitors_form=VisitorsPassageForm())


    return redirect(f"/monitoring")

