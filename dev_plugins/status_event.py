import shotgun_api3 as sa
import datetime
import time
from pprint import pprint
import threading
import os
import sys

global result
result= []

log_file = '/tmp/status_event.log'
#sys.stdout = open( log_file , 'a+' )

# DEV = 0
# if not DEV:
sg = sa.Shotgun('https://west.shotgunstudio.com',
            api_key='6h&ziahfuGbqdubxrxeyopinl',
            script_name = 'eventTrigger',
            # api_key = 'bznladfaecqjff3f^dnrysavX',
            # script_name = 'event',
            )
# else:
#     sg = sa.Shotgun('https://wswg1.shotgunstudio.com',
#                 api_key='yeIit5stwbhgyhefsawqkv&zj',
#                 script_name = 'eventDaemon',
#                 )

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
    fields = [
                'description','created_at','attribute_name','entity','project.Project.name',
                'user.HumanUser.firstname','meta'
    ]
    order = [{'field_name':'id', 'direction':'desc'}]
    filters =  [
                    ['attribute_name','is','sg_status_list' ],
                    ['event_type','is','Shotgun_Task_Change' ],
                ]
    if old_id == 0:
        items = [sg.find_one( 'EventLogEntry',filters, fields ,order )]
    else:
        filters.append( ['id', 'greater_than' , old_id ] )
        items = sg.find( 'EventLogEntry',filters, fields ,order )

    if not items:
        # print 'None'
        return old_id
        # filters =  [
        #             ['attribute_name','is','sg_status_list' ],
        #             ['event_type','is','Shotgun_Task_Change' ],
        #             # ['project.Project.name', 'is_not', '_Pipeline' ],
        #             ['id', 'greater_than' , old_id ],
        #             #['description','in','cmpt']
        #             ]
        # items = sg.find_one( 'EventLogEntry',filters, fields ,order )
        # return items['id']


    for item in items:
        update_txt = ''
        created = item['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        if item['entity'] == None:
            # print '\n'
            #pprint( item )
            continue
            #return

        if item['entity']['type'] == 'Task':
            task = sg.find_one( 'Task',
                            [
                                ['id','is',item['entity']['id'] ],
                                ['sg_status_list', 'in', ['cmpt'] ]
                            ],
                            ['entity','type'] )


            if not task or not task['entity']:
                #return
                continue

            print '@'*60
            print '{:15}: {}'.format( 'Project' , item['project.Project.name'] )
            print '{:15}: {}'.format( 'Entity'  , task['entity']['name'] )
            print '{:15}: {}'.format( 'ID'      , item['id'] )
            print '{:15}: {}'.format( 'Created' , created )
            print '{:15}: {}'.format( 'Description' , item['description'] )
            print '\n'


            lev2 = sg.find_one(
                                task['entity']['type'],
                                [['id','is',task['entity']['id']]],
                                ['code','tasks']
                                )
            tasks = []
            task_st = {}
            for _task in lev2['tasks']:
                if task['id'] == _task['id']:
                    tasks.append( _task )
                    continue

                task_st = sg.find_one(
                                        'Task',
                                        [
                                            ['id','is',_task['id']],
                                       ],
                                        ['sg_status_list']
                                   )
                if task_st['sg_status_list'] in [ 'cmpt' ]:
                    tasks.append( task_st )

#                if _task['sg_status_list'] == 'omit':
#                    tasks.append( _task )
#                    continue

            if len( lev2['tasks'] ) == len(tasks):
                update_txt = sg.update( lev2['type'],lev2['id'],{'sg_status_list':'cmpt'} )

        if update_txt and task_st:
            print '[Task status update Entity status', '.'*50
            print '[ updated ] : ',update_txt
            print '{:15}: {}'.format( 'created_at'  , created )
            print '{:15}: {}'.format( 'Project'     , item['project.Project.name'] )
            print '{:15}: {}'.format( 'Link'        , lev2['code'] )
            print '{:15}: {}'.format( 'attribute'   , item['attribute_name'] )
            print '{:15}: {}'.format( 'description' , item['description'] )
            print 'https://wswg.shotgunstudio.com/detail/task/{}'.format( task_st['id'] )
            print '.'*80
            print '\n'

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
    print '[ today_id ]', items
    return items[0][-1]['id'] if items[0] else False

def set_status_id( _id ):
    with open( '/tmp/sg_status_id.tx' , 'w' ) as f:
        f.write( str(_id) )


def get_status_id( ):
    status_file = '/tmp/sg_status_id.tx'
    if not os.path.exists( status_file ):
        return False
    with open( status_file ) as f:
        result = f.read()
    if result :
        print "last id : ", int( result)
        return int(result)
    else:

        return today_id()


def main( last_id = False ):
    return status_update_event( last_id )


def main2():
    old_id = get_status_id()
    if not old_id:
        old_id = today_id()

    while True:
        time.sleep( 5 )
        #now = time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
        #print '\n',now,'\t','*'*20
        #print_logs()
        result = status_update_event(old_id )
        set_status_id( result )
        old_id = result


if __name__ == '__main__':
    import argparse

    #parser = argparse.ArgumentParser()
    ##
    ## --start 20190213
    ## today , specific 
    #arg = parser.add_argument( '-s', '--start' , default='0' )
#    result = parser.parse_args()
#    if result.start == '0':
#        old_id = today_id()
#
#    elif len( result.start )== 8:
#        old_id = today_id( result.start )
#
#    else:
#        old_id = get_status_id()
    old_id = get_status_id()
#    
#    pid = os.getpid()
#    with open( '/tmp/status_event.pid', 'w' ) as f:
#        f.write( str(pid) )

#    now = time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
#
    #print '[ PID     ] ', pid
    print '[ last id ] ',old_id

    while True:
#        now = time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
#        print '\n',now,'\t','*'*20
        #print_logs()

#        result = status_update_event(old_id )
#        set_status_id( result )
#        old_id = result
#        print '\n'
#        print '[ Error  ]', time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
#        print '[ old id ]', old_id
#        print 'https://wswg.shotgunstudio.com/detail/EventLogEntry/{}'.format( old_id )
#        print '\n'
#        time.sleep( 10 )
#        continue 

        try:
           result = status_update_event(old_id )
           set_status_id( result )
           old_id = result
        except KeyboardInterrupt:
            break
#        except ProtocolError:
#            print 'protocol error'
#            continue
        except :
           print '\n'
           print '[ Error  ]', time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
           print '[ old id ]', old_id
           print 'https://west.shotgunstudio.com/detail/EventLogEntry/{}'.format( old_id )
           # pprint( result )
           print '\n'
           continue

        time.sleep( 10 )



