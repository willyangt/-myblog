#!/usr/bin/env python
# coding: utf-8
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session

from flask_wtf.csrf import CSRFProtect, generate_csrf

from config import config ,Config
# from flask_login import LoginManager

# login_manager = LoginManager()


# 实例出ｄｂ
db = SQLAlchemy()

# 实例ｒｅｄｉｓ----制定解码为Ｔｒｕｅ，不然拿出来的是１６进制码
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_POST, decode_responses=True)

# 创建日志
# 集成项目日志
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)





def create_app(config_name):
    # 实例出ａｐｐ
    app = Flask(__name__)
    # db.init_app(app)
    # login_manager.init_app(app)

    # 加载配置信息
    app.config.from_object(config[config_name])
    # SQLAlchemy关联程序实例
    db.init_app(app)
    # Session关联ａｐｐ－－flask_session的拓展,用；来配置与数据库的连接，为状态保持的ｓｅｓｓｉｏｎ提供缓存地址
    Session(app)
    # 启用csrf保护
    CSRFProtect(app)

    # 用请求钩子把ｃｓｒｆ_ｔｏｋｅｎ写入浏览器ｃｏｏｋｉｅ
    @app.after_request
    def after_request(response):
        # 调用方法生成ｃｏｏｋｉｅ
        csrf_token = generate_csrf()
        # 添加入响应返回
        response.set_cookie('csrf_token', csrf_token)
        return response

    return app


