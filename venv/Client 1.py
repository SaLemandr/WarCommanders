import socket
import json


sock = socket.socket()
sock.connect(('localhost', 9080))


while True:
    data = input()
    sock.send(json.loads(data))
