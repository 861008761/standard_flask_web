#-*- acoding:utf-8 -*-
from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app
from flask import flash
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email
from ..decorators import admin_required, permission_required
from ..models import Permission
from flask.ext.login import login_required

# @main.route('/', methods = ['GET', 'POST'])
# def index():
# 	return render_template('index.html', current_time = datetime.utcnow(), language='zh-cn')

# @main.route('/<name>')
# def user(name):
# 	form = NameForm()
# 	if form.validate_on_submit():
# 		oldname = session.get('name')
# 		session['known'] = True
# 		if oldname is not None and oldname != form.name.data:
# 			session['known'] = False
# 			flash('you have changed your name')
# 		session['name'] = form.name.data
# 		form.name.data = ''
# 		return redirect(url_for('.user', name = session.get('name')))
# 	return render_template('user.html', name = name, known = session.get('known', False), form = form)

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/<name>', methods = ['GET', 'POST'])
def user(name):
    form = NameForm()
    if form.validate_on_submit():
        if name != form.name.data:
            flash('you changed your name')
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.user', name = session.get('name')))#之前一直错是因为methods没有设置get、post
    return render_template('user.html', name = name, known = session.get('known', False), current_time = datetime.utcnow(), form = NameForm(), language = 'zh-cn')


@main.route('/admin')
@login_required
@admin_required
def admin():
    return "For administrators only!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def modorator():
    return "For comment moderators!"










