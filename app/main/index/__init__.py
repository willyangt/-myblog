from flask import Blueprint


# 创建蓝图
index= Blueprint("index", __name__)

# 关联视图
from . import views