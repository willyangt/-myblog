from flask import Blueprint

administer = Blueprint('administer', __name__)


from . import views