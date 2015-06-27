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

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


## Initializing the app
app = Flask(__name__)
app.debug = True
config = Config()
host_conf = None
## Main pages
@app.route('/')
def index():
    return render_template('index.html')

#Return a fortune : line randomly selected in a file
@app.route('/fortune', methods=['GET', 'POST'])
def fortune():
    if request.method == 'GET':
        file_fortune = open("../"+config.fortune_service.path_file_fortunes, 'r')
        selected_line = random.choice(file_fortune.readlines()) #No close in that call since file closes automatically after call.
        response = dict(host_conf=host_conf, result=selected_line)
        print "line selected : " +selected_line
        i=0
        #nb = raw_input('Choose a number: ')

        return json.dumps(response)
    elif request.method == 'POST':
        #selected_line = random.choice(open(config.fortune_service.path_file_fortunes, 'r').readlines()) #No close in that call since file closes automatically after call.
        response = dict(ok=False)#, result=selected_line)
        return json.dumps(response)




if __name__ == "__main__":
    ip = sys.argv[1]
    port = sys.argv[2]

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    host_conf = {'ip': ip, 'port':int(port)}
    IOLoop.instance().start()
    # app.run(host=config.fortune_service.ip, port=config.fortune_service.port, debug=True)
   # app.run(host=config.fortune_service.ip, port=int(port), debug=True)