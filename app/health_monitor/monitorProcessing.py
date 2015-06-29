from datetime import datetime
import sys
sys.path.append('..')
sys.path.append('../../libs')

import os
from config import Config
from twisted.internet import protocol
from twisted.internet import reactor
from logger import CustomLogger
from mongoWebMonitor import WebServiceMonitor, StatusWebService, Logs
import mongoengine
import threading, time
import socket
import httplib
import json

cust_logger = CustomLogger("monitor_health_%d"%os.getpid())

config = Config()
SIZE_BUFFER_HB = 21
HB_DATAGRAM = "heartbeat"
TIMEOUT_HB = 10
PERIOD_CHECK_HB = 3
PERIOD_CHECK_STATUS = 5

def monitorDaemon():
    pass


class Heartbeats(dict):
    '''
        extend the dict class for thread-safeties reasons.
    '''
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
        list_timed_out = [{'ip':ip, 'port':port, 'monitor_port':port_monitor} for (ip, port,port_monitor), valtime in self.items() if valtime < time_limit]
        self._lock.release()
        return list_timed_out

class ListenerHeartBeat(threading.Thread):
    '''
        Thread handler : Listen to heartbeats coming from web services, and maintain the dict so that nodes which did not send 
        heartbeats during a certain amount of time are considered as unreachable
    '''
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
                sender_formatted =  sender[0]
                if sender[0]=="127.0.0.1":
                    sender_formatted = "localhost"
                if datagram.startswith(HB_DATAGRAM) :
                    cust_logger.info("received Datagram from web service")
                    _,port_sender, port_monitor = datagram.split('#')
                    self.heartbeats[(sender_formatted, int(port_sender), int(port_monitor))] = time.time()
                    web_service = WebServiceMonitor.objects(web_server_ip=sender_formatted, web_server_port = int(port_sender)).first()
                    if not web_service :
                        web_service = WebServiceMonitor(web_server_ip=sender_formatted, web_server_port=int(port_sender), monitor_port=int(port_monitor))
                    web_service.status_monitor = StatusWebService.STATUS_BEATING
                    web_service.save()
            except socket.timeout:
                pass

def heartBeatDaemon(heartbeats):
    '''
        Thread handler which update the status of the nodes if they don't send any heartbeat
    '''
    event_thread = threading.Event()
    event_thread.set()
    listener = ListenerHeartBeat(event_thread, heartbeats)
    listener.start()
    try:
        while True:
            list_timed_out = heartbeats.listTimedOut
            for dic in list_timed_out:
                web_service = WebServiceMonitor.objects(web_server_ip=dic['ip'], web_server_port = dic['port']).first()
                if web_service.status_monitor != StatusWebService.STATUS_LOST:
                    cust_logger.info("%s:%d has timedout"%(dic['ip'],dic['port']))
                    web_service.status_monitor=StatusWebService.STATUS_LOST
                    web_service.save()
            time.sleep(PERIOD_CHECK_HB)
    except ValueError as e:
        cust_logger.error("HeartBeatDeamon stopped: "+ str(e))
        pass

def checksDaemon(heartbeats):
    '''
        check directly the connexion http with the web service, without going through load balancing. 
        Check of the load balancer must be added. Update the status of the web services depending on 
        the success of the connexion.
    '''
    while(True):
        for url_to_check,ws in [ ("%s:%d"%(ws[0],ws[1]),ws) for ws in heartbeats]:
            ws_db = WebServiceMonitor.objects(web_server_ip=ws[0], web_server_port=ws[1]).first()
            oldStatus = ws_db.status_service
            if not ws_db:
                continue
            try:     
                connexion = httplib.HTTPConnection(url_to_check,timeout=6)
                connexion.request("GET", "/fortune")
                time_before = time.time()
                res = connexion.getresponse()
                response_time = time.time()-time_before
                if oldStatus != res.status:
                    cust_logger.info("%s status changed. old: %s new: %s" % (url_to_check, ws_db.status_service, res.status))

                    #if status changed and is now 200, we remove old logs
                    if res.status == 200:
                        list_logs = Logs.objects(web_server_ID=(ws[0]+":%d"%ws[1]))
                        for log in list_logs:
                            log.delete()
                else: #status is the same
                    cust_logger.info("%s remains the same with status %d"%(url_to_check,res.status))
                
                ws_db.status_service = res.status
                ws_db.response_time = response_time
                ws_db.successfull_calls +=1
                ws_db.save()
            #in case the connection is not possible, status is -1
            except httplib.BadStatusLine:
                ws_db.status_service = -1
                ws_db.save()
                cust_logger.warning("connexion ended with BAD STATUS")

            except StandardError as e:
                ws_db.status_service = -1
                ws_db.save()
                cust_logger.warning("connexion ended with standard Error: "+str(e))

            #When status is not 200 but the web service monitor is alive, we ask the logs     
            if oldStatus != ws_db.status_service and ws_db.status_service != 200 and ws_db.status_monitor == StatusWebService.STATUS_BEATING:
                cust_logger.info("Requesting logs on %s:%d"%(ws[0],ws[2]))
                sendMessageUdpFromTo("request_logs","localhost", config.health_monitor.port_udp_process, ws[0], ws[2])

        time.sleep(PERIOD_CHECK_STATUS)

#parse a log into 3 separated fields to be stored in the database.
def parseLog(log):
    date_log,type_content = log.split(" - ")

    date_datetime = datetime.strptime(date_log, "%Y-%m-%d %H:%M:%S,%f")
    type_log, content_log = type_content.split(":: ")
    return date_datetime, type_log, content_log

#Interface to receive from outside various datagrams
class UdpProtocol(protocol.DatagramProtocol):
    def __init__(self, heartbeats):
        self.heartbeats = heartbeats

    def datagramReceived(self, data, (host, port)):
        if data.startswith("logs"):
            _,host,port,logs = data.split('#')
            logs_list = json.loads(logs)
            for log in logs_list:
                date,type_log,content = parseLog(log)
                log_to_save = Logs(web_server_ID=(host+":%d"%int(port)), log_timestamp=date, log_type=type_log, log_content=content )
                log_to_save.save()
        elif data.startswith("last_exception"):
            _,host,port,exception = data.split('#')
            ws = WebServiceMonitor.objects(web_server_ip=host,web_server_port=port).first()
            ws.last_excpt_raised = exception
            ws.save()
        #load_balancer sends the list of servers
        elif data.startswith("list_servers") and (host, port) == (config.load_bal_monitor.ip, config.load_bal_monitor.port_udp):
            cust_logger.info("received list servers")
            _,list_json = data.split('#')
            heartbeats = [ {(server['ip'], server['port'], server['monitor_port']) : time.time()} for server in json.loads(list_json)]



def sendMessageUdpFromTo(header, source_ip, source_port, dest_ip, dest_port):
    hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hbSocket.sendto(header+"#%s#%d"%(source_ip, source_port),(dest_ip, dest_port))

def sendMessageDiscovery(header, source_ip, source_port, source_hb, dest_ip, dest_port):
    hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hbSocket.sendto(header+"#%s#%d#%d"%(source_ip, source_port, source_hb),(dest_ip, dest_port))


if __name__ == "__main__":
    #if len(sys.argv) > 1: 
    #    config = GlobalConfig.from_json(sys.argv[1])


    path_file_log = cust_logger.add_file("logMonitor/logFmonitor")

    db = mongoengine.connect(config.health_monitor.mongo_db)
    db.drop_database(config.health_monitor.mongo_db)

    heartbeats = Heartbeats()
    heartbeat_thread = threading.Thread(name='hb_daemon', target=heartBeatDaemon, args=([heartbeats]))
    heartbeat_thread.setDaemon(True)
    heartbeat_thread.start()

    check_daemon = threading.Thread(name='checks_daemon', target=checksDaemon, args=([heartbeats]))
    check_daemon.setDaemon(True)
    check_daemon.start()


    #log_daemon = threading.Thread(name='checks_daemon', target=checksDaemon, args=([heartbeats]))
    #log_daemon.setDaemon(True)
    #log_daemon.start()

    #we request the list of the current servers used to the loadBalancer
    sendMessageDiscovery("request_monitor","localhost", config.health_monitor.port_udp_process, config.health_monitor.port_hb, "localhost", config.load_bal_monitor.port_udp)

    
    reactor.listenUDP(config.health_monitor.port_udp_process, UdpProtocol(heartbeats))
    reactor.run()