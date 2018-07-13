from flask.blueprints import Blueprint
# 创建登陆注册蓝图
entrance = Blueprint("entrance", __name__, url_prefix="/entrance")

from . import views