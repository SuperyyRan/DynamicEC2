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
#   @filename:  ARMA-M.py
#   @brief:     the customed algorithm 
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
from DynamicEC2.common.VmList import *
from DynamicEC2.algorithms.arma_predict import *
        
class arma_m():
    def __init__(self, task_queue, submitted_list, finished_list, vm_list, require_cpu, lock_vm_deactive):
        self.taskQueue = task_queue
        self.taskFinishedList = finished_list
        self.taskSubmittedList = submitted_list
        self.vm_list = vm_list
        self.require_cpu = require_cpu
        self.lock_vm_deactive = lock_vm_deactive
        self.R_n = []
        self.C_n = 0
        self.slot = 10
        self.N = 6*10
        self.flag_N = 0
        self.N_s = 6*80
        self.flag_N_s = 0
        #for result
        self.num_n = []
        self.busy_n = []

    def run(self):
        logging.info('Begin to monitoring and reallocating the VMs...')
        deactive = threading.Thread(target=self.thread_deactive_vm)
        deactive.setDaemon(True)
        deactive.start()

        while self.require_cpu[1] != 1 or self.taskQueue.qsize() != 0 or len(self.taskSubmittedList) != 0:
            if self.require_cpu[1] == 1 and result_flag == 0:
                self.result()
                result_flag += 1
            self.flag_N += 1
            self.flag_N_s += 1
	    logging.info('the falg_N is %d' %(self.flag_N))            
	    logging.info('the falg_N_s is %d' %(self.flag_N_s)) 
            #for result
            
            self.C_n = len(self.vm_list.vlist) + len(self.vm_list.starting_list)
            self.num_n.append(self.C_n)
            self.busy_n.append(len(self.taskSubmittedList))

            if self.flag_N%self.N == 0:
                #todo: reallocate the VMs
                logging.info('---------Begin to reallcate the number of VMs (ARMA-M)-----------')
                a_n = self.taskQueue.qsize() + 1 + len(self.taskSubmittedList)
                self.R_n.append(a_n)
                
                if self.lock_vm_deactive.acquire():
                    self.vm_list.num_deactive = 0
                    self.lock_vm_deactive.release()
                
                if self.flag_N_s < self.N_s:
                    logging.info('N_s smaller than %d' %(self.N_s))
                    if self.vm_list.idle_cpu > 1:
                        logging.info('Vms need be stopped')
                        if self.lock_vm_deactive.acquire():
                            self.vm_list.num_deactive = self.vm_list.idle_cpu/2
                            self.lock_vm_deactive.release()
                    elif self.vm_list.idle_cpu == 0:
                        logging.info('VMs need be added')
                        self.vm_list.activateVM(self.taskQueue.qsize()/2)

                if self.flag_N_s >= self.N_s:
                    P_Rn = arma_predict(self.R_n, 1)*1.05
                    logging.info('-----the predicted value:%f' %(P_Rn))
                    if self.C_n < P_Rn:
                        logging.info('--------Increase %d VMs in this period--------'%(int(P_Rn-self.C_n)))
                        self.vm_list.activateVM(int(P_Rn-self.C_n))
                    elif self.C_n >= P_Rn:
                        logging.info('--------Decrease %d VMs in this period--------'%(int(self.C_n-P_Rn)))
                        #self.vm_list.num_deactive = self.vm_list.deactiveVM(self.C_n-delta_Cn)
                        if self.lock_vm_deactive.acquire():
                            self.vm_list.num_deactive = int(self.C_n-P_Rn)
                            self.lock_vm_deactive.release()
                self.flag_N = 0

            time.sleep(self.slot)
            logging.info('--------report idle_cpu-------%d' %(self.vm_list.idle_cpu))
            logging.info('--------report task queue-------%d' %(self.taskQueue.qsize()))
            logging.info('--------report submitted task-------%d' %(len(self.taskSubmittedList)))
            logging.info('--------report finished task-------%d' %(len(self.taskFinishedList)))
        
        self.result()
    
    def thread_deactive_vm(self):
        while self.require_cpu[1] != 1 or self.taskQueue.qsize() != 0 or len(self.taskSubmittedList) != 0:
            if self.lock_vm_deactive.acquire():
                self.vm_list.num_deactive = self.vm_list.deactiveVM(self.vm_list.num_deactive)
                self.lock_vm_deactive.release()
            time.sleep(5)

    def result(self):
        logging.info('The record for the info of tasks:')
        wait_time_list = []
	for i in self.taskFinishedList:
            #i.printTask()
	    logging.info('-----Task id:-----%d' %(i.id))
            logging.info('-----Task cpu:-----%d' %(i.cpu))
            logging.info('-----Task para:-----%d' % (i.execParameter))
            logging.info('-----Task type:-----%s' % (i.taskType))
            logging.info('-----Task arrival time:-----%f' % (i.arrival_time))
            if i.start_time != -1.0:
                logging.info('-----Task start time:-----%f' % (i.start_time))
            if i.end_time != -1.0:
                logging.info('-----Task end time:-----%f' % (i.end_time))
            if i.finish_flags != -1: 
                logging.info('-----Task finish flag:-----%d' % (i.finish_flags))   
	    wait_time_list.append(i.start_time-i.arrival_time)
	logging.info(wait_time_list)
        
        logging.info('The record for the number of VMs at n_th slot:')
        logging.info(self.num_n)
        logging.info('The record for the number of busy VMs at n_th slot:')
        logging.info(self.busy_n)
