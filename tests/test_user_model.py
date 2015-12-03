import unittest
from app.models import User

class UserModelTest(unittest.TestCase):
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