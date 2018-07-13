from flask import request, jsonify, current_app, make_response

from app.utils.response_code import RET
from app.utils.captcha.captcha import captcha
from . import entrance
from app import redis_store
from app import constants

@entrance.route('/image_code')
def image_code():
    """生成图片验证码并返回"""
    # ｊｓ生成用于唯一标识验证码
    image_code_id = request.args.get("image_code_id")
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg = "image_code_id不存在")
    # 调用第三方工具得到验证码图片及验证码字符串
    name, text, image = captcha.generate_captcha()
    # 将真实字符串保存到ｒｅｄｉｓ
    try:
        redis_store.setex("ImageCode" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="保存图片验证码错误")
    # 把图片返回给前段展示
    else:
        # 生成响应对象返回ｉｍａｇｅ
        response = make_response(image)
        response.headers["Content--Type"] = "image/jpg"
        return response
