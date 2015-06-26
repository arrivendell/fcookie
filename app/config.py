import json

class Config:

    class FortuneService:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=5000


    class HealthMonitor:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port=8000