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


try:
        import cPickle as pickle
except:
        import pickle

from DynamicEC2.common.Task import *
from DynamicEC2.common.VM import *
        
class ProcessFinishedTask(threading.Thread):
    def __init__(self, recv_task, submitted_list, finished_list, vm_list, mutex_sub, require_cpu, lock_vm_idle):
        self.mutex_lock = mutex_sub
        threading.Thread.__init__(self)
        self.taskFinishedList = finished_list
        self.taskSubmittedList = submitted_list
        self.vm_list = vm_list
        self.recv_task = recv_task
        self.lock_vm_idle = lock_vm_idle
        self.require_cpu = require_cpu

    def run(self):
        self.mutex_lock.acquire()
        for t in self.taskSubmittedList:
	    logging.info('-----------process finish------------')
            if t.id == self.recv_task.id:
		logging.info('------find the task-------')
                t.finish_flags -= 1
		logging.info('The finish flasgs is %d ' %(t.finish_flags))
            if t.finish_flags == 0:
                logging.info('-----------finish point------------')
                t_finished = t
                self.taskSubmittedList.remove(t)
                t_finished.end_time = time.time()
                self.taskFinishedList.append(t_finished)
                self.mutex_lock.release()
                self.vm_list.releaseVM(t_finished)
               # if self.lock_vm_idle.acquire():
               #     logging.info('Task is finished, release the occupied VMs')
               #     self.vm_list.releaseVM(t_finished)
               #     if self.vm_list.idle_cpu >= self.require_cpu[0] and self.require_cpu[0] != -1000:
               #         self.lock_vm_idle.notify()
               #     self.lock_vm_idle.release()
            	return
        self.mutex_lock.release()
