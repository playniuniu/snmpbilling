#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8

snmp_list = [
    {'dev_name': 'ne40e-232', 'ip_addr': '221.192.23.232', 'community': 'luquanne40e12!@', 'user': 'sjz'},
    {'dev_name': 'ne40e-233', 'ip_addr': '221.192.23.233', 'community': 'luquanne40e12!@', 'user': 'sjz'},
    {'dev_name': 's9312-253', 'ip_addr': '110.249.211.253', 'community': 'luquanne4012!@', 'user': 'sjz'},
    {'dev_name': 's9312-254', 'ip_addr': '110.249.211.254', 'community': 'luquanne40e12!@', 'user': 'sjz'},
    {'dev_name': 'esn-1', 'ip_addr': '61.182.128.1', 'community': 'IDCHBPTT2o', 'user': 'sjz'},
    # {'dev_name': 'esn-1', 'ip_addr': '61.182.128.1', 'community': 'IDCHB&)!*-1SNMPro', 'user': 'sjz'},
    # {'dev_name': 'esn-2', 'ip_addr': '61.182.128.2', 'community': 'IDCHB&)!*-2SNMPro', 'user': 'sjz'},
]

snmp_mib = [
    {'mib': 'IF-MIB', 'key': 'ifIndex'},
    {'mib': 'IF-MIB', 'key': 'ifDescr'},
    {'mib': 'IF-MIB', 'key': 'ifHCInOctets'},
    {'mib': 'IF-MIB', 'key': 'ifHCOutOctets'},
]

snmp_interval = 300

database_prefix = "billing_"

database_list = [
    {'ip': '110.249.213.18', },
    # {'ip': '110.249.213.20',},
]
