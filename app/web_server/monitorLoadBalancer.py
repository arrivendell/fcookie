
import string
import sys
import time
sys.path.append('..')
sys.path.append('../../libs')
sys.path.append('../..')

class MonitorLoadBalancer:
    def __init__(self, servers_manager, configuration):
        self.servers_manager = servers_manager
        self.configuration = configuration

