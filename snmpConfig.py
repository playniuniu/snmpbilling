#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8
snmp_mib = [
    {'mib': 'IF-MIB', 'key': 'ifIndex'},
    {'mib': 'IF-MIB', 'key': 'ifDescr'},
    {'mib': 'IF-MIB', 'key': 'ifHCInOctets'},
    {'mib': 'IF-MIB', 'key': 'ifHCOutOctets'},
]

snmp_interval = 300

mongo_db_common = "idc_common"
mongo_db_billing = "idc_billing"

mongo_db_list = [
    {'ip':'110.249.213.22','port':27017},
]
