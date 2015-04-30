#!/home/jyyl/env/snmp/bin/python3

import logging
from sh import snmpwalk


class collect():

    """Collect snmp port infomation"""

    data_list = []

    def __init__(self, ip_addr='localhost', community='public', udp_port=161):
        self.ip_addr = ip_addr
        self.community = community
        self.udp_port = udp_port

    def getSnmpInfo(self, mib_arg):
        oid_args = self.generateOID(mib_arg)

        try:
            snmp_res = snmpwalk('-Os', '-OQ', '-v2c', '-c', self.community, self.ip_addr, oid_args)
        except:
            logging.error("ERROR! Cannot get snmp info with ip: %s community: %s oid: %s" % (self.ip_addr, self.community, oid_args))
            return None

        if snmp_res is not None:
            snmp_res = snmp_res.rstrip('\n')
            # snmpget value is single line
            if 'index' in mib_arg:
                return [snmp_res]
            # snmpwalk value is list
            else:
                return snmp_res.split('\n')

        return None

    def generateOID(self, arg_table):
        if ('mib' not in arg_table) or ('key' not in arg_table):
            logging.error('ERROR: Parse oid error!')
            return None

        oid_args = ""
        oid_args = arg_table['mib'] + '::' + arg_table['key']

        if 'index' in arg_table:
            oid_args += '.' + str(arg_table['index'])

        return oid_args

    def bind_snmp_data(self, mib_arg, res_data_list):
        if res_data_list is None:
            return False

        # Check self.data_list empty or not
        if len(self.data_list) == 0:
            # Init self.port
            for data_line in res_data_list:
                try:
                    res_data = self.parseSnmpValue(mib_arg, data_line)['data']
                    self.data_list.append(res_data)
                except:
                    logging.error("Update port list error")
                    return False

            return True

        else:
            if len(res_data_list) != len(self.data_list):
                print(res_data_list)
                print(self.data_list)
                logging.error("Data length is not same")
                return False

            for line_no in range(len(self.data_list)):
                try:
                    res_data = self.parseSnmpValue(mib_arg, res_data_list[line_no])['data']
                    self.data_list[line_no].update(res_data)
                except:
                    print(self.parseSnmpValue(mib_arg, res_data_list[line_no]))
                    logging.error("Update port list error")
                    return False

            return True

    def parseSnmpValue(self, mib_arg, data_line):

        if data_line is None:
            return None

        try:
            name, value = data_line.split(' = ')
        except:
            logging.error("Cannot parse snmp data %s" % data_line)
            return None

        try:
            key, index = name.split(".")
        except:
            logging.error("Cannot parse snmp data index %s" % data_line)
            return None

        if 'key' in mib_arg and mib_arg['key'] != key:
            logging.error("key is not same %s" % data_line)
            return None

        if 'index' in mib_arg and int(mib_arg['index']) != int(index):
            logging.error("index is not same %s" % data_line)
            return None

        return {'key': key, 'index': int(index), 'data': {key: value}}

    def run(self, mib_arg_list, type='snmpwalk'):

        self.data_list = []

        for mib_arg in mib_arg_list:
            snmp_res = self.getSnmpInfo(mib_arg)

            # validate every mib value read correct
            if self.bind_snmp_data(mib_arg, snmp_res) is False:
                return None

        logging.info("Collect IP: %s for %s items" %
                (self.ip_addr, str(len(self.data_list))))

        return self.data_list


def _testunit():
    logging.basicConfig(level=logging.WARN)
    # community = 'luquanne40e12!@'
    # ip_addr = '110.249.211.254'

    ip_addr = '61.182.128.1'
    community = 'IDCHBPTT2o'

    mib_arg_list = [
        {'mib': 'IF-MIB', 'key': 'ifIndex'},
        {'mib': 'IF-MIB', 'key': 'ifDescr'},
        {'mib': 'IF-MIB', 'key': 'ifHCInOctets'},
        {'mib': 'IF-MIB', 'key': 'ifHCOutOctets'},
    ]
    snmpobj = collect(ip_addr, community)
    table = snmpobj.run(mib_arg_list)
    print(table)

    mib_arg_list = [
        {'mib': 'IF-MIB', 'key': 'ifIndex', 'index': 55},
        {'mib': 'IF-MIB', 'key': 'ifDescr', 'index': 55},
        {'mib': 'IF-MIB', 'key': 'ifHCInOctets', 'index': 55},
        {'mib': 'IF-MIB', 'key': 'ifHCOutOctets', 'index': 55},
    ]
    table = snmpobj.run(mib_arg_list)
    print(table)

    mib_arg_list = [
        {'mib': 'SNMPv2-MIB', 'key': 'sysName', 'index': 0},
        {'mib': 'SNMPv2-MIB', 'key': 'sysDescr', 'index': 0},
        {'mib': 'SNMPv2-MIB', 'key': 'sysLocation', 'index': 0},
        {'mib': 'SNMPv2-MIB', 'key': 'sysContact', 'index': 0},
    ]
    table = snmpobj.run(mib_arg_list)
    print(table)

if __name__ == '__main__':
    _testunit()
