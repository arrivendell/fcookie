import datetime
import mongoengine

class StatusWebService:
    STATUS_LOST = "UNREACHABLE"
    STATUS_BEATING = "RUNNING"
    STATUS_UP = "UP"
    STATUS_UNKNOWN = "UNKNOWN"
    STATUS_UNKNOWN = "UNKNOWN"

class WebServiceMonitor(mongoengine.Document):
    web_server_ip = mongoengine.StringField(required=True)
    web_server_port = mongoengine.IntField(required=True)
    monitor_port = mongoengine.IntField(required=True)
    status_monitor = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    status_service = mongoengine.IntField(default=0) #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    status_through_lb = mongoengine.StringField(default="UNKNOWN") #status can be UNKNOWN, RUNNING, FAULTY, UNREACHABLE
    response_time = mongoengine.FloatField(default=0.0)
    last_excpt_raised = mongoengine.StringField(default="")
    successfull_calls = mongoengine.IntField(default=0)

    #def __repr__(self):
     #   return "ip = "

    def __repr__(self):
        return ('<WebServiceMonitor ip={} port={} status monitor={} status service={} status \
            through lb={} response time={} last_excpt_raised = {}>'.format(self.web_server_ip, self.web_server_port, \
                self.status_monitor, self.status_service, self.status_through_lb, self.response_time, self.last_excpt_raised))


class Logs(mongoengine.Document):
    web_server_ID = mongoengine.StringField(required=True)
    log_timestamp = mongoengine.DateTimeField(required=True)
    log_type = mongoengine.StringField(default="") 
    log_content = mongoengine.StringField(default="") 
