#-*- acoding:utf-8 -*-
import unittest
from app.models import User, Role, Permission, AnonymousUser
from app import db, create_app

class UserModelTest(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_password_setter(self):
		u = User(password = '123')
		self.assertTrue(u.password_hash is not None)
	def test_no_password_getter(self):
		u = User(password = '123')
		with self.assertRaises(AttributeError):
			u.password
	def test_verification(self):
		u = User(password = '123')
		self.assertTrue(u.verify_password('123'))
		self.assertFalse(u.verify_password('234'))
	def test_password_salts_are_random(self):
		u1 = User(password = '123')
		u2 = User(password = '123')
		self.assertFalse(u1.password_hash == u2.password_hash)

	def test_generate_confirm_token(self):
		u = User()
		self.assertTrue(u.generate_confirmation_token() is not None)
	def test_confirm(self):
		u = User()
		token = u.generate_confirmation_token()
		self.assertTrue(u.confirm(token) is True)

	def test_user_permission(self):
		Role.insert_role()#必须先执行这句话--创建出角色才可以，否则创建用户的初始化函数中，用户角色无法判断
		u = User(email='john@qq.com', password='cat')
		u2 = User(email = "861008761@qq.com")
		self.assertTrue(u.can(Permission.WRITE_ARTICLES))
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertTrue(u.can(Permission.COMMENT))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
		self.assertFalse(u.is_administrator())
		self.assertTrue(u2.is_administrator())
		self.assertTrue(u2.can(Permission.MODERATE_COMMENTS))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.COMMENT))












