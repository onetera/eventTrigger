# :coding: utf-8

import sys

sys.path.append( '/westworld/inhouse/tool/rez-packages/deadline/10.2.0/platform-linux/arch-x86_64/site-packages' )
import Deadline.DeadlineConnect as Connect
import glob
import os
from pprint import pprint

import shotgun_api3 as sa

sg = sa.Shotgun(
                'https://west.shotgunstudio.com',
                api_key='6h&ziahfuGbqdubxrxeyopinl',
                script_name = 'eventTrigger',
            )


drive_map = {
    'ftp_vietnam' : '/ftp/west_rnd',
}

def get_ftp_tag_id( old_id ):
    filters = [
        [ 'event_type', 'is', 'Shotgun_Version_Change' ],
        [ 'attribute_name' , 'is', 'tags' ],
        [ 'id', 'greater_than', old_id ]
    ] 

    keys = [
        'meta',
        'entity.Version.tags',
    ]

    result = sg.find_one( 
        'EventLogEntry' , filters, keys
    )



    if result and 'ftp' in result['entity.Version.tags'][0]['name']:
        return result['id']
    else:
        return old_id 


def get_event( event_id ):
    event = sg.find_one( 
        'EventLogEntry' , 
        [
            [ 'id', 'greater_than', event_id ],
            [ 'event_type', 'is', 'Shotgun_Version_Change' ],
            [ 'attribute_name' , 'is', 'tags' ],
        ],
        [ 
            'entity.Version.sg_path_to_frames',
            'entity.Version.sg_path_to_movie',
            'entity.Version.id',
            'entity.Version.tags',
            'entity.Version.project.Project.name',
            'entity.Version.code',
        ]
    )
    if event and 'ftp' in event['entity.Version.tags'][0]['name']:
        return event
    else:
        return {'id':event_id}


def submit_job( sg_ver ):
    if 'entity.Version.code' not in sg_ver.keys():
        return
    conn = Connect.DeadlineCon( '10.0.25.28', '8081' )
    user = os.environ[ 'USER' ]

    basename   = os.path.basename( sg_ver['entity.Version.sg_path_to_frames'] ).split( '.' )[0]
    proj       = sg_ver['entity.Version.project.Project.name']
    ver_name   = sg_ver['entity.Version.code']
    dirname    = os.path.dirname( sg_ver['entity.Version.sg_path_to_frames'] ) 
    ext        = os.path.splitext( sg_ver['entity.Version.sg_path_to_frames'] )[1] 
    vendor_tag = sg_ver[ 'entity.Version.tags' ]
    drv_map    = drive_map[ vendor_tag[0]['name'] ]

    cmd_file = '/show/{}/tmp/deadline_log/cmd_{}.txt'.format( proj, ver_name )
    if not os.path.exists( os.path.dirname(cmd_file) ):
        os.makedirs( os.path.dirname(cmd_file) )
    file_list = [ x for x in glob.glob( dirname + os.sep + '*' + ext )  ]
    file_list.sort()

    sg_user = sg.find_one( 
                    'HumanUser' ,
                    [ 
                        ['sg_ww_id' , 'is' ,user ]
                    ],
                    ['name']
    )
    
    if not sg_user:
        sg_user = {'name':'west'}
    

    job_info = {
        'Name' : ' [ {} ][ {} ][ Move2FTP :  {} ]'.format( 
                                    sg_user['name'], proj, ver_name 
        ) , 
        'UserName' : user,
        'Group'     : 'io',
        'Plugin' : 'CommandScript',
        'frames' : '0-{}'.format( len( file_list) -1 ),
    }

    plugin_info = {
        "ShellExecute" : "False",
        "Shell" : "default",
        "StartupDirectory" : ""        
    }
    

    ftp_tg = dirname.partition( 'show' )
    if not os.path.exists( drv_map + os.sep + 'show' + dirname.partition('show')[2] + os.sep ):
        os.makedirs( drv_map + os.sep + 'show' + dirname.partition('show')[2]  )
                
    #cmd = '/usr/bin/rsync -av {} {}'.format( 
    cmd = '/usr/bin/cp -rf {} {}'.format( 
                dirname + os.sep ,
                os.path.abspath( drv_map + os.sep + 'show' + dirname.partition('show')[2] + os.sep + os.pardir + os.sep )
    )
    
    with open( cmd_file , 'w' ) as f:
        f.write( cmd )

    job = conn.Jobs.SubmitJob( job_info, plugin_info, cmd_file )
    pprint( job )

def main( _id ):
    #event_id = get_ftp_tag_id( _id )
    result = get_event( _id )
    pprint( result )
    submit_job( result )

    return result['id']




