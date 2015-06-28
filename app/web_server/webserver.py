#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
sys.path.append('../../libs')
sys.path.append('../..')

import os
import string
import getopt
from flask import Flask, render_template,request
import mongoengine
from config import Config
from logger import CustomLogger
import json
import random
import time
import threading
import socket
from webServiceMIB import WebServiceMIB, StatusWebService

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


## Initializing the app
app = Flask(__name__)
app.debug = True
config = Config()
host_conf = None

cust_logger = CustomLogger("web_server_%d"%os.getpid())

## Main pages
@app.route('/')
def index():
    return render_template('index.html')

#Return a fortune : line randomly selected in a file
@app.route('/fortune', methods=['GET', 'POST'])
def fortune():
    if request.method == 'GET':
        cust_logger.info("Received GET request")
        try:
            file_fortune = open("../"+config.fortune_service.path_file_fortunes, 'r')
            selected_line = random.choice(file_fortune.readlines()) #No close in that call since file closes automatically after call.
            response = dict(host_conf=host_conf, result=selected_line)
            print "line selected : " +selected_line
        except IOError as e:
            cust_logger.error("cannot open document, I/O error({0}): {1}".format(e.errno, e.strerror))
            response = dict(host_conf=host_conf, result="error")
            #We save the last exception raised in the database
            mib = WebServiceMIB.objects(port=host_conf['port']).first()
            if mib:
                mib.last_excpt_raised = str(e)
                mib.save()
        except TypeError as e:
            cust_logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            response = dict(host_conf=host_conf, result="error")
            mib = WebServiceMIB.objects(port=host_conf['port']).first()
            if mib:
                mib.last_excpt_raised = str(e)
        except IndexError as e:
            cust_logger.error("no lines to read, I/O error({0}): {1}".format(e.errno, e.strerror))
            response = dict(host_conf=host_conf, result="error")
            mib = WebServiceMIB.objects(port=host_conf['port']).first()
            if mib:
                mib.last_excpt_raised = str(e)
        except:
            cust_logger.error( "Unexpected error:", sys.exc_info()[0] )
            response = dict(host_conf=host_conf, result="error")
            mib = WebServiceMIB.objects(port=host_conf['port']).first()
            if mib:
                mib.last_excpt_raised = str(e)
            raise
 
        #simulate long execution
        time.sleep(2)

        return json.dumps(response)
    elif request.method == 'POST':
        cust_logger.error("Unexpected post request received")
        raise TypeError



if __name__ == "__main__":
    (options, args) = getopt.getopt(sys.argv[1:], "s:m:l:h",
        ["source=", "monitor=","loadBal=", "help"])
    source_port, load_bal_ip, load_bal_port, monitor_port = None, None, None, None
    for opt, val in options:
        if (opt in ("-s", "--source")):
            source_port = int(val)
        if (opt in ("-m", "--monitor")):
            monitor_port = int(val)
        if (opt in ("-l", "--loadBal")):
            (load_bal_ip, load_bal_port) = val.split(":")
            #send notification to load_balancer
            hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            hbSocket.sendto("add_server#%s#%d#%d"%("localhost", source_port, monitor_port), (load_bal_ip, int(load_bal_port)))
    ip = "localhost"

    db = mongoengine.connect("%s#%d"%(ip,source_port))
    db.drop_database("%s#%d"%(ip,source_port))
    
    path_file_log = cust_logger.add_file("logWeb/%d"%source_port+"/logFweb")
    
    mib = WebServiceMIB(port = source_port, status = StatusWebService.STATUS_UP , log_file_path =  path_file_log )
    mib.save()


    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(source_port)
    host_conf = {'ip': ip, 'port':int(source_port)}
    IOLoop.instance().start()