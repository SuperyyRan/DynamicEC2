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
#   @filename:  DIPLDP.py
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
from DynamicEC2.algorithms.rate_function import *
        
class dipldp():
    def __init__(self, task_queue, submitted_list, finished_list, vm_list, require_cpu, lock_vm_deactive):
        self.taskQueue = task_queue
        self.taskFinishedList = finished_list
        self.taskSubmittedList = submitted_list
        self.vm_list = vm_list
        self.require_cpu = require_cpu
        self.lock_vm_deactive = lock_vm_deactive
        self.a_n = [0, 0]
        self.f_n = [0, 0]
        self.R_n = 0
        self.C_n = 0
        self.delta_n = []
        self.Pi_delta = {}
        self.slot = 10
        self.N = 6*10
        self.flag_N = 0
        self.N_s = 6*20
        self.flag_N_s = 0
        self.epsilon = 0.01
        self.over_p = 0.0
        #for result
        self.num_n = []
        self.busy_n = []
        
    def run(self):
        logging.info('Begin to monitoring and reallocating the VMs...')
        deactive = threading.Thread(target=self.thread_deactive_vm)
        deactive.setDaemon(True)
        deactive.start()

        self.a_n[0] = self.taskQueue.qsize() + 1 + len(self.taskSubmittedList)
        self.f_n[0] = len(self.taskFinishedList)
        time.sleep(self.slot)
        result_flag = 0
        while self.require_cpu[1] != 1 or self.taskQueue.qsize() != 0 or len(self.taskSubmittedList) != 0:
            if self.require_cpu[1] == 1 and result_flag == 0:
                self.result()
                result_flag += 1
            self.flag_N += 1
            self.flag_N_s += 1
	    logging.info('the falg_N is %d' %(self.flag_N))            
	    logging.info('the falg_N_s is %d' %(self.flag_N_s))            

            self.a_n[1] = self.taskQueue.qsize() + 1 + len(self.taskSubmittedList)
            self.f_n[1] = len(self.taskFinishedList)
            delta_tmp = self.a_n[1]-self.a_n[0] - (self.f_n[1]-self.f_n[0])
            self.delta_n.append(delta_tmp)
            
            self.a_n[0] = self.a_n[1]
            self.f_n[0] = self.f_n[1]
            
            self.R_n = self.a_n[1]
            self.C_n = len(self.vm_list.vlist) + len(self.vm_list.starting_list)
            #for result
            self.num_n.append(self.C_n)
            self.busy_n.append(len(self.taskSubmittedList))

            if self.flag_N%self.N == 0:
                #todo: reallocate the VMs
                logging.info('---------Begin to reallcate the number of VMs-----------')
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
                    self.p_delta() 
                    a_0 = (float(self.C_n) - float(self.R_n))/float(self.N)
                    logging.info('the value of a_0 is %f' %(a_0))
                    l_a = max_f(a_0, self.Pi_delta)
                    self.over_p = exp(self.N*(0-l_a))           
                    logging.info('the value of over_p is %f' %(self.over_p))                    

                    delta_Cn = self.C_n
                    while self.over_p > self.epsilon:
                        delta_Cn += 1
                        l_a = max_f((float(delta_Cn) - float(self.R_n))/float(self.N), self.Pi_delta)
                        self.over_p = exp(self.N*(0-l_a))
                        logging.info('the value of over_p is %f' %(self.over_p))                    
                    while self.over_p <= self.epsilon:
                        delta_Cn -= 1
                        l_a = max_f((float(delta_Cn) - float(self.R_n))/float(self.N), self.Pi_delta)
                        self.over_p = exp(self.N*(0-l_a))
                        logging.info('the value of over_p is %f' %(self.over_p))                    
                        if self.over_p >= self.epsilon:
                            delta_Cn += 1
                            break
                    if delta_Cn > self.C_n:
                        logging.info('--------Increase %d VMs in this period--------'%(delta_Cn-self.C_n))
                        self.vm_list.activateVM(delta_Cn-self.C_n)
                    elif delta_Cn < self.C_n and delta_Cn > 0:
                        logging.info('--------Decrease %d VMs in this period--------'%(self.C_n-delta_Cn))
                        #self.vm_list.num_deactive = self.vm_list.deactiveVM(self.C_n-delta_Cn)
                        if self.lock_vm_deactive.acquire():
                            self.vm_list.num_deactive = self.C_n-delta_Cn
                            self.lock_vm_deactive.release()
                    elif delta_Cn < self.C_n and delta_Cn <= 0:
                        if self.lock_vm_deactive.acquire():
                            self.vm_list.num_deactive = self.vm_list.idle_cpu
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

    def p_delta(self):
        self.Pi_delta = {}
        len_delta = len(self.delta_n)
        slice_delta = self.delta_n[len_delta-self.N_s:]
        max_delta = max(slice_delta)
        min_delta = min(slice_delta)
        for i in range(min_delta, max_delta+1):
            for j in slice_delta:
                if i == j:
                    if self.Pi_delta.has_key(i) == False:
                        self.Pi_delta[i] = 0.0
                    self.Pi_delta[i] = self.Pi_delta[i] + 1/float(self.N_s)
        logging.info('The probability of delta:')
        logging.info(self.Pi_delta)

    def result(self):
        logging.info('The record for the number of VMs at n_th slot:')
        logging.info(self.num_n)
        logging.info('The record for the number of busy VMs at n_th slot:')
        logging.info(self.busy_n)
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
