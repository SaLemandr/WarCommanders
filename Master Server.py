import socket
import json
import threading
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy import create_engine
import time


engine = create_engine('sqlite:///Users.db', echo=True)
Base = declarative_base()
sock = socket.socket()
sock.bind(('localhost', 9090))
Session = sessionmaker(bind=engine)
session = Session()
client_list = []
Thread_list = []


class User(Base):
    """"""
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    NickName = Column(String)
    Password = Column(String)
    Money = Column(Integer, default=0)

    def __init__(self, nickname, password):
        self.NickName = nickname
        self.Password = password


Base.metadata.create_all(engine)


class Client:

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr


def add_client():
    i = 0
    while True:
        sock.listen(5)
        conn, addr = sock.accept()
        client_list.append(Client(conn, addr))
        Thread_list.append(threading.Thread(target=search, args=(client_list[i], )))
        Thread_list[i].start()
        i += 1
        time.sleep(0.1)


def process_message(message):
    return [json.loads(x) for x in message.decode('utf-8').split('<||>') if x]


def login(nickname, password, current_client):
    for users in session.query(User).filter(User.NickName == nickname):
        if password == users.Password:
            data = ["OK", nickname, users.Money]
            current_client.sock.send(json.dumps(data).encode('utf-8'))


def register(nickname, password, current_client):
    a = User(nickname, password)
    session.add(a)
    session.commit()
    current_client.sock.send(json.dumps("OK").encode('utf-8'))


def search(client):
    data = None
    while data != "SEARCH":
        message = client.sock.recv(1024)
        data = process_message(message)
        if data[0][0] == "REGISTER":
            register(data[0][1], data[0][2], client)
        if data[0][0] == "LOGIN":
            login(data[0][1], data[0][2], client)
    data = ["CONNECT", "127.0.0.1:9090"]
    client.sock.send(json.dumps(data).encode('utf-8'))


Thread_clients = threading.Thread(target=add_client, )
Thread_clients.start()


