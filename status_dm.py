# :coding: utf-8

import time
import logging
import os
import sys
import signal
import argparse

import shotgun_api3 as sa
import datetime
import time
from pprint import pprint
import threading

global result
result= []

#sg = sa.Shotgun('https://wswg.shotgunstudio.com',
#                api_key='d4f25676239bff829454edd3a5d97bac13c6d38c526367f9623286c4775ca4dd',
#                script_name = 'utils',
#                )
sg = sa.Shotgun('https://wswg1.shotgunstudio.com',
                api_key='yeIit5stwbhgyhefsawqkv&zj',
                script_name = 'eventDaemon',
                )

def get_event_log( sm,sd,em,ed ):
    _sd = datetime.datetime( 2019, sm, sd )
    _ed = datetime.datetime( 2019, em, ed )
    filters =  [
                    ['attribute_name','is','sg_status_list' ],
                    ['created_at','between',[_sd,_ed] ],
                ]
    order = [{'field_name':'id', 'direction':'desc'}]
    #fields = ['description','created_at','attribute_name','entity']
    fields = ['description','created_at','attribute_name','entity']
    #result = sg.find( 'EventLogEntry',filters,fields)
    result = sg.find( 'EventLogEntry',filters,fields, order )
    return result


def print_logs():
    result = get_event_log( 2,12,2,15 )
    temp = []
    lev2s = []
    for item in result:
        if item['attribute_name'] == 'sg_status_list':
            if item['entity'] == None:
                continue
            if item['entity']['type'] == 'Task':
                #temp.append( item )
                task = sg.find_one( 'Task',[['id','is',item['entity']['id']] ],
                                ['entity'] )
                #temp.append( task )
                lev2 = sg.find_one( 
                                    task['entity']['type'], 
                                    [['id','is',task['entity']['id']]],
                                    ['code','tasks']
                                    )
                tasks = []
                for task in lev2['tasks']:
                    task_st = sg.find_one(
                                            'Task',[['id','is',task['id']]],
                                            ['sg_status_list'] )
                    if task_st['sg_status_list'] == 'cmpt':
                        tasks.append( task_st )
                if len( lev2['tasks'] ) == len(tasks):
                    sg.update( lev2['type'],lev2['id'],{'sg_status_list':'cmpt'} )



def status_update_event( old_id=0 ):
    fields = ['description','created_at','attribute_name','entity']
    order = [{'field_name':'id', 'direction':'desc'}]
    filters =  [
                    ['attribute_name','is','sg_status_list' ],
                ]
    if old_id == 0:
        items = [sg.find_one( 'EventLogEntry',filters, fields ,order )]
    else:
        filters.append( ['id', 'greater_than' , old_id ] )
        items = sg.find( 'EventLogEntry',filters, fields ,order )
    if not items:
        filters =  [
                    ['attribute_name','is','sg_status_list' ],
                    ['project.Project.name', 'is_not', '_Pipeline' ],
                    ]
        items = sg.find_one( 'EventLogEntry',filters, fields ,order )
        return items['id']

    print '@'*50
    print '{:15}: {}'.format( 'Total Items', len( items ) )
    print '@'*50
    for item in items:
        update_txt = ''
        created = item['created_at'].strftime('%Y-%m-%d %H:%M:%S') 

        if item['entity']['type'] == 'Task':
            #temp.append( item )
            task = sg.find_one( 'Task',[['id','is',item['entity']['id']] ],
                            ['entity'] )
            #temp.append( task )
            if not task['entity']:
                continue
            lev2 = sg.find_one( 
                                task['entity']['type'], 
                                [['id','is',task['entity']['id']]],
                                ['code','tasks']
                                )
            tasks = []
            for task in lev2['tasks']:
                task_st = sg.find_one(
                                        'Task',[['id','is',task['id']]],
                                        ['sg_status_list'] )
                if task_st['sg_status_list'] == 'cmpt':
                    tasks.append( task_st )
            if len( lev2['tasks'] ) == len(tasks):
                print lev2
                #update_txt = sg.update( lev2['type'],lev2['id'],{'sg_status_list':'cmpt'} )

        if update_txt:
            print '[ updated ] : ',update_txt
            print '{:15}: {}'.format( 'created_at', created )
            print '{:15}: {}'.format( 'attribute',item['attribute_name'] ) 
            print '{:15}: {}'.format( 'description',item['description'] ) 
    return items[0]['id']
    #pprint( item )

def today_id( _date = '' ):
    fields  = ['description','created_at','attribute_name','entity','user']
    order   = [{'field_name':'id', 'direction':'desc'}]
    if _date:
        today = datetime.datetime( int(_date[:4]) , int( _date[4:6] ) , int( _date[6:] ) ) 
    else:
        today   = datetime.datetime.today()
    now     = datetime.datetime.now()
    filters =  [
                    ['created_at','between', [today, now] ],
                    ['attribute_name','is','sg_status_list' ],
                    ['project.Project.name','is_not','_Pipeline'],
                ]
    items   = [
                sg.find( 'EventLogEntry',filters, fields ,order )
              ]
    return items[0][-1]['id']

def set_status_id( _id ):
    with open( '/tmp/sg_status_id.tx' , 'w' ) as f:
        f.write( str(_id) )
    
def get_status_id( ):
    status_file = '/tmp/sg_status_id.tx'
    if not os.path.exists( status_file ):
        return False
    with open( status_file ) as f:
        result = f.read()
    return result
    

def main():
    old_id = get_status_id()
    if not old_id:
        old_id = today_id()
    
    while True:
        time.sleep( 5 )
        now = time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
        print '\n',now,'\t','*'*20
        #print_logs()
        result = status_update_event(old_id )
        set_status_id( result )
        old_id = result
        

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
        self.logger.info( '@'*40 )
        self.logger.info("Start Shotgun Event, PID {0}".format(os.getpid()))

        old_id = today_id()
        while not self.__stop:
            time.sleep( 5 )
            now = time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
            self.logger.info( '\n'+now+'\t'+'*'*20 )
            self.logger.info( old_id )
            
            #print_logs()
            result = self.status_update_event(old_id )

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

    def status_update_event( old_id=0 ):
        fields = ['description','created_at','attribute_name','entity']
        order = [{'field_name':'id', 'direction':'desc'}]
        filters =  [
                        ['attribute_name','is','sg_status_list' ],
                    ]
        if old_id == 0:
            items = [sg.find_one( 'EventLogEntry',filters, fields ,order )]
        else:
            filters.append( ['id', 'greater_than' , old_id ] )
            items = sg.find( 'EventLogEntry',filters, fields ,order )
        if not items:
            filters =  [
                        ['attribute_name','is','sg_status_list' ],
                        ['project.Project.name', 'is_not', '_Pipeline' ],
                        ]
            items = sg.find_one( 'EventLogEntry',filters, fields ,order )
            return items['id']

        self.logger.info( '@'*50 )
        self.logger.info( '{:15}: {}'.format( 'Total Items', len( items ) ) )
        self.logger.info( '@'*50 )
        for item in items:
            update_txt = ''
            created = item['created_at'].strftime('%Y-%m-%d %H:%M:%S') 

            if item['entity']['type'] == 'Task':
                #temp.append( item )
                task = sg.find_one( 'Task',[['id','is',item['entity']['id']] ],
                                ['entity'] )
                #temp.append( task )
                if not task['entity']:
                    continue
                lev2 = sg.find_one( 
                                    task['entity']['type'], 
                                    [['id','is',task['entity']['id']]],
                                    ['code','tasks']
                                    )
                tasks = []
                for task in lev2['tasks']:
                    task_st = sg.find_one(
                                            'Task',[['id','is',task['id']]],
                                            ['sg_status_list'] )
                    if task_st['sg_status_list'] == 'cmpt':
                        tasks.append( task_st )
                if len( lev2['tasks'] ) == len(tasks):
                    print lev2
                    #update_txt = sg.update( lev2['type'],lev2['id'],{'sg_status_list':'cmpt'} )

            if update_txt:
                self.logger.info( '[ updated ] : ',update_txt )
                self.logger.info( '{:15}: {}'.format( 'created_at', created ) )
                self.logger.info( '{:15}: {}'.format( 'attribute',item['attribute_name'] ) )
                self.logger.info( '{:15}: {}'.format( 'description',item['description'] ) )
        return items[0]['id']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", help="pid filename", default="/tmp/status_event.pid" )
    parser.add_argument("--log", help="log filename", default="/tmp/status_event.log")
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
