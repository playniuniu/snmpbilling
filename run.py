#!/home/jyyl/env/snmp/bin/python3
# coding:utf-8

from multiprocessing import Pool
import os
import sys
import logging
import time
import pymongo

from collect import collect
from snmpdb import snmpdb
from baseDaemon import baseDaemon
import snmpConfig


class snmpDaemon(baseDaemon):

    def __init__(self, pid_file='/tmp/snmpbilling.pid'):
        baseDaemon.__init__(self, pid_file)
        self.snmp_list = []
        self.debug_mode = False
    
    # snmp 的读取和写入进程
    def snmprun_process(self, args):
        snmpobj = collect(args['snmp_ip'], args['snmp_community'])
        snmp_data = snmpobj.run(snmpConfig.snmp_mib)

        current_time = time.time()

        # write multiple database for backup
        for database in snmpConfig.mongo_db_list:
            try:
                mongo_db_ip = database['ip']
                mongo_db_port = database['port']
                snmp_database = snmpdb(mongo_db_ip, mongo_db_port)
                snmp_database.useCollections(args['db_name'], args['table_name'])
                snmp_database.writeSnmpData(snmp_data, current_time)
            except:
                logging.error("Write to database %s error" % ip_address)

        logging.debug("Process dev: %s ip: %s pid: %s complete" %
            (args['dev_id'], args['snmp_ip'], str(os.getpid())))

    # snmp 进程队列
    def snmp_queen(self, args):
        if not self.debug_mode:
            # Terminate subprocess if main process is stoped
            if os.getppid() != self.parent_pid:
                logging.info("Pid: {} terminated by parent process!".format(os.getpid()))
                exit(1)

        queen_task = args
        queen_task['db_name'] = snmpConfig.mongo_db_billing
        current_month = time.strftime("%Y%m")
        queen_task['dev_id'] = str(queen_task['_id'])
        queen_task['table_name'] = 'bill' + '_' + queen_task['dev_id'] + '_' + current_month

        logging.debug("start process dev:{} ip:{}"
            .format(queen_task['dev_id'], queen_task['snmp_ip']))

        self.snmprun_process(queen_task)
    
    # 取得数据库的所有信息
    def get_device_list(self):
        try:
            mainDB = snmpConfig.mongo_db_list[0]
            mongoClient = pymongo.MongoClient(mainDB['ip'], mainDB['port'])
            mongoDatabase = mongoClient[snmpConfig.mongo_db_common]
            mongoCollection = mongoDatabase['devices']
            device_list = mongoCollection.find({})
        except:
            logging.error("Could not connect to database %s:%s" %
                (mongoDatabase, mongoCollection))
            return None

        return list(device_list)

    # 主进程
    def run(self):
        self.parent_pid = os.getpid()
        snmp_interval = snmpConfig.snmp_interval

        with Pool() as pool:
            while True:
                self.snmp_list.extend(self.get_device_list())

                while len(self.snmp_list) > 0:
                    task_args = self.snmp_list.pop()
                    pool.apply_async(self.snmp_queen, args=(task_args, ))

                time.sleep(snmp_interval)


def _testunit():
    logging.basicConfig(format='%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S', level=logging.DEBUG, filename='/tmp/snmpbilling.log')

    testDaemon = snmpDaemon()
    testDaemon.debug_mode = True
    device_list = testDaemon.get_device_list()
    print("get device test: ")
    print(str(device_list))
    print("write data test: ")
    testDaemon.snmp_queen(device_list[0])

def main():
    logging.basicConfig(format='%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S', level=logging.DEBUG, filename='/tmp/snmpbilling.log')

    snmp_daemon = snmpDaemon()

    if len(sys.argv) == 2:
        logging.info('{} {}'.format(sys.argv[0], sys.argv[1]))

        if 'start' == sys.argv[1]:
            snmp_daemon.start()
        elif 'stop' == sys.argv[1]:
            snmp_daemon.stop()
        elif 'restart' == sys.argv[1]:
            snmp_daemon.restart()
        elif 'status' == sys.argv[1]:
            snmp_daemon.status()
        else:
            print("Usage: {} start|stop|restart|status".format(sys.argv[0]))
            sys.exit(2)
        sys.exit(0)
    else:
        print("Usage: {} start|stop|restart|status".format(sys.argv[0]))
        sys.exit(2)


if __name__ == '__main__':
    # _testunit()
    main()
