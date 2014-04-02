from __future__ import absolute_import
from flask import Flask
from glob import glob

app = Flask(__name__)
app.secret_key = "iaspls"

import project.routes
