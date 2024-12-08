"""
Core data structures and state management for the game.
Contains base configurations, action definitions, and game state tracking.
"""

from uuid import uuid4, UUID
from dataclasses import dataclass

class NegativePopulationError(Exception):
    """
    Raised when trying to set a negative population value
    
    Args:
        population: The invalid population value
    """
    def __init__(self, population: int):
        self.message = f"Population cannot be negative, got {population}"
        super().__init__(self.message)

class NegativeUnitsError(Exception):
    """
    Raised when trying to set a negative number of units
    
    Args:
        units: The invalid units value
    """
    def __init__(self, units: int):
        self.message = f"Cannot have negative units, got {units}"
        super().__init__(self.message)

class InvalidBaseLevelError(Exception):
    """
    Raised when trying to set an invalid base level
    
    Args:
        level: The invalid level value
    """
    def __init__(self, level: int):
        self.message = f"Base level must be between 0 and 14, got {level}"
        super().__init__(self.message)

class InvalidTroopAmountError(Exception):
    """
    Raised when trying to move an invalid number of troops
    
    Args:
        amount: The invalid amount value
    """
    def __init__(self, amount: int):
        self.message = f"Cannot send {amount} troops (must be positive)"
        super().__init__(self.message)

class InsufficientTroopsError(Exception):
    """
    Raised when trying to move more troops than available
    
    Args:
        requested: Number of troops requested
        available: Number of troops available
    """
    def __init__(self, requested: int, available: int):
        self.message = f"Insufficient troops: requested {requested}, but only {available} available"
        super().__init__(self.message)

def compute_euclid_distance(src_pos: tuple[int, int, int], dest_pos: tuple[int, int, int]) -> float:
    """
    Calculates the Euclidean distance between two 3D points
    
    Args:
        src_pos: Source position (x, y, z)
        dest_pos: Destination position (x, y, z)
    
    Returns:
        float: Euclidean distance between the points
    """
    def dist(src: int, pos: int) -> float:
        return (src - pos)**2
    
    return sum([dist(src, pos) for src, pos in zip(src_pos, dest_pos)])

@dataclass
class Base:
    """
    Represents a base in the game
    
    Attributes:
        uid: Unique identifier for the base
        name: Display name of the base
        player: ID of the player who owns the base (0 = unowned)
        population: Current number of troops in the base
        units_until_upgrade: Number of units needed for next upgrade
        position: 3D coordinates of the base (x, y, z)
        level: Current level of the base (1-14)
    """
    uid: int
    name: str
    player: int
    population: int
    units_until_upgrade: int
    position: tuple[int, int, int]
    level: int

    def __init__(self, uid: int, name: str, player: int, population: int, units_until_upgrade: int,
                 position: tuple[int, int, int], level: int):
        """
        Initialize a new base with validation checks
        
        Raises:
            NegativePopulationError: If population is negative
            NegativeUnitsError: If units_until_upgrade is negative
            InvalidBaseLevelError: If level is not between 0 and 14
        """
        if population < 0:
            raise NegativePopulationError(population)
        if units_until_upgrade < 0:
            raise NegativeUnitsError(units_until_upgrade)
        if level < 0 or level > 14:
            raise InvalidBaseLevelError(level)
            
        self.uid = uid
        self.name = name
        self.player = player
        self.population = population
        self.units_until_upgrade = units_until_upgrade
        self.position = position
        self.level = level
 
    def to_dict(self) -> dict:
        """Convert base data to dictionary format for serialization"""
        return {
            "uid": self.uid,
            "name": self.name,
            "player": self.player,
            "population": self.population,
            "level": self.level, 
            "units_until_upgrade": self.units_until_upgrade,
            "position": {
                "x": self.position[0],
                "y": self.position[1],
                "z": self.position[2]
            }
        }

    def update_population(self, amount: int) -> None:
        """
        Update the base population
        
        Args:
            amount: Amount to add (can be negative)
            
        Raises:
            NegativePopulationError: If resulting population would be negative
        """
        new_population = self.population + amount
        if new_population < 0:
            raise NegativePopulationError(new_population)
        self.population = new_population

@dataclass
class BaseLevel:
    """
    Configuration for each base level
    
    Attributes:
        max_population: Maximum troops the base can hold
        upgrade_cost: Number of troops needed to upgrade to next level
        spawn_rate: Number of new troops generated per tick
    """
    max_population: int
    upgrade_cost: int
    spawn_rate: int

    def to_dict(self) -> dict:
        """Convert level configuration to dictionary format"""
        return {
            "max_population": self.max_population,
            "upgrade_cost": self.upgrade_cost,
            "spawn_rate": self.spawn_rate
        }

@dataclass
class UserAction:
    """
    Represents a player's action request
    
    Attributes:
        src_base: Source base for the action
        dest_base: Target base for the action
        amount: Number of troops involved
    """
    src_base: int
    dest_base: int
    amount: int

    def __init__(self, src_base: Base, dest_base: Base, amount: int):
        """
        Initialize a new user action with validation
        
        Raises:
            AssertionError: If amount is invalid or insufficient troops
        """
        if amount <= 0:
            raise InvalidTroopAmountError(amount)
        if src_base.population < amount:
            raise InsufficientTroopsError(amount, src_base.population)

        self.src_base = src_base.uid
        self.dest_base = dest_base.uid
        self.amount = amount

    def to_dict(self) -> dict:
        """Convert action to dictionary format"""
        return {
            "src": self.src_base,
            "dest": self.dest_base,
            "amount": self.amount
        }

@dataclass
class GameState:
    """
    Current state of the game
    
    Attributes:
        uid: Unique game identifier
        tick: Current game tick
        player_count: Total number of players
        remaining_players: Number of active players
        player: Current player's ID
    """
    uid: int
    tick: int
    player_count: int
    remaining_players: int
    player: int

    def __post_init__(self):
        """Validate game state values"""
        if self.tick < 0:
            raise ValueError("Tick cannot be negative")
        if self.player_count < 2:
            raise ValueError("Need at least 2 players")
        if self.remaining_players > self.player_count:
            raise ValueError("Cannot have more remaining than total players")
        if self.player < 1:
            raise ValueError("Player IDs must be positive")

    def to_dict(self) -> dict:
        """Convert game state to dictionary format"""
        return {
            "uid": self.uid,
            "tick": self.tick,
            "player_count": self.player_count,
            "remaining_players": self.remaining_players,
            "player": self.player
        }

@dataclass
class Paths:
    """
    Configuration for troop movement mechanics
    
    Attributes:
        grace_period: Number of ticks before troops start dying
        death_rate: Number of troops that die per tick after grace period
    """
    grace_period: int = 10
    death_rate: int = 1

    def to_dict(self) -> dict:
        """Convert path configuration to dictionary format"""
        return {
            "grace_period": self.grace_period,
            "death_rate": self.death_rate
        }

@dataclass
class Action:
    """
    Represents an ongoing action in the game
    
    Attributes:
        src_base: Source base ID
        dest_base: Destination base ID
        src_position: Source position
        dest_position: Destination position
        uuid: Unique identifier for the action
        player: ID of the player performing the action
        amount: Number of troops involved
        travelled: Distance troops have moved
    """
    src_base: int
    dest_base: int
    src_position: tuple[int, int, int]
    dest_position: tuple[int, int, int]
    uuid: UUID
    player: int
    amount: int
    travelled: int
 
    def __init__(self, player: int, src_base: Base, dest_base: Base, amount: int):
        """
        Initialize a new action
        
        Args:
            player: ID of the player performing the action
            src_base: Source base object
            dest_base: Destination base object
            amount: Number of troops to move
        """
        self.uuid = uuid4()
        self.player = player
        self.src_base = src_base.uid
        self.dest_base = dest_base.uid
        self.src_position = src_base.position
        self.dest_position = dest_base.position
        self.amount = amount
        self.travelled = 0

    def to_dict(self) -> dict:
        """Convert action to dictionary format with progress information"""
        return {
            "uuid": self.uuid,
            "src": self.src_base,
            "dest": self.dest_base,
            "player": self.player,
            "amount": self.amount,
            "progress": {
                "distance": compute_euclid_distance(self.src_position, self.dest_position),
                "amount": self.travelled
            }
        }

# Base level configurations with increasing capabilities
BaseLevel1 = BaseLevel(max_population=20, upgrade_cost=10, spawn_rate=1)
BaseLevel2 = BaseLevel(max_population=40, upgrade_cost=20, spawn_rate=2)
BaseLevel3 = BaseLevel(max_population=80, upgrade_cost=30, spawn_rate=3)
BaseLevel4 = BaseLevel(max_population=100, upgrade_cost=40, spawn_rate=4)
BaseLevel5 = BaseLevel(max_population=200, upgrade_cost=50, spawn_rate=5)
BaseLevel6 = BaseLevel(max_population=300, upgrade_cost=100, spawn_rate=6)
BaseLevel7 = BaseLevel(max_population=400, upgrade_cost=200, spawn_rate=7)
BaseLevel8 = BaseLevel(max_population=500, upgrade_cost=400, spawn_rate=8)
BaseLevel9 = BaseLevel(max_population=600, upgrade_cost=600, spawn_rate=9)
BaseLevel10 = BaseLevel(max_population=700, upgrade_cost=800, spawn_rate=10)
BaseLevel11 = BaseLevel(max_population=800, upgrade_cost=1000, spawn_rate=15)
BaseLevel12 = BaseLevel(max_population=900, upgrade_cost=1500, spawn_rate=20)
BaseLevel13 = BaseLevel(max_population=1000, upgrade_cost=2000, spawn_rate=25)
BaseLevel14 = BaseLevel(max_population=2000, upgrade_cost=3000, spawn_rate=50)

