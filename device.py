#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8

import pymongo
import logging
from time import time
from collect import collect

class snmpDevice():

    deviceInfoMIB = [
        {'mib': 'SNMPv2-MIB', 'key': 'sysName', 'index': 0},
        {'mib': 'SNMPv2-MIB', 'key': 'sysDescr', 'index': 0},
        {'mib': 'SNMPv2-MIB', 'key': 'sysLocation', 'index': 0},
        {'mib': 'SNMPv2-MIB', 'key': 'sysContact', 'index': 0},
    ]

    devicePortMIB = [
        {'mib': 'IF-MIB', 'key': 'ifIndex'},
        {'mib': 'IF-MIB', 'key': 'ifDescr'},
        {'mib': 'IF-MIB', 'key': 'ifType'},
        {'mib': 'IF-MIB', 'key': 'ifSpeed'},
    ]

    def __init__(self):
        pass

    def getDeviceInfo(self, snmp_ip, snmp_community, udp_port=161):

        snmpobj = collect(snmp_ip, snmp_community, udp_port)
        device_info = snmpobj.run(self.deviceInfoMIB, 'snmpget')

        if device_info is None:
            logging.error("ERROR! Get device snmp from %s:%s with %s error!"
                      % (snmp_ip, udp_port, snmp_community))
            return False

        else:
            self.snmpobj = snmpobj
            self.snmp_ip = snmp_ip
            self.snmp_community = snmp_community
            self.udp_port = udp_port
            self.device_info = self.parseDeviceInfo(device_info)

            logging.info("Get device snmp ip %s sys name %s "
                      % (snmp_ip, self.device_info['sysName']))

            return True

    def parseDeviceInfo(self, snmp_device_info):
        device_info = {}
        for item in snmp_device_info:
            device_info.update(item)
        return device_info

    def getPortInfo(self):
        port_info = self.snmpobj.run(self.devicePortMIB)
        
        if port_info is None:
            logging.error("ERROR! Get device port from %s:%s with %s error!"
                      % (self.snmp_ip, self.udp_port, self.snmp_community))
            return False
        
        self.port_info = port_info
        logging.info("Get device snmp ip %s port %s "
                  % (self.snmp_ip, len(self.port_info)))
        return True

    def connDB(self, ip_addr='127.0.0.1', port=27017):

        try:
            self.mongoClient = pymongo.MongoClient(ip_addr, port)
        except pymongo.errors.ConnectionFailure as e:
            logging.error("Could not connect to MongoDB %s:%s because %s" %
                (ip_addr, str(port), e))
            exit(1)

    def useCollections(self, dbName, collections):

        try:
            self.db = self.mongoClient[dbName]
            self.conn = self.db[collections]
        except:
            logging.error("Could not connect to database %s:%s" %
                (dbName, collections))
            exit(1)

        self.dbName = dbName
        self.clName = collections

    def writeDeviceData(self, dbName, args):

        self.useCollections(dbName, 'devices')

        device_info = {
            'sys_name': self.device_info['sysName'],
            'sys_desc': self.device_info['sysDescr'],
            'snmp_ip': self.snmp_ip,
            'snmp_community': self.snmp_community,
            'snmp_port': self.udp_port,
            'dev_owner': args['dev_owner'],
            'dev_group': args['dev_group'],
            'update_time': int(time()),
        }

        write_data = {"$set": device_info}
        key = {'snmp_ip': self.snmp_ip, 'snmp_community': self.snmp_community, 'dev_owner': args['dev_owner']}

        try:
            self.conn.update_one(key, write_data, upsert=True)
        except:
            logging.error("Could not insert device name: %s ip: %s"
                          % (self.device_info['sysName'], self.snmp_ip))

    def writePortData(self, dbName, args):
        dev_id = ''
        
        # 查找相应的 Device
        self.useCollections(dbName, 'devices')
        try:
            device_key = {'snmp_ip': self.snmp_ip, 'snmp_community': self.snmp_community, 'dev_owner': args['dev_owner']}
            device_info = self.conn.find_one(device_key)
            dev_id = str(device_info['_id'])
        except:
            logging.error("Could not find device ip: %s" % (self.snmp_ip))
            return False
        
        # 插入端口数据
        self.useCollections(dbName, 'ports')
        port_info = {
            'port_list': self.port_info,
        }
        write_data = {"$set": port_info}
        
        try:
            self.conn.update_one({'dev_id': dev_id}, write_data, upsert=True)
        except:
            logging.error("Could not insert port info name: %s ip: %s"
                          % (self.device_info['sysName'], self.snmp_ip))

    def writeSnmpData(self, dbName, args):
        if self.getPortInfo():
            self.writeDeviceData(dbName, args)
            self.writePortData(dbName, args)

def _testunit():
    logging.basicConfig(level=logging.INFO)

    database_ip = '110.249.213.22'
    database_name = 'idc_common'
    snmp_list = [
        {'snmp_ip': '61.182.128.1', 'snmp_community': 'IDCHBPTT2o', 'dev_owner': 'esn', 'dev_group': 'hb'},
        {'snmp_ip': '221.192.23.232', 'snmp_community': 'luquanne40e12!@', 'dev_owner': 'js', 'dev_group': 'sjz'},
        {'snmp_ip': '221.192.23.233', 'snmp_community': 'luquanne40e12!@', 'dev_owner': 'js', 'dev_group': 'sjz'},
        {'snmp_ip': '110.249.211.253', 'snmp_community': 'luquanne40e12!@', 'dev_owner': 'js', 'dev_group': 'sjz'},
        {'snmp_ip': '110.249.211.254', 'snmp_community': 'luquanne40e12!@', 'dev_owner': 'js', 'dev_group': 'sjz'},
    ]

    snmp_device = snmpDevice()

    for device in snmp_list:
        snmp_community = device['snmp_community']
        snmp_ip = device['snmp_ip']

        if snmp_device.getDeviceInfo(snmp_ip, snmp_community):
            snmp_device.connDB(database_ip)
            snmp_device.writeSnmpData(database_name, device)

if __name__ == '__main__':
    _testunit()
