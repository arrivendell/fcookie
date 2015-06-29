#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
sys.path.append('..')
sys.path.append('../../libs')
sys.path.append('../..')

import os
import string
import getopt
import mongoengine
from config import Config
import json
import random
import time
import threading
import socket
from twisted.internet import protocol, reactor
from webServiceMIB import WebServiceMIB
from logger import CustomLogger
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


monitors = []
PERIOD_BEAT = 3
PERIOD_EXCEPTION = 2 

cust_logger = CustomLogger("monitor_web_server_%d"%os.getpid())




################# HEART BEAT MANAGEMENT ########################

#web_listen_port is the port where the webservice listen, monitor_listen_port is the listenning port of this monitor
def heartbeatDaemon(web_listen_port, monitor_listen_port,list_monitors):
    while True:
        hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for monitor in list_monitors:
            hbSocket.sendto("heartbeat#%d#%d"% (int(web_listen_port), int(monitor_listen_port)), (monitor['ip'],int(monitor['port_hb'])))
        time.sleep(PERIOD_BEAT)

############# EXCEPTION MANAGEMENT #################################

#check any update of the exception field in the database and send it to the monitors if there is a change
def lastExceptionDaemon(web_ip, web_listen_port,list_monitors):
    while(WebServiceMIB.objects(port=web_listen_port).first() is None):
        pass
    old_last_exception = WebServiceMIB.objects(port=web_listen_port).first().last_excpt_raised
    while True:
        mib = WebServiceMIB.objects(port=web_listen_port).first()
        if mib.last_excpt_raised != old_last_exception:
            hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for monitor in list_monitors:
                hbSocket.sendto("last_exception#%s#%d#%s"% (web_ip,int(web_listen_port), mib.last_excpt_raised), (monitor['ip'],int(monitor['port'])))
        time.sleep(PERIOD_EXCEPTION)


########################### LISTEN UDP ##################################

#Interface to receive from outside various datagrams
class UdpProtocol(protocol.DatagramProtocol):

    def __init__(self,lock,source_ip, web_listen_port):
        self.lock = lock
        self.source_ip = source_ip
        self.web_listen_port = web_listen_port

    def datagramReceived(self, data, (host, port)):
        if data.startswith("request_logs"):
            cust_logger.info("logs requested")
            _,response_ip, response_port = data.split('#') 
            self.lock.acquire()
            with open(WebServiceMIB.objects(port=web_listen_port).first().log_file_path,"r") as f:
                f.seek(0,2)
                size = f.tell()
                f.seek(max (size - 1024, 0),0)
                lines = f.readlines()
            self.lock.release()
            socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socketUDP.sendto("logs#%s#%d#%s"%(self.source_ip, self.web_listen_port,json.dumps(lines)), (response_ip, int(response_port)))
        if data.startswith("add_monitor"):
            cust_logger.info("Add monitor")
            _,monitor_ip, monitor_port, monitor_hb = data.split('#') 
            new_monitor = dict(ip=monitor_ip, port=monitor_port, port_hb=monitor_hb) 
            if new_monitor not in monitors:
                monitors.append(new_monitor)

                  

########################## MAIN #######################################


if __name__ == "__main__":
    (options, args) = getopt.getopt(sys.argv[1:], "s:m:l:h",
        ["source=", "monitor=","loadBal=", "help"])
    web_listen_port, load_bal_ip, load_bal_port, monitor_listen_port = None, None, None, None
    for opt, val in options:
        if (opt in ("-s", "--source")):
            web_listen_port = int(val)
        if (opt in ("-m", "--monitor")):
            cust_logger.info("monitor : %d"%int(val))
            monitor_listen_port = int(val)
        if (opt in ("-l", "--loadBal")):
            (load_bal_ip, load_bal_port) = val.split(":")
    ip = "localhost"

    #lock for logs reading
    lock = threading.Lock()

    path_file_log = cust_logger.add_file("logWeb/monitor%d"%web_listen_port+"/logFweb")
    db = mongoengine.connect("%s#%d"%(ip,web_listen_port))
    #db.drop_database("%s#%d"%(ip,web_listen_port))


    heartbeat_thread = threading.Thread(name='heartbeat', target=heartbeatDaemon, args=(web_listen_port,monitor_listen_port,monitors)) #Care about lists as arguments, if not in [] then list is split
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()

    last_excpt_daemon = threading.Thread(name='last_exception', target=lastExceptionDaemon, args=(ip,web_listen_port,monitors)) #Care about lists as arguments, if not in [] then list is split
    last_excpt_daemon.setDaemon(True)
    last_excpt_daemon.start()

    reactor.listenUDP(monitor_listen_port, UdpProtocol(lock,ip,web_listen_port))
    reactor.run()