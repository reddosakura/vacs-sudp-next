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

        requests_actual = build_request(
            f"http://localhost:3002/api/v3/requests/list/?monitoring=false&fdate={datetime.datetime.now().date()}&tdate={datetime.datetime.now().date()}&is_filtered=false&is_consideration=false&is_approval=false&is_admin=false"
        )

        if requests_actual.status_code != 200:
            flash('Request list not found.')
            return render_template("pages/request_report.html", user={"role": None})

        # pprint(requests_actual.json(), sort_dicts=False)
        # print(len(requests_actual.json()['requests']))

        return render_template("pages/request_report.html",
                               user=user.json(),
                               requests_data=requests_actual.json()['requests'],
                               form=form
                               )

    except httpx.ConnectError:
        flash('Request list not found.')
        return render_template("pages/request_report.html", user={"role": None})



@repbp.route('/search', methods=['GET'])
def search():
    form = RequestFilterSearchForm(request.args)
    # if form.validate_on_submit():
    print(form.data)

    return redirect("/reports")
    # return render_template("pages/request_report.html")
