#-*- acoding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo, Regexp
from wtforms import ValidationError
from ..models import User
from flask.ext.login import current_user

class LoginForm(Form):
	#username = StringField('Username', validators = [Required(), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
	#	'Usernames must have only letters, '
	#	'numbers, dots or underscores')])
	email = StringField(u'邮箱地址', validators = [Required(u'不能为空'), Length(1, 64, message = u'长度为1到64位'), Email(u'邮箱地址格式错误')])
	password = PasswordField(u'密码', validators = [Required(u'不能为空')])
	remember_me = BooleanField(u'记住密码')
	submit = SubmitField(u'登录')

class RegisterForm(Form):
	username = StringField(u'昵称', validators = [Required(u'不能为空'), Length(1,16, message = u'长度为1到16位'), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                               u'用户名必须只包含字母,数字,点或者下划线并以字母开头')])
	email = StringField(u'邮箱地址', validators = [Required(u'不能为空'), Length(1,64, message = u'长度为1到64位'), Email(u'邮箱地址格式错误')])
	password = PasswordField(u'密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位'), EqualTo('confirm_password', message = u'密码不匹配！')])
	confirm_password = PasswordField(u'确认密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位')])
	Register = SubmitField(u'注册')
	def validate_email(self, field):
		user = User.query.filter_by(email = self.email.data).first()
		if user:
			raise ValidationError(u'该邮箱地址已被注册')
	def validate_username(self, field):
		user = User.query.filter_by(username = self.username.data).first()
		if user:
			raise ValidationError(u'该用户名已被注册')

class ChangePasswordForm(Form):
	oldpassword = PasswordField(u'旧密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位')])
	newpassword = PasswordField(u'新密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位'), EqualTo('confirm_password', message = u'密码不匹配！')])
	confirm_password = PasswordField(u'确认密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位')])
	submit = SubmitField(u'确定修改')
	#出现下面的函数的效果和 auth/views.py 中的 modifypwd 函数效果相同，因此只需要其中一种就可以
	def validate_oldpassword(self, field):#函数名好像必须和参数oldpassword、newpassword相同
		u = User.query.filter_by(email = current_user.email).first()
		if not u.verify_password(self.oldpassword.data):
			raise ValidationError(u'旧密码错误')
	def validate_newpassword(self, field):
		u = User.query.filter_by(email = current_user.email).first()
		if u.verify_password(self.newpassword.data):
			raise ValidationError(u'新旧密码不能相同')

class ResetPasswordRequestForm(Form):
	email = StringField(u'邮箱地址', validators = [Required(u'不能为空'), Length(1,64, message = u'长度为1到64位'), Email(u'邮箱地址格式错误')])
	submit = SubmitField(u'重置密码')

class ResetPasswordForm(Form):
	email = StringField(u'邮箱地址', validators = [Required(u'不能为空'), Length(1,64, message = u'长度为1到64位'), Email(u'邮箱地址格式错误')])
	password = PasswordField(u'新密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位'), EqualTo('confirm_password', message = u'密码不匹配')])
	confirm_password = PasswordField(u'确认密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位')])
	submit = SubmitField(u'重置')

class ChangeEmailForm(Form):
	newemail = StringField(u'新邮箱地址', validators = [Required(u'不能为空'), Length(1,64, message = u'长度为1到64位'), Email(u'邮箱地址格式错误')])
	password = PasswordField(u'验证当前账号密码', validators = [Required(u'不能为空'), Length(8,16, message = u'长度为8到16位')])
	submit = SubmitField(u'发送确认邮件')










