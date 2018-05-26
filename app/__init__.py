#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()






def create_app():
    app = Flask(__name__)
    # db.init_app(app)
    login_manager.init_app(app)
    return app

