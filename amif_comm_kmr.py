import select

__author__ = 'Jan Kempeneers'

###############################################################
# for file manipulation
import os

import socket
import sys
import time

print(sys.version)

###############################################################
PORT = 30001  # Arbitrary non-privileged port
IP_IIWA = '172.31.1.10'

start_kogame_var = b'(3)/n'
send_status_kogame = b'(1)/n'
ready = b'100'
busy = b'102'
finished = b'103'

ask_file = "C:/C3_HMI/cmmComm/remote.ask"
msg_file = "C:/C3_HMI/cmmComm/remote.msg"
ans_file = "C:/C3_HMI/cmmComm/remote.ans"
commfiles = [ask_file, ans_file, msg_file]
ans_file_found = False

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

    # 'demost_kmr\n' \
    # 'demost_kmr\n' \

def start_kogame():
    tempfile = "C:/C3_HMI/cmmComm/tempfile.txt"
    askfile = "C:/C3_HMI/cmmComm/remote.ask"
    text = 'EXECUTE_PATH_PART_PROGRAM\n' \
           'C:\MCOSMOS\DATA\n' \
           'demost_kmr\n' \
           'demost_kmr\n' \
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
                    remove_msg_file = False
                    with open(file) as f:
                        msg_firstline = f.readline()
                        if msg_firstline == 'PPERR\n':
                            kogame_status = busy
                        elif msg_firstline == 'PPEND\n':
                            kogame_status = ready
                            remove_msg_file = True
                    if remove_msg_file:
                        os.remove(file)
                        ans_file_found = False
                        print(msg_firstline)
                except:
                    print('could not read remote.msg file')
                    kogame_status = busy
                    pass
    if not file_found and not ans_file_found:
        kogame_status = ready

    return kogame_status


# clear_cmmComm()
status_kogame = monitor_kogame()

iiwa_socket_connection = False
while not iiwa_socket_connection:
    iiwa_socket_object = open_socket(IP_IIWA, PORT)
    iiwa_socket = iiwa_socket_object[0]
    iiwa_socket_connection = iiwa_socket_object[1]

iiwa_socket.settimeout(2)

status_kogame = monitor_kogame()
iiwa_socket.send(status_kogame)

while True:
    iiwa_msg = read_socket(iiwa_socket)
    time.sleep(1)
    if iiwa_msg == start_kogame_var:
        if monitor_kogame() == ready:
            status_kogame = busy
            start_kogame()
            iiwa_socket.send(status_kogame)
        else:
            status_kogame = monitor_kogame()
            print(status_kogame)
            iiwa_socket.send(status_kogame)
    else:
        status_kogame = monitor_kogame()
        print(status_kogame)
        iiwa_socket.send(status_kogame)




