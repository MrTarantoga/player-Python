import generator_state
from coolname import generate_slug
import random
from collections.abc import Generator
from enum import Enum
from typing import Optional

base_level_config = {
    1: generator_state.BaseLevel1,
    2: generator_state.BaseLevel2,
    3: generator_state.BaseLevel3,
    4: generator_state.BaseLevel4,
    5: generator_state.BaseLevel5,
    6: generator_state.BaseLevel6,
    7: generator_state.BaseLevel7,
    8: generator_state.BaseLevel8,
    9: generator_state.BaseLevel9,
    10: generator_state.BaseLevel10,
    11: generator_state.BaseLevel11,
    12: generator_state.BaseLevel12,
    13: generator_state.BaseLevel13,
    13: generator_state.BaseLevel14
}

class TroopAction(Enum):
    TRANSFER = 0
    UPGRADE = 1
    ATTACK = 2

def generate_random_map(
        number_of_bases: int,
        max_base_level: int,
        x: tuple[int, int],
        y: tuple[int, int],
        z: tuple[int, int]
) -> Generator[generator_state.Base]:
    assert number_of_bases > 2, "At least two bases are mandatory"
    assert max_base_level <= 14, "Max 14 levels are defined"
    assert max_base_level >= 0, "Min 0 level are defined"
    assert x[1] - x[0] > 1, "x range must have a difference of at least 1" 
    assert y[1] - y[0] > 1, "y range must have a difference of at least 1" 
    assert z[1] - z[0] > 1, "z range must have a difference of at least 1"


    for id in range(1, number_of_bases+1):
        level = random.randint(1, max_base_level)
        max_population_for_level = base_level_config[level].max_population

        base = generator_state.Base(
                id=id,
                name=generate_slug(2),
                player=0, # Not associated base (reserved caracter)
                population=random.randint(1, max_population_for_level),
                level=level,
                units_until_upgrade=base_level_config[level].upgrade_cost,
                position=(
                    random.randint(x[0], x[1]),
                    random.randint(y[0], y[1]),
                    random.randint(z[0], z[1])
                )
            )
        yield base

def assert_player_to_bases(bases: list[generator_state.Base], players: list[int]) -> list[generator_state.Base]:
    assert len(players) <= len(bases), "The number of players cannot exceed, the number of bases"
    assert len(players) >= 2, "At least two players are mandatory"
    for player in random.shuffle(players):
        bases[random.randint(0, len(bases)-1)].player = player
    return bases


class UserIsNotAllowedToPerformOnBase(Exception):
    def __init__(self, user_id: int, base_id: int):
        self.message = f"The base {base_id} is not associated to user {user_id}"
        super().__init__(self.message)

class NotEnoughTroopsInBase(Exception):
    def __init__(self, user_id: int, base_id: int, amount: int, population: int):
        self.message = f"The user {user_id} with base {base_id} has not enough population {population} to perform action"
        super().__init__(self.message)

class NoFurtherUpgradesPossible(Exception):
    def __init__(self, player: int, base_id: int):
        self.message = f"The player {player} exceeds the maximum level in base {base_id}"
        super().__init__(self.message)

def define_action(bases: list[generator_state.Base], u_action: generator_state.UserAction, game_state: generator_state.GameState) -> TroopAction:
    player = game_state.player
    player_bases_uid = []
    other_bases_uid = []

    for base in bases:
        if base.player == player:
            player_bases_uid.append(base.uid)
        else:
            other_bases_uid.append(base.uid)

    assert len(player_bases_uid) > 0, "Player has no base"

    if u_action.src_base not in player_bases_uid:
        raise UserIsNotAllowedToPerformOnBase(game_state.player, u_action.src_base)

    if u_action.dest_base in player_bases_uid:
        if u_action.dest_base == u_action.src_base:
            return TroopAction.UPGRADE
        else:
            return TroopAction.TRANSFER
    else:
        return TroopAction.ATTACK

    
def compute_user_action(bases: list[generator_state.Base], u_action: generator_state.UserAction, game_state: generator_state.GameState) -> Optional[generator_state.Action, list[generator_state.Base]]:
    troop_action = define_action(bases, u_action, game_state)
    for idx, base in enumerate(bases):
        if base.uid == u_action.uid:
            player_base_idx = idx 

            if base.population - u_action.amount < 0:
                raise NotEnoughTroopsInBase(game_state.player, base.uid, u_action.amount, base.population)
            else:
                new_base_population = base.population - u_action.amount
                return bases
    if troop_action == TroopAction.UPGRADE:
        if bases[player_base_idx].units_until_upgrade - new_base_population <= 0:
            if bases[player_base_idx].level < 14:
                bases[player_base_idx].level += 1
            else:
                raise NoFurtherUpgradesPossible(game_state.player, bases[player_base_idx].uid)
        bases[player_base_idx].population = new_base_population
    else:
        action = generator_state.Action(
            game_state.player,
            u_action.src_base,
            u_action.dest_base,
            u_action.amount
        )
        return action

def compute_action(bases: list[generator_state.Base], action: generator_state.Action):
    
