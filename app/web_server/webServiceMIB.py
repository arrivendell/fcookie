import datetime
import mongoengine

class WebServiceMIB(mongoengine.Document):
    status = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    
    response_time = mongoengine.FloatField(default=0.0)
    av_response_time = mongoengine.FloatField(default=0.0)

    #def __repr__(self):
     #   return "ip = "

    #def __repr__(self):
    #    return ('<WebServiceMonitor ip={} port={} status monitor={} status service={} status \
    #        through lb={} response time={} average resp time = {}>'.format(self.web_server_ip, self.web_server_port, \
    #            self.status_monitor, self.status_service, self.status_through_lb, self.response_time, self.av_response_time))