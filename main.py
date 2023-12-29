# main.py
from flask import Flask
from application.database import db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.secret_key = "secret"
    db.init_app(app)

    app.app_context().push()

    return app


app = create_app()

from application.controllers import *

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=2345, debug=True)
