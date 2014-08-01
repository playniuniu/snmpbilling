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

    def getSnmpInfo(self, mib_args, snmp_type='snmpwalk'):
        self.cmdGenerator = cmdgen.CommandGenerator()

        if snmp_type == 'snmpwalk':
            errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGenerator.nextCmd(
                cmdgen.CommunityData(self.community),
                cmdgen.UdpTransportTarget((self.ip_addr, self.udp_port)),
                *mib_args
            )

        elif snmp_type == 'snmpget':
            errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGenerator.getCmd(
                cmdgen.CommunityData(self.community),
                cmdgen.UdpTransportTarget((self.ip_addr, self.udp_port)),
                mib_args,
                # lookupValues=True,
                # lookupNames=True
            )

        else:
            logging.error("ERROR! Wrong type: %s" % snmp_type)
            return None

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

    def run(self, args, snmp_type='snmpwalk'):

        mib_args = self.generateMibVariable(args, snmp_type)
        varBindTable = self.getSnmpInfo(mib_args, snmp_type)

        if varBindTable is None:
            return None
        else:
            # Important! clear collect_list
            self.collect_list = []

            self.parseBindTable(varBindTable, snmp_type)
            collect_items = str(len(self.collect_list))
            logging.info("Collect %s ip: %s for %s items" %
                (self.name, self.ip_addr, collect_items))
            return self.collect_list

    def parseBindTable(self, varBindTable, snmp_type):

        for varBindTableRow in varBindTable:
            oid_dict = {}

            # made snmpget value same as list
            if snmp_type == 'snmpget':
                varBindTableRow = [varBindTableRow, ]

            for (oid, val) in varBindTableRow:
                oid_name, oid_value = self.parseOid(oid, val)
                oid_dict[oid_name] = oid_value

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

    def generateMibVariable(self, mib_args, snmp_type='snmpwalk'):
        if snmp_type == "snmpwalk":
            mib_args_list = []
            for row in mib_args:
                mib_args_list.append(
                    cmdgen.MibVariable(row['mib'], row['key']))
            return mib_args_list

        if snmp_type == "snmpget":
            return cmdgen.MibVariable(mib_args['mib'], mib_args['key'], int(mib_args['index']))


def _testunit():
    logging.basicConfig(level=logging.INFO)
    community = 'luquanne40e12!@'
    ip_addr = '110.249.211.254'
    name = 's9312-254'

    mib_arg_list = [
        {'mib': 'IF-MIB', 'key': 'ifIndex'},
        {'mib': 'IF-MIB', 'key': 'ifDescr'},
        {'mib': 'IF-MIB', 'key': 'ifInOctets'},
        {'mib': 'IF-MIB', 'key': 'ifOutOctets'},
    ]
    snmpobj = collect(name, ip_addr, community)
    table = snmpobj.run(mib_arg_list)
    print(table)

    mib_arg = {'mib': 'IF-MIB', 'key': 'ifDescr', 'index': 20}
    table = snmpobj.run(mib_arg, 'snmpget')
    print(table)

if __name__ == '__main__':
    _testunit()
