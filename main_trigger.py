# :coding: utf-8
#
#
# TODO
#1.log setup
#2.foler에서 플러그인 호출
#3.플러그인 실행
#


import os
import sys
import imp
import time
from pprint import pprint
import datetime as dt
import shotgun_api3 as sa
import os
import glob
import yaml

sg = sa.Shotgun(
    'https://west.shotgunstudio.com',
    api_key='6h&ziahfuGbqdubxrxeyopinl',
    script_name = 'eventTrigger',
)


MOD_DIR     = os.path.abspath( os.path.dirname( __file__ ) )
PLUGIN_PATH = os.path.join( MOD_DIR , 'plugins' )
LOG_DIR     = os.path.join( MOD_DIR , 'log'     )


DEV = 0

class PluginCollection:
    def __init__( self ):
        self.files = [ Plugin( x ) for x in glob.glob( PLUGIN_PATH + os.sep + '*.py' ) \
                       if basename(x)[0] not in '_'
                       ]
        print( 'Plugins Collection' )
        print( [ x.name for x in self.files ] )                        

    def __iter__(self):
        for x in self.files:
            yield x


class Plugin:
    def __init__( self, path ):
        self._path = path
        self.name = basename( path )
        self.load()
        self.id_file  = MOD_DIR + os.sep + './last_id'  + os.sep +  self.name + '.id'
        self.log_file = LOG_DIR + os.sep + self.name + '.' + dt.datetime.strftime( dt.datetime.now() , '%Y%m' )+ '.log'

    def load(self):
        self.plugin = imp.load_source( self.name , self._path )

    def main(self, arg ):
        self.plugin = imp.load_source( self.name , self._path )
        return self.plugin.main(arg)

    def __str__(self):
        return str( self.plugin )

    def excution_status(self):
        with open( MOD_DIR + os.sep + './config.yml') as f:
            data = yaml.load( f, Loader = yaml.FullLoader )
        status = data['plugins'][self.name]['excution']
        return status

    def set_status_id( self , _id ):
        with open( self.id_file , 'w' ) as f:
            f.write( str(_id) )

    def get_status_id( self ):
        if not os.path.exists( self.id_file ):
            return False
        with open( self.id_file ) as f:
            result = f.read()
        return int(result)


def timelog():
    return time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )


def log_filepath():
    log_file = 'event.'+ dt.datetime.strftime( dt.datetime.now() , '%Y%m' )+ '.log'
    log_path = os.path.join( LOG_DIR , log_file ) 
    if not os.path.exists( log_path ):
        f = open( log_path ,'w' )
        f.close()
    return log_path


def main():
    
    log_path = log_filepath()
    
    so = open( log_path, 'a+')
    sys.stdout = so

    print( " *** Started main event logger *** " )

    pc = PluginCollection()
    print( '-'*50 )
    print( '[Started log]' , timelog() )
    print( '-'*50 )
    print()
    sys.stdout.flush()

    while True:
        time.sleep( 3 )

#        log_path = log_filepath()
#        so = open( log_path, 'a+')
#        sys.stdout = so

       # print time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )
       # sys.stdout.flush()
       # continue

#        for plugin in pc:
#            last_id = plugin.get_status_id()
#            result  = plugin.main( last_id )
#            plugin.set_status_id( result )
#        continue

        #########################################################################
        ##  Excution part
        ##  Non-comment for excution part
        #########################################################################
        for plugin in pc:
            print( plugin.name )
            #print( '[{}] id: {}'.format( plugin.name, str( last_id ) ) )
            if plugin.excution_status():
                if DEV:
                    last_id = plugin.get_status_id()
                    result  = plugin.main( last_id )
                    print( '[{}] id: {}'.format( plugin.name, str( last_id ) ) )
                    plugin.set_status_id( result )
                    #continue

                else:
                    try:
                        last_id = plugin.get_status_id()
                        result = plugin.main( last_id )
                    except sa.ProtocolError:
                        print( "Protocol Error" )
                    except KeyboardInterrupt:
                        print( "[ KeyboardInterrput ] %s"% timelog() )
                        break
                    except:
                        print( '^'*80 )
                        print( '[ {} ] {} : {} '.format( plugin.name, ' Unknown error', last_id ) )
                        print( '^'*80 )
                        result = last_id + 1
                    finally:
                        if plugin.excution_status():
                            plugin.set_status_id( result )
                        sys.stdout.flush()
                print( '[ {} ] excution_status {} : {}'.format( plugin.name, last_id, plugin.excution_status() ) )
                sys.stdout.flush()
#            print( '[ '+plugin._name + ' ] excution_status : ' + plugin.excution_status(), last_id ) 
#

def basename( path ):
    return os.path.splitext( os.path.basename(path))[0]


if __name__ == '__main__':
    main()





