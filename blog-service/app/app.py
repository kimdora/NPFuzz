#!/usr/bin/python
from os import urandom
from flask import Flask

from blogservice import BlogService

app = Flask(__name__)
app.secret_key = urandom(24)
app.register_blueprint(BlogService, url_prefix='/blog')
