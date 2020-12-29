# :coding: utf-8

from pprint import pprint
import datetime as dt
import time
import shotgun_api3 as sa
import os



#global MAIN_ID
MAIN_ID = 0

class SingletonInstane:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance


sg = sa.Shotgun(
                'https://wswg.shotgunstudio.com',
                api_key='d4f25676239bff829454edd3a5d97bac13c6d38c526367f9623286c4775ca4dd',
                script_name = 'utils',
            )

def get_version_status( last_id ):
    pass




def set_status_id( _id ):
    with open( '/tmp/ver_status_id.tx' , 'w' ) as f:
        f.write( str(_id) )

def get_status_id( ):
    status_file = '/tmp/ver_status_id.tx'
    if not os.path.exists( status_file ):

        return False
    with open( status_file ) as f:
        result = f.read()
    print 'result id : ', result
    return int(result)

def sync_version_to_task( old_id ):
#    if MAIN_ID == old_id:
#        print "Previous ID is same with old id"
#        return

    filters = [
        ['attribute_name','is','sg_status_list'],
        ['event_type','is','Shotgun_Version_Change'],
    ]
    keys = [
        'created_at','description', 'entity','project.Project.name',
        'entity.Version.sg_task',
        'entity.Version.sg_task.Task.sg_status_list',
        'entity.Version.sg_status_list',
    ]
    if not old_id:
        today = dt.datetime(
            dt.datetime.now().year,
            dt.datetime.now().month,
            dt.datetime.now().day,
#            dt.datetime.now().hour,
#            dt.datetime.now().minute
        )
        filters.append( ['created_at','greater_than',today] )
    else:
        filters.append( ['id', 'greater_than', old_id ] )

    result = sg.find_one(
    #results = sg.find(
        'EventLogEntry', filters , keys
    )
    if not result:
        result = {}
        result['id'] = old_id
        return old_id
    #for result in results:
    if old_id == result['id']:
        print "Previous ID is same with old id"
        result = {}
        result['id'] = old_id
        return old_id
    # pprint( result )
    # print '\n'

    if result and result['entity'] and result['entity.Version.sg_task']:
        updated = sg.update(
                    'Task', result['entity.Version.sg_task']['id'],
                    {'sg_status_list':result['entity.Version.sg_status_list'] }
                   )
        if updated:
            created = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            print '[Version status update Task status]','*'*50
            print '{:15} : {}'.format( 'ID'         , result['id'] )
            print '{:15} : {} / {}'.format( 'Project'    , result['project.Project.name'],
                                            result['entity']['name']  )
            print '{:15} : {}'.format( 'created_at' , created )
            print '{:15} : {}'.format( 'Description', result['description'] )
            print 'https://wswg.shotgunstudio.com/detail/task/{}'.format( result['entity.Version.sg_task']['id'] )
            print '\n'

            return result['id']
        else:
            print "[ No Updated ]"
            return result['id']
    else:
        pprint( result )
        print "entity or Version.sg_task is none type"
        return result['id']

def main( last_id = False ):
    return sync_version_to_task( last_id )


def main2():
    old_id = get_status_id()
    #old_id = False
    

#    while True:        
#        time.sleep( 10 )
#        result = sync_version_to_task( old_id )
#        if result == 'No':
#            continue
#        set_status_id( result['id'] )
#        old_id = result['id']


#    print '[ old id ]', old_id
    while True:
        try:
            time.sleep( 10 )
            result = sync_version_to_task( old_id )
            if result == 'No':
                continue
            set_status_id( result['id'] )
            old_id = result['id']
        except KeyboardInterrupt:
            break
        except:
            print '\n'
            print '[ Error  ]',time.strftime( '%Y-%m-%d %H:%S', time.localtime() )
            print '[ old id ]',old_id
           #pprint( result )


        # try:
        #     time.sleep( 5 )
        #     result = sync_version_to_task( old_id )
        #     set_status_id( result['id'] )
        #     old_id = result['id']
        # except:
        #     old_id = get_status_id()
        #     print '\n'
        #     print '[ Error ]'



if __name__ == '__main__':
    main()
    # print get_status_id()

    # filter = [
    #     ['create_at','greater_than',]
    # ]
    # today = dt.datetime(
    #                     dt.datetime.now().year,
    #                     dt.datetime.now().month,
    #                      dt.datetime.now().day
    #                      )
    # result = sg.find_one(
    #                     'EventLogEntry',
    #                     [
    #                         ['attribute_name','is','sg_status_list'],
    #                         ['event_type','is','Shotgun_Version_Change'],
    #                         ['created_at','greater_than',today]
    #                     ],
    #                     ['created_at','description', 'entity','project.Project.name']
    #                      )
    # created = result['created_at'].strftime('%Y-%m-%d %H:%M:%S')
    # print '{:15} : {}'.format( 'ID'         , result['id'] )
    # print '{:15} : {}'.format( 'Project'    , result['project.Project.name'] )
    # print '{:15} : {}'.format( 'Entity'     , result['entity']['name'] )
    # print '{:15} : {}'.format( 'created_at' , created )
    # print '{:15} : {}'.format( 'Description', result['description'] )
