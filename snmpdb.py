#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8

import pymongo
import logging
import time

class snmpdb():

    def __init__(self, ip_addr='127.0.0.1', port=27017):

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

    def writeSnmpData(self, snmptable, timestamp):
        items = 0

        for row in snmptable:
            current_date = time.strftime("%Y%m%d")
            key_value = '-'.join([current_date, row['ifIndex']])
            key = {'key': key_value}

            dataOperation = {
                "$set": {'date': current_date, 'ifIndex': row['ifIndex'], 'ifDescr': row['ifDescr']},
                "$push": {"ifHCInOctets": row['ifHCInOctets'], "ifHCOutOctets": row['ifHCOutOctets'], "timestamp": int(timestamp)}
            }

            try:
                self.conn.update(key, dataOperation, upsert=True)
                items += 1
            except:
                logging.error("Could not insert data %s" % row['key'])

        logging.info("Insert into %s:%s with %s/%s items" %
            (self.dbName, self.clName, str(items), str(len(snmptable))))


def _testunit():
    from collect import collect
    logging.basicConfig(level=logging.INFO)

    snmp_ip = '61.182.128.1'
    snmp_community = 'IDCHBPTT2o'
    dev_id = 'test'
    database_name = 'idc_billing'
    current_month = time.strftime("%Y%m")

    mib_arg_list = [
        {'mib': 'IF-MIB', 'key': 'ifIndex'},
        {'mib': 'IF-MIB', 'key': 'ifDescr'},
        {'mib': 'IF-MIB', 'key': 'ifHCInOctets'},
        {'mib': 'IF-MIB', 'key': 'ifHCOutOctets'},
    ]

    snmpobj = collect(snmp_ip, snmp_community)
    snmp_data = snmpobj.run(mib_arg_list)

    collections_name = '_'.join(['bill', dev_id, current_month])

    snmp_database = snmpdb('110.249.213.22')
    snmp_database.useCollections(database_name, collections_name)
    snmp_database.writeSnmpData(snmp_data, time.time())


if __name__ == '__main__':
    _testunit()
