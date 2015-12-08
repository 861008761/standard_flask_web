#-*- acoding:utf-8 -*-
from . import auth
from flask import render_template, redirect, request, url_for, flash
from forms import LoginForm, RegisterForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm, ChangeEmailForm
from flask.ext.login import login_required
from app.models import User
from flask.ext.login import login_user, logout_user
from .. import db
from ..email import send_email
from flask.ext.login import current_user

#用户登录
@auth.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is None:
			flash(u'该邮箱地址尚未注册，请注册之后再登录')
		else:
			if user is not None and user.verify_password(form.password.data):
				login_user(user, form.remember_me.data)
				return redirect(request.args.get('next') or url_for('main.index'))
			else:
				flash(u'密码错误')
	return render_template('auth/login.html', form = form)

#有一些页面不可以是匿名用户访问的，所以先跳转到登录页面，但是为了实现：在登录之后继续打开
#之前匿名访问的页面。所以将原来页面的地址放在请求上下文的request的args的next中。
#如果next不存在了，就跳转到首页去了。

#登出用户
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash(u'注销登录')
	return redirect(url_for('main.index'))

@auth.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(username = form.username.data, email = form.email.data, password = form.password.data)
		db.session.add(user)
		db.session.commit()
		#这里的这句话必须写，原因“注意,即便通过配置,程序已经可以在请求末尾自动提交数据库变化,这里
		#也要添加 db.session.commit() 调用。问题在于,提交数据库之后才能赋予新用户 id 值,而确认令牌需要用到 id,所以不能延后提交”
		token = user.generate_confirmation_token()
		send_email(user.email, u'验证账号', 'auth/email/confirm', user = user, token = token)
		flash(u'我们已向您的注册邮箱发送了一封确认邮件，请注意查收')
		return redirect(url_for('main.index'))
	return render_template('register.html', form = form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:#避免重复点击邮件链接的确认
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash(u'账号验证完成')
	else:
		flash(u'错误的验证链接或链接已失效')
	return redirect(url_for('main.index'))

#对一些没有确认的用户进行限制，以及引导其再次确认
@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
	if current_user.is_authenticated \
		and not current_user.confirmed \
		and request.endpoint[:5] != 'auth.' \
		and request.endpoint != 'static':
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:#理解：如果一个当前用户是匿名用户，那么不可能进入未确认界面
	#因为都没有账号，怎么能是“未验证账号”呢；其次，如果账号已经验证过的用户不小心来到这个页面，直接跳到首页就可以了
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

#再次发送确认信息
@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email, u'验证账号', 'auth/email/confirm', user = current_user, token = token)
	flash(u'我们已向您的注册邮箱发送了一封确认邮件，请注意查收')
	return redirect(url_for('main.index'))

#修改密码
@auth.route('/modifypwd', methods = ['GET', 'POST'])
@login_required
def modifypwd():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = current_user.email).first()
		if not user.verify_password(form.oldpassword.data):
			flash(u'旧密码输入错误')
		else:
			if user.verify_password(form.newpassword.data):
				flash(u'新旧密码不能相同，请使用其他密码')
			else:
				user.password = form.newpassword.data
				db.session.add(user)
				db.session.commit()
				flash(u'你刚刚修改了密码')
				return redirect(url_for('main.index'))
	return render_template('auth/modifypwd.html', form = form)

#不登录，重设密码
@auth.route('/resetquest', methods = ['GET', 'POST'])
def resetquest():
	if not current_user.is_anonymous:#如果用户已经登录，跳转到首页
		return redirect(url_for('main.index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None:
			token = user.generate_confirmation_token()
			send_email(form.email.data, u'重置密码', '/auth/email/reset', user = user, token = token)
			flash(u'我们已向您的注册邮箱发送了一封重置密码确认邮件，请注意查收')
		else:
			flash(u'该邮箱地址尚未注册！')
		#return redirect(url_for('main.index'))
	return render_template('auth/resetquest.html', form = form)

#如果用户直接在地址里面输入这个路由？因为进入这个页面同样需要输入邮箱，所以还是与resetrequest视图函数中相同的user
@auth.route('/reset/<token>', methods = ['GET', 'POST'])
def reset(token):
	if not current_user.is_anonymous:#如果用户已经登录，跳转到首页
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is None:
			flash(u'邮箱地址错误')
		else:
			if user.confirm(token):
				user.password = form.password.data
				db.session.add(user)
				db.session.commit()
				flash(u'你刚刚重置了密码')
				return redirect(url_for('auth.login'))
			else:
				flash(u'错误的验证链接或链接已失效')
			#return redirect(url_for('main.index'))
	return render_template('auth/resetquest.html', form = form)

#修改邮箱地址
@auth.route('/changeemail', methods = ['GET', 'POST'])
@login_required
def changeemail():
	form = ChangeEmailForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = current_user.email).first()
		if User.query.filter_by(email = form.newemail.data).first():
			flash(u'该邮箱地址已被注册，请换用其他邮箱')
		else:
			if user.verify_password(form.password.data):
				token = user.generate_confirmationwithaddress_token(address = form.newemail.data)
				send_email(form.newemail.data, u'验证新的邮箱地址', '/auth/email/changeemail', user = user, token = token)
				flash(u'我们已向您的注册邮箱发送了一封重置邮箱确认邮件，请注意查收')
			else:
				flash(u'密码错误')
	return render_template('auth/changeemail.html', form = form)

@auth.route('/newemail/<token>')
@login_required
def newemail(token):
	user = User.query.filter_by(email = current_user.email).first()
	if user.confirm_address(token) is False:
		flash(u'验证失败')
	else:
		flash(u'邮箱地址已更改成功，请使用新的邮箱地址登录')
		logout_user()
	return redirect(url_for('auth.login'))

#作用：未认证的用户访问这个路由，Flask-Login会拦截请求，并转到登录页面
@auth.route('/secret')
@login_required
def secret():
	return u'已授权用户可显示'

















