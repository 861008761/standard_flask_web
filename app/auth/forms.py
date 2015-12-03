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
	email = StringField('Email', validators = [Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators = [Required()])
	remember_me = BooleanField('keep me logged in')
	submit = SubmitField('Log In')

class RegisterForm(Form):
	username = StringField('Username:', validators = [Required(), Length(1,16), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                               'Usernames must have only letters, '
'numbers, dots or underscores')])
	email = StringField('Email', validators = [Required(), Length(1,64), Email()])
	password = PasswordField('Password', validators = [Required(), Length(8,16), EqualTo('confirm_password', message = 'passwords must match')])
	confirm_password = PasswordField('Confirm password', validators = [Required(), Length(8,16)])
	Register = SubmitField('Register')
	def validate_email(self, field):
		user = User.query.filter_by(email = self.email.data).first()
		if user:
			raise ValidationError('Email already in use')
	def validate_username(self, field):
		user = User.query.filter_by(username = self.username.data).first()
		if user:
			raise ValidationError('Username already in use')

class ChangePasswordForm(Form):
	oldpassword = PasswordField('oldpassword', validators = [Required(), Length(8,16)])
	newpassword = PasswordField('newpassword', validators = [Required(), Length(8,16), EqualTo('confirm_password', message = 'password must match')])
	confirm_password = PasswordField('confirm password', validators = [Required(), Length(8,16)])
	submit = SubmitField('Confirm Change')
	#出现下面的函数的效果和 auth/views.py 中的 modifypwd 函数效果相同，因此只需要其中一种就可以
	def validate_oldpassword(self, field):#函数名好像必须和参数oldpassword、newpassword相同
		u = User.query.filter_by(email = current_user.email).first()
		if not u.verify_password(self.oldpassword.data):
			raise ValidationError('old password is wrong')
	def validate_newpassword(self, field):
		u = User.query.filter_by(email = current_user.email).first()
		if u.verify_password(self.newpassword.data):
			raise ValidationError('new password can\'t equal to old password')

class ResetPasswordRequestForm(Form):
	email = StringField('email', validators = [Required(), Length(1,64), Email()])
	submit = SubmitField('Reset Password')

class ResetPasswordForm(Form):
	email = StringField('email', validators = [Required(), Length(1,64), Email()])
	password = PasswordField('new password', validators = [Required(), Length(8,16), EqualTo('confirm_password', message = 'password must match')])
	confirm_password = PasswordField('confirm password', validators = [Required(), Length(8,16)])
	submit = SubmitField('Confirm Reset')

class ChangeEmailForm(Form):
	newemail = StringField('new email address', validators = [Required(), Length(1,64), Email()])
	password = PasswordField('password', validators = [Required(), Length(8,16)])
	submit = SubmitField('Send confirmation email')









