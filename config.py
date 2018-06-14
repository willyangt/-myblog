import os
import os.path
from redis import StrictRedis
# 找到当前目录
base_dir = os.path.abspath(os.path.dirname(__file__))

# 主配置类
class Config(object):

    # redis地址
    REDIS_HOST = '127.0.0.1'
    REDIS_POST = 6379

    DEBUG = True
# 设置秘钥--base64生成的随机码
    SECRET_KEY = 'v3SJ7aJLfjNZjuNGsPImCD3mLPjU9J6NL/5c7b/67Y5ml8drQtABJjiRj1lbBs3suenhnUSnA6q0oSLeH6Mojg=='
    # 配置ｍｙｓｑｌ数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/myblog'
    # 动态追踪关闭
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # 指定ｓｅｓｓｉｏｎ缓存入ｅｄｉｓ数据库
    SESSION_TYPE = 'redis'
    # ｓｅｓｓｉｏｎ签名
    SESSION_USE_SINGER = True
    # ｓｅｓｓｉｏｎ存活时间
    PERMANENT_SESSION_LIFETIME = 86400

    # 配置ｒｅｄｉｓ数据库
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_POST)

# 开发模式类
class Development(Config):
    DEBUG = True

# 生产模式类
class Production(Config):
    DEBUG = False


config = {
    'develop': Development,
    'product': Production
}