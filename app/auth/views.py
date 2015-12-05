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

#登入用户
@auth.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid email or password')
	return render_template('auth/login.html', form = form)

#有一些页面不可以是匿名用户访问的，所以先跳转到登录页面，但是为了实现：在登录之后继续打开
#之前匿名访问的页面。所以将原来页面的地址放在请求上下文的request的args的next中。
#如果next不存在了，就跳转到首页去了。

#登出用户
@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('you have been logged out')
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
		send_email(user.email, 'Confirm your account', 'auth/email/confirm', user = user, token = token)
		flash('A confirmation email has been sent to your email.')
		return redirect(url_for('main.index'))
	return render_template('register.html', form = form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:#避免重复点击邮件链接的确认
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('you have just confirmed your account')
	else:
		flash('The confirmation link is invalid or has exipred.')
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
	send_email(current_user.email, 'Confirm your account', 'auth/email/confirm', user = current_user, token = token)
	flash('A new confirmation email has been sent to your email')
	return redirect(url_for('main.index'))

#修改密码
@auth.route('/modifypwd', methods = ['GET', 'POST'])
@login_required
def modifypwd():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = current_user.email).first()
		if not user.verify_password(form.oldpassword.data):
			flash('Error: you old password is wrong!')
		else:
			if user.verify_password(form.newpassword.data):
				flash('new password is the same as last one, please change a new password')
			else:
				user.password = form.newpassword.data
				db.session.add(user)
				db.session.commit()
				flash('you have changed your password successfully')
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
			send_email(form.email.data, 'Reset your account', '/auth/email/reset', user = user, token = token)
			flash('A confirmation email has been sent to your email')
		else:
			flash('your email address have not registered yet')
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
			flash('Your email address is wrong')
		else:
			if user.confirm(token):
				user.password = form.password.data
				db.session.add(user)
				db.session.commit()
				flash('your have already reset your password')
				return redirect(url_for('auth.login'))
			else:
				flash('your link is invalid or expired')
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
			flash('this email address already registered, please use another one')
		else:
			if user.verify_password(form.password.data):
				token = user.generate_confirmationwithaddress_token(address = form.newemail.data)
				send_email(form.newemail.data, 'Confirm your new email address', '/auth/email/changeemail', user = user, token = token)
				flash('A confirmation email has been sent to your new email address!')
			else:
				flash('Invalid password')
	return render_template('auth/changeemail.html', form = form)

@auth.route('/newemail/<token>')
@login_required
def newemail(token):
	user = User.query.filter_by(email = current_user.email).first()
	if user.confirm_address(token) is False:
		flash('Confirmation failed')
	else:
		flash('Your email address is changed, please log in with new email address!')
		logout_user()
	return redirect(url_for('auth.login'))

#作用：未认证的用户访问这个路由，Flask-Login会拦截请求，并转到登录页面
@auth.route('/secret')
@login_required
def secret():
	return 'Only authenicated users are allowed'

















