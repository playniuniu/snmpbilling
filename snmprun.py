#!/home/jyyl/env/snmp/bin/python3
# coding:utf-8

from multiprocessing import Pool
import os
import sys
import logging
import time

from collect import collect
from snmpdb import snmpdb
from datetime import date
from baseDaemon import baseDaemon
import snmpConfig


class snmpDaemon(baseDaemon):

    def __init__(self, pid_file='/tmp/snmprun.pid', pool_max=10):
        baseDaemon.__init__(self, pid_file)
        self.pool_max = pool_max
        self.snmp_list = []

    def snmprun_process(self, args):

        snmpobj = collect(args['dev_name'], args['ip_addr'], args['community'])
        snmp_data = snmpobj.run()

        snmp_database = snmpdb()
        snmp_database.useCollections(args['db_name'], args['table_name'])
        snmp_database.writeSnmpData(snmp_data)

        logging.debug("Process dev: %s ip: %s pid: %s complete" %
            (args['dev_name'], args['ip_addr'], str(os.getpid())))

    def snmp_queen(self, args):

        if os.getppid() != self.parent_pid:
            exit(1)

        queen_task = args
        queen_task['db_name'] = snmpConfig.mongodb_name
        current_month = date.today().strftime("%Y%m")
        queen_task['table_name'] = snmpConfig.mongodb_name + '_' + current_month

        logging.debug("start process dev:{} ip:{}"
            .format(queen_task['dev_name'], queen_task['ip_addr']))

        self.snmprun_process(queen_task)

    def snmp_runprocess1(self, task):
        print('Run task %s: %s' % (os.getpid(), task['dev_name']))
        start = time.time()
        time.sleep(10)
        end = time.time()
        print('Task %s runs %0.2f seconds.' % (os.getpid(), (end - start)))

    def run(self):
        self.parent_pid = os.getpid()
        snmp_interval = snmpConfig.snmp_interval

        with Pool() as pool:

            while True:
                self.snmp_list.extend(snmpConfig.snmp_list)

                while len(self.snmp_list) > 0:
                    task_args = self.snmp_list.pop()
                    pool.apply_async(self.snmp_queen, args=(task_args, ))

                time.sleep(snmp_interval)


def main():
    logging.basicConfig(format='%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S', level=logging.DEBUG)

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
            print ("Usage: {} start|stop|restart|status".format(sys.argv[0]))
            sys.exit(2)
        sys.exit(0)
    else:
        print ("Usage: {} start|stop|restart|status".format(sys.argv[0]))
        sys.exit(2)


if __name__ == '__main__':
    main()
