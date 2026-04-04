import heapq
import asyncio
import math
from models import Point


def is_unblocked(row: int, column: int, grid: list[list[int]]) -> bool:
    return grid[row][column] == 0


def is_destination(current_x: int, current_y: int, dest: Point):
    return (current_x == dest.x) and (current_y == dest.y)


def is_valid_boundary(x: int, y: int, grid: list[list[int]]) -> bool:
    max_y = len(grid)
    max_x = len(grid[0]) if max_y > 0 else 0
    return 0 <= y < max_y and 0 <= x < max_x


def reconstruct_path(came_from: dict, current_tuple: tuple) -> list[dict]:
    path = [{"x": current_tuple[0], "y": current_tuple[1]}]
    while current_tuple in came_from:
        current_tuple = came_from[current_tuple]
        path.append({"x": current_tuple[0], "y": current_tuple[1]})
    path.reverse()
    return path


def get_euclidean_distance(p1: Point, p2: dict):
    return math.sqrt((p1.x - p2["x"]) ** 2 + (p1.y - p2["y"]) ** 2)


async def dijkstra(run_id: str, start: Point, end: Point, grid: list[list[int]], active_simulations: dict):
    open_set = []
    counter = 0

    # (distance_from_start, counter, Point)
    heapq.heappush(open_set, (0, counter, start))

    came_from = {}
    dist = {(start.x, start.y): 0}

    directions = [
        (0, -1), (0, 1), (-1, 0), (1, 0),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    while open_set and active_simulations[run_id].get("is_running", False):
        current_dist, _, current = heapq.heappop(open_set)
        curr_tuple = (current.x, current.y)

        if is_destination(current.x, current.y, end):
            final_path = reconstruct_path(came_from, curr_tuple)
            yield {
                "status": "finished",
                "path": final_path,
                "log": "Target Found!"
            }
            return

        for dx, dy in directions:
            nx, ny = current.x + dx, current.y + dy
            neighbor_tuple = (nx, ny)

            if not is_valid_boundary(nx, ny, grid):
                continue
            if not is_unblocked(ny, nx, grid):
                continue

            move_cost = 1 if dx == 0 or dy == 0 else 1.414
            new_dist = dist[curr_tuple] + move_cost

            if neighbor_tuple not in dist or new_dist < dist[neighbor_tuple]:
                dist[neighbor_tuple] = new_dist
                came_from[neighbor_tuple] = curr_tuple

                counter += 1
                heapq.heappush(open_set, (new_dist, counter, Point(x=nx, y=ny)))

        yield {
            "agentPos": {"x": current.x, "y": current.y},
            "visitedNode": {"x": current.x, "y": current.y},
            "log": f"[DIJKSTRA] Evaluated ({current.x}, {current.y}) | Distance: {round(current_dist, 1)}"
        }

        slider_val = active_simulations[run_id].get("speed", 50)
        delay = max(0.01, 1.0 - (slider_val / 100.0))
        await asyncio.sleep(delay)

    if active_simulations[run_id].get("is_running", False):
        yield {
            "status": "finished",
            "path": [],
            "log": "No valid path found!"
        }


async def run_multi_camp_dijkstra(run_id: str, start_node: Point, target_node: Point, camps: list[dict], grid: list[list[int]], active_simulations: dict):
    scuttles = [c for c in camps if c.get("type") == "river"]
    main_camps = [c for c in camps if c.get("type") != "river"]

    main_camps.sort(key=lambda c: get_euclidean_distance(start_node, c))

    ordered_targets = main_camps[:]
    if main_camps and scuttles:
        last_camp = main_camps[-1]
        last_camp_point = Point(x=last_camp["x"], y=last_camp["y"])
        closest_scuttle = min(scuttles, key=lambda s: get_euclidean_distance(last_camp_point, s))
        ordered_targets.append(closest_scuttle)

    current_start = start_node
    full_path = []

    for target_camp in ordered_targets:
        target_point = Point(x=target_camp["x"], y=target_camp["y"])

        yield {
            "log": f"Routing to {target_camp['id']}"
        }

        async for payload in dijkstra(run_id, current_start, target_point, grid, active_simulations):
            if payload.get("status") == "finished":
                if payload.get("path"):
                    if not full_path:
                        full_path.extend(payload["path"])
                    else:
                        full_path.extend(payload["path"][1:])
                break
            else:
                yield payload

        current_start = target_point

    yield {
        "log": "Routing to target point"
    }

    async for payload in dijkstra(run_id, current_start, target_node, grid, active_simulations):
        if payload.get("status") == "finished":
            if payload.get("path"):
                if not full_path:
                    full_path.extend(payload["path"])
                else:
                    full_path.extend(payload["path"][1:])
            break
        else:
            yield payload

    yield {
        "status": "finished",
        "path": full_path,
        "log": "Jungle Clear Complete!"
    }