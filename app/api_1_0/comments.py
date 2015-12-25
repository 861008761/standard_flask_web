#-*- acoding:utf-8 -*-
from flask import jsonify, g, request
from . import api
from .authentication import auth
from .decorators import permission_required
from .errors import forbidden
from ..models import Comment, Permission
from .. import db

#所有评论
#测试代码通过：http --json --auth '861008761@qq.com':'123456' --json GET ht
#tp://127.0.0.1:5000/api/v1.0/comments/
@api.route('/comments/')
@auth.login_required
def get_comments():
	comments = Comment.query.all()
	return jsonify({'comments': [comment.to_json() for comment in comments]})

#一篇评论
#测试代码通过：http --json --auth '861008761@qq.com':'123456' --json GET ht
#tp://127.0.0.1:5000/api/v1.0/comments/1
@api.route('/comments/<int:id>')
@auth.login_required
def get_comment(id):
	comment = Comment.query.get_or_404(id)
	return jsonify(comment.to_json())

#编辑评论
#测试代码通过 注意多个参数时测试代码的写法 用空格隔开：http --json --auth '861008761@qq.com':'123456' --json PUT ht
#tp://127.0.0.1:5000/api/v1.0/comments/1 "disabled=0" "body=jack is mine"
@api.route('/comments/<int:id>', methods = ['PUT'])
@permission_required(Permission.COMMENT)
def edit_comment(id):
	comment = Comment.query.get_or_404(id)
	if g.current_user != comment.author and not g.current_user.can(Permission.ADMINISTER):
		return forbidden('Insufficient permissions')
	comment.body = request.json.get('body', comment.body)#理解：如果body在json中，就用body替换，否则用comment.body替换？？？
	if request.json.get('disabled') == '0':
		comment.disabled = False
	elif request.json.get('disabled') == '1':
		comment.disabled = True
	db.session.add(comment)
	return jsonify(comment.to_json())

#管理评论
# @api.route('/comments-enable/<int:id>', methods = ['PUT'])
# @permission_required(Permission.COMMENT)
# def enable_comment(id):
# 	comment = Comment.query.get_or_404(id)
# 	if g.current_user != comment.author and not g.current_user.can(Permission.ADMINISTER):
# 		return forbidden('Insufficient permissions')
# 	if request.json.get('disabled') == '0':
# 		comment.disabled = False
# 	if request.json.get('disabled') == '1':
# 		comment.disabled = True
# 	if request.json.get('disabled') is None:
# 		comment.disabled = comment.disabled
# 	print request.json.get('disabled')
# 	db.session.add(comment)
# 	return jsonify(comment.to_json())









