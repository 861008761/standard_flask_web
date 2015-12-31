#-*- acoding:utf-8 -*-
from flask import render_template, redirect, url_for, current_app, abort, request, make_response
from flask import flash
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, AvatarForm
from .. import db
from ..models import User, Role, Post, Comment
from ..decorators import admin_required, permission_required
from ..models import Permission
from flask.ext.login import login_required, current_user
from werkzeug import secure_filename

import os
from PIL import Image
from .utils import mkdir, mkdirbysize, mkdirbydate, safefilename, thumbnail, logger

@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '', max_age = 7*24*60*60)
	return resp

@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '1', max_age = 7*24*60*60)
	return resp

#根据show_followed参数值决定是否显示关注文章
@main.route('/', methods=['GET', 'POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post = Post(body = form.body.data, author = current_user._get_current_object())
		db.session.add(post)
		form.body.data = ''
		flash(u'博客已发送')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed', ''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	posts = pagination.items
	return render_template('index.html', form = form, posts = posts, pagination = pagination, show_followed = show_followed)

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

#博客的分享链接
@main.route('/post/<int:id>', methods = ['GET', 'POST'])
def post(id):
	post = Post.query.filter_by(id = id).first()
	form = CommentForm()
	if not current_user.is_authenticated:
		flash(u'尚未登录')
	if form.validate_on_submit():
		if current_user.can(Permission.COMMENT):
			comment = Comment(body = form.body.data, post = post, author = current_user._get_current_object(), disabled = False)
			db.session.add(comment)
			flash(u'新的评论')
			return redirect(url_for('.post', id = post.id, page = -1))
	page = request.args.get('page', 1, type = int)
	if page == -1:
		page = (post.comments.count() - 1) / current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
	pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out = False)
	comments = pagination.items
	return render_template('post.html', posts = [post], comments = comments, form = form, pagination = pagination)

#博客的编辑页面
@main.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit_post(id):
	post = Post.query.filter_by(id = id).first()
	if current_user != post.author and not current_user.can(Permission.ADMINISTER):#注意：这里不能使用is not的表达
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		flash(u'修改成功')
		return redirect(url_for('.index'))
	form.body.data = post.body
	return render_template('edit_post.html', form = form, posts = [post])

#用户关注
@main.route('/follow/<int:id>', methods = ['GET', 'POST'])
@login_required
@permission_required(Permission.FOLLOW)
def follow(id):
	user = User.query.filter_by(id = id).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash(u'已经关注过该用户')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		current_user.follow(user)
		flash(u'关注成功')
	return redirect(url_for('.user', username = user.username))

#用户取消关注
@main.route('/unfollow/<int:id>', methods = ['GET', 'POST'])
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(id):
	user = User.query.filter_by(id = id).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash(u'没有关注过该用户')
		return redirect(url_for('.user', username = user.username))
	if current_user.is_following(user):
		current_user.unfollow(user)
		flash(u'取消关注成功')
	return redirect(url_for('.user', username = user.username))

#关注当前用户的人列表
@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first() 
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	pagination = user.followers.paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	follows = [{'user' : item.follower, 'timestamp' : item.timestamp} for item in pagination.items]
	return render_template('followers.html', user = user, title = u"粉丝列表", endpoint = '.followers', pagination = pagination, follows = follows)

#当前用户关注的人列表
@main.route('/followed-by/<username>', methods = ['GET', 'POST'])
def followed_by(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash(u'用户不存在')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	pagination = user.followed.paginate(page, per_page = current_app.config['FALSKY_POSTS_PER_PAGE'], error_out = False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
	return render_template('followers.html', user = user, title = u"关注列表", endpoint = '.followers', pagination = pagination, follows = follows)

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
		flash(u'已保存')
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
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash(u'已保存')
		return redirect(url_for('.user', username = user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form = form, user = user)

#管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page = request.args.get('page', 1, type = int)
	pagination = Comment.query.order_by(Comment.timestamp.asc()).paginate(page, per_page = current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out = False)
	comments = pagination.items
	return render_template('moderate.html', comments = comments, pagination = pagination, page = page)

#屏蔽评论
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = True
	db.session.add(comment)
	flash(u'评论已屏蔽')
	return redirect(url_for('.moderate', page = request.args.get('page', 1, type = int)))

#恢复评论
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment = Comment.query.get_or_404(id)
	comment.disabled = False
	db.session.add(comment)
	flash(u'评论已恢复')
	return redirect(url_for('.moderate', page = request.args.get('page', 1, type = int)))

#上传头像
UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@main.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			import os
			filename = secure_filename(file.filename)
			filename = current_user.getUserName() + '_' + filename
			# print current_user.getUserName
			filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
			print filepath
			current_user.setImage_url(filepath)
			file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('.uploaded_file', filename = filename))
	return render_template('uploadimage.html')

#查看已上传
from flask import send_from_directory
@login_required
@main.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# from .forms import PhotoForm
# import os
# @main.route('/upload', methods = ['GET', 'POST'])
# def upload():
#     form = PhotoForm()
#     if form.validate_on_submit():
#         filename = secure_filename(form.photo.data.filename)
#         file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
#     else:
#         filename = None
#     return render_template('upload.html', form = form, filename = filename)



#验证角色修饰器
@main.route('/admin')
@login_required
@admin_required
def admin():
    return u"具有管理员权限可见！"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def modorator():
    return u"具有管理评论权限可见"



@main.route('/avatar', methods=['GET', 'POST'])
@login_required
def avatar():
    form = AvatarForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            safe_filename = safefilename(form.avatar_url.data.filename)

            # create directory
            upload_url = mkdir(current_app.config['UPLOADDIR'])
            avatar_path = mkdir(os.path.join(upload_url, 'avatar'))
            size150_path = mkdirbysize(avatar_path, size=150)
            date150_path, date_dir = mkdirbydate(size150_path)

            # avatar_url_sql = os.path.join(date_dir, safe_filename)

            im = rim = crop150 = None
            try:
                im = Image.open(form.avatar_url.data)
                width, height = im.size
                nwidth, nheight = thumbnail(width, height, 500.0)
                rim = im.resize((nwidth, nheight), Image.ANTIALIAS)
                logger.info('picture {}, {} has been resize to {} {}'.format(width, height, nwidth, nheight))

                size = (int(form.data.get('x1')), int(form.data.get('y1')), int(form.data.get('x2')), int(form.data.get('y2')))
                crop150 = rim.crop(size).resize((150, 150), Image.ANTIALIAS)
                logger.info('picture has been crop')

                crop150.save(os.path.join(date150_path, safe_filename))
                logger.info('picture has upload successful')
                flash(u'上传头像成功', category='success')
                filepath2 = os.path.join(date150_path, safe_filename)
                current_user.setImage_url(filepath2)
                return redirect('.')
            except:
                logger.error('picture crop and save error')
                flash(u'上传头像失败', category='error')
            finally:
                if crop150:
                    crop150.close()
                if rim:
                    rim.close()
                if im:
                    im.close()
    template_name_or_list = 'uploadimage.html'
    return render_template(**locals())




