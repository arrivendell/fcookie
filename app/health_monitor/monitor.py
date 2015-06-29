import datetime
import mongoengine
import sys
sys.path.append('..')
sys.path.append('../../libs')

from config import Config
from flask import Flask, render_template
from twisted.internet import protocol
from datetime import datetime
from mongoWebMonitor import WebServiceMonitor, StatusWebService, Logs
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

    services = WebServiceMonitor.objects()[:]
    services_to_send = []
    print services
    log_string=""
    for service in services:
        print service.web_server_ip + ':' + str(service.web_server_port)
        for log in Logs.objects(web_server_ID=service.web_server_ip + ':' + str(service.web_server_port)):
            log_string += ' '.join([datetime.strftime(log.log_timestamp, "%Y-%m-%d_%Hh%Mm%Ss"), log.log_type, log.log_content]) 
        
        print log_string
        service_dict = dict(service_id=service.web_server_ip + ':' + str(service.web_server_port), status_monitor=service.status_monitor,
            status_service=service.status_service, status_through_lb=service.status_through_lb, response_time=service.response_time,
             last_excpt_raised=service.last_excpt_raised, logs=log_string) 
        services_to_send.append(service_dict)
    print services_to_send
    return render_template("index.html", services = services_to_send)

if __name__ == "__main__":
    #if len(sys.argv) > 1: 
    #    config = GlobalConfig.from_json(sys.argv[1])

    db = mongoengine.connect(config.health_monitor.mongo_db)

    app.run(host="0.0.0.0", port=config.health_monitor.port, debug=True, use_reloader=False)