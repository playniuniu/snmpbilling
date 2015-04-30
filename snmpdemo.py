#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8
from pysnmp.entity.rfc3413.oneliner import cmdgen

cmdGen = cmdgen.CommandGenerator()

errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.nextCmd(
    cmdgen.CommunityData('luquanne40e12!@'),
    cmdgen.UdpTransportTarget(('110.249.211.254', 161)),
    # cmdgen.MibVariable('IF-MIB', ''),
    cmdgen.MibVariable('SNMPv2-MIB', ''),
    lookupValues=True,
    lookupNames=True,
)

if errorIndication:
    print(errorIndication)
else:
    if errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBindTable[-1][int(errorIndex) - 1] or '?'))
    else:
        for varBindTableRow in varBindTable:
            for name, val in varBindTableRow:
                print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
