# fcookie
fortune cookie + health monitor

Welcome to the guide about how to run this program.

First of all, let me present the architecture of the folder :

"app/" contains all the source code, basically splitted in two folders :   
==> "health_monitor" :  
        source code related to the monitoring software, containing     
        --> the monitoring web server ("monitor.py"), which can be run whenever you want  
        --> the processing program that fills the database with data coming from monitored nodes (Must be lauch only if loadBalancer.py is launch)  
        --> some mongoDB documents (mongoWebMonitor.py) to represent the data displayed on the website  
        --> a script for testing this part, that must be launched after the other one in the web service folder  
        -->2 folders, "static" and "templates" containing the resources to process the html view, according to Flask architecture   

===> "web_server" :  
       source code related to the load balancer and the web service  
        --> loadBalancer.py, the load balancer with its monitoring interface included ( should be separate file in the future). Can be launched 1st or just after the web service instances  
        --> webservice.py, containing a web service using flask  
        --> webservice_falty.py, a webservice with a wrong path for the fortune file  
        -->"monitorProcessWS.py" that is the monitoring interface of the webserver  
        --> "webServiceMIB.py", where the database documents to represent the web service are defined  
        --> a script that can be run to test the whole process, but not really useful now  
        -->2 folders, "static" and "templates" containing the resources to process the html view, according to Flask   architecture, and containing the "Fortunes.txt" file used to randomly send back fortune sentences   

Example of execution:
First, find the file "config_serv.json" in the folder "app/" and set the servers how you want them to be set.
This file represent the servers that could be used during the execution ( possible_servers) and the one that will be used from the beginning (in_use_servers)
According to this file, you can now launch your servers and their monitoring interface in that way :

> python webserver.py -s 5000 -m 5500 (and only if add server manually to the list -l localhost:6000)
> python monitorProcessWS.py -s 5000 -m 5500  ( must be the same as webserver.py)

Where s is the port on which the service will listen to the requests, and -m is the port used by the monitoring interface to listen.

Now, launch the loadBalancer:
> python loadBalancer.py -s 8000
(it will launch the proxy listening on port -s )

then go to the health_monitor folder and launch in the order you want :

> python monitor.py
> python monitorProcessing.py

Using one terminal per script is useful to see what is happening

You can connect to localhost:8000/fortune to have a fortune sentence, ( it should take at least 2 seconds to simulate big operation to run, there is a 2 second window to overload the proxy and see him adding servers.) 
connect to localhost:7013 to see the monitoring interface
Both the default ports are written in the file config.py

The monitoring interface should display as many green rectangle as you have launched of web services. Click on it to see the details, 
refresh the page to see the evolution !
