#-*- acoding:utf-8 -*-
from flask import jsonify
from app.exceptions import ValidationError
from . import api

def bad_request(message):
	response = jsonify({'error': 'bad request', 'message': message})
	response.status_code = 400
	return response

def unauthorized(message):
	response = jsonify({'error': 'unauthorized', 'message': message})
	response.status_code = 401
	return response

def forbidden(message):
	response = jsonify({'error': 'forbidden', 'message': message})
	response.status_code = 403
	return response

#这里使用的 errorhandler 修饰器和注册 HTTP 状态码处理程序时使用的是同一个,
#只不过 此时接收的参数是 Exception 类,只要抛出了指定类的异常,就会调用被修饰的
#函数。注意,这个修饰器从 API 蓝本中调用,所以只有当处理蓝本中的路由时抛出了异常才会调用 这个处理程序。
@api.errorhandler(ValidationError)
def validation_error(e):
	return bad_request(e.args[0])


