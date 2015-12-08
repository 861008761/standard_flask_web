#-*- acoding:utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Role, User
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField

class NameForm(Form):
	name = StringField(u'姓名?', validators = [Required(u'不能为空')])
	submit = SubmitField(u'提交')

class EditProfileForm(Form):
	real_name = StringField(u'真实姓名', validators = [Length(0,64, message = u'长度为0到64位')])
	location = StringField(u'所在地', validators = [Length(0,64, message = u'长度为0到64位')])
	about_me = TextAreaField(u'关于我')
	submit = SubmitField(u'提交')

class EditProfileAdminForm(Form):
	email = StringField(u'邮箱地址', validators = [Required(u'不能为空'), Length(1,64, message = u'长度为1到64位'), 
		Email(u'邮箱地址格式错误')])
	username = StringField(u'用户名', validators = [Required(u'不能为空'), Length(1,64, message = u'长度为1到64位'), 
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
			u'用户名必须只包含字母,数字,点或者下划线并以字母开头')])
	confirmed = BooleanField('Confirmed')
	role = SelectField(u'用户角色', coerce = int)

	name = StringField(u'真实姓名', validators = [Length(0,64, message = u'长度为0到64位')])
	location = StringField(u'所在地', validators = [Length(0,64, message = u'长度为0到64位')])
	about_me = TextAreaField(u'关于我')
	submit = SubmitField(u'提交')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if self.email.data != self.user.email and User.query.filter_by(email = self.email.data).first():
			raise ValidationError(u'邮箱地址已被注册')
	def validate_username(self, field):
		if self.username.data != self.user.username and User.query.filter_by(username = self.username.data).first():
			raise ValidationError(u'用户名已被注册')

class PostForm(Form):
	body = PageDownField(u'缩点什么吧?', validators = [Required(u'不能为空')])
	submit = SubmitField(u'发送')

class CommentForm(Form):
	body = StringField('', validators = [Required(u'不能为空')])
	submit = SubmitField(u'发送')













