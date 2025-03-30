from flask import Blueprint, render_template, request, flash, redirect


cambp = Blueprint('cambp', __name__)


@cambp.route('/')
def index():
    return render_template("pages/camera.html", user={"role": None}, camera_status=True)
