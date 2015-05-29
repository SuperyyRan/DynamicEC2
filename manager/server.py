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
#   @filename:  server.py
#   @brief:     server for managing dynamic resource provioning
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################

import logging
import socket
import sys
import Queue
import threading

try:
    import cPickle as pickle
except:
    import pickle

 
if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/") 

from DynamicEC2.common.Task import *
from DynamicEC2.common.VM import *
from DynamicEC2.common.VmList import *
from DynamicEC2.common.Logger import *
from DynamicEC2.common.Config import *
from DynamicEC2.rhapi.ec2api import *

import pro_requests
import get_requests
import pro_vms
import pro_finish

global mutex_sub, lock_vm_idle, lock_for_check, lock_vm_deactive
mutex_sub = threading.Lock()
lock_vm_idle = threading.Condition()
lock_for_check = threading.Condition()
lock_vm_deactive = threading.Condition()

global taskQueue
taskQueue = Queue.Queue(0)
global taskSubmittedList
taskSubmittedList = []
global taskFinishedList
taskFinishedList = []
global require_cpu
require_cpu = [-1000, 0]
global vm_list
vm_list = VmList(lock_vm_idle, lock_for_check, lock_vm_deactive, require_cpu)

def main():
    logging.info('The server is starting now...')
    init_log(logging.DEBUG)
    global taskQueue
    global vm_list
    global taskSubmittedList
    global require_cpu
    global lock_vm_idle
    global taskFinishedList
    
    get_server = get_requests.GetRequests(taskQueue)
    get_server.setDaemon(True)
    get_server.start()

    pro_server = pro_requests.ProcessReq(taskQueue, taskSubmittedList, vm_list, require_cpu, lock_vm_idle, mutex_sub)
    pro_server.setDaemon(True)
    pro_server.start()

    algorithms = sys.argv[1:]
    if not algorithms:
        algorithms = ['DIPLDP']
    selected_alg = algorithms[0]
    logging.info('The selected algorithm is %s' % (selected_alg))
    pro_vm_server = pro_vms.ProvideVMs(vm_list,
                                        taskQueue,
                                        taskSubmittedList,
                                        taskFinishedList,
                                        require_cpu, 
                                        selected_alg,
                                        lock_vm_deactive)
    pro_vm_server.setDaemon(True)
    pro_vm_server.start()

    logging.info("Start the message recv server.....")
    mqserver = getValue('mq','rabbitMQServer')
    connection = pika.BlockingConnection(pika.ConnectionParameters(mqserver))
    channel = connection.channel()
    channel.exchange_declare(exchange='messages', type='direct')

    routings = ['server']
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    for routing in routings:
        channel.queue_bind(exchange='messages',
                            queue=queue_name,
                            routing_key=routing)

    channel.basic_consume(callback, queue=queue_name, no_ack=False)
    logging.info('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    
def callback(ch, method, properties, body):
    global taskFinishedList
    global taskSubmittedList
    global mutex_sub
    global lock_vm_idle
    global require_cpu
    global vm_list
    content = pickle.loads(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    if content.type == 'Task_End':
        recv_task = pickle.loads(content.arg)
        logging.info(" Task %d is fininshed" %(recv_task.id))
        finish_t = pro_finish.ProcessFinishedTask(recv_task, 
                                        taskSubmittedList, 
                                        taskFinishedList, 
                                        vm_list, 
                                        mutex_sub, 
                                        require_cpu, 
                                        lock_vm_idle)
        finish_t.setDaemon(True)
        finish_t.start()

if __name__ == '__main__':
    main()
