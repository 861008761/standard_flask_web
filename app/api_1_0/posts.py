#-*- acoding:utf-8 -*-
from ..models import Post, Permission, Comment
from flask import request, g, jsonify, url_for, current_app
from app import db
from . import api
from .authentication import auth
from .decorators import permission_required
from .errors import forbidden

#查看全部文章(分页查看技术)
#测试代码通过：http --json --auth '861008761@qq.com':'123456' --json GET ht
#tp://127.0.0.1:5000/api/v1.0/posts/
@api.route('/posts/')
@auth.login_required
def get_posts():
	page = request.args.get('page', 1, type = int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	posts = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_posts', page = page - 1, _external = True)
	next = None
	if pagination.has_next:
		next = url_for('api.get_posts', page = page + 1, _external = True)
	json_posts = {
					'posts': [post.to_json() for post in posts], 
					'prev': prev, 
					'next': next, 
					'page': page, 
					'count': pagination.total
				 }
	return jsonify(json_posts)

#查看单篇文章
#测试代码通过：http --json --auth '861008761@qq.com':'123456' --json GET ht
#tp://127.0.0.1:5000/api/v1.0/posts/1
@api.route('/posts/<int:id>')
@auth.login_required
def get_post(id):
	post = Post.query.get_or_404(id)
	return jsonify(post.to_json())

#增加新文章
#测试代码通过：http --json --auth '861008761@qq.com':'123456' --json POST http://127.0.0.1:5000/api/v1.0/posts/ "body=new post again"
@api.route('/posts/', methods = ['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
	post = Post.from_json(request.json)
	post.author = g.current_user
	db.session.add(post)
	db.session.commit()
	return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id = post.id, _external = True)}

#修改(编辑)文章
#非本人非管理员用户jack2试图修改evelyn文章，拒绝：
#http --json --auth '1920727070@qq.com':'123456' --json PUT ht
#tp://127.0.0.1:5000/api/v1.0/posts/1 "body=edit your blog just now"
#报错：
# HTTP/1.0 403 FORBIDDEN
# Content-Length: 68
# Content-Type: application/json
# Date: Wed, 09 Dec 2015 13:05:01 GMT
# Server: Werkzeug/0.11.2 Python/2.7.10

# {
#     "error": "forbidden", 
#     "message": "Insufficient permissions"
# }

# 管理员修改用户blog内容通过测试：
# http --json --auth '861008761@qq.com':'123456' --json PUT http://127.0.0.1:5000/api/v1.0/posts/1 "body=edit your blog just now"
# HTTP/1.0 200 OK
# Content-Length: 335
# Content-Type: application/json
# Date: Wed, 09 Dec 2015 13:11:20 GMT
# Server: Werkzeug/0.11.2 Python/2.7.10

# {
#     "author": "http://127.0.0.1:5000/api/v1.0/users/1", 
#     "body": "edit your blog just now", 
#     "body_html": "<p>edit your blog just now</p>", 
#     "comment_count": 1, 
#     "comments": "http://127.0.0.1:5000/api/v1.0/posts/1/comments/", 
#     "timestamp": "Sat, 28 Nov 2015 00:00:00 GMT", 
#     "url": "http://127.0.0.1:5000/api/v1.0/posts/1"
# }
@api.route('/posts/<int:id>', methods = ['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
	post = Post.query.get_or_404(id)
	if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
		return forbidden('Insufficient permissions')
	post.body = request.json.get('body', post.body)
	db.session.add(post)
	return jsonify(post.to_json())

#获取单篇文章已有评论
#测试通过代码：http --json --auth '1920727070@qq.com':'123456' --json GET ht
#tp://127.0.0.1:5000/api/v1.0/posts/1/comments/
@api.route('/posts/<int:id>/comments/')
@auth.login_required
def get_post_comments(id):
	post = Post.query.get_or_404(id)
	page = request.args.get('page', 1, type = int)
	pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page, per_page = 5, error_out = False)
	prev = None
	if pagination.has_prev:
		prev = url_for('api.get_post_comments', id = id, page = page - 1, _external = True)
	next = None
	if pagination.has_next:
		next = url_for('api.get_post_comments', id = id, page = page + 1, _external = True)
	comments = pagination.items
	return jsonify({
					'comments': [comment.to_json() for comment in comments], 
					'prev': prev, 
					'next': next, 
					'page': page, 
					'pageCount': pagination.total
					})
					

#添加新的评论
#测试通过代码：http --json --auth '1920727070@qq.com':'123456' --json POST ht
#tp://127.0.0.1:5000/api/v1.0/posts/1/comments/ "body=my test comment"
@api.route('/posts/<int:id>/comments/', methods = ['POST'])
@auth.login_required
@permission_required(Permission.COMMENT)
def new_comment(id):
	comment = Comment.from_json(request.json)
	comment.author_id = g.current_user.id
	comment.post_id = id
	comment.disabled = False
	db.session.add(comment)
	db.session.commit()
	return jsonify(comment.to_json()), 201, {'Location': url_for('api.get_comment', id = comment.id, _external = True)}

#修改(编辑)评论















