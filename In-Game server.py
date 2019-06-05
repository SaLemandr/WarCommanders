import socket
import json
import map
from Warrior import Warrior
import threading
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random


def process_message(message):
    return [json.loads(x) for x in message.decode('utf-8').split('<||>') if x]


def new_turn(Client, OtherClient):
    checkfree = False
    Turn.acquire()
    Client.turn_number += 1
    choose_cards = []
    new_data = ["TURN", str(Client.turn_number), str(Client.points), str(Client.money)]
    for i in range(3):
        choose_cards[i] = str(random.randint(1, 5))
        new_data.append(choose_cards[i])
    data = Client.sock.recv(1024)
    data1 = process_message(data)
    if data1[0][0] == "CHOOSE":
        Client.Hand.append(int(data1[0][1]))
        Client.sock.send(json.dumps("CHOOSE OK").encode('utf-8'))
    OtherClient.sock.send(json.dumps(new_data).encode('utf-8'))
    new_data = ["ENEMY", str(Client.points)]
    OtherClient.sock.send(json.dumps(new_data).encode('utf-8'))


def move(data1):
    prev_x = None
    prev_y = None
    way = data1[0]
    x = []
    y = []
    for i in data1:
        value = 0
        x = []
        y = []
        while value != ' ':
            x.append(i[value])
        while value < i.len():
            y.append(i[value])
        x = str(x)
        y = str(y)
        if (prev_x is not None) and (prev_y is not None):
            UnitMap.map[int(x)][int(y)] = UnitMap.map[prev_x][prev_y]
            UnitMap.map[prev_x][prev_y] = None
            UnitMap.map[int(x)][int(y)].speed -= UnitMap.movemap[prev_x][prev_x]
        prev_x = int(x)
        prev_y = int(y)
    way.append(str(x) + ' ' + str(y))
    return way


def attack(Client, OtherClient, data1):
    damage = UnitMap.map[int(data[1])][int(data[2])].attack(UnitMap.map[int(data[3])][int(data[4])])
    if UnitMap.map[int(data[3])][int(data[4])].hp <= 0:
        UnitMap.map[int(data[3])][int(data[4])] = None
    new_data = ["ATTACK", data1[1], data[2], data[3], data[4], damage]
    Client.sock.send(json.dumps(new_data))
    OtherClient.sock.send(json.dumps(new_data))


def put_warrior(Client, session, id, map, x, y):
    if Client.number == 1:
        if x == "0":
            for Warriors in session.query(Warrior).filter(Warrior.id == id):
                map[int(x)][int(y)] = Warrior(id=Warriors.id, name=Warriors.name, cost=Warriors.cost,
                                              armor=Warriors.armor, range=Warriors.range, dmg=Warriors.dmg,
                                              hp=Warriors.hp, speed=Warriors.speed)
                Client.money -= Warriors.cost
    else:
        if x == "14":
            for Warriors in session.query(Warrior).filter(Warrior.id == id):
                map[int(x)][int(y)] = Warrior(id=Warriors.id, name=Warriors.name, cost=Warriors.cost,
                                              armor=Warriors.armor, range=Warriors.range, dmg=Warriors.dmg,
                                              hp=Warriors.hp, speed=Warriors.speed)
                Client.money -= map[int(x)][int(y)].cost


def turn(Client, OtherClient):
    new_turn(Client, OtherClient)
    while True:
        data = json.loads(Client.sock.recv(1024))

        if data[0] == "MOVE":
            data.remove("MOVE")
            UnitMap.map[int(data[3])][int(data[4])] = UnitMap.map[int(data[1])][int(data[2])]
            UnitMap.map[int(data[1])][int(data[2])] = None
            Client.sock.send(json.dumps(UnitMap.map[int(data[3])][int(data[4])]))

        if data[0] == "SPAWN":
            put_warrior(Client, session, data[1], UnitMap.map, data[2], data[3])
            new_data = ("SPAWN", "ALLIED", data[1], data[2], data[3])
            Client.sock.send(json.dumps(new_data))
            new_data = ("SPAWN", "ENEMY", data[1], data[2], data[3])
            OtherClient.sock.send(json.dumps(new_data))

        if data[0] == "ATTACK":
            attack(Client, OtherClient, data)

        if data == "NEXTTURN":
            Turn.release()
            checkfree = True
            break

    time.sleep(10)


def replace_cards(Client, data1):
    data = []
    data[0] = "REPLACE"
    for x in range(len(data1)):
        Client.Hand[data[x + 1]] = random.randint(1, 5)
        data.append(str(Client.Hand))
    Client.sock.send(json.dumps(data))


def start_match(Client):
    data1 = Client.sock.recv(1024)
    data1 = json.loads(data1)
    if data1[0] != "NONE":
        replace_cards(Client, data1)
    data1 = "START"
    Client.sock.send(data1)


def change(map):
    changedmap = json.dumps(map)
    Client1.sock.send(changedmap)
    Client2.sock.send(changedmap)


class Client:

    def __init__(self, sock, addr, num):
        self.sock = sock
        self.addr = addr
        self.money = 100
        self.Hand = Warrior.Hand
        self.turn_number = 0
        self.number = num
        self.points = 0
        self.points_income = 1


checkfree = True
UnitMap = map.map(map.b, map.a)
sock = socket.socket()
sock.bind(('', 9080))
Turn = threading.Lock()
engine = create_engine('sqlite:///Cards.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


def play(Client, OtherClient):
    start_match(Client)
    while True:
        while not checkfree:
            time.sleep(1)
        turn(Client, OtherClient)


sock.listen(1)
conn1, addr1 = sock.accept()
print("Connected: ", addr1)
data = json.dumps(UnitMap.map.b)
conn1.send(data)
sock.listen(1)
conn2, addr2 = sock.accept()
conn2.send(data)
print("Connected: ", addr2)
Client1 = Client(conn1, addr1, 1)
Client2 = Client(conn2, addr2, 2)
Thread1 = threading.Thread(target=play, args=(Client1, Client2))
Thread2 = threading.Thread(target=play, args=(Client2, Client1))
Thread1.start()
Thread2.start()
