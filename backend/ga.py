import asyncio
import math
import random

from models import GAConfig, Point

DIRECTIONS = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
    (-1, -1),
    (-1, 1),
    (1, -1),
    (1, 1),
]


def is_unblocked(row: int, column: int, grid: list[list[int]]) -> bool:
    return grid[row][column] == 0


def is_valid_boundary(x: int, y: int, grid: list[list[int]]) -> bool:
    max_y = len(grid)
    max_x = len(grid[0]) if max_y > 0 else 0
    return 0 <= y < max_y and 0 <= x < max_x


def euclidean_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def count_blocked_neighbors(x: int, y: int, grid: list[list[int]]) -> int:
    blocked_neighbors = 0

    for dx, dy in DIRECTIONS:
        next_x = x + dx
        next_y = y + dy

        if not is_valid_boundary(next_x, next_y, grid) or not is_unblocked(next_y, next_x, grid):
            blocked_neighbors += 1

    return blocked_neighbors


def get_euclidean_distance(p1: Point, p2: dict) -> float:
    return euclidean_distance(p1.x, p1.y, p2["x"], p2["y"])


def clamp_config(config: GAConfig | None) -> GAConfig:
    config = config or GAConfig()

    population_size = max(2, min(config.population_size, 300))
    dna_length = max(5, min(config.dna_length, 500))
    elite_count = max(1, min(config.elite_count, population_size))
    max_generations = max(1, min(config.max_generations, 500))

    mutation_rate = config.mutation_rate
    if mutation_rate > 1:
        mutation_rate /= 100.0
    mutation_rate = max(0.0, min(mutation_rate, 1.0))

    return GAConfig(
        population_size=population_size,
        dna_length=dna_length,
        mutation_rate=mutation_rate,
        elite_count=elite_count,
        max_generations=max_generations,
    )


def create_random_dna(length: int) -> list[tuple[int, int]]:
    return [random.choice(DIRECTIONS) for _ in range(length)]


def clone_path(path: list[tuple[int, int]]) -> list[dict]:
    return [{"x": x, "y": y} for x, y in path]


def simulate_agent(start: Point, goal: Point, grid: list[list[int]], dna: list[tuple[int, int]]) -> dict:
    current_x = start.x
    current_y = start.y
    path = [(current_x, current_y)]
    visited_counts = {(current_x, current_y): 1}

    reached_goal = False
    hit_wall = False
    steps_taken = 0

    for step_index, (dx, dy) in enumerate(dna, start=1):
        next_x = current_x + dx
        next_y = current_y + dy

        if not is_valid_boundary(next_x, next_y, grid) or not is_unblocked(next_y, next_x, grid):
            hit_wall = True
            break

        current_x = next_x
        current_y = next_y
        path.append((current_x, current_y))
        visited_counts[(current_x, current_y)] = visited_counts.get((current_x, current_y), 0) + 1
        steps_taken = step_index

        if current_x == goal.x and current_y == goal.y:
            reached_goal = True
            break

    distance_to_goal = euclidean_distance(current_x, current_y, goal.x, goal.y)
    repeated_steps = sum(count - 1 for count in visited_counts.values() if count > 1)
    path_length = len(path) - 1
    blocked_neighbors = count_blocked_neighbors(current_x, current_y, grid)
    dead_end_penalty = 0

    if blocked_neighbors >= 7:
        dead_end_penalty = 180
    elif blocked_neighbors >= 5:
        dead_end_penalty = 60

    if reached_goal:
        fitness = 1_000_000 - (steps_taken * 15) - repeated_steps
    else:
        fitness = -(distance_to_goal * 100) - (path_length * 0.5) - (repeated_steps * 5)
        if hit_wall:
            fitness -= 250
        fitness -= blocked_neighbors * 8
        fitness -= dead_end_penalty

    return {
        "dna": dna,
        "path": clone_path(path),
        "final_position": {"x": current_x, "y": current_y},
        "reached_goal": reached_goal,
        "hit_wall": hit_wall,
        "distance_to_goal": distance_to_goal,
        "fitness": fitness,
        "steps_taken": steps_taken,
        "path_length": path_length,
    }


def tournament_select(scored_population: list[dict], tournament_size: int = 3) -> list[tuple[int, int]]:
    sample_size = min(tournament_size, len(scored_population))
    competitors = random.sample(scored_population, sample_size)
    winner = max(competitors, key=lambda agent: agent["fitness"])
    return winner["dna"]


def crossover(parent_a: list[tuple[int, int]], parent_b: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if len(parent_a) <= 2:
        return parent_a[:]

    cut_points = sorted(random.sample(range(1, len(parent_a)), 2))
    first_cut, second_cut = cut_points

    return (
        parent_a[:first_cut]
        + parent_b[first_cut:second_cut]
        + parent_a[second_cut:]
    )


def mutate(dna: list[tuple[int, int]], mutation_rate: float) -> list[tuple[int, int]]:
    mutated = dna[:]
    for index in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[index] = random.choice(DIRECTIONS)
    return mutated


def build_next_generation(scored_population: list[dict], config: GAConfig) -> list[list[tuple[int, int]]]:
    sorted_population = sorted(scored_population, key=lambda agent: agent["fitness"], reverse=True)
    next_generation = [agent["dna"][:] for agent in sorted_population[:config.elite_count]]
    immigrant_count = max(2, config.population_size // 20)

    while len(next_generation) < config.population_size - immigrant_count:
        parent_a = tournament_select(sorted_population)
        parent_b = tournament_select(sorted_population)
        child = crossover(parent_a, parent_b)
        next_generation.append(mutate(child, config.mutation_rate))

    while len(next_generation) < config.population_size:
        next_generation.append(create_random_dna(config.dna_length))

    return next_generation


def ordered_camp_targets(start_node: Point, camps: list[dict]) -> list[dict]:
    if not camps:
        return []

    scuttles = [camp for camp in camps if camp.get("type") == "river"]
    main_camps = [camp for camp in camps if camp.get("type") != "river"]

    main_camps.sort(key=lambda camp: get_euclidean_distance(start_node, camp))

    if not main_camps:
        return scuttles[:1]

    if not scuttles:
        return main_camps

    last_camp = main_camps[-1]
    last_camp_point = Point(x=last_camp["x"], y=last_camp["y"])
    closest_scuttle = min(
        scuttles,
        key=lambda scuttle: get_euclidean_distance(last_camp_point, scuttle),
    )

    return main_camps + [closest_scuttle]


def extend_full_path(full_path: list[dict], segment_path: list[dict]) -> None:
    if not segment_path:
        return

    if not full_path:
        full_path.extend(segment_path)
        return

    full_path.extend(segment_path[1:])


async def genetic_algorithm(
    run_id: str,
    start: Point,
    goal: Point,
    grid: list[list[int]],
    active_simulations: dict,
    config: GAConfig | None,
):
    config = clamp_config(config)
    population = [create_random_dna(config.dna_length) for _ in range(config.population_size)]

    for generation in range(1, config.max_generations + 1):
        if not active_simulations[run_id].get("is_running", False):
            return

        scored_population = [
            simulate_agent(start, goal, grid, dna)
            for dna in population
        ]
        scored_population.sort(key=lambda agent: agent["fitness"], reverse=True)
        best_agent = scored_population[0]

        yield {
            "agentPos": best_agent["final_position"],
            "populationPositions": [agent["final_position"] for agent in scored_population],
            "generationPaths": [agent["path"] for agent in scored_population],
            "log": (
                f"[GA] Generation {generation}/{config.max_generations} | "
                f"Best distance: {best_agent['distance_to_goal']:.2f} | "
                f"Best fitness: {best_agent['fitness']:.1f}"
            ),
        }

        if best_agent["reached_goal"]:
            yield {
                "status": "finished",
                "path": best_agent["path"],
                "log": (
                    f"[GA] Target found in generation {generation} "
                    f"after {best_agent['steps_taken']} moves."
                ),
            }
            return

        population = build_next_generation(scored_population, config)

        slider_val = active_simulations[run_id].get("speed", 50)
        delay = max(0.01, 1.0 - (slider_val / 100.0))
        await asyncio.sleep(delay)

    if active_simulations[run_id].get("is_running", False):
        yield {
            "status": "finished",
            "path": [],
            "log": "[GA] No agent reached the target before the generation limit.",
        }


async def run_multi_camp_ga(
    run_id: str,
    start_node: Point,
    target_node: Point,
    camps: list[dict],
    grid: list[list[int]],
    active_simulations: dict,
    config: GAConfig | None,
):
    current_start = start_node
    full_path = []
    ordered_targets = ordered_camp_targets(start_node, camps)

    for target_camp in ordered_targets:
        target_point = Point(x=target_camp["x"], y=target_camp["y"])

        yield {
            "log": f"[GA] Evolving route to {target_camp['id']}"
        }

        async for payload in genetic_algorithm(
            run_id,
            current_start,
            target_point,
            grid,
            active_simulations,
            config,
        ):
            if payload.get("status") == "finished":
                segment_path = payload.get("path", [])
                if not segment_path:
                    yield {
                        "status": "finished",
                        "path": full_path,
                        "log": f"[GA] Failed to reach {target_camp['id']}.",
                    }
                    return

                extend_full_path(full_path, segment_path)
                break

            yield payload

        current_start = target_point

    yield {
        "log": "[GA] Evolving route to target point"
    }

    async for payload in genetic_algorithm(
        run_id,
        current_start,
        target_node,
        grid,
        active_simulations,
        config,
    ):
        if payload.get("status") == "finished":
            segment_path = payload.get("path", [])
            if not segment_path:
                yield {
                    "status": "finished",
                    "path": full_path,
                    "log": "[GA] Failed to reach the final target.",
                }
                return

            extend_full_path(full_path, segment_path)
            break

        yield payload

    yield {
        "status": "finished",
        "path": full_path,
        "log": "[GA] Evolution complete. Jungle clear route found!",
    }
