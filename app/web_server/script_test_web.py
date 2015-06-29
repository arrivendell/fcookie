import os
import subprocess
import time


if __name__ == '__main__':
    list_proc = []
    ##first launch the servers potentially used by the load balancer
    list_proc.append(subprocess.Popen(['python', 'webserver.py','-s 5100', '-m 5500']))
    list_proc.append(subprocess.Popen(['python', 'monitorProcessWS.py','-s 5100', '-m 5500']))

    #faulty webserver
    list_proc.append(subprocess.Popen(['python', 'webserver.py','-s 5101', '-m 5501']))
    list_proc.append(subprocess.Popen(['python', 'monitorProcessWS.py','-s 5101', '-m 5501']))
#
    list_proc.append(subprocess.Popen(['python', 'webserver.py','-s 5102', '-m 5502']))
    list_proc.append(subprocess.Popen(['python', 'monitorProcessWS.py','-s 5102', '-m 5502']))
#
    list_proc.append(subprocess.Popen(['python', 'webserver.py','-s 5003', '-m 5503']))
    list_proc.append(subprocess.Popen(['python', 'monitorProcessWS.py','-s 5003', '-m 5503']))

    list_proc.append(subprocess.Popen(['python', 'loadBalancer.py','-s 8000']))

    time.sleep(30)
    for process in list_proc:
       process.kill()
#
#