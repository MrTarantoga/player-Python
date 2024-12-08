import generator_state
from coolname import generate_slug
import random
from collections.abc import Generator
from enum import Enum
from typing import Optional, Union

# Configuration of base levels with their corresponding classes
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
    14: generator_state.BaseLevel14
}

# Enum for different types of troop actions
class TroopAction(Enum):
    TRANSFER = 0  # Move troops between own bases
    UPGRADE = 1   # Upgrade a base
    ATTACK = 2    # Attack other players

# Exception classes for different error cases
class BaseNotFoundError(Exception):
    """
    Raised when trying to perform an action with a non-existent base
    
    Args:
        base_id: ID of the base that couldn't be found
        base_type: Type of the base ('source' or 'destination')
    """
    def __init__(self, base_id: int, base_type: str):
        self.message = f"Could not find {base_type} base with id {base_id}"
        super().__init__(self.message)

class UserIsNotAllowedToPerformOnBase(Exception):
    """
    Raised when a player tries to perform an action on a base they don't own
    
    Args:
        user_id: ID of the player attempting the action
        base_id: ID of the base they tried to act on
    """
    def __init__(self, user_id: int, base_id: int):
        self.message = f"The base {base_id} is not associated to user {user_id}"
        super().__init__(self.message)

class NotEnoughTroopsInBase(Exception):
    """
    Raised when trying to move more troops than available in a base
    
    Args:
        user_id: ID of the player attempting the action
        base_id: ID of the source base
        amount: Number of troops requested
        population: Current population of the base
    """
    def __init__(self, user_id: int, base_id: int, amount: int, population: int):
        self.message = f"The user {user_id} with base {base_id} has not enough population {population} to perform action"
        super().__init__(self.message)

class NoFurtherUpgradesPossible(Exception):
    """
    Raised when trying to upgrade a base that's already at maximum level
    
    Args:
        player: ID of the player attempting the upgrade
        base_id: ID of the base that can't be upgraded
    """
    def __init__(self, player: int, base_id: int):
        self.message = f"The player {player} exceeds the maximum level in base {base_id}"
        super().__init__(self.message)

class InsufficientBasesError(Exception):
    """
    Raised when trying to create a map with too few bases
    
    Args:
        number_of_bases: The provided number of bases
    """
    def __init__(self, number_of_bases: int):
        self.message = f"At least two bases are required, got {number_of_bases}"
        super().__init__(self.message)

class InvalidBaseLevelError(Exception):
    """
    Raised when base level is outside the valid range
    
    Args:
        level: The provided base level
        reason: Description of why the level is invalid
    """
    def __init__(self, level: int, reason: str):
        self.message = f"Invalid base level {level}: {reason}"
        super().__init__(self.message)

class InvalidCoordinateRangeError(Exception):
    """
    Raised when coordinate range is too small
    
    Args:
        dimension: The coordinate dimension (x, y, or z)
        range_tuple: The provided range tuple
    """
    def __init__(self, dimension: str, range_tuple: tuple[int, int]):
        self.message = f"{dimension} range must have a difference of at least 1, got {range_tuple}"
        super().__init__(self.message)

class PlayerCountError(Exception):
    """
    Raised when player count is invalid
    
    Args:
        player_count: Number of players
        base_count: Number of bases
        reason: Description of why the count is invalid
    """
    def __init__(self, player_count: int, base_count: int, reason: str):
        self.message = f"Invalid player count {player_count} for {base_count} bases: {reason}"
        super().__init__(self.message)

class NoBasesForPlayerError(Exception):
    """
    Raised when a player has no bases
    
    Args:
        player_id: ID of the player
    """
    def __init__(self, player_id: int):
        self.message = f"Player {player_id} has no bases"
        super().__init__(self.message)

def generate_random_map(
        number_of_bases: int,
        max_base_level: int,
        x: tuple[int, int],
        y: tuple[int, int],
        z: tuple[int, int]
) -> Generator[generator_state.Base]:
    """
    Generates a random map with bases
    
    Args:
        number_of_bases: Number of bases to generate
        max_base_level: Maximum level for bases
        x, y, z: Tuples containing min/max coordinates for each dimension
    
    Yields:
        Base: Generated base objects
    """
    if number_of_bases <= 2:
        raise InsufficientBasesError(number_of_bases)
    if max_base_level > 14:
        raise InvalidBaseLevelError(max_base_level, "maximum level is 14")
    if max_base_level < 0:
        raise InvalidBaseLevelError(max_base_level, "minimum level is 0")
    if x[1] - x[0] <= 1:
        raise InvalidCoordinateRangeError("x", x)
    if y[1] - y[0] <= 1:
        raise InvalidCoordinateRangeError("y", y)
    if z[1] - z[0] <= 1:
        raise InvalidCoordinateRangeError("z", z)

    for id in range(1, number_of_bases+1):
        level = random.randint(1, max_base_level)
        max_population_for_level = base_level_config[level].max_population

        base = generator_state.Base(
                uid=id,
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
    """
    Randomly assigns players to bases
    
    Args:
        bases: List of all bases
        players: List of player IDs
    
    Returns:
        List of bases with assigned players
    """
    if len(players) > len(bases):
        raise PlayerCountError(len(players), len(bases), "number of players cannot exceed number of bases")
    if len(players) < 2:
        raise PlayerCountError(len(players), len(bases), "at least two players are required")
    
    # Ensure each player gets at least one base
    bases_to_assign = random.sample(bases, len(players))
    for base, player in zip(bases_to_assign, players):
        base.player = player
    
    return bases

def define_action(bases: list[generator_state.Base], u_action: generator_state.UserAction, game_state: generator_state.GameState) -> TroopAction:
    """
    Determines the type of action based on source and destination base
    
    Args:
        bases: List of all bases
        u_action: User action
        game_state: Current game state
    
    Returns:
        TroopAction: Type of action (TRANSFER, UPGRADE or ATTACK)
    """
    player = game_state.player
    player_bases_uid = []
    other_bases_uid = []

    for base in bases:
        if base.player == player:
            player_bases_uid.append(base.uid)
        else:
            other_bases_uid.append(base.uid)

    if len(player_bases_uid) == 0:
        raise NoBasesForPlayerError(player)

    if u_action.src_base not in player_bases_uid:
        raise UserIsNotAllowedToPerformOnBase(game_state.player, u_action.src_base)

    if u_action.dest_base in player_bases_uid:
        if u_action.dest_base == u_action.src_base:
            return TroopAction.UPGRADE
        else:
            return TroopAction.TRANSFER
    else:
        return TroopAction.ATTACK

    
def compute_user_action(bases: list[generator_state.Base], u_action: generator_state.UserAction, game_state: generator_state.GameState) -> Union[generator_state.Action, list[generator_state.Base]]:
    """
    Processes a user action and creates a game action from it
    
    Args:
        bases: List of all bases
        u_action: User action
        game_state: Current game state
    
    Returns:
        Union[Action, list[Base]]: Either a new Action or the updated base list (for upgrades)
    
    Raises:
        BaseNotFoundError: If the source base cannot be found
        NotEnoughTroopsInBase: If there aren't enough troops for the action
        NoFurtherUpgradesPossible: If base is already at max level
    """
    troop_action = define_action(bases, u_action, game_state)
    
    # Find source and destination bases
    src_base = None
    dest_base = None
    for base in bases:
        if base.uid == u_action.src_base:
            src_base = base
        if base.uid == u_action.dest_base:
            dest_base = base
        if src_base is not None and dest_base is not None:
            break
            
    if src_base is None:
        raise BaseNotFoundError(u_action.src_base, "source")
    if dest_base is None:
        raise BaseNotFoundError(u_action.dest_base, "destination")
    
    # Prüfe Truppenverfügbarkeit
    if src_base.population < u_action.amount:
        raise NotEnoughTroopsInBase(
            game_state.player, 
            src_base.uid, 
            u_action.amount, 
            src_base.population
        )
    
    # Handle Upgrade
    if troop_action == TroopAction.UPGRADE:
        if src_base.level >= 14:
            raise NoFurtherUpgradesPossible(game_state.player, src_base.uid)
            
        # Calculate total available troops (current + transferred)
        total_troops = src_base.population + u_action.amount
        
        # Find index of source base in list
        src_base_idx = next(i for i, base in enumerate(bases) if base.uid == src_base.uid)
        
        # Check if we have enough troops for upgrade
        if total_troops >= src_base.units_until_upgrade:
            bases[src_base_idx].level += 1  # Update level in list
            # New population is total troops minus upgrade cost
            bases[src_base_idx].population = total_troops - src_base.units_until_upgrade
        else:
            # If not enough for upgrade, just add the transferred troops
            bases[src_base_idx].population = total_troops
        return bases
    
    # Handle Transfer/Attack
    action = generator_state.Action(
        game_state.player,
        src_base,  # Pass the base object, not the population
        dest_base,  # Pass the base object
        u_action.amount
    )
    src_base.population -= u_action.amount  # Update population after creating action
    return action

def compute_action(bases: list[generator_state.Base], action: generator_state.Action) -> Union[generator_state.Action, generator_state.Base, None]:
    """
    Computes a single movement step for an ongoing action
    
    Args:
        bases: List of all bases
        action: Action to process
    
    Returns:
        - Action: If troops are still moving
        - Base: If troops have reached their destination
        - None: If all troops have died
    
    Raises:
        BaseNotFoundError: When source or destination base cannot be found
    """
    # Finde Quell- und Zielbasis
    src_base = None
    dest_base = None
    for base in bases:
        if base.uid == action.src_base:
            src_base = base
        elif base.uid == action.dest_base:
            dest_base = base
        if src_base is not None and dest_base is not None:
            break

    if src_base is None:
        raise BaseNotFoundError(action.src_base, "source")
    if dest_base is None:
        raise BaseNotFoundError(action.dest_base, "destination")

    # Berechne die Gesamtdistanz zwischen den Basen
    total_distance = generator_state.compute_euclid_distance(src_base.position, dest_base.position)
    
    # Erhöhe travelled um 1 für diesen Tick
    action.travelled += 1
    
    # Wenn noch nicht am Ziel, bewege weiter
    if action.travelled < total_distance:
        # Nach 10 Schritten stirbt pro Tick ein Soldat
        if action.travelled > 10:
            action.amount = max(0, action.amount - 1)
            if action.amount == 0:
                return None
        return action
    
    # Truppen sind am Ziel angekommen
    dest_base.population += action.amount
    return dest_base

    
