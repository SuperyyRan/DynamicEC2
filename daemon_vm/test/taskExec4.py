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
if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")

from DynamicEC2.common.Task import *
from DynamicEC2.common.Message import *
from DynamicEC2.common.Config import *
from tasks.nqueens import *

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
    print ' [*] Waiting for messages. To exit press CTRL+C'
    channel.start_consuming()
    
def callback(ch, method, properties, body):
    global run_flag
    content = pickle.loads(body)
    print 'Message type: %s' %(content.type)
    #print " [x] Received %r" % (body,)
    #todo: exec the task
    if content.type == 'Task':
        recv_task = pickle.loads(content.arg)
        print 'receive the task'
        print 'Task id: %d' %(recv_task.id)
        if recv_task.taskType == 'NQUEENS' and run_flag == 'stopped':
            print '-----begin to execute----------'
            start_time = time.time()
            q = NQueen(recv_task,0,0)
            q.start()
            end_time = time.time()
            #response = Message('Task_End', pickle.dumps(recv_task))
            #ch.basic_publish(exchange='messages', routing_key='server', body=pickle.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            print "Executing Task!!!"
        elif recv_task.taskType == 'FACE_DETECTION' and run_flag == 'stopped':
            #exec_face_detection
            pass
    elif content.type == 'Check':
        #response = Message('Check', pickle.dumps(task))
        #ch.basic_publish(exchange='messages', routing_key='server', body=response)
        if run_flag == 'stopped': 
            response = Message('ReCheck', 'Idle')
            ch.basic_publish(exchange='messages', routing_key='server-check', body=pickle.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            print content.arg
        else:
            response = Message('ReCheck', 'Busy')
            ch.basic_publish(exchange='messages', routing_key='server-check', body=pickle.dumps(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)
            print content.arg

# for test
def getInstanceId():
    ret = 'i-5544e9a2'
    return ret

if __name__ == '__main__':
    global run_flag
    run_flag = 'stopped'
    vm_private_ip = getInstanceId()   
    routings = [vm_private_ip,]
    execTask(routings)
