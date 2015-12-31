#-*- acoding:utf-8 -*-
from flask.ext.httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from flask import g, jsonify, request
from .errors import unauthorized, forbidden
from . import api
auth = HTTPBasicAuth()

# 验证回调函数，这个auth是上面的auth = HTTPBasicAuth()的对象，而蓝本auth的用法是auth.route('/xxx')。额，我图样了。。。


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/authentication', methods=['POST'])
def verifypassword():
    email_or_token = request.json.get('email_or_token')
    password = request.json.get('password')
    print email_or_token
    print password
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    if user.verify_password(password):
        return jsonify(user.to_json())

# 认证密令不正确,服务器向客户端返回401错误
# 默认情况下,Flask-HTTPAuth自 动生成这个状态码,但为了和 API 返回的其他错误保持一致,我们可以自定义这个错误响应


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

# @api.route('/posts/')
# @auth.login_required
# def get_posts():
# 	pass

# 为保护路由,可使用修饰器 auth.login_required
# 现在,API 蓝本中的所有路由都能进行自动认证。而且作为附加认证,before_request 处
# 理程序还会拒绝已通过认证但没有确认账户的用户。


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

# 特殊的url 生成令牌给用户


@api.route('/token')
def token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
