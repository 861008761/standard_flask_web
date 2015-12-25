#-*- acoding:utf-8 -*-
from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from .utils import create_logger

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protect = 'strong'
login_manager.login_view = 'auth.login'
# 创建 logger 对象
logger = create_logger()

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)#不知道这句话的作用是什么，app = Flask(__name__)不是已经创建app了吗

	bootstrap.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	pagedown.init_app(app)

	from .main import main as main_blueprint
	from .auth import auth as auth_blueprint
	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(main_blueprint)
	app.register_blueprint(auth_blueprint, url_prefix = '/auth')
	app.register_blueprint(api_1_0_blueprint, url_prefix = '/api/v1.0')
	#附加路由和自定义的错误页面
	return app