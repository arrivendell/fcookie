#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
sys.path.append('../../libs')
sys.path.append('../..')

from flask import Flask, render_template,request
import mongoengine
from config import Config
import json
import random


## Initializing the app
app = Flask(__name__)
app.debug = True
config = Config()

## Main pages
@app.route('/')
def index():
    return render_template('index.html')

#Return a fortune : line randomly selected in a file
@app.route('/fortune', methods=['GET', 'POST'])
def fortune():
    if request.method == 'GET':
        selected_line = random.choice(open("../"+config.fortune_service.path_file_fortunes, 'r').readlines()) #No close in that call since file closes automatically after call.
        response = dict(ok=True, result=selected_line)
        return json.dumps(selected_line)
    elif request.method == 'POST':
        #selected_line = random.choice(open(config.fortune_service.path_file_fortunes, 'r').readlines()) #No close in that call since file closes automatically after call.
        response = dict(ok=False)#, result=selected_line)
        return json.dumps(response)




if __name__ == "__main__":
  
    app.run(host=config.fortune_service.ip, port=config.fortune_service.port, debug=True)