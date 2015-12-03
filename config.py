#-*- acoding:utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'my secret key'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	MAIL_SERVER = 'smtp.163.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = True
	#MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	#MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	MAIL_USERNAME = '55617@163.com'
	MAIL_PASSWORD = '1992yang'
	FLASKY_MAIL_SUBJECT_PREFIX = '[FLASKY]'
	FLASKY_MAIL_SENDER = '55617@163.com'
	FLASKY_MAIL_ADMIN = os.environ.get('FLASKY_ADMIN')

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

	SQLALCHEMY_TRACK_MODIFICATIONS = False
	print 'config'#在app/__init__文件中创建app的函数create_app中调用了，这说明init是先执行的

class TestingConfig(Config): 
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
	'development' : DevelopmentConfig,
	'testing' : TestingConfig,
	'production' : ProductionConfig,

	'default' : DevelopmentConfig
	}