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

    def __init__(self, pid_file='/tmp/' + sys.argv[0] + '.pid'):
        baseDaemon.__init__(self, pid_file)
        self.snmp_list = []
        self.debug_mode = False

    def snmprun_process(self, args):

        snmpobj = collect(args['ip_addr'], args['community'])
        snmp_data = snmpobj.run(snmpConfig.snmp_mib)

        current_time = time.time()

        # write multiple database for backup
        for database in snmpConfig.database_list:
            try:
                ip_address = database['ip']
                snmp_database = snmpdb(ip_address)
                snmp_database.useCollections(args['db_name'], args['table_name'])
                snmp_database.writeSnmpData(snmp_data, current_time)
            except:
                logging.error("Write to database %s error" % ip_address)

        logging.debug("Process dev: %s ip: %s pid: %s complete" %
            (args['dev_name'], args['ip_addr'], str(os.getpid())))

    def snmp_queen(self, args):

        if not self.debug_mode:
            # Terminate subprocess if main process is stoped
            if os.getppid() != self.parent_pid:
                logging.info("Pid: {} terminated by parent process!".format(os.getpid()))
                exit(1)

        queen_task = args
        queen_task['db_name'] = snmpConfig.database_prefix + queen_task['user']
        current_month = date.today().strftime("%Y%m")
        queen_task['table_name'] = current_month + '_' + queen_task['dev_name']

        logging.debug("start process dev:{} ip:{}"
            .format(queen_task['dev_name'], queen_task['ip_addr']))

        self.snmprun_process(queen_task)

    def demo_queen(self, task):
        logging.debug('Run task %s: %s' % (os.getpid(), task['dev_name']))
        start = time.time()
        time.sleep(5)
        end = time.time()
        logging.debug('Task %s runs %0.2f seconds.' % (os.getpid(), (end - start)))

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


def _testunit():
    args = {'dev_name': 'ne40e-232', 'ip_addr': '221.192.23.232',
            'community': 'luquanne40e12!@', 'user': 'sjz'}
    testDemon = snmpDaemon()
    testDemon.debug_mode = True
    testDemon.snmp_queen(args)


def main():
    logging.basicConfig(format='%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S', level=logging.DEBUG, filename='/tmp/snmprun.log')

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
