from uuid import uuid4, UUID
from dataclasses import dataclass

def compute_euclid_distance(src_pos: tuple[int, int, int], dest_pos: tuple[int, int, int]):
    def dist(src: int, pos: int):
        return (src - pos)**2
    
    return sum([dist(src, pos) for src, pos in zip(src_pos, dist)])

@dataclass
class Base():
    uid: int
    name: str
    player: int
    population: int
    units_until_upgrade: int
    position: tuple[int, int, int]
    level: int

    def __init__(self, uid: int, name: str, player: str, population: int, units_until_upgrade: int,
                 position: tuple[int, int, int], level: int):
        assert population >= 0, "Population cannot be negativ"
        assert units_until_upgrade >= 0, "We cannot have negative units"
        assert level >= 0 and level <= 14, "Only level between 0 and 14 are allowed"
        self.uid = uid
        self.name = name
        self.player = player
        self.population = population
        self.units_until_upgrade = units_until_upgrade
        self.position = position
        self.level = level
 
    def to_dict(self):
        return {
            "uid": self.uid,
            "name": self.name,
            "player": self.player,
            "population": self.population,
            "level": self.level, 
            "units_until_upgrade": self.units_until_upgrade,
            "position":
            {
                "x": self.position[0],
                "y": self.position[1],
                "z": self.position[2]
            }
        }

@dataclass
class BaseLevel():
    max_population: int
    upgrade_cost: int
    spawn_rate: int

    def to_dict(self):
        return {
            "max_population": self.max_population,
            "upgrade_cost": self.upgrade_cost,
            "spawn_rate": self.spawn_rate
        }

@dataclass
class UserAction():
    src_base: Base
    dest_base: Base
    amount: int

    def __init__(self, src_base: Base, dest_base: Base, amount: int):
        assert amount > 0, "We cannot send 0 or negativ amount of bits"
        assert src_base.population >= amount, "You can only send troops you have"

        self.src_base = src_base
        self.dest_base = dest_base
        self.amount = amount

    def to_dict(self):
        return {
            "src": self.src_base.uid,
            "dest": self.dest_base.uid,
            "amount": self.amount
        }

@dataclass
class GameState():
    uid: int
    tick: int
    player_count: int
    remaining_players: int
    player: int

    def to_dict(self):
        return {
            "uid": self.uid,
            "tick": self.tick,
            "player_count": self.player_count,
            "remaining_players": self.remaining_players,
            "player": self.player
        }

@dataclass
class Paths():
    grace_period: int = 10
    death_rate: int = 1

    def to_dict(self):
        return {
            "grace_period": self.grace_period,
            "death_rate": self.death_rate
        }

@dataclass
class Action():
    src_base: Base
    dest_base: Base
    uuid: UUID
    player: int
    amount: int
    travelled: int
 
    def __init__(self, player: int, src_base: Base,
                 dest_base: Base, amount: int):
        self.uuid = uuid4()
        self.player = player
        self.src_base = src_base
        self.dest_base = dest_base
        self.amount = amount
        self.travelled = 0

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "src": self.src_base.uid,
            "dest": self.dest_base.uid,
            "player": self.player,
            "amount": self.amount,
            "progress": {
                "distance": compute_euclid_distance(self.src_base.position, self.dest_base.position),
                "amount": self.travelled
            }
        }


BaseLevel1 = BaseLevel(max_population = 20,
                       upgrade_cost = 10,
                       spawn_rate = 1)

BaseLevel2 = BaseLevel(max_population = 40,
                       upgrade_cost = 20,
                       spawn_rate = 2)

BaseLevel3 = BaseLevel(max_population = 80,
                       upgrade_cost = 30,
                       spawn_rate = 3)

BaseLevel4 = BaseLevel(max_population = 100,
                       upgrade_cost = 40,
                       spawn_rate = 4)

BaseLevel5 = BaseLevel(max_population = 200,
                       upgrade_cost = 50,
                       spawn_rate = 5)

BaseLevel6 = BaseLevel(max_population = 300,
                       upgrade_cost = 100,
                       spawn_rate = 6)

BaseLevel7 = BaseLevel(max_population = 400,
                       upgrade_cost = 200,
                       spawn_rate = 7)

BaseLevel8 = BaseLevel(max_population = 500,
                       upgrade_cost = 400,
                       spawn_rate = 8)

BaseLevel9 = BaseLevel(max_population = 600,
                       upgrade_cost = 600,
                       spawn_rate = 9)

BaseLevel10 = BaseLevel(max_population = 700,
                       upgrade_cost = 800,
                       spawn_rate = 10)

BaseLevel11 = BaseLevel(max_population = 800,
                       upgrade_cost = 1000,
                       spawn_rate = 15)

BaseLevel12 = BaseLevel(max_population = 900,
                       upgrade_cost = 1500,
                       spawn_rate = 20)

BaseLevel13 = BaseLevel(max_population = 1000,
                       upgrade_cost = 2000,
                       spawn_rate = 25)

BaseLevel14 = BaseLevel(max_population = 2000,
                       upgrade_cost = 3000,
                       spawn_rate = 50)

