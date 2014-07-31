#!/home/jyyl/env/snmp/bin/python3
# coding: utf-8

import pymongo
import logging


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

    def writeSnmpData(self, snmptable):
        items = 0

        for row in snmptable:
            key = {'key': row['key']}
            basedata = {"$set": {'ip_addr': row['ip_addr'], 'date': row['date'], 'ifIndex': row['ifIndex']}}
            ifInOctets = {"$push": {"ifInOctets": row['ifInOctets']}}
            ifOutOctets = {"$push": {"ifOutOctets": row['ifOutOctets']}}

            try:
                self.conn.update(key, basedata, upsert=True)
                self.conn.update(key, ifInOctets, upsert=True)
                self.conn.update(key, ifOutOctets, upsert=True)
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
    name = 's9312-254'
    current_month = date.today().strftime("%Y%m")

    snmpobj = collect(name, ip_addr, community)
    snmp_data = snmpobj.run()

    db_name = 'billing'
    collections_name = 'billing_' + current_month

    snmp_database = snmpdb()
    snmp_database.useCollections(db_name, collections_name)
    snmp_database.writeSnmpData(snmp_data)


if __name__ == '__main__':
    _testunit()
