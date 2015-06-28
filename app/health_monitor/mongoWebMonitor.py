import datetime
import mongoengine

class WebServiceMonitor(mongoengine.Document):
    web_server_ip = mongoengine.StringField(required=True)
    web_server_port = mongoengine.IntField(required=True)
    status_monitor = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    status_service = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    status_through_lb = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    response_time = mongoengine.FloatField(default=0.0)
    av_response_time = mongoengine.FloatField(default=0.0)

    #def __repr__(self):
     #   return "ip = "

    def __repr__(self):
        return ('<WebServiceMonitor ip={} port={} status monitor={} status service={} status \
            through lb={} response time={} average resp time = {}>'.format(self.web_server_ip, self.web_server_port, \
                self.status_monitor, self.status_service, self.status_through_lb, self.response_time, self.av_response_time))