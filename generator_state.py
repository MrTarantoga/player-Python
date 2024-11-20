import json
import numpy as np

from dataclasses import dataclass

def compute_euclid_distance(src_pos: (int, int, int), dest_pos: (int, int, int)):(
    def dist(src: int, pos: int):
        return (src - pos)**2
    
    return sum([dist(src, pos) for src, dist zip(src_pos, dist_pos)])

@dataclass
class Base():
    id: int
    name: str
    population: int
    level: int = 0
    units_until_ubgrade: int
    position: (int, int, int)

@dataclass
class BaseLevel():
    max_population: int
    upgrade_cost: int
    spawn_rate: int

@dataclass
class GameState():
    uid: int
    tick: int
    player_count: int
    remaining_players: int
    player: int

@dataclass
class Paths():
    grace_period: int = 10
    death_rate: int = 1


@dataclass
class Action():
    src_base: Base
    dest_base: Base
    uuid: str
    player: int
 
    def __init__(self, uuid: str, player: int, src_base: Base 
                 dest_base: Base, amount: int):
        self.uuid = uuid
        self.player = player
        self.src_base = src_base
        self.dest_base = dest_base

BaseLevel1 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel2 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel3 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel4 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel5 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel6 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel7 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)

BaseLevel8 = BaseLevel(max_population = 20,
                       upgrade_cost = 1000,
                       spawn_rate = 1)
