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
#   @filename:  taskExec.py
#   @brief:     a daemon process in EC2 instance to execute the tasks
#   @version:   1.0
#   @author:    Yongyi Ran (yyran@ustc.edu.cn)
#   @date:      2015-04-20
#
###################################################################################


import pika, sys
import time
import logging

#if not "/home/ubuntu/" in sys.path:
#    sys.path.append("/home/ubuntu/")

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")


from DynamicEC2.common.Task import *
from DynamicEC2.common.Message import *
from DynamicEC2.common.Config import *
from tasks.nqueens import *
from DynamicEC2.rhapi.ec2api import *
from tasks.face_detection import *

try:
    import cPickle as pickle
except:
    import pickle

global run_flag

def execTask(routings):
    connection = pika.BlockingConnection(pika.ConnectionParameters(getValue('mq','rabbitMQServer')))
    channel = connection.channel()

    channel.exchange_declare(exchange='messages', type='direct')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    for routing in routings:
        channel.queue_bind(exchange='messages',
                            queue=queue_name,
                            routing_key=routing)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=queue_name, no_ack=False)
    logging.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    
def callback(ch, method, properties, body):
    global run_flag
    content = pickle.loads(body)
    logging.info('Message type: %s' %(content.type))
    #print " [x] Received %r" % (body,)
    #todo: exec the task
    if content.type == 'Task':
        recv_task = pickle.loads(content.arg)
        logging.info('The received task id: %d' %(recv_task.id))
        if recv_task.taskType == 'NQUEENS' and run_flag == 'stopped':
            logging.info('-----begin to execute----------')
            start_time = time.time()
            q = NQueen(recv_task,0,0)
            q.start()
            end_time = time.time()
            #response = Message('Task_End', pickle.dumps(recv_task))
            #ch.basic_publish(exchange='messages', routing_key='server', body=pickle.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info("Task Completed!!!")
        elif recv_task.taskType == 'FACE_DETECTION' and run_flag == 'stopped':
            #exec_face_detection
            start_time = time.time()
            face_detection.run(recv_task)
            end_time = time.time()
            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info("Task Completed!!!")
    elif content.type == 'Check':
        if run_flag == 'stopped': 
            response = Message('ReCheck', 'Idle')
            ch.basic_publish(exchange='messages', routing_key='server-check', body=pickle.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info(content.arg)
        else:
            response = Message('ReCheck', 'Busy')
            ch.basic_publish(exchange='messages', routing_key='server-check', body=pickle.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            logging.info(content.arg)

# for test
def getInstanceId():
    #ret = 'i-5544e9a2'
    api = RHAPI()
    ret = api.getInstanceId("eth0")
    logging.info('The id of this Instance is:%s'%(ret))
    return ret

if __name__ == '__main__':
    init_vm_log(logging.DEBUG)
    global run_flag
    run_flag = 'stopped'
    vm_id = getInstanceId()   
    routings = [vm_id,]
    execTask(routings)
