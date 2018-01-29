import select

__author__ = 'Jan Kempeneers'

###############################################################
# for file manipulation
import os

import socket
import sys
import time
import log
import threading
import params_dashboard

print(sys.version)

###############################################################
log_file = 'c:/Users/Administrator/PycharmProjects/AMIF/log_file.txt'
logger = log.Log(log_file)

PORT = 30001  # Arbitrary non-privileged port
IP_IIWA = '10.32.3.193'

start_kogame_var = b'(3)/n'
send_status_kogame = b'(1)/n'
continue_kogame_var = b'(5)/n'


ready = b'100'
busy = b'102'
finished = b'103'

ask_file = "C:/C3_HMI/cmmComm/remote.ask"
msg_file = "C:/C3_HMI/cmmComm/remote.msg"
ans_file = "C:/C3_HMI/cmmComm/remote.ans"
commfiles = [ask_file, ans_file, msg_file]
ans_file_found = False
clicked_continue = False


def open_socket(IP, PORT):
    max_retries = 3
    connect_answer = 'a'
    # open a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    # try to connect to server
    for i in range(max_retries):
        try:
            connect_answer = s.connect((IP, PORT))
        except:
            pass
        print(connect_answer)
        if connect_answer is None:
            hostname = socket.gethostname()
            hostaddress = socket.getaddrinfo(IP_IIWA, PORT)
            print('Socket connected with hostname: {} at addressinfo:{}'.format(hostname, hostaddress))
            connection = True
            break
    else:
        print('unable to establish socket connection to iiwa')
        connection = False

    return s, connection


def read_socket(s):
    msg = ''
    #    print(s)
    try:
        msg = s.recv(1024)
    except socket.timeout as e:
        print('socket timed out')
        pass
    except:
        sys.exit(1)
    if msg:
        print('received msg: {}'.format(msg))
    else:
        print('no message available')
    return msg

    # 'demost_horloge\n' \
    # 'demost_horloge\n' \

    # 'jtekt_16-3067\n' \
    # 'PG\n' \

    # 'demost_kmr\n' \
    # 'demost_kmr\n' \

# added this dummy function to replace real one below for safety reasons
def start_kogame():
    time.sleep(1)
    pass

'''
def start_kogame():
    tempfile = "C:/C3_HMI/cmmComm/tempfile.txt"
    askfile = "C:/C3_HMI/cmmComm/remote.ask"
    text = 'EXECUTE_PATH_PART_PROGRAM\n' \
           'C:\MCOSMOS\DATA\n' \
           'jtekt_16-3067\n' \
           'PG\n' \
           '0\n' \
           '0\n' \
           '0\n' \
           '1\n' \
           '1\n' \
           'Ko-ga-me CMM-1\n' \
           'STAT'

    try:
        with open(tempfile, 'w') as f:
            f.write(text)
    except:
        print('could not create tempfile')
        pass

    try:
        os.rename(tempfile, askfile)
    except:
        print('could not rename tempfile to askfile')
        pass
'''

def clear_cmmComm():
    for file in commfiles:
        file_exists = os.path.isfile(file)
        if file_exists:
            os.remove(file)


def monitor_kogame():
    kogame_status = busy
    file_found = False
    for file in commfiles:
        file_exists = os.path.isfile(file)
        if file_exists:
            if file == ask_file:
                file_found = True
                kogame_status = busy
                break
            elif file == ans_file:
                file_found = True
                global ans_file_found
                ans_file_found = True
                os.remove(ans_file)
                kogame_status = busy
            elif file == msg_file:
                file_found = True
                try:
                    with open(file) as f:
                        msg_firstline = f.readline()
                        if msg_firstline == 'PPERR\n':
                            kogame_status = busy
                        elif msg_firstline == 'PPEND\n':
                            kogame_status = ready
                    os.remove(file)
                    ans_file_found = False
                    print(msg_firstline)
                    # enter line for log command
                    logger.log_entry(log_file)
                except:
                    print('could not read remote.msg file')
                    kogame_status = busy
                    pass
    if not file_found and not ans_file_found:
        kogame_status = ready

    return kogame_status


clear_cmmComm()

thread1 = threading.Thread(target=params_dashboard.run, args=[])
thread1.start()

status_kogame = monitor_kogame()

iiwa_socket_connection = False
while not iiwa_socket_connection:
    iiwa_socket_object = open_socket(IP_IIWA, PORT)
    iiwa_socket = iiwa_socket_object[0]
    iiwa_socket_connection = iiwa_socket_object[1]

iiwa_socket.settimeout(2)

status_kogame = monitor_kogame()
iiwa_socket.send(status_kogame)

'''
Added click to ba able to start Kogame program and wait at programmable stop, then click 'ok' to continue 
in the program. Goal was to save time otherwise lost waiting for Kogame to start.
'''
import win32api, win32con
def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


while True:
    iiwa_msg = read_socket(iiwa_socket)
    time.sleep(0.25)
    if iiwa_msg == start_kogame_var:
        if monitor_kogame() == ready:
            # status_kogame = busy
            start_kogame()
            iiwa_socket.send(status_kogame)
        else:
            status_kogame = monitor_kogame()
            print(status_kogame)
            iiwa_socket.send(status_kogame)
    elif iiwa_msg == continue_kogame_var:
        # click(1360,910)
        click(1090,590)
    else:
        status_kogame = monitor_kogame()
        print(status_kogame)
        iiwa_socket.send(status_kogame)




