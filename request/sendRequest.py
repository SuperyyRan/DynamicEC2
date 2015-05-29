#!/usr/bin/env python
# -*- coding:utf-8 -*-
###################################################################################
#
#   Copyright 2015-2016 University Of Science and Technology of China (USTC)
#   Licensed under the Apache License, Version 2.0 (the "License"); you may 
#   not use this file except in compliance with the License. You may obtain 
#   a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   @filename:  gen_requests.py
#   @brief:     generating requests (poisson distribution)
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import sys
import logging
import numpy as np
import random

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")

from DynamicEC2.common.Task import *
from DynamicEC2.common.Logger import *
from DynamicEC2.common.Config import *

try:
    import cPickle as pickle
except:
    import pickle

def send_requests():
    init_log(logging.DEBUG)
    import socket  
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((getValue('sys','serverAddr1'), int(getValue('sys','listen_port1'))))  
    import time  

    str_tasks = ''
    f = open('all_task.txt', 'r')
    str_tasks = f.read()
    str_list = str_tasks.split('\n\n')
    
    id = 1
    cpu = 1
    time_request = np.loadtxt('request_time.txt')
    for i in time_request:
        logging.info('The next task will arrive after %f seconds.' %(i))
        time.sleep(float(i))
        
        if str_list[id-1] != '':
            str_task = pickle.loads(str_list[id-1])
            m_task = Task(id, str_task.userId, cpu, str_task.execParameter, str_task.taskType)
        else:
            continue

        logging.info("send a Task to server: %d" % (id))
        m_task.printTask()
        d_task = pickle.dumps(m_task)
        sock.send(d_task)
        logging.info(sock.recv(1024))
        id += 1
    #end_task
    m_task = Task(-1,1,cpu,-1,'END')
    logging.info("send a end signal to Server..")
    d_task = pickle.dumps(m_task)
    sock.send(d_task)
    logging.info(sock.recv(1024))

    sock.close()

if __name__=="__main__":
    send_requests()
