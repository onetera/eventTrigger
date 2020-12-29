# :coding: utf-8

import time
import logging
import os
import sys
import signal
import argparse

import status_event

class SG_Daemon:
    def __init__(self, log_file=None):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.logger = logging.getLogger("SG_event_trigger")
        self.log_file = log_file

        if log_file:
            self.log_handler = logging.FileHandler(self.log_file)
            self.logger.addHandler(self.log_handler)

        self.__stop = False

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def main(self):
        print '@'*40
        self.logger.info("Start Singing, PID {0}".format(os.getpid()))
        print '@'*40
        while not self.__stop:
            time.sleep( 5 )
            now = time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
            print '\n',now,'\t','*'*20
            #print_logs()
            result = status_update_event(old_id )
            set_status_id( result )
            old_id = result

            #self.logger.info( status_event.main() ) 
            #self.logger.info(self.SONG_LIST[i % len(self.SONG_LIST)])
            #i += 1
            #time.sleep(5)


    def stop(self, signum, frame):
        self.__stop = True
        self.logger.info("Receive Signal {0}".format(signum))
        self.logger.info("Stop Event Trigger")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", help="pid filename", required=True)
    parser.add_argument("--log", help="log filename", default=None)
    args = parser.parse_args()

    pid = os.fork()
    if pid > 0:
        print 'pid : ', pid
        exit(0)
    else:
        os.chdir('/')
        os.setsid()
        os.umask(0)

        pid = os.fork()
        if pid > 0 :
            print 'pid : ', pid
            exit(0)
        else:
            sys.stdout.flush()
            sys.stderr.flush()

            si = open( os.devnull, 'r' )
            so = open( os.devnull, 'a+' )
            se = open( os.devnull, 'a+' )

            os.dup2( si.fileno(), sys.stdin.fileno() )
            os.dup2( so.fileno(), sys.stdout.fileno() )
            os.dup2( se.fileno(), sys.stderr.fileno() )

            with open( args.pid, "w" ) as pid_file:
                pid_file.write(str(os.getpid()))

            sg_dm = SG_Daemon(args.log)
            exit_code = sg_dm.main()
            exit( exit_code )
