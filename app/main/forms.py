from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Role, User
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField

class NameForm(Form):
	name = StringField('what\'s your name?', validators = [Required()])
	submit = SubmitField('Submit')

class EditProfileForm(Form):
	real_name = StringField('Real name', validators = [Length(0,64)])
	location = StringField('Location', validators = [Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
	email = StringField('Email', validators = [Required(), Length(1,64), Email()])
	username = StringField('Username', validators = [Required(), Length(1,64), 
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
			'Usernames must have only letters, '
			'numbers, dots or underscores')])
	confirm = BooleanField('Confirmed')
	role = SelectField('Role', coerce = int)

	name = StringField('Real name', validators = [Length(0,64)])
	location = StringField('Location', validators = [Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self, field):
		if self.email.data != self.user.email and User.query.filter_by(email = self.email.data):
			raise ValidationError('email address already in use')
	def validate_username(self, field):
		if self.username.data != self.user.username and User.query.filter_by(username = self.username.data):
			raise ValidationError('username has been registered')

class PostForm(Form):
	body = PageDownField('What\'s in your mind?', validators = [Required()])
	submit = SubmitField('submit')















