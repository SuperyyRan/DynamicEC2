#!/usr/bin/env python
# -*- coding:utf-8 -*-
##################################################################################
#
#   Copyright 2015-2016 University Of Science and Technology of China (USTC)
#   Licensed under the Apache License, Version 2.0 (the "License"); you may 
#   not use this file except in compliance with the License. You may obtain 
#   a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   @filename:  pro_requests.py
#   @brief:     process the task from clients
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import Queue
import threading
import time
import sys
import logging

#if not "/home/greencloud/" in sys.path:
#    sys.path.append("/home/greencloud/")

try:
        import cPickle as pickle
except:
        import pickle

from DynamicEC2.common.Task import *
from DynamicEC2.common.VM import *
from DynamicEC2.messages.sendMessage import *
        
class ProcessReq(threading.Thread):
    def __init__(self, queue, outqueue, vm_list, require_cpu, lock_vm_idle, mutex_sub):
        self._lock = lock_vm_idle
        threading.Thread.__init__(self)
        self.taskQueue = queue
        self.taskSubmittedList = outqueue
        self.vm_list = vm_list
        self.require_cpu = require_cpu
	self.mutex_sub = mutex_sub

    def run(self):
        while True:
            m_task = self.taskQueue.get()
            if m_task.id == -1:
                self.require_cpu[1] = 1
                continue
            if self._lock.acquire():
                self.require_cpu[0] = m_task.cpu
                logging.info("Idle number of CPU: %d" % (self.vm_list.idle_cpu))
                logging.info("Required CPU is: %d" % (m_task.cpu))
                while self.vm_list.idle_cpu < self.require_cpu[0]:
                    logging.info("Task %d is waiting for process." % (m_task.id))
                    self._lock.wait()
                if self.vm_list.idle_cpu >= self.require_cpu[0] and self.require_cpu[0] != -1000:
                    logging.info("Task %d is processing Now" % (m_task.id))
                    #todo: allocate VM and submit task
                    self.vm_list.useVM(m_task)
                    #self.submitTask(m_task.allocated_vms)
                    m_task.start_time = time.time()
                    m_task.printTask()
                    m_task.printAllocatedVMsofTask()    
		self.mutex_sub.acquire()
	        self.taskSubmittedList.append(m_task)
		self.mutex_sub.release()
                logging.info("Submitted number of task is: %d" % (len(self.taskSubmittedList)))
                self.require_cpu[0] = -1000
                self._lock.release()
            self.taskQueue.task_done()
            time.sleep(1)
