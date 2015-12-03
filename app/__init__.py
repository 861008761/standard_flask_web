#-*- acoding:utf-8 -*-

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protect = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)#不知道这句话的作用是什么，app = Flask(__name__)不是已经创建app了吗

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)

	from .main import main as main_blueprint
	from .auth import auth as auth_blueprint
	app.register_blueprint(main_blueprint)
	app.register_blueprint(auth_blueprint)
	#附加路由和自定义的错误页面
	print 'app/init'#create_app是系统运行时manage.py文件调用的
	return app