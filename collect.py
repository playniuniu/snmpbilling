#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8
import logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.entity.rfc3413 import mibvar
from datetime import date


class collect():

    collect_list = []

    def __init__(self, name, ip_addr, community, udp_port=161):
        self.name = name
        self.ip_addr = ip_addr
        self.community = community
        self.udp_port = udp_port
        self.current_date = date.today().strftime("%Y%m%d")

    def getSnmpInfo(self):
        self.cmdGenerator = cmdgen.CommandGenerator()

        errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGenerator.nextCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.ip_addr, self.udp_port)),
            (('IF-MIB', 'ifIndex'),),
            (('IF-MIB', 'ifDescr'),),
            (('IF-MIB', 'ifInOctets'),),
            (('IF-MIB', 'ifOutOctets'),),
        )

        if errorIndication:
            logging.error("ERROR! Cannot connect to %s with %s" %
                (self.ip_addr, self.community))
            logging.error("ERROR! {}".format(errorIndication))
            return None

        elif errorStatus:
            logging.error("ERROR! Snmp error %s at %s" %
                (errorStatus.prettyPrint(), varBindTable[-1][int(errorIndex) - 1]))
            return None

        else:
            return varBindTable

    def run(self):
        varBindTable = self.getSnmpInfo()
        if not varBindTable:
            return None
        else:
            # Important! clear collect_list
            self.collect_list = []

            self.parseBindTable(varBindTable)
            collect_items = str(len(self.collect_list))
            logging.info("Collect %s ip: %s for %s items" %
                (self.name, self.ip_addr, collect_items))
            return self.collect_list

    def parseBindTable(self, varBindTable):
        for varBindTableRow in varBindTable:
            oid_dict = {}

            for oid, val in varBindTableRow:
                oid_name, oid_value = self.parseOid(oid, val)
                oid_dict[oid_name] = oid_value

            oid_dict = self.generateSnmpTableRow(oid_dict)
            self.collect_list.append(oid_dict)

    def parseOid(self, oid, val):
        (symName, modName), indices = mibvar.oidToMibName(
            self.cmdGenerator.mibViewController, oid
        )

        value = mibvar.cloneFromMibValue(
            self.cmdGenerator.mibViewController, modName, symName, val
        )

        # index = '.'.join(map(lambda v: v.prettyPrint(), indices))
        return symName, value.prettyPrint()

    def generateSnmpTableRow(self, oid_dict):
        key = '-'.join([self.name, oid_dict['ifDescr'], self.current_date])
        oid_dict['key'] = key
        oid_dict['name'] = self.name
        oid_dict['ip_addr'] = self.ip_addr
        oid_dict['date'] = self.current_date
        return oid_dict


def _testunit():
    logging.basicConfig(level=logging.INFO)
    community = 'luquanne40e12!@'
    ip_addr = '110.249.211.254'
    name = 's9312-254'

    snmpobj = collect(name, ip_addr, community)
    table = snmpobj.run()
    print(table)

if __name__ == '__main__':
    _testunit()
