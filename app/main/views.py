#-*- acoding:utf-8 -*-
from flask import render_template, redirect, url_for, current_app, abort, request
from flask import flash
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import User, Role, Post
from ..decorators import admin_required, permission_required
from ..models import Permission
from flask.ext.login import login_required, current_user

@main.route('/', methods=['GET', 'POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(body = form.body.data, author = current_user._get_current_object())
		db.session.add(post)
		form.body.data = ''
		flash('blog is recorded')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	posts = pagination.items
	return render_template('index.html', form = form, posts = posts, pagination = pagination)

#个人信息页面，路径形式：/user/jack
@main.route('/user/<username>', methods = ['GET', 'POST'])
def user(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type = int)
    #pagination = Post.query.filter_by(author = user).order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
    posts = pagination.items
    return render_template('user.html', user = user, posts = posts, pagination = pagination)

#普通用户编辑个人信息表单
@main.route('/edit_profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = current_user.email).first()
		user.name = form.real_name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('Edit profile successfuily')
		return redirect(url_for('.user', username = user.username))
	return render_template('edit_profile.html', form = form)

#管理员的编辑个人信息表单
@main.route('/edit_profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user = user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirm = form.confirm.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('Edit your profile successfuily!')
		return redirect(url_for('.user', username = user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirm.data = user.confirm
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form = form, user = user)


#验证角色修饰器
@main.route('/admin')
@login_required
@admin_required
def admin():
    return "For administrators only!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def modorator():
    return "For comment moderators!"








