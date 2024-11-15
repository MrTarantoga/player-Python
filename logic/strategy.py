from typing import List
from models.game_state import GameState
from models.game_config import GameConfig, BaseLevel
from models.player_action import PlayerAction
from models.base import Base
# import numpy as np
import math
import pandas as pd

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

# Das muss weg
def populationAverage(bases: list[Base]):
    basesPopulation=0
    for base in bases:
        basesPopulation+=base.population

    return basesPopulation/len(bases)

def getEnemyValues(otherBases: list[Base], config: GameConfig):
    data = {}
    enemyUid = []
    enemyGrowthRate = []
    enemyMaxPopulation = []
    enemyPopulation = []

    for targetBase in otherBases:
        enemyUid.append(targetBase.uid)
        enemyGrowthRate.append(config.base_levels[targetBase.level].spawn_rate)
        enemyMaxPopulation.append(config.base_levels[targetBase.level].max_population)
        enemyPopulation.append(targetBase.population)

    data["index"] = enemyUid
    data["growth_rate"] = enemyGrowthRate
    data["max_population"] = enemyMaxPopulation
    data["population"] = enemyPopulation

    return data

# Generate Array with ale enemies and the costs to conquer them
def iterateBases(otherBases: list[Base], ourBases: list[Base], config: GameConfig) -> list[PlayerAction]:
    bestTargetBase: list[PlayerAction]  = []

    #allBases = pd.DataFrame(data)
    data = getEnemyValues(otherBases, config)

    for ourBase in ourBases:
        enemydist = []
        for targetBase in otherBases:
            
            #enemydist[targetBase.uid] = (get_base_distance(ourBase,targetBase) - config.paths.grace_period)
            enemydist.append(get_base_distance(ourBase,targetBase))
        data[ourBase.uid] = enemydist

    allBases = pd.DataFrame(data)
    allBases = allBases.set_index(["index", "growth_rate", "max_population", "population"])
    allBases_distanceCosts = allBases.copy()
    # add death_rate for euclidean distance to enemy
    allBases_distanceCosts = (allBases_distanceCosts.loc[:] - config.paths.grace_period).clip(lower=0) * config.paths.death_rate

    # add gain of enemy during travel (TODO: cap gain by max_population)
    allBases_distanceCosts = allBases_distanceCosts.loc[:] + (allBases * allBases.index.get_level_values("growth_rate"))
    # add population of enemy at travel start
    allBases_distanceCosts = allBases_distanceCosts.loc[:] + allBases.index.get_level_values("population")

    # search for all possible targets
    for ourBase in ourBases:
        possibleTargets = allBases_distanceCosts[ourBase.uid].sort_values(ascending=True).copy()
        for possibleTargetIndex, possibleTarget in possibleTargets.items():
            if possibleTarget < ourBase.population:
                # add enemy as target
                bestTargetBase.append([ourBase.uid, possibleTargetIndex[0], possibleTarget + 1])
                # reduce population of our ally
                ourBase.population -= possibleTarget + 1
                # eliminate enemy from possible targets (next ally must attack other enemies)
                allBases_distanceCosts.drop([possibleTargetIndex])
            else:
                break
    
    return bestTargetBase


def decide(gameState: GameState) -> List[PlayerAction]:
    # TODO: place your logic here
    
    # Our player
    our_player = gameState.game.player

    bases = gameState.bases

    #global minDefenders 
    #minDefenders = populationAverage(bases)/2
    our_bases, other_bases, empty_bases = filter_bases(bases, our_player)
    
    return iterateBases(other_bases, our_bases + empty_bases, gameState.config)

    