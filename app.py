from flask import Flask, redirect
from modules.auth.auth_app import authbp
from modules.processing.processing_app import procbp
from modules.requests.request_app import reqbp
from modules.users.users_app import usersbp

app = Flask(__name__)
app.config['SECRET_KEY'] = '71ab49b1708ec1919ab7338c07fef5eb892c8bd052fdc772615248ff1f933847b8d4bbb340a1836185e0b3e4d911b6e2311faf22f0295676cead31f35dfd9f87'
app.register_blueprint(authbp, url_prefix='/auth')
app.register_blueprint(usersbp, url_prefix='/users')
app.register_blueprint(reqbp, url_prefix='/requests')
app.register_blueprint(procbp, url_prefix='/processing')

@app.route('/')
def index():
    return redirect("/auth")

if __name__ == '__main__':
    app.run()
