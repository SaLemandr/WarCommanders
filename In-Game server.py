import socket
import json
import map
from Warrior import Warrior
import threading
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random


def put_warrior(Client, session, id, map, x, y):
    for Warriors in session.query(Warrior).filter(Warrior.id == id):
        map[int(x)][int(y)] = Warrior(id=Warriors.id, name=Warriors.name, cost=Warriors.cost, armor=Warriors.armor,
                                      range=Warriors.range, dmg=Warriors.dmg, hp=Warriors.hp, speed=Warriors.speed)
        Client.money -= Warriors.cost
    change(map)


def turn(Client):
    checkfree = False
    Turn.acquire()
    Client.turn_number += 1
    choose_cards = []
    data = ["TURN", str(Client.turn_number), str(Client.points), str(Client.money)]
    for i in range(3):
        choose_cards[i] = str(random.randint(1, 5))
        data.append(choose_cards[i])
    Client.sock.send(json.dumps(data).encode())
    while True:
        data = Client.sock.recv(1024)
        data = json.loads(data.decode())

        if data[0] == "0":
            break

        if data[0] == "1":
            UnitMap.map[int(data[3])][int(data[4])] = UnitMap.map[int(data[1])][int(data[2])]
            UnitMap.map[int(data[1])][int(data[2])] = None
            Client.sock.send(json.dumps(UnitMap.map[int(data[3])][int(data[4])]))

        if data[0] == "SPAWN":
            put_warrior(Client, session, data[1], UnitMap.map, data[2], data[3])

        if data[0] == "3":
            UnitMap.map[int(data[1])][int(data[2])].attack(UnitMap.map[int(data[3])][int(data[4])])
            if UnitMap.map[int(data[3])][int(data[4])].hp <= 0:
                UnitMap.map[int(data[3])][int(data[4])] = None
            Client.sock.send(json.dumps(UnitMap.map[int(data[3])][int(data[4])]))

        if data == "NEXTTURN":
            Turn.release()
            checkfree = True
            break

    time.sleep(10)


def move_warrior(Client, map, x1, y1, x2, y2):
    map[x1][y1] = map[x2][y2]
    map[x1][y1] = None
    Client.sock.send(json.dumps(map[x2][y2]))
    change(map)


def replace_cards(Client, data1):
    data = []
    data[0] = "REPLACE"
    for x in range(len(data1)):
        Client.Hand[data[x + 1]] = str(random.randint(1, 5))
    data = json.dumps(data)
    Client.sock.send(data.encode())


def start_match(Client):
    data1 = Client.sock.recv(1024)
    data1 = json.loads(data1.decode())
    if data1[0] != "NONE":
        replace_cards(Client, data1)
    data1 = "START".encode()
    Client.sock.send(data1)


def change(map):
    changedmap = json.dumps(map)
    Client1.sock.send(changedmap.encode())
    Client2.sock.send(changedmap.encode())


class Client:

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.money = 0
        self.active = True
        self.Hand = Warrior.Hand
        self.turn_number = 0


checkfree = True
UnitMap = map.map(map.b, map.a)
sock = socket.socket()
sock.bind(('', 9080))
Turn = threading.Lock()
engine = create_engine('sqlite:///Cards.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


def play(Client):
    start_match(Client)
    while True:
        while not checkfree:
            time.sleep(1)
        turn(Client)



sock.listen(1)
conn1, addr1 = sock.accept()
print("Connected: ", addr1)
data = json.dumps(UnitMap.map.b)
conn1.send(data.encode())
sock.listen(1)
conn2, addr2 = sock.accept()
conn2.send(data.encode())
print("Connected: ", addr2)
Client1 = Client(conn1, addr1)
Client2 = Client(conn2, addr2)
Thread1 = threading.Thread(target=play, args=(Client1, ))
Thread2 = threading.Thread(target=play, args=(Client2, ))
Thread1.start()
Thread2.start()




