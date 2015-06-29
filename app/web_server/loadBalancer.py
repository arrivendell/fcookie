#!/usr/local/bin/python
import getopt
import string
import sys
import time
import threading
import socket
import json

sys.path.append('..')
sys.path.append('../../libs')
sys.path.append('../..')

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import error
from logger import CustomLogger
from config import Config
import random
#logger for this module
cust_logger = CustomLogger("loadBalancer")
servers_manager = None
monitors = []
config = Config()

###########SERVER MANAGER#################
class ServersManager:
    '''
        manage the different list of servers : one containing the potential servers that one can use,
        the other containing the servers that the load balancer is using, and the last one contains the servers
        that are available aka they are not working. An index number is stored to keep track of the last server used 
        in the potential server. This is to be removed for a future use and replace by a non-linear management
    '''
    def __init__(self, possible_servers, in_use_servers):
        self.available_servers = in_use_servers[:] #initialized with the in use servers
        #we show the initialization for better debug
        cust_logger.info("ServerManager initialized with possible_servers: %s"%', '.join(["%s:%d/%d"%(server['ip'], server['port'], server['monitor_port']) for server in possible_servers]))
        cust_logger.info("ServerManager initialized with in use servers: %s"%', '.join(["%s:%d/%d"%(server['ip'], server['port'], server['monitor_port']) for server in in_use_servers]))

        self.in_use_servers = in_use_servers
        self.possible_servers = possible_servers

        self.number = len(self.in_use_servers)-1

    def addServer(self):
        '''
            add a potential server to the in_use list. The opposite can be implemented to remove one on in_use list
        '''
        if self.number < len(self.possible_servers) :
            self.available_servers.append(self.possible_servers[self.number+1])
            self.in_use_servers.append(self.possible_servers[self.number+1])
            cust_logger.info("Adding new server host :%s port: %d" % (self.possible_servers[self.number+1]['ip'],  self.possible_servers[self.number+1]['port']))
            self.number+=1
            for monitor in monitors:
                sendListServers(self, monitor['ip'], monitor['port'])
                sendMonitorToServers(self.servers_manager, monitor)
            return self.possible_servers[self.number]
        else :
            cust_logger.warning("No more servers to add")
            raise IndexError('No more server to add')



################ PROXY #########################
class ProxyHttpClient(protocol.Protocol):
    '''
        interface of the proxy that sends back the data received to the client
    '''


    def __init__(self, transport, servers_manager):
        self.serverTransport = transport
        self.servers_manager = servers_manager

    def sendMessage(self, data):
        self.transport.write(data)

    def dataReceived(self, data):
        self.data = data
        #We try to extract the json from the http packet, strating from 1st { to the end of data.
        try :
            sender = json.loads(self.data[self.data.find('{'):])['host_conf']
        except ValueError :
            cust_logger.warning("json loading failed: %s" % self.data[self.data.find('{'):])
            return
        sender = {'ip':sender['ip'], 'port':int(sender['port']), 'monitor_port':int(sender['monitor_port'])}
        cust_logger.info("response server: " + ' '.join(self.data.split('\r\n')))
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
    '''
        interface of the proxy that receives the data from a client and forwards it to one of the server.
        Acts as a relay and load balancer. Each time we send a request to a web service, we remove it's id from the available
        list. We choose among the remaining one to send the request. When we receive the response of the server,
        we put back the id in the available list. If it reaches a length of 0, we try to wait, and then add a server if possible
    '''

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
                    #choice is random but FIFO could have been used and may be better to have the load nicely shared 
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
            #we log the request in one line only by removing the linebreaks
            cust_logger.info("request client: " + ' '.join(self.data.split('\r\n')) + "sent to %s:%d"%(client_param['ip'], client_param['port']))
            client = protocol.ClientCreator(reactor, ProxyHttpClient, self.transport, self.factory.servers_manager)
            try:
                #d = client.connectTCP(client_param['ip'],client_param['port'] )
                d = client.connectTCP(client_param['ip'],client_param['port'] )
                d.addCallback(self.forwardToClient, client)
            except error.ConnectionRefusedError as e:
                cust_logger.error("connection with web_server impossible: %s"%str(e))

    def forwardToClient(self, client, data):
        client.sendMessage(self.data)


class ProxyHttpServerFactory(protocol.ServerFactory):

    protocol = ProxyHttpServer

    def __init__(self, servers_manager):
        self.servers_manager = servers_manager


################ GENERAL ##########################

def sendListServers(servers_manager,monitor_ip, monitor_port):
    cust_logger.info("Sending list to monitor %s:%d"%(monitor_ip, int(monitor_port)))
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.sendto("list_servers#%s"%json.dumps(servers_manager.in_use_servers), (monitor_ip,int(monitor_port)))

#to send our monitors to the web_services
def sendMonitorToServers(servers_manager,monitor):
    for server in servers_manager.in_use_servers:
        cust_logger.info("Sending monitor %s:%d/%d to servers"%(monitor['ip'], monitor['port'], monitor['port_hb']))
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.sendto("add_monitor#%s#%d#%d"%(monitor['ip'], monitor['port'], monitor['port_hb']), (server['ip'],server['monitor_port']))



###################### Listen to udp packets #########################

class UdpProtocol(protocol.DatagramProtocol):
    '''
        udp protocol manager that is binded and listen to a connexion. It is to be moved in a separate process since it deals with 
        monitors managment. It also provides a way to dynamically add a server to the potential servers, by sending a specific packet
        to the socket
    '''

    def __init__(self, servers_manager):
        self.servers_manager = servers_manager


    def datagramReceived(self, data, (host, port)):
        if data.startswith("add_server"):
            cust_logger.info("Received new server notification")
            _, server_ip, server_port, server_monitor_port = data.split('#')
            self.servers_manager.possible_servers.append({'ip': server_ip, 'port': int(server_port), 'monitor_port':int(server_monitor_port)})
            sendMonitorToServers(self.servers_manager, new_monitor)
        elif data.startswith("request_monitor"):
            cust_logger.info("Received packet from monitor")
            _, monitor_ip, monitor_port, monitor_hb = data.split('#')
            new_monitor = dict(ip=monitor_ip, port=int(monitor_port), port_hb=int(monitor_hb))
            if new_monitor not in monitors:
                cust_logger.info("Adding new monitor %s:%d/%d to list"%(monitor_ip, int(monitor_port), int(monitor_hb)))
                monitors.append(new_monitor)
            #we propagate the new in all cases for server down and up again
            sendMonitorToServers(self.servers_manager, new_monitor)
            sendListServers(self.servers_manager, monitor_ip, monitor_port)





############## MAIN ########################

def main():
    #Define the path to the log file
    path_file_log = cust_logger.add_file("log/logFile")
    #we get the arguments
    (opts, args) = getopt.getopt(sys.argv[1:], "s:h",
        ["source=", "help"])
    sourcePort, targetHost = None, None, 
    for option, argval in opts:
        if (option in ("-s", "--source")):
            sourcePort = int(argval)

    # initialize servers manager 
    possible_servers = json.load(open(config.load_bal_monitor.path_config))['possible_servers']
    in_use_servers = json.load(open(config.load_bal_monitor.path_config))['in_use_servers']

    servers_manager = ServersManager(possible_servers, in_use_servers)
    

    # start the twisted reactor
    reactor.listenUDP(8001, UdpProtocol(servers_manager))
    reactor.listenTCP(sourcePort,
    ProxyHttpServerFactory(servers_manager))
    reactor.run()


if __name__ == "__main__":
  main()
