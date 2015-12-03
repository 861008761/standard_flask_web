#-*- acoding:utf-8 -*-
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

#用户回调函数，返回用户对象或者None
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), unique = True, index = True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	email = db.Column(db.String(64), unique = True, index = True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default = False)
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	def generate_confirmation_token(self, expiration = 3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm' : self.id})
	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True
	def __repr__(self):
		return '<user %s>' % self.username

	def generate_confirmationwithaddress_token(self, expiration = 3600, address = None):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm' : self.id, 'address' : address})

	def confirm_address(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		if data.get('confirm') != self.id:
			return None
		address = data.get('address')
		if self.query.filter_by(email = address).first() is not None:
			return None
		return data.get('address')

class Role(db.Model):
	__tablename__ = "roles"
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique = True)
	def __repr__(self):
		return '<role %s>' % self.name
	users = db.relationship('User', backref = 'role', lazy = 'dynamic')