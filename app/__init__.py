from flask import Flask
from flask_jwt import JWT
from conf.config import config
import logging
from logging.config import fileConfig
import os
from app.rest.security import authenticate, identity

fileConfig('conf/log-app.conf')


def get_logger(name):
    return logging.getLogger(name)


def get_basedir():
    return os.path.abspath(os.path.dirname(__file__))


def get_config():
    return config[os.getenv('FLASK_CONFIG') or 'default']


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    jwt = JWT(app, authenticate, identity)

    from .rest import rest as rest_blueprint
    app.register_blueprint(rest_blueprint)

    return app
