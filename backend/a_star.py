import heapq
import asyncio
import json
from models import Point 
import math

# Helpers
def is_unblocked(row: int, column: int, grid: list[list[int]]) -> bool:
    return grid[row][column] == 0

def is_destination(current_x: int, current_y: int, dest: Point):
    return (current_x == dest.x) and (current_y == dest.y)

def h_score(src: Point, dest: Point):
    # Euclidean distance
    return math.sqrt((src.x - dest.x) ** 2 + (src.y - dest.y) ** 2)

def is_valid_boundary(x: int, y: int, grid: list[list[int]]) -> bool:
    """Ensures the coordinates don't fall off the edge of the array."""
    max_y = len(grid)
    max_x = len(grid[0]) if max_y > 0 else 0
    return 0 <= y < max_y and 0 <= x < max_x

def reconstruct_path(came_from: dict, current_tuple: tuple) -> list[dict]:
    """Traces the dictionary backwards to build the final route."""
    path = [{"x": current_tuple[0], "y": current_tuple[1]}]
    while current_tuple in came_from:
        current_tuple = came_from[current_tuple]
        path.append({"x": current_tuple[0], "y": current_tuple[1]})
    
    path.reverse()
    return path

def get_euclidean_distance(p1: Point, p2: dict):
    return math.sqrt((p1.x - p2['x'])**2 + (p1.y - p2['y'])**2)

async def a_star(run_id: str, start: Point, end: Point, grid: list[list[int]], active_simulations: dict):
    # Store tuples of: (f_score, counter, Point)
    open_set = []
    counter = 0 # Tie-breaker for heapq if two nodes have the exact same f_score
    
    heapq.heappush(open_set, (0, counter, start))

    # Dictionaries to track scores and paths using (x, y) tuples as keys
    came_from = {}
    g_score = {(start.x, start.y): 0}
    f_score = {(start.x, start.y): h_score(start, end)}

    directions = [
        (0, -1), (0, 1), (-1, 0), (1, 0),   # Up, Down, Left, Right
        (-1, -1), (-1, 1), (1, -1), (1, 1)  # Diagonals
    ]

    while open_set and active_simulations[run_id].get("is_running", False):
        
        # Grab the node with the lowest f_score
        current_f, _, current = heapq.heappop(open_set)
        curr_tuple = (current.x, current.y)

        if is_destination(current.x, current.y, end):
            final_path = reconstruct_path(came_from, curr_tuple)
            yield {
                "status": "finished",
                "path": final_path,
                "log": "Target Found!"
            }
            return # Exit the generator

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = current.x + dx, current.y + dy
            neighbor_tuple = (nx, ny)

            # Skip if out of bounds or hitting a wall
            if not is_valid_boundary(nx, ny, grid):
                continue
            if not is_unblocked(ny, nx, grid):
                continue

            # Moving diagonally costs slightly more than moving straight
            move_cost = 1 if dx == 0 or dy == 0 else 1.414
            curr_g_score = g_score[curr_tuple] + move_cost

            # If this is a new node, or found a faster way to an old node
            if neighbor_tuple not in g_score or curr_g_score < g_score[neighbor_tuple]:
                neighbor_node = Point(x=nx, y=ny)
                
                came_from[neighbor_tuple] = curr_tuple
                g_score[neighbor_tuple] = curr_g_score
                f_score[neighbor_tuple] = curr_g_score + h_score(neighbor_node, end)

                counter += 1
                heapq.heappush(open_set, (f_score[neighbor_tuple], counter, neighbor_node))

        # Yield the current step to send to frontend
        yield {
            "agentPos": {"x": current.x, "y": current.y},
            "visitedNode": {"x": current.x, "y": current.y},
            "log": f"[A_STAR] Evaluated ({current.x}, {current.y}) | F-Score: {round(current_f, 1)}"
        }

        # Check the frontend speed slider to pause execution
        slider_val = active_simulations[run_id].get("speed", 50)
        delay = max(0.01, 1.0 - (slider_val / 100.0))
        await asyncio.sleep(delay)

    # Path is impossible to find
    if active_simulations[run_id].get("is_running", False):
        yield {
            "status": "finished",
            "path": [],
            "log": "No valid path found!"
        }

async def run_multi_camp_a_star(run_id: str, start_node: Point, target_node: Point, camps: list[dict], grid: list[list[int]], active_simulations: dict):
    
    # Separate Scuttles from the main camps
    scuttles = [c for c in camps if c.get('type') == 'river']
    main_camps = [c for c in camps if c.get('type') != 'river']

    # Sort main camps by distance from the Start Node
    main_camps.sort(key=lambda c: get_euclidean_distance(start_node, c))

    # Find closest scuttle to the last camp
    last_camp = main_camps[-1]
    last_camp_point = Point(x=last_camp['x'], y=last_camp['y'])
    closest_scuttle = min(scuttles, key=lambda scuttle: get_euclidean_distance(last_camp_point, scuttle))

    ordered_targets = main_camps + [closest_scuttle]

    current_start = start_node
    full_path = []

    for target_camp in ordered_targets:
        
        target_point = Point(x=target_camp['x'], y=target_camp['y'])
        
        yield {
            "log": f"Routing to {target_camp['id']}"
        }

        # Run A* from current point to next camp
        async for payload in a_star(run_id, current_start, target_point, grid, active_simulations):
            
            # Intercept the "finished" message so it doesn't kill the SSE stream
            if payload.get("status") == "finished":
                if payload.get("path"):
                    full_path.extend(payload["path"])
                break 
            else:
                yield payload

        # Update the start position for next segment
        current_start = target_point

    yield {
        "log": f"Routing to target point"
    }

    async for payload in a_star(run_id, current_start, target_node, grid, active_simulations):
        if payload.get("status") == "finished":
            if payload.get("path"):
                full_path.extend(payload["path"])
            break 
        else:
            yield payload

    yield {
        "status": "finished",
        "path": full_path,
        "log": "Jungle Clear Complete!"
    }