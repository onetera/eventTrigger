import psutil
import os

def main():
    if not os.path.exists( '/tmp/status_event.pid' ):
        return
    with open( '/tmp/status_event.pid' ) as f:
        pid = f.read()
    if not psutil.pid_exists( pid ):
        os.system( 'python /home/ohjoo@wysiwygstudios.co.kr/work/shotgun/eventTrigger/status_event.py -s 324' )





if __name__ == '__main__':
    main()
