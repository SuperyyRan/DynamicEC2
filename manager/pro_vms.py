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
#   @filename:  pro_vms.py
#   @brief:     execute the dynamic resource provioning algorithms
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

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")

from DynamicEC2.common.Task import *
from DynamicEC2.common.VM import *
from DynamicEC2.common.VmList import *
from DynamicEC2.rhapi.ec2api import *
from DynamicEC2.algorithms.DIPLDP import *
from DynamicEC2.algorithms.ARMA_M import *

class ProvideVMs(threading.Thread):
    def __init__(self, vm_list, taskQueue, taskSubmittedList, taskFinishedList, require_cpu, selected_alg, lock_vm_deactive):
        threading.Thread.__init__(self)
        self.vm_list = vm_list
        #self.require_cpu = require_cpu 
        self.taskQueue = taskQueue
        self.taskSubmittedList = taskSubmittedList
        self.taskFinishedList = taskFinishedList
        self.require_cpu = require_cpu
        self.algorithm = selected_alg
        self.lock_vm_deactive = lock_vm_deactive
    
    def run2(self):
        checkready = threading.Thread(target=self.vm_list.checkReady)
        checkready.setDaemon(True)
        checkready.start()

        self.vm_list.initVmList()
	if self.vm_list.idle_cpu <= 8:
	    self.vm_list.activateVM(8-self.vm_list.idle_cpu)        
	logging.info('--------------idle_cpu: %d' %(self.vm_list.idle_cpu))
        time.sleep(10)
        
        if self.algorithm == 'DIPLDP':
            handler = dipldp(self.taskQueue, 
                            self.taskSubmittedList, 
                            self.taskFinishedList, 
                            self.vm_list, 
                            self.require_cpu,
                            self.lock_vm_deactive)
            handler.run()
        elif self.algorithm == 'ARMA-M':
            logging.info('-----Enter the ARMA-M algorithm-------')
            handler2 = arma_m(self.taskQueue, 
                            self.taskSubmittedList, 
                            self.taskFinishedList, 
                            self.vm_list, 
                            self.require_cpu,
                            self.lock_vm_deactive)
            handler2.run()

        #self.vm_list.activateVM(2)
        #time.sleep(50)
        #stop_num = 3
        #while stop_num:
        #    logging.info('--------start deactive-------------%d' %(stop_num))
        #    stop_num = self.vm_list.deactiveVM(stop_num)
        #    time.sleep(5)
        
        #while True:
        #    logging.info('--------report idel_cpu-------%d' %(self.vm_list.idle_cpu))
        #    logging.info('--------report stopped vm-------%d' %(len(self.vm_list.stop_list)))
        #    time.sleep(10)
	#    logging.info('--------report idle_cpu-------%d' %(self.vm_list.idle_cpu))
	#    logging.info('--------report task queue-------%d' %(self.taskQueue.qsize()))
	#    logging.info('--------report submitted task-------%d' %(len(self.taskSubmittedList)))
	#    logging.info('--------report finished task-------%d' %(len(self.taskFinishedList)))

    def run(self):
        self.run2()
