from flask import Blueprint, render_template

procbp = Blueprint('procbp', __name__)

@procbp.route("/", methods=["GET"])
def index():
    return render_template("pages/processing.html")
