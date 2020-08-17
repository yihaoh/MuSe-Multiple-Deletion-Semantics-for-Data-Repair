from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
# from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm  # , \
# ResetPasswordRequestForm, ResetPasswordForm
from app.models import User

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.main.database_generator.dba import *

import os


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("lol")
        return redirect(url_for('main.input'))
    form = LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():
        print('submitting login')
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.input')

        # loadDefaultDB(form.username.data)
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.input'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        print('user logged in!!!!!')
        return redirect(url_for('main.input'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        # create the customized database for the user
        # loadDefaultDB(form.username.data)
        initSetup(form.username.data)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # print("here")
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    # return render_template('index.html', title='Home', posts=posts)
    return redirect(url_for('main.input'))


def initSetup(dbname):
    # create folder for user to store customized data
    # try:
    #     os.mkdir('~/Desktop/DelSem_demo/Demo/' + dbname)
    # except OSError:
    #     print('fail to create folder')

    # load default database
    loadDefaultDB(dbname)


def loadDefaultDB(dbname):
    # create new database
    conn = psycopg2.connect(database="postgres", user="postgres", password="123", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE ' + dbname + ';')
    conn.commit()

    cur.close()
    conn.close()

    # populate new database with tables
    conn = psycopg2.connect(database=dbname, user="postgres", password="123", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute('CREATE TABLE organization (oid int, name varchar(150));')
    cur.execute('CREATE TABLE author (aid int, name varchar(60), oid int);')
    cur.execute('CREATE TABLE cite (citing int, cited int);')
    cur.execute('CREATE TABLE writes (aid int, pid int);')
    cur.execute('CREATE TABLE publication (pid int, title varchar(200), year int);')
    conn.commit()

    cur.execute('CREATE TABLE delta_organization (oid int, name varchar(150));')
    cur.execute('CREATE TABLE delta_author (aid int, name varchar(60), oid int);')
    cur.execute('CREATE TABLE delta_cite (citing int, cited int);')
    cur.execute('CREATE TABLE delta_writes (aid int, pid int);')
    cur.execute('CREATE TABLE delta_publication (pid int, title varchar(200), year int);')
    conn.commit()

    cur.close()
    conn.close()

    # populate tables with data
    tbl_names = ['author', 'publication', 'writes', 'organization', 'cite']
    db = DatabaseEngine(dbname)
    db.delete_tables(tbl_names)
    db.load_database_tables(tbl_names)
    del db
