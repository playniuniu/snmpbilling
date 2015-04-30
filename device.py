#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8

import pymongo
import logging
from time import time
from collect import collect
import snmpConfig


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

    def getDeviceInfo(self, ip_addr, community, udp_port=161):

        snmpobj = collect(ip_addr, community, udp_port)
        device_info = snmpobj.run(self.deviceInfoMIB, 'snmpget')

        if device_info is None:
            logging.error("ERROR! Get device snmp from %s:%s with %s error!"
                      % (ip_addr, udp_port, community))
            return False

        else:
            self.snmpobj = snmpobj
            self.device_ip = ip_addr
            self.community = community
            self.udp_port = udp_port
            self.device_info = self.parseDeviceInfo(device_info)

            logging.info("Get device snmp ip %s sys name %s "
                      % (ip_addr, self.device_info['sysName']))

            return True

    def parseDeviceInfo(self, snmp_device_info):
        device_info = {}
        for item in snmp_device_info:
            device_info.update(item)
        return device_info

    def getPortInfo(self):
        self.port_info = self.snmpobj.run(self.devicePortMIB)

        logging.info("Get device snmp ip %s port %s "
                  % (self.device_ip, len(self.port_info)))

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

    def writeDeviceData(self, dbName, key, owner):

        self.useCollections(dbName, 'devices')

        device_info = {
            'sys_name': self.device_info['sysName'],
            'sys_descr': self.device_info['sysDescr'],
            'ip': self.device_ip,
            'community': self.community,
            'port': self.udp_port,
            'owner': owner,
            'update_time': time(),
        }

        write_data = {"$set": device_info}

        try:
            self.conn.update(key, write_data, upsert=True)
        except:
            logging.error("Could not insert device name: %s ip: %s"
                          % (self.device_info['sysName'], self.device_ip))

    def writePortData(self, dbName, key, owner):

        self.useCollections(dbName, 'ports')

        port_info = {
            'sys_name': self.device_info['sysName'],
            'ip': self.device_ip,
            'port_list': self.port_info,
        }

        write_data = {"$set": port_info}

        try:
            self.conn.update(key, write_data, upsert=True)
        except:
            logging.error("Could not insert port info name: %s ip: %s"
                          % (self.device_info['sysName'], self.device_ip))

    def writeSnmpData(self, dbName, dev_name, owner):
        self.getPortInfo()
        key = {'dev_name': dev_name}
        self.writeDeviceData(dbName, key, owner)
        self.writePortData(dbName, key, owner)


def _testunit():
    logging.basicConfig(level=logging.INFO)

    snmp_device = snmpDevice()

    for device in snmpConfig.snmp_list:

        community = device['community']
        ip_addr = device['ip_addr']
        user = device['user']
        dev_name = device['dev_name']

        if snmp_device.getDeviceInfo(ip_addr, community):

            for database in snmpConfig.database_list:
                database_address = database['ip']
                snmp_device.connDB(database_address)
                database_name = snmpConfig.database_prefix + user
                snmp_device.writeSnmpData(database_name, dev_name, user)


if __name__ == '__main__':
    _testunit()
