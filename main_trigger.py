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

sg = sa.Shotgun(
    'https://west.shotgunstudio.com',
    api_key='6h&ziahfuGbqdubxrxeyopinl',
    script_name = 'eventTrigger',
)

PLUGIN_PATH= '/storenext/inhouse/tool/shotgun/event_trigger/plugins' 
#LOG_DIR =  '/storenext/inhouse/tool/shotgun/eventTrigger/log'
LOG_DIR = '/storenext/inhouse/log/eventTrigger'
#PLUGIN_PATH=os.path.join( os.getcwd() , 'plugins' )
#LOG_DIR = os.path.join( os.getcwd() , 'log')



class PluginCollection:
    def __init__( self ):
        self.files = [ Plugin( x ) for x in glob.glob( PLUGIN_PATH + os.sep + '*.py' ) \
                       if basename(x)[0] not in '_'
                       ]

    def __iter__(self):
        for x in self.files:
            yield x


class Plugin:
    def __init__( self, path ):
        self._path = path
        self._name = basename( path )
        self.load()

    def load(self):
        self.plugin = imp.load_source( self._name , self._path )

    def main(self, arg ):
        self.plugin = imp.load_source( self._name , self._path )
        return self.plugin.main(arg)

    def __str__(self):
        return str( self.plugin )

    def set_status_id( self , _id ):
        event_file =  '/storenext/inhouse/tool/shotgun/event_trigger/last_id' + os.sep + self._name + '.id' 
        #event_file = os.path.join( '/storenext/inhouse/tool/shotgun/eventTrigger/last_id' , self._name + '.id' )
        #event_file = os.path.join( os.getcwd(), 'last_id' , self._name + '.id' )
        with open( event_file , 'w' ) as f:
            f.write( str(_id) )

    def get_status_id( self ):
        status_file =  '/storenext/inhouse/tool/shotgun/event_trigger/last_id' + os.sep +  self._name + '.id' 
        #status_file =  os.path.join( '/storenext/inhouse/tool/shotgun/eventTrigger/last_id', self._name + '.id' )
        #status_file =  os.path.join( '/storenext/inhouse/tool/shotgun/eventTrigger/last_id', self._name + '.id' )
        if not os.path.exists( status_file ):
            return False
        with open( status_file ) as f:
            result = f.read()
        return int(result)

def timelog():
    return time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )

def main():
    # pc = PluginCollection()
    # while True:
    #     time.sleep( 5 )
    #     for plugin in pc:
    #         last_id = plugin.get_status_id()
    #         result  = plugin.main( last_id )
    #         plugin.set_status_id( result )
    #         # sys.stdout.flush()
    #     continue
    # return

    log_file = 'event.'+ dt.datetime.strftime( dt.datetime.now() , '%Y%m' )+ '.log'
    log_path = os.path.join( LOG_DIR , log_file ) 
    if not os.path.exists( log_path ):
        f = open( log_path ,'w' )
        f.close()
    so = open( log_path, 'a+')
    sys.stdout = so

    print " *** Started main event logger *** "

    pc = PluginCollection()
    print '-'*50
    print '[Started log]',timelog()
    print '-'*50
    print
    sys.stdout.flush()

    while True:
        time.sleep( 5 )

       # print time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )
       # sys.stdout.flush()
       # continue

#        for plugin in pc:
#            last_id = plugin.get_status_id()
#            result  = plugin.main( last_id )
#            plugin.set_status_id( result )
#            sys.stdout.flush()
#        continue

        for plugin in pc:
            try:
                last_id = plugin.get_status_id()
                result = plugin.main( last_id )
            except sa.ProtocolError:
                print "Protocol Error"
            except KeyboardInterrupt:
                print "[ KeyboardInterrput ] %s"% timelog()
                break
            except:
                print '^'*80
                print '[',plugin._name,']', ' Unkwon error', last_id
                print '^'*80
                result = last_id + 1
            finally:
                plugin.set_status_id( result )
                sys.stdout.flush()
#

def basename( path ):
    return os.path.splitext( os.path.basename(path))[0]


if __name__ == '__main__':
    main()






