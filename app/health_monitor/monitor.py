import datetime
import mongoengine
import sys
sys.path.append('..')
sys.path.append('../../libs')

from config import Config
from flask import Flask, render_template
from twisted.internet import protocol
from mongoWebMonitor import WebServiceMonitor
import mongoengine
import threading, time
import socket

## Initializing the app
app = Flask(__name__)
app.debug = True
config = Config()
SIZE_BUFFER_HB = 16
HB_DATAGRAM = "heartbeat"
TIMEOUT_HB=10
PERIOD_CHECK_HB =3
STATUS_LOST = "UNREACHABLE"
STATUS_BEATING = "RUNNING"
STATUS_UNKNOWN = "UNKNOWN"

@app.route('/')
def index():
    return render_template('index.html', user=user)
        

def monitorDaemon():
    pass
class Heartbeats(dict):
    def __init__(self):
        super(Heartbeats, self).__init__()
        self._lock = threading.Lock()

    def __setitem__(self, key, value):
        self._lock.acquire()
        super(Heartbeats, self).__setitem__(key,value)
        self._lock.release()

    @property
    def listTimedOut(self):
        time_limit= time.time() - TIMEOUT_HB
        self._lock.acquire()
        list_timed_out = [{'ip':ip, 'port':port} for (ip, port), valtime in self.items() if valtime < time_limit]
        self._lock.release()
        return list_timed_out

class ListenerHeartBeat(threading.Thread):
    def __init__(self, event_thread, heartbeats):
        super(ListenerHeartBeat, self).__init__()
        self.heartbeats = heartbeats
        self.event_thread = event_thread
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.settimeout(TIMEOUT_HB)
        self.listen_socket.bind((socket.gethostbyname(config.health_monitor.ip), config.health_monitor.port_hb))


    def run(self):
        while self.event_thread.isSet():
            try:
                datagram, sender = self.listen_socket.recvfrom(SIZE_BUFFER_HB)
                if datagram.startswith(HB_DATAGRAM) :
                    print " received Datagram !"
                    _,port_sender = datagram.split('#')
                    self.heartbeats[(sender[0], int(port_sender))] = time.time()
                    web_service = WebServiceMonitor.objects(web_server_ip=sender[0], web_server_port = int(port_sender)).first()
                    if not web_service :
                        web_service = WebServiceMonitor(web_server_ip=sender[0], web_server_port = int(port_sender))
                    web_service.status_monitor = STATUS_BEATING
                    web_service.save()
            except socket.timeout:
                pass

def heartBeatDaemon():
    event_thread = threading.Event()
    event_thread.set()
    heartbeats = Heartbeats()
    listener = ListenerHeartBeat(event_thread, heartbeats)
    listener.start()
    try:
        while True:
            list_timed_out = heartbeats.listTimedOut
            print list_timed_out
            for (ip, port) in list_timed_out:
                web_service = WebServiceMonitor.objects(web_server_ip=ip, web_server_port = port).first()
                web_service.status_monitor = STATUS_LOST
                web_service.save()
            time.sleep(PERIOD_CHECK_HB)
    except ValueError:
        pass



def sendNotificationToLB(monitor_ip, monitor_port, ip_lb, port_lb):
    hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hbSocket.sendto("request_monitor#%s#%d"%(monitor_ip, monitor_port), (ip_lb, port_lb))

if __name__ == "__main__":
    #if len(sys.argv) > 1: 
    #    config = GlobalConfig.from_json(sys.argv[1])

    db = mongoengine.connect(config.health_monitor.mongo_db)

    heartbeat_thread = threading.Thread(name='hb_daemon', target=heartBeatDaemon)
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()
    sendNotificationToLB("localhost", 6000, "localhost", 8001)
    app.run(host="0.0.0.0", port=config.health_monitor.port, debug=True, use_reloader=False)