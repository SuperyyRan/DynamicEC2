#!/usr/bin/env python

import boto.ec2
import logging
import time
import sys

if not "/home/yyran/" in sys.path:
    sys.path.append("/home/yyran/")

from DynamicEC2.common.VM import *
from DynamicEC2.common.Logger import *

class RHAPI:
    def __init__(self):
        self.conn = boto.ec2.connect_to_region("us-west-2",
	                			aws_access_key_id='your access key id',
			                	aws_secret_access_key='your secret access key')
        boto.set_stream_logger('boto')
        #self.conn = boto.ec2.connect_to_region("us-west-2")

    def createInstance(self, imgID='your image'):
        try: 
            res = self.conn.run_instances(imgID,
                                key_name='your key name',
                                instance_type='t2.micro', 
                                security_group_ids=['your security group'], 
                                subnet_id='subnet id')
        except Exception as e:     
            logging.error(e)
            sys.exit(1)
        if res:
            c_vm = VM(res.instances[0].id, 1)
            c_vm.vflag = True
            return c_vm
        else:
            return None

    def stopInstance(self, vmId):
        try:
            status = self.conn.get_all_reservations(instance_ids=[vmId])
        except Exception as e:     
            logging.error(e)
            #print e
            sys.exit(1)
        if status:
            logging.debug(status[0].instances[0].id)
            logging.debug(status[0].instances[0].state)
            if status[0].instances[0].state == 'running' or status[0].instances[0].state == 'pending':
                if self.conn.stop_instances(instance_ids=[vmId]):
                    logging.info('Stop instance %s success!' %(vmId))
                    return True
                else:
                    logging.info('Stop instance %s failed!' %(vmId))
                    return False
            elif status[0].instances[0].state == 'stopped' or status[0].instances[0].state == 'stopping':
                logging.info('This instance %s is already stopped.' % (vmId))
                return True
            else:
                logging.info('The state of the instance %s is not right, stop failed!' %(vmId))
                return False
        else:
            logging.info('The instance %s not exist!' %(vmId))
            return False

    def terminateInstance(self, vmId):
        try:
            status = self.conn.get_all_reservations(instance_ids=[vmId])
        except Exception as e:     
            logging.error(e)
            #print e
            sys.exit(1)
        if status:
            logging.info(status[0].instances[0].id)
            logging.info(status[0].instances[0].state)
            if status[0].instances[0].state != 'terminated':
                if self.conn.terminate_instances(instance_ids=[vmId]):
                    logging.info('Ternimated instance %s success!' %(vmId))
                    return True
                else:
                    logging.info('Ternimated instance %s failed!' %(vmId))
                    return False
            else:
                logging.info('This instance %s is already terminated.' % (vmId))
                return True
        else:
            logging.info('The instance %s not exist!' %(vmId))
            return False

    def startInstance(self, vmId):
        try:
            status = self.conn.get_all_reservations(instance_ids=[vmId])
        except Exception as e:     
            logging.error(e)
            #print e
            sys.exit(1)
        if status:
            logging.info(status[0].instances[0].id)
            logging.info(status[0].instances[0].state)
            if status[0].instances[0].state == 'running' or status[0].instances[0].state == 'pending':
                    logging.info('Instance %s is already running!' %(vmId))
                    return True
            elif status[0].instances[0].state == 'stopped':
                if self.conn.start_instances(instance_ids=[vmId]):
                    logging.info('Running instance %s success.' % (vmId))
                    return True
                else:
                    logging.info('Runing intance %s failed.' % (vmId))
                    return False
            elif status[0].instances[0].state == 'stopping':
                    time.sleep(2)
                    self.startInstance(vmId)
            else:
                logging.info('The state of the instance %s is not right, run failed!' %(vmId))
                return False
        else:
            logging.info('The instance %s not exist!' %(vmId))
            return False

    #initialize 
    def getAllInstance(self, vmlist):
        res = self.conn.get_all_reservations()
        #exception_set = ['i-7ccd328b', 'i-a8cd325f', 'i-b812d44f', 'i-e6ec2a11']
        for r in res:
            logging.info(r.instances[0].state)
            logging.info(r.instances[0].id)
            logging.info(r.instances[0].ip_address)
            logging.info(r.instances[0].private_ip_address) 
            if r.instances[0].id not in exception_set:
                if r.instances[0].state == 'running' or r.instances[0].state == 'pending':
                    vm = VM(r.instances[0].id, 1)
                    vm.vflag = True
                    vmlist.addVm(vm)
                elif r.instances[0].state == 'stopped' or r.instances[0].state == 'stopping':
                    vm = VM(r.instances[0].id, 1)
                    vm.vflag = False
                    vmlist.stopVM(vm)
    
    def getInstanceId(self, ifname):
        res = self.conn.get_all_reservations()
        for r in res:
            logging.info(r.instances[0].id)
            logging.info(r.instances[0].ip_address)
            logging.info(r.instances[0].private_ip_address) 
            if r.instances[0].private_ip_address == self.get_local_ip(ifname):
                return r.instances[0].id
    
    def get_local_ip(self, ifname): 
        import socket, fcntl, struct 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15])) 
        ret = socket.inet_ntoa(inet[20:24]) 
        return ret 

    def checkStatus(self, vId):
        try:
            res = self.conn.get_all_reservations(instance_ids=[vId])
        except Exception as e:
            logging.error(e)
            #print e
            sys.exit(1)
        if res:
            logging.info(res[0].instances[0].id)
            logging.info(res[0].instances[0].state)
            if res[0].instances[0].state == 'running':
                logging.info('Instance %s is already running!' %(vId))
                s = self.conn.get_all_instance_status(instance_ids=[vId])
                #print s[0].id
                #print s[0].state_name
                logging.info(s[0].instance_status.details['reachability'])
                #print s[0].events
                if s[0].instance_status.details['reachability'] == 'passed':
                    logging.info('Instance %s is ready to run task!' %(vId))
                    return 'passed'
                else:
                    logging.info('Instance %s is now initializing!' %(vId))
                    return 'initializing'
            elif res[0].instances[0].state == 'stopped' or res[0].instances[0].state == 'stopping':
                logging.info('Instance %s is now stopped.' % (vId))
                return 'stopped'
        else:
            logging.info('The instance %s not exist!' %(vId))
            return ''

#for test
if __name__ == '__main__':
    init_log(logging.DEBUG)
    api = RHAPI()
    api.checkStatus('i-7db40a8a')
