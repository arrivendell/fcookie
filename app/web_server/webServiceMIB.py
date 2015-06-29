import datetime
import mongoengine

class StatusWebService:
    STATUS_LOST = "UNREACHABLE"
    STATUS_BEATING = "RUNNING"
    STATUS_UP = "UP"
    STATUS_UNKNOWN = "UNKNOWN"
#Data representing the web-service. Base of communication with monitor
class WebServiceMIB(mongoengine.Document):
    port = mongoengine.IntField(required=True)
    status = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    response_time = mongoengine.FloatField(default=0.0)
    av_response_time = mongoengine.FloatField(default=0.0)
    log_file_path = mongoengine.StringField(default="")
    last_excpt_raised = mongoengine.StringField(default="")

    #def __repr__(self):
     #   return "ip = "

    #def __repr__(self):
    #    return ('<WebServiceMonitor ip={} port={} status monitor={} status service={} status \
    #        through lb={} response time={} average resp time = {}>'.format(self.web_server_ip, self.web_server_port, \
    #            self.status_monitor, self.status_service, self.status_through_lb, self.response_time, self.av_response_time))