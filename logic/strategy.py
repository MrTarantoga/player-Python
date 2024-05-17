from typing import List
from models.game_state import GameState
from models.game_config import GameConfig, BaseLevel
from models.player_action import PlayerAction
from models.base import Base
# import numpy as np
import math

minDefenders = 5
def euclid(x1: int, y1: int, z1: int, x2: int, y2: int, z2: int):
    return math.floor(math.sqrt(((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)))

def get_base_distance(base_1: Base, base_2: Base) -> float:
    return euclid(
        base_1.position.x, base_1.position.y, base_1.position.z,
        base_2.position.x, base_2.position.y, base_2.position.z
    )

def get_base_level(base: Base, base_levels: list[BaseLevel]) -> BaseLevel:
    return base_levels[base.level]
    

def filter_bases(bases: list[Base], our_player: int) -> tuple[list[Base], list[Base], list[Base]]:
    our_bases = []
    other_bases = []
    empty_bases = []

    for base in bases:
        if base.player == our_player:
            our_bases.append(base)
        elif base.player == 0:
            empty_bases.append(base)
        else:
            other_bases.append(base)
    
    return (our_bases, other_bases, empty_bases)

# def get_nearest_base(bases: list[Base], src_base: Base) -> Base:
#     nearest_base = bases[0]
    
#     for base in bases:
#         if get_nearest_base(src_base, base)

def survivors(srcBase: Base, destBase: Base, config: GameConfig, bits: int) -> int:
    grace_period = config.paths.grace_period
    death_rate = config.paths.death_rate
    deaths = max((get_base_distance(srcBase,destBase) - grace_period), 0) * death_rate
    return max(bits - deaths, 0)

def defendersAtTime(destTime: int, destBase: Base, config: GameConfig) -> int:
    spawn_rate = get_base_level(destBase, config.base_levels).spawn_rate
    return destBase.population+destTime*spawn_rate
        
def attackDecision(attackers: int, destBase: Base, config: GameConfig, destTime: int) -> int:
    return attackers-defendersAtTime(destTime,destBase,config)

def populationAverage(bases: list[Base]):
    basesPopulation=0
    for base in bases:
        basesPopulation+=base.population

    return basesPopulation/len(bases)

def iterateBases(otherBases: list[Base], ourBases: list[Base], config: GameConfig):
    bestTargetBase=None
    mostSurvivors=0
    for targetBase in otherBases:
        sumSurvivors=0
        for selectedBase in ourBases:
            sumSurvivors+=survivors(selectedBase, targetBase, config, max(selectedBase.population-minDefenders,0)) #TODO wert minDefenders dynamisch generieren
        if sumSurvivors>mostSurvivors:
            mostSurvivors = sumSurvivors
            bestTargetBase = targetBase
    
    return bestTargetBase

def attack(otherBases: list[Base], ourBases: list[Base], config: GameConfig) -> list[PlayerAction]:
    attackList: list[PlayerAction] = []
    targetBase = iterateBases(otherBases, ourBases, config) 
    if targetBase is not None:
        for srcBase in ourBases:
            attackList.append([srcBase.uid,targetBase.uid,srcBase.population-minDefenders])
        return attackList
    
    return attackList


def decide(gameState: GameState) -> List[PlayerAction]:
    # TODO: place your logic here
    
    
    # Our player
    our_player = gameState.game.player

    bases = gameState.bases

    #global minDefenders 
    #minDefenders = populationAverage(bases)/2
    our_bases, other_bases, empty_bases = filter_bases(bases, our_player)
    

    return attack(other_bases,our_bases.append(empty_bases),gameState.config)

    