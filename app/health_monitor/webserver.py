#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
sys.path.append('../../libs')

from flask import Flask, render_template
import mongoengine

import json


## Initializing the app
app = Flask(__name__)
app.debug = True
