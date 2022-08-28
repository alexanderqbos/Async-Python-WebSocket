#!/usr/bin/python3

import random
import socket
import sys

KEY_SIZE = 8
MSG_SIZE = 160
BUF_SIZE = 3 + KEY_SIZE + MSG_SIZE

GET_CMD = 'GET'
PUT_CMD = 'PUT'

HOST = '127.0.0.1'
PORT = 12345

def get_line(current_socket):
    buffer = b''
    size = 0
    while True:
        data = current_socket.recv(1)
        size += 1
        if data == b'\n' or size >= BUF_SIZE:
            return buffer
        buffer = buffer + data

def setup_cnx(num):
    print('Client', num, 'starting')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock

def send_put_msg(sock, num):
    key = str(num) + ''
    while len(key) < KEY_SIZE:
        key = key + str(random.randint(0, 9))

    msg = ''
    while len(msg) < MSG_SIZE:
        msg = msg + str(random.randint(0, 9))

    print('Client', num, 'sending', PUT_CMD, key)
    sock.sendall((PUT_CMD + key + msg + '\n').encode('utf-8'))
    print('Client', num, 'received', get_line(sock))

    return (key, msg)

def send_get_msg(sock, num, key, msg):
    sock.close()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print('Client', num, 'sending', GET_CMD, key)
    sock.sendall((GET_CMD + key + '\n').encode('utf-8'))
    data = get_line(sock)
    print('Client', num, 'received', ('' if msg.encode('utf-8') == data else 'in') + 'correct message')

NUM_SESSIONS = 5
if len(sys.argv) == 2:
    newVal = int(sys.argv[1])
    if NUM_SESSIONS < newVal:
        NUM_SESSIONS = newVal

socks = []
msgs = []
for i in range(NUM_SESSIONS):
    socks.append((i, setup_cnx(i)))

for (i, sock) in reversed(socks):
    msgs.append((i, sock, send_put_msg(sock, i)))

for (i, sock, (key, msg)) in msgs:
    send_get_msg(sock, i, key, msg)

def send_individually(s, sock):
    for c in s:
        sock.sendall(str(c).encode('utf-8'))
    return get_line(sock)

sock = setup_cnx(-1)
fragmented_put_cmd = 'PUTabcdefghThis is a test\nX'
if send_individually(fragmented_put_cmd, sock) != b'OK':
    print(b'Last put failed')
else:
    print(b'Last put ok')
sock.close()

sock = setup_cnx(-2)
fragmented_get_cmd = 'GETabcdefgh\n'
if send_individually(fragmented_get_cmd, sock) != b'This is a test':
    print(b'Last get failed')
else:
    print(b'Last get ok')
sock.close()
