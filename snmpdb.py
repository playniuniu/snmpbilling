#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8

import pymongo
import logging
from datetime import date
from time import time


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
            current_date = date.today().strftime("%Y%m%d")
            key_value = '-'.join([current_date, row['ifDescr']])
            key = {'key': key_value}

            basedata = {"$set": {'date': current_date, 'ifIndex': row['ifIndex'], 'ifDescr': row['ifDescr']}}
            ifInOctets = {"$push": {"ifInOctets": row['ifInOctets']}}
            ifOutOctets = {"$push": {"ifOutOctets": row['ifOutOctets']}}
            timedata = {"$push": {"timestamp": int(timestamp)}}

            try:
                self.conn.update(key, basedata, upsert=True)
                self.conn.update(key, ifInOctets, upsert=True)
                self.conn.update(key, ifOutOctets, upsert=True)
                self.conn.update(key, timedata, upsert=True)
                items += 1
            except:
                logging.error("Could not insert data %s" % row['key'])

        logging.info("Insert into %s:%s with %s/%s items" %
            (self.dbName, self.clName, str(items), str(len(snmptable))))


def _testunit():
    from collect import collect
    from datetime import date
    logging.basicConfig(level=logging.INFO)

    community = 'luquanne40e12!@'
    ip_addr = '110.249.211.254'
    dev_name = 's9312_254'
    user = 'sjz'
    current_month = date.today().strftime("%Y%m")

    mib_arg_list = [
        {'mib': 'IF-MIB', 'key': 'ifIndex'},
        {'mib': 'IF-MIB', 'key': 'ifDescr'},
        {'mib': 'IF-MIB', 'key': 'ifInOctets'},
        {'mib': 'IF-MIB', 'key': 'ifOutOctets'},
    ]

    snmpobj = collect(ip_addr, community)
    snmp_data = snmpobj.run(mib_arg_list)

    collections_name = '-'.join([current_month, dev_name ])

    snmp_database = snmpdb('110.249.213.18')
    snmp_database.useCollections('billing_' + user, collections_name)
    snmp_database.writeSnmpData(snmp_data, time())


if __name__ == '__main__':
    _testunit()
