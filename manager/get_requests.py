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
#   @filename:  get_requests.py
#   @brief:     a thread for receive requests from clients
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################

import socket
import sys
import logging
import Queue
import threading

try:
    import cPickle as pickle
except:
    import pickle

 
#if not "/home/greencloud/" in sys.path:
#    sys.path.append("/home/greencloud/") 

from DynamicEC2.common.Task import *
from DynamicEC2.common.Config import *

class GetRequests(threading.Thread):
  def __init__(self, queue):
    threading.Thread.__init__(self)
    self.taskQueue = queue
    
  def run(self):
    logging.info("Get requests server is starting....")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.bind((getValue('sys','serverAddr1'), int(getValue('sys','listen_port1'))))
    sock.listen(5)
    logging.info("Server is listenting port 8001, with max connection 5")
    
    task_id = 1
    while True:
        #rewrite the id in the server-end
        connection,address = sock.accept()
        while True:
	    buf = connection.recv(1024)
	    if buf != '':
		m_task = pickle.loads(buf)
                #m_task.printTask()
		if m_task.id != -1:
		    logging.debug("Get a Task: %d" % (m_task.id))
		    connection.send('The server received one task!')
		    m_task.id = task_id
                    m_task.arrival_time = time.time()
                    task_id += 1
                    m_task.printTask()
                    self.taskQueue.put(m_task)
                    logging.debug("The size of taskQueue is: %d" % (self.taskQueue.qsize()))
		else:
		    connection.send('End the task process!')
		    logging.info("Tasks are sent over..no more tasks")
                    m_task.printTask()
                    self.taskQueue.put(m_task)
                    break
	    else:
		logging.error('\033[1;31;40m' + 'Task is null, break!' + '\033[0m')
		break
	time.sleep(1)
        logging.info("closing one connection.")
        connection.close()
