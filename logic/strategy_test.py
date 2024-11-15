import unittest
import uuid

from logic.strategy import decide, euclid, get_base_level, filter_bases, survivors, defendersAtTime, iterateBases, getEnemyValues
from models.base import Base
from models.base_level import BaseLevel
from models.board_action import BoardAction
from models.game import Game
from models.game_config import GameConfig, PathConfig
from models.base_level import BaseLevel
from models.base import Base

from models.game_state import GameState
from models.player_action import PlayerAction
from models.position import Position
from models.progress import Progress

class TestStrategy(unittest.TestCase):

    our_player = 1
    def test_decide(self):
        test_base = Base(0, "test base", 1, 100, 1, 200, Position(0, 0, 0))

        test_game_state = GameState(
            [BoardAction(uuid.uuid4(), 0, 1, 2, 100, Progress(10, 4))],
            [test_base],
            GameConfig([BaseLevel(0, 0, 0)], PathConfig(0, 0)),
            Game(0, 0, 2, 2, 0),
        )

    base_levels = [
        BaseLevel(max_population=20,
            upgrade_cost=1000,
            spawn_rate=1
        ),
        BaseLevel(
            max_population=40,
            upgrade_cost=1000,
            spawn_rate=2
        ),
        BaseLevel(
            max_population=80,
            upgrade_cost=1000,
            spawn_rate=3
        )
    ]

    game_config = GameConfig(
        base_levels=base_levels,
        paths=PathConfig(
            grace_period=10,
            death_rate=1
        )
    )

    # game = Game({
    #     'uid': uid,
    #     'tick': tick,
    #     'player_count': playerCount,
    #     'remaining_players': remainingPlayers,
    #     'player': player
    # })
    
    enemy_bases = [
        # Base.fromAttributes(Position.fromAttributes(5, 0, 1), 0, 2, 2, 0, 0), 
        # Base.fromAttributes(Position.fromAttributes(7, 1, 2), 0, 3, 2, 0, 0), 
        Base(uid=0, name='Our Base', player=1, population=100, level=0, units_until_upgrade=1, position=Position(5, 0, 1)),
        Base(uid=0, name='Our Base', player=1, population=100, level=0, units_until_upgrade=1, position=Position(7, 1, 2))
    ]
    our_bases = [
        # Base.fromAttributes(Position.fromAttributes(4, 0, 1), 0, our_player, 2, 0, 0), 
        # Base.fromAttributes(Position.fromAttributes(3, 0, 2), 0, our_player, 2, 0, 0),
        Base(uid=0, name='Our Base', player=our_player, population=100, level=0, units_until_upgrade=1, position=Position(4, 0, 1)),
        Base(uid=0, name='Our Base', player=our_player, population=100, level=0, units_until_upgrade=1, position=Position(3, 0, 2))
    ]

    # def test_decide(self):
    #     test_base = Base.fromAttributes(Position.fromAttributes(0, 0, 0), 0, 0, 0, 0, 0)
    #     test_game_state = GameState.fromAttributes([BoardAction.fromAttributes(uuid.uuid4(), 0, Progress.fromAttributes(0, 0))], [test_base], GameConfig.fromAttributes([BaseLevel.fromAttributes(0, 0, 0)], PathsConfig.fromAttributes(0, 0)), Game.fromAttributes(0, 0, 0, 0, 0))

    #     want = PlayerAction(0, 0, 0)

    #     result = decide(test_game_state)
    #     self.assertEqual(str(want), str(result))

    def test_euclid(self):
        want = 1
        result = euclid(0, 0, 0, 1, 0, 0)
        self.assertEqual(want, result)
        
        want = 10
        result = euclid(7, 4, 3, 17, 6, 0)
        self.assertEqual(want, result)
    

    def test_get_base_level(self):
        want = self.base_levels[0]

        base = Base(uid=0, name='1', player=self.our_player, population=100, level=0, units_until_upgrade=1, position=Position(5, 0, 1))
        result = get_base_level(base, self.base_levels)

        self.assertEqual(want, result)


    def test_filter_bases(self):
        result_our, result_other, result_empty = filter_bases(self.enemy_bases, self.our_player)
        self.assertEqual(str([]), str(result_our))
        self.assertEqual(str(self.enemy_bases), str(result_other))
        self.assertEqual(str([]), str(result_empty))
        
        result_our, result_other, result_empty = filter_bases(self.our_bases + self.enemy_bases, self.our_player)
        self.assertEqual(str(self.our_bases), str(result_our))
        self.assertEqual(str(self.enemy_bases), str(result_other))
        self.assertEqual(str([]), str(result_empty))


    def test_survivors(self):
        bits = 10
        # our_base = Base.fromAttributes(Position.fromAttributes(18, 0, 1), 0, self.our_player, 2, 0, 0)
        our_base = Base(uid=0, name='Our Base', player=self.our_player, population=100, level=0, units_until_upgrade=1, position=Position(18, 0, 1))
        # target_base = Base.fromAttributes(Position.fromAttributes(8, 0, 1), 0, 0, 2, 0, 0)
        target_base = Base(uid=0, name='1', player=self.our_player, population=100, level=0, units_until_upgrade=1, position=Position(8, 0, 1))
        # surv = survivors(our_base, target_base,self.game_config, bits)
        # our_base = Base.fromAttributes(Position.fromAttributes(20, 0, 1), 0, self.our_player, 2, 0, 0)
        surv = survivors(our_base, target_base, self.game_config, bits)
        self.assertEqual(8, surv)


    def test_defendersAtTime(self):
        # base_level 1 --> spawn_rate 2
        # population 20
        # base = Base.fromAttributes(Position.fromAttributes(5, 0, 1), 0, 2, 20, 1, 0)
        base = Base(uid=0, name='Our Base', player=self.our_player, population=100, level=0, units_until_upgrade=1, position=Position(5, 0, 1))
        want = 24
        result = defendersAtTime(2, base, self.game_config)
        self.assertEqual(want, result)

    def test_get_enemy_values(self):
        other_bases = [
            Base(uid=0, name='A', player=1, population=100, level=0, units_until_upgrade=1, position=Position(5, 0, 1)),
            Base(uid=1, name='B', player=1, population=100, level=0, units_until_upgrade=1, position=Position(5, 0, 1))
        ]

        enemy_values = getEnemyValues(other_bases, self.game_config)

        expected = {
            'index': [0, 1],
            'growth_rate': [
                self.game_config.base_levels[other_bases[0].level].spawn_rate,
                self.game_config.base_levels[other_bases[1].level].spawn_rate
            ],
            'max_population': [
                self.game_config.base_levels[other_bases[0].level].max_population,
                self.game_config.base_levels[other_bases[1].level].max_population
            ],
            'population': [100, 100]
        }

        self.assertEqual(enemy_values, expected)

    def test_interate_bases(self):
        our_bases = [self.our_bases[0]]
        other_bases = [self.enemy_bases[0]]
        iterateBases(other_bases, our_bases, self.game_config)

    def test_attack(self):
        other_bases = self.enemy_bases[1]
        our_bases = self.our_bases[1]
        # attack(other_bases, our_bases, self.game_config)



if __name__ == "__main__":
    unittest.main()
