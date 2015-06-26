import json

class Config:

    class FortuneService:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=5000
            self.path_file_fortunes = "web_server/static/fortunes/fortunes.txt"


    class HealthMonitor:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=8000

    def __init__(self):
        self.fortune_service = self.FortuneService()
        self.health_monitor = self.HealthMonitor()