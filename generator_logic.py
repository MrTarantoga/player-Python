import generator_state
from coolname import generate_slug
import random
from collections.abc import Generator

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

def generate_random_map(
        number_of_players: int,
        max_base_level: int,
        x: tuple[int, int],
        y: tuple[int, int],
        z: tuple[int, int]
) -> Generator[generator_state.Base]:
    assert number_of_players > 2, "At least two players are mandatory"
    assert max_base_level <= 14, "Max 14 levels are defined"
    assert max_base_level >= 0, "Min 0 level are defined"
    assert x[1] - x[0] > 1, "x range must have a difference of at least 1" 
    assert y[1] - y[0] > 1, "y range must have a difference of at least 1" 
    assert z[1] - z[0] > 1, "z range must have a difference of at least 1" 

    for id in range(1, number_of_players+1):
        level = random.randint(1, max_base_level)
        max_population_for_level = base_level_config[level].max_population

        base = generator_state.Base(
                id=id,
                name=generate_slug(2),
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


def compute_action(bases: list[generator_state.Base], u_action: generator_state.UserAction):
    