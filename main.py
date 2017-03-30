# telnet program example
import socket, select, string, sys
import time
import os
import sys
import xbox
import threading
import math
HOST = "192.168.1.1"

vel = 0
turn = 0

def write_telnet(s, command):
  s.send(command + '\n')

def set_speed(s, v_l, v_r):
    if v_l > 1:
        v_l = 1
    if v_l < -1:
        v_l = -1
    if v_r > 1:
        v_r = 1
    if v_r < -1:
        v_r = -1

    vli = int(v_l * 100)
    vri = int(v_r * 100)
    write_telnet(s, "drive " + str(vli) + " " + str(vri))

def update_speed(s):
    if abs(vel) < 0.1:
        set_speed(s, turn, - turn)
    else:
        set_speed(s, vel + turn, vel - turn)

def manual_drive(s):
    #generic call back
    def controlCallBack(xboxControlId, value):
        if xboxControlId == 6 and value == 1:
            write_telnet(s, "reward 100")
            print("reward 100")
        if xboxControlId == 7 and value == 1:
            write_telnet(s, "reward -100")
            write_telnet(s, "drive 0 0")
            print("reward -100")
        if xboxControlId == 9 and value == 1:
            write_telnet(s, "ai_mode")
            print("handing over to AI")
        if xboxControlId == 8 and value == 1:
            write_telnet(s, "drive 0 0")
            print("pause here")
        if xboxControlId == 4:
            global vel
            vel = value / 200.0
            update_speed(s)
        if xboxControlId == 5:
            global vel
            vel = -value / 200.0
            update_speed(s)
        #print "Control Id = {}, Value = {}".format(xboxControlId, value)

    #specific callbacks for the left thumb (X & Y)
    def leftThumbX(xValue):
        global turn
	# ORIENTATION
        turn = xValue / 200.0
        update_speed(s)
    def leftThumbY(yValue):
        global vel
	# SPEED
	##vel = yValue / 200.0

    #setup xbox controller, set out the deadzone and scale, also invert the Y Axis (for some reason in Pygame negative is up - wierd! 
    xboxCont = xbox.XboxController(controlCallBack, deadzone = 2, scale = 100, invertYAxis = True)

    #setup the left thumb (X & Y) callbacks
    xboxCont.setupControlCallback(xboxCont.XboxControls.LTHUMBX, leftThumbX)
    xboxCont.setupControlCallback(xboxCont.XboxControls.LTHUMBY, leftThumbY)

    try:
        #start the controller
        xboxCont.start()
        print "xbox controller running"
        while True:
            time.sleep(1)

    #Ctrl C
    except KeyboardInterrupt:
        print "User cancelled"
    
    #error        
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
        
    finally:
        #stop the controller
        xboxCont.stop()

def telnetCon(s):
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print 'Connection closed'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg)

#main function
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((HOST, 2323))
    except:
        print('ERROR: Unable to connect.')
        print("")
        print("Is Alice-Bot Running?")
        print("Are you in the correct WLAN?")
        sys.exit()
     
    print 'Connected to remote host'
    time.sleep(0.2)
    write_telnet(s, "human")

    th = threading.Thread(target=telnetCon, args=(s,))
    th.daemon = True
    th.start()

    #th = threading.Thread(target=auto_speed, args=(s,))
    #th.daemon = True
    #th.start()

    manual_drive(s)

