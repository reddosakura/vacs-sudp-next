import datetime
from pprint import pprint

import httpx
from flask import Blueprint, render_template, request, flash, redirect

from forms import RequestFilterSearchForm
from utills.utils import build_request

repbp = Blueprint('repbp', __name__)


@repbp.route('/')
def index():
    form = RequestFilterSearchForm()
    try:
        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        requests_ = build_request(
            f"http://localhost:3002/api/v3/requests/list/?monitoring=false&fdate={datetime.datetime.now().date()}&tdate={datetime.datetime.now().date()}&is_filtered=false&is_consideration=false&is_approval=false&is_admin=false"
        )

        if requests_.status_code != 200:
            flash('Request list not found.')
            return render_template("pages/request_report.html", user={"role": None})

        # pprint(requests_actual.json(), sort_dicts=False)
        # print(len(requests_actual.json()['requests']))

        return render_template("pages/request_report.html",
                               user=user.json(),
                               requests_data=requests_.json()['requests'],
                               form=form
                               )

    except httpx.ConnectError:
        flash('НЕ УДАЛОСЬ СВЯЗАТЬСЯ С СЕРВИСОМ ЗАЯВОК. API НЕДОСТУПЕН')
        return render_template("pages/request_report.html", user={"role": None}, form=form)



@repbp.route('/search', methods=['GET'])
def search():
    form = RequestFilterSearchForm(request.args)
    # if form.validate_on_submit():
    print(form.data)

    try:

        user = build_request(
            f"http://localhost:3001/api/v3/users/{request.cookies.get('id')}"
        )

        if user.status_code != 200:
            return redirect("/auth")

        if not form.search_field.data and not form.filter_fdate.data and not form.filter_tdate.data and form.status_select.data == '0':
            return redirect("/reports")

        else:
            url = "http://localhost:3002/api/v3/request/search?&is_reports=true"

            if form.search_field.data:
                url += f"&value={form.search_field.data}"

            if form.filter_fdate.data and form.filter_tdate.data:
                url += f"&fdate={form.filter_fdate.data}&tdate={form.filter_tdate.data}"
            if form.status_select.data != '0':
                url += f"&status={form.status_select.data}"


            print(url)
            requests_ = build_request(url)

            # print(requests_.status_code)
            # print(requests_.json())

            if requests_.status_code != 200:
                flash(f'СЕРВИС ЗАЯВОК ВЕРНУЛ НЕКОРРЕКТНЫЙ КОД: {requests_.status_code}')
                return render_template("pages/request_report.html", user={"role": None})


            return render_template("pages/request_report.html",
                                   user=user.json(),
                                   requests_data=requests_.json()['requests'],
                                   form=form
                                   )
    except httpx.ConnectError:
        flash('НЕ УДАЛОСЬ СВЯЗАТЬСЯ С СЕРВИСОМ ЗАЯВОК. API НЕДОСТУПЕН')
        return render_template("pages/request_report.html", user={"role": None}, form=RequestFilterSearchForm())
