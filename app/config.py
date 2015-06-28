import json

class Config:

    class FortuneService:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=5001
            self.path_file_fortunes = "web_server/static/fortunes/fortunes.txt"


    class MonitorLoadBalancerConfig:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=8000
            self.port_udp=8001
            self.mongo_db = "load_balancer"
            self.path_config = "../config_serv.json"


    class MonitorService:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=7013
            self.mongo_db = "monitoring_service"
            self.port_hb = 7014
            self.port_udp_process = 7015


    def __init__(self):
        self.fortune_service = self.FortuneService()
        self.load_bal_monitor = self.MonitorLoadBalancerConfig()
        self.health_monitor = self.MonitorService()