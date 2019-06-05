from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy import create_engine
import random


engine = create_engine('sqlite:///Cards.db', echo=True)
Base = declarative_base()


class Warrior(Base):
    """"""
    __tablename__ = "German"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    cost = Column(Integer)
    armor = Column(Integer)
    range = Column(Integer)
    dmg = Column(Integer)
    hp = Column(Integer)
    speed = Column(Integer)

    def __init__(self, id, name, armor, range, hp, dmg, speed, cost):
        self.id = id
        self.name = name
        self.cost = cost
        self.armor = armor
        self.range = range
        self.dmg = dmg
        self.hp = hp
        self.speed = speed
        self.move_points = speed

    def attack(self, warrior):
        if self.dmg - warrior.armr > 0:
            damage = self.dmg - warrior.armr
            warrior.hp -= damage
        else:
            damage = 0
        return str(damage)


Base.metadata.create_all(engine)


class Hand:
    hand = [None, None, None, None]

    def __init__(self):
        for i in range(len(self.hand)):
            self.hand[i] = random.randint(1,5)


