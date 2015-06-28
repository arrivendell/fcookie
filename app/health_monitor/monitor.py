import datetime
import mongoengine
import sys
sys.path.append('..')
sys.path.append('../../libs')

from config import Config
from flask import Flask, render_template
from twisted.internet import protocol
from mongoWebMonitor import WebServiceMonitor, StatusWebService
import mongoengine
import threading, time
import socket
import httplib

## Initializing the app
app = Flask(__name__)
app.debug = True
config = Config()


@app.route('/')
def index():
    return render_template('index.html', user=user)
        

if __name__ == "__main__":
    #if len(sys.argv) > 1: 
    #    config = GlobalConfig.from_json(sys.argv[1])

    db = mongoengine.connect(config.health_monitor.mongo_db)

    app.run(host="0.0.0.0", port=config.health_monitor.port, debug=True, use_reloader=False)