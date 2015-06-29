import os
import subprocess
import time


if __name__ == '__main__':
    list_proc = []
    ##first launch the servers potentially used by the load balancer
    list_proc.append(subprocess.Popen(['python', 'monitor.py']))
    list_proc.append(subprocess.Popen(['python', 'monitorProcessing.py']))

    time.sleep(30)
    for process in list_proc:
       process.terminate()
#
#