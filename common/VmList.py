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
#   @filename:  VM.py
#   @brief:     A class definition of VM
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import time
import threading
import logging

from DynamicEC2.messages.sendMessage import *
from DynamicEC2.messages.roundMessage import *
from DynamicEC2.common.Message import *
from DynamicEC2.rhapi.ec2api import *
from DynamicEC2.common.VM import *

try:
        import cPickle as pickle
except:
        import pickle


class VmList:
    def __init__(self, lock_vm_idle, lock_for_check, lock_vm_deactive, require_cpu):
        self.vlist = []
        self.stop_list = []
        self.starting_list = []
        self.idle_cpu = 0
        self.mutex = threading.Lock()
        self.mutex_vlist = threading.Lock()
        self.lock_condition = lock_vm_idle
        self.require_cpu = require_cpu
        self.lock_for_check = lock_for_check
        self.lock_vm_deactive = lock_vm_deactive
        
        self.num_deactive = 0

    def initVmList(self):
        self.mutex.acquire()
        api = RHAPI()
        res = api.conn.get_all_reservations()
        exception_set = ['i-7db40a8a', 'i-7ccd328b', 'i-3eb00ec9', 'i-a8cd325f', 'i-b812d44f', 'i-e6ec2a11']
        for r in res:
            logging.info(r.instances[0].state)
            logging.info(r.instances[0].id)
            logging.info(r.instances[0].ip_address)
            logging.info(r.instances[0].private_ip_address) 
            if r.instances[0].id not in exception_set:
                if r.instances[0].state == 'running' or r.instances[0].state == 'pending':
                    vm = VM(r.instances[0].id, 1)
                    vm.vflag = True
                    self.addVm(vm)
                elif r.instances[0].state == 'stopped' or r.instances[0].state == 'stopping':
                    vm = VM(r.instances[0].id, 1)
                    vm.vflag = False
                    self.stopVM(vm)
        self.mutex.release()


    def addVm(self, vm):
        #todo: running a VM in EC2
        self.mutex_vlist.acquire()
        for j in self.starting_list:
            if j.vId == vm.vId:
                self.starting_list.remove(j)
                break
        for i in self.vlist:
            if i.vId == vm.vId:
                logging.info("This VM is already existed: -------%s" % (vm.vId))
                self.mutex_vlist.release()
                return True
        vm.vflag = True
        vm.vstatus = True
        self.vlist.append(vm)
        logging.info("The id of added VM: -------%s" % (vm.vId))
        self.idle_cpu = self.idle_cpu + vm.vcpu
        logging.info('The idle_cpu is: %d' %(self.idle_cpu))
        
        if self.lock_condition.acquire():
            if self.idle_cpu >= self.require_cpu[0] and self.require_cpu[0] != -1000:
                logging.info('notify there are sufficient resource')
                self.lock_condition.notify()
            self.lock_condition.release()

        self.mutex_vlist.release()
        return True


    def activateVM(self, num_vm):
        self.mutex.acquire()
        if self.lock_for_check.acquire():
            if len(self.stop_list) < num_vm:
                active_num = len(self.stop_list)
                add_num = num_vm - active_num
            else:
                active_num = num_vm
                add_num = 0
            #for i in range(active_num):
            logging.info('-----the active num is: %d' %(active_num))
            api = RHAPI()
            while active_num:
                for i in self.stop_list:    
                    if api.startInstance(i.vId):
                        self.stop_list.remove(i)
                        i.vflag = True
                        i.vstatus = False
                        self.starting_list.append(i)
                        logging.info('----starting one vm from the stop list----')
                        active_num -= 1
                        logging.info('-----the active num is: %d' %(active_num))
                        break
            while add_num:
		if len(self.vlist)+len(self.starting_list)+len(self.stop_list) >= 40:
		    add_num = 0
		    break
		c_vm = api.createInstance()
                if c_vm:
                    c_vm.vflag = True
                    c_vm.vstatus = False
                    self.starting_list.append(c_vm)
                    add_num -= 1
            self.lock_for_check.notify()
            self.lock_for_check.release()
        self.mutex.release()

    def checkReady(self):
        while True:
            if self.lock_for_check.acquire():
                if len(self.starting_list) == 0:
                    self.lock_for_check.wait()
                logging.info('------the length of starting list------%d' %(len(self.starting_list)))
                logging.info('------checking the starting list------')
                api = RHAPI()
                for i in self.starting_list:
                    logging.info('-------check the vm %s--------' %(i.vId))
                    if api.checkStatus(i.vId) == 'passed':
                        msg = Message('Check', 'Check the status of %s.' %(i.vId))
                        status = roundMessage(i.vId, pickle.dumps(msg))
                        if status == 'Idle':
                            self.mutex.acquire()
                            self.addVm(i)
                            self.mutex.release()
                        elif status == 'Error':
                            api.conn.reboot_instances(instance_ids=[i.vId])
                self.lock_for_check.release()
            time.sleep(15)


    def deactiveVM(self,vm_num):
        self.mutex.acquire()
        index = vm_num
        for i in range(index):
            for i in self.vlist:
                if i.vstatus == True:
                    api = RHAPI()
                    self.stopVM(i)
                    c_vm = api.stopInstance(i.vId)
                    vm_num -= 1
                    break
        self.mutex.release()
        logging.info('----more %d vm need be deactive-----' %(vm_num))
        return vm_num   

    def stopVM(self, vm):
        self.mutex_vlist.acquire()
        #todo: stoping a vm in EC2
        for i in self.vlist:
            if i.vId == vm.vId and i.vstatus == True:
                self.vlist.remove(i)
                i.vflag = False
                i.vstatus = False
                self.stop_list.append(i)
                self.idle_cpu = self.idle_cpu - i.vcpu
                logging.info('stop vm lead to idle cpu reduce')
                self.mutex_vlist.release()
                return True
            elif i.vId == vm.vId and i.vstatus == False:
                logging.info('stop vm failed, task is running.')
                self.mutex_vlist.release()
                return False
        for j in self.stop_list:
            if j.vId == vm.vId:
                self.mutex_vlist.release()
                return True
        vm.vflag = False
        vm.vstatus = False
        self.stop_list.append(vm)
        logging.info('--------length of stop list-------%d' %(len(self.stop_list)))
        self.mutex_vlist.release()
        return True
    

    def useVM(self, task):
        self.mutex.acquire()
        self.mutex_vlist.acquire()
        logging.info('Begining to use VMs')
        num_cpu = task.cpu
        mes = Message('Task', pickle.dumps(task))
        if self.idle_cpu < num_cpu:
            logging.info('The resource is not statisfied')
            self.mutex_vlist.release()                                                                                         
            self.mutex.release()
            return False
        for v in self.vlist:
            if v.vstatus == True and v.vflag == True and num_cpu >= 1:
                #todo: confirm the VM is available
                self.idle_cpu = self.idle_cpu - v.vcpu
                logging.debug("The idle cpu after process a task: %d" % (self.idle_cpu))
                num_cpu = num_cpu - v.vcpu
                v.vstatus = False
                v.vtaskId = task.id
                #v.vflag = True
                logging.debug("The used vm id is: -----------%s" % (v.vId))
                logging.info("The processing task id is: %d" % (task.id))
                task.allocated_vms.append(v)
                sendMessage([v.vId], pickle.dumps(mes))
            if num_cpu <= 0:
                break
        task.finish_flags = len(task.allocated_vms)
        self.mutex_vlist.release()
        self.mutex.release()
        return True

    def releaseVM(self, task):
        self.mutex.acquire()
        self.mutex_vlist.acquire()
        for v in self.vlist:
            for t_vm in task.allocated_vms:
                if v.vId == t_vm.vId:
                    v.vstatus = True
                    v.vtaskId = -1
                    self.idle_cpu = self.idle_cpu + v.vcpu
        logging.info('The VMs are released.')

        #if self.num_deactive != 0:
        #    if self.lock_vm_deactive.acquire():
        #        self.lock_vm_deactive.notify()
        #        self.lock_vm_deactive.release()
        #    self.mutex_vlist.release()
        #    self.mutex.release()
        #    return

        if self.lock_condition.acquire():
            if self.idle_cpu >= self.require_cpu[0] and self.require_cpu[0] != -1000:
                self.lock_condition.notify()
            self.lock_condition.release()
        
        self.mutex_vlist.release()
        self.mutex.release()

    def getAvailableCPU(self):
        return self.idle_cpu
