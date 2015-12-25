#-*- acoding:utf-8 -*-
from ..models import User, Permission, Post
from flask import request, g, jsonify, url_for, current_app
from app import db
from . import api
from .authentication import auth
from .decorators import permission_required
from .errors import forbidden
from werkzeug import secure_filename
import os

#一个用户
#http --json --auth '861008761@qq.com':'123456' --json GET http://127.0.0.1:5000/api/v1.0/users/1
#
@api.route('/users/<int:id>')
@auth.login_required
def get_user(id):
	user = User.query.get_or_404(id)
	return jsonify(user.to_json())

#一个用户的所有博客文章
#http --json --auth '861008761@qq.com':'123456' --json GET http://127.0.0.1:5000/api/v1.0/users/1/posts/
#
@api.route('/users/<int:id>/posts/')
@auth.login_required
def get_user_posts(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type = int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	posts = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_user_posts', id = id, page = page - 1, _external = True)
	next = None
	if pagination.has_next:
		next = url_for('api.get_user_posts', id = id, page = page + 1, _external = True)
	return jsonify({
					'posts': [post.to_json() for post in posts], 
					'prev': prev, 
					'next': next, 
					'count': pagination.total
					})

#一个用户所关注用户发布的文章
#http --json --auth '861008761@qq.com':'123456' --json GET http://127.0.0.1:5000/api/v1.0/users/1/timeline/
@api.route('/users/<int:id>/timeline/')
@auth.login_required
def get_user_followed_posts(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type = int)
	pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	posts = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_user_followed_posts', id = id, page = page - 1, _external = True)
	next = None
	if pagination.has_next:
		next = url_for('api.get_user_followed_posts', id = id, page = page + 1, _external = True)
	return jsonify({
					'posts': [post.to_json() for post in posts], 
					'prev': prev, 
					'next': next, 
					'count': pagination.total
					})

#管理员编辑用户信息
#http --json --auth '861008761@qq.com':'123456' --json PUT http://127.0.0.1:5000/api/v1.0/users/1 "username=rebaccccca"
@api.route('/users/<int:id>', methods = ['PUT'])
@permission_required(Permission.ADMINISTER)
def edit_user(id):
	user = User.query.get_or_404(id)
	if g.current_user != user and not g.current_user.can(Permission.ADMINISTER):
		return forbidden('Insufficient permissions')
	user.username = request.json.get('username', user.username)
	user.location = request.json.get('location', user.location)
	user.about_me = request.json.get('about_me', user.about_me)
	db.session.add(user)
	db.session.commit()
	return jsonify(user.to_json())

#用户更换头像
@api.route('/avatar/<int:id>', methods = ['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_avatar(id):
	user = User.query.get_or_404(id)
	if g.current_user != user and not g.current_user.can(Permission.WRITE_ARTICLES):
		return forbidden('Insufficient permissions')
	file = request.files['file']
	filename = secure_filename(file.filename)
	filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
	print filepath
	file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
	user.image_url = filepath
	db.session.add(user)
	db.session.commit()
	return jsonify(user.to_json())

#用户关注者与被关注者
#关注用户
#取消关注
#用户关注列表
#管理员编辑用户信息
#
#












