# :coding: utf-8

from pprint import pprint
import datetime as dt
import time
import shotgun_api3 as sa
import os




sg = sa.Shotgun(
                'https://wswg.shotgunstudio.com',
                api_key='d4f25676239bff829454edd3a5d97bac13c6d38c526367f9623286c4775ca4dd',
                script_name = 'utils',
            )


def main( old_id ):

    filters = [
        ['attribute_name','is','sg_status_list'],
        ['project.Project.name','not_in',['_Pipeline']],
        ['event_type','in',['Shotgun_Shot_Change','Shotgun_Asset_Change'] ],
    ]
    keys = [
        'created_at','description', 'entity','project.Project.name','code',
        'tasks','meta',
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

    # result = sg.find_one(
    results = sg.find(
        'EventLogEntry', filters , keys
    )
    if not results:
        # filters = [
        #     ['attribute_name','is','sg_status_list'],
        #     ['event_type','in',['Shotgun_Shot_Change','Shotgun_Asset_Change'] ],
        #     ['created_at','less_than',today]
        # ]
        # result = sg.find_one(
        #     'EventLogEntry', filters , keys
        # )

        return old_id

    batch_data = []
    results = [ x for x in results if x['meta']['new_value'] == 'omit' and x['entity'] ]
    if not results:
        return old_id
    for result in results:

        # if old_id == result['id']:
        #     print "Previous ID is same with old id"
        #     result = {}
        #     result['id'] = old_id
        #     return old_id

        item = sg.find_one(
            result['entity']['type'],
            [
                ['id','is',result['entity']['id'] ],
            ],
            ['tasks','project.Project.name','code','sg_status_list']
        )
        for task in item['tasks']:
            data = {}
            # data['id'] = task['id']
            data['sg_status_list'] = 'omit'
            batch_data.append({"request_type": "update",
                               "entity_type": "Task",
                               "entity_id": task['id'],
                               "data": data})
            print 'https://wswg.shotgunstudio.com/detail/task/{}'.format( task['id'] )

        print '[ omitted ] ','*'*70
        print '{:15} : {}'.format( 'ID'         , result['id'] )
        print '{:15} : {} / {}'.format( 'Project'    , result['project.Project.name'],
                                        result['entity']['name']  )
        print '{:15} : {}'.format( 'created_at' , result['created_at'] )
        print '{:15} : {}'.format( 'Description', result['description'] )
        print 'https://wswg.shotgunstudio.com/detail/{}/{}'.format(
                                                                    result['entity']['type'],
                                                                    result['entity']['id']
                                                                    )
        print '\n'
    sg.batch( batch_data )
    log_list = [ result['id'] for x in results ]
    log_list.sort()
    return log_list[-1]



if __name__ == '__main__':
    print 'start!'
    old_id  = False
    result = main( old_id )
    # old_id = result
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
