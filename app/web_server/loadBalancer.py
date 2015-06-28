#!/usr/local/bin/python
import getopt
import string
import sys
import time
import threading

import json

sys.path.append('..')
sys.path.append('../../libs')
sys.path.append('../..')

from twisted.internet import protocol
from twisted.internet import reactor
from logger import CustomLogger
import random
#logger for this module
cust_logger = CustomLogger("loadBalancer")
servers_manager = None
class ServersManager:
    def __init__(self, possible_servers, in_use_servers):
        self.available_servers = in_use_servers[:] #initialized with the in use servers
        self.in_use_servers = in_use_servers
        self.possible_servers = possible_servers
        self.number = 0

    def addServer(self):
        if self.number < len(self.possible_servers) :
            self.available_servers.append(self.possible_servers[self.number+1])
            self.in_use_servers.append(self.possible_servers[self.number+1])
            cust_logger.info("Adding new server host :%s port: %d" % (self.possible_servers[self.number+1]['ip'],  self.possible_servers[self.number+1]['port']))
            self.number+=1
            return self.possible_servers[self.number]
        else :
            cust_logger.warning("No more servers to add")
            raise IndexError('No more server to add')


class ProxyHttpClient(protocol.Protocol):


    def __init__(self, transport, servers_manager):
        self.serverTransport = transport
        self.servers_manager = servers_manager

    def sendMessage(self, data):
        self.transport.write(data)

    def dataReceived(self, data):
        self.data = data
        try :
            sender = json.loads(self.data[self.data.find('{'):])['host_conf']
        except ValueError :
            cust_logger.warning("json loading failed : %s" % self.data[self.data.find('{'):])
            return
        sender = {'ip':sender['ip'], 'port':int(sender['port'])}
        cust_logger.info("response server :" + self.data)
        #we check if the server sending us the answer is in the servers we use, not add him to the available list if not
        if sender not in self.servers_manager.in_use_servers:
            cust_logger.warning("Received a response from an unhandled server host : %s port: %d" % (sender['ip'], int(sender['port'])))
        else :
            self.servers_manager.available_servers.append(sender)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.serverTransport.write(self.data)
        self.serverTransport.loseConnection()

class ProxyHttpServer(protocol.Protocol):
  

    def dataReceived(self, data):
        self.data = data
        print data
        #if a server shows up
        if self.data.startswith("add_server"):
            cust_logger.info("Received new server notification")
            _, server_ip, server_port = self.data.split('#')
            self.factory.targets.append({'ip': server_ip, 'port': server_port})
        else :
            is_empty = False
            for i in range(5):
                if len(self.factory.servers_manager.available_servers) > 0:
                    client_param=random.choice(self.factory.servers_manager.available_servers)
                    self.factory.servers_manager.available_servers.remove(client_param)
                    is_empty = False
                    break
                else :
                    is_empty = True
                    time.sleep(0.05)
            if is_empty :
                cust_logger.info("No more available server, adding one server")
                try :
                    client_param = self.factory.servers_manager.addServer()
                except IndexError:
                    cust_logger.warning("Add server failed, no more servers to add")
                    #while(len(self.factory.servers_manager.available_servers) == 0):
                     #   pass
                    return

                self.factory.servers_manager.available_servers.remove(client_param)

            cust_logger.info("request client :" + self.data)
            client = protocol.ClientCreator(reactor, ProxyHttpClient, self.transport, self.factory.servers_manager)
            d = client.connectTCP(client_param['ip'],client_param['port'] )
            d.addCallback(self.forwardToClient, client)

    def forwardToClient(self, client, data):
        client.sendMessage(self.data)


class ProxyHttpServerFactory(protocol.ServerFactory):

    protocol = ProxyHttpServer

    def __init__(self, servers_manager):
        self.servers_manager = servers_manager

class UdpProtocol(protocol.DatagramProtocol):

    def __init__(self, servers_manager):
        self.servers_manager = servers_manager


    def datagramReceived(self, data, (host, port)):
        if data.startswith("add_server"):
            cust_logger.info("Received new server notification")
            _, server_ip, server_port = data.split('#')
            self.servers_manager.possible_servers.append({'ip': server_ip, 'port': int(server_port)})
        elif data.startswith("request_monitor"):
            cust_logger.info("Received packet from monitor")
            _, monitor_ip, monitor_port = data.split('#')
            cust_logger.info("Sending list to monitor %s:#d"%(monitor_ip, monitor_port))
            hbSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            hbSocket.sendto(json.dumps(self.servers_manager.in_use_servers, (monitor_ip, monitor_port)))


def monitorDaemon(servers_manager,i):
    pass#ust_logger.info("Starting monitor Daemon")
    #
    #r#eactor.listenUDP(8001, UdpProtocol())
    #r#eactor.run()
    #c#ust_logger.info("Exiting monitor Daemon")
#

def main():
    cust_logger.add_file("log/logFile")
    (opts, args) = getopt.getopt(sys.argv[1:], "s:t:h",
        ["source=", "target=", "help"])
    sourcePort, targetHost, targetPort, target2 = None, None, None, None
    for option, argval in opts:
        if (option in ("-s", "--source")):
            sourcePort = int(argval)
        if (option in ("-t", "--target")):
            (targetHost, targetPort, target2) = string.split(argval, ":")

    # initialize servers manager 
    servers_manager = ServersManager([{'ip': targetHost , 'port': int(targetPort)}, {'ip': targetHost , 'port': int(target2)}], [{'ip': targetHost , 'port': int(targetPort)}])
    
    #start daemon
    daemon_thread = threading.Thread(name='monitor', target=monitorDaemon, args=(servers_manager,2))
    daemon_thread.setDaemon(True)
    daemon_thread.start()
#

    # start the twisted reactor
    reactor.listenUDP(8001, UdpProtocol(servers_manager))
    reactor.listenTCP(sourcePort,
    ProxyHttpServerFactory(servers_manager))
    reactor.run()


if __name__ == "__main__":
  main()
