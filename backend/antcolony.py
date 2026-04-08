import asyncio
import random
import math
import json
from models import Point

async def run_ant_colony(run_id, start, target, grid, camps, active_simulations):
    if isinstance(start, dict): start = Point(**start)
    if isinstance(target, dict): target = Point(**target)

    rows = len(grid)
    cols = len(grid[0])
    
    ordered_targets = []
    for camp in camps:
        ordered_targets.append({"x": camp["x"], "y": camp["y"], "id": camp.get("id", "Camp")})
    ordered_targets.append({"x": target.x, "y": target.y, "id": "Final Target"})

    current_pos = {"x": start.x, "y": start.y}
    full_path = [{"x": start.x, "y": start.y}]
    
    yield {"log": f"[ANT_COLONY] Planning route through {len(ordered_targets)} locations."}

    for goal in ordered_targets:
        if not active_simulations.get(run_id, {}).get("is_running", False): break
        
        yield {"log": f"Ants searching for {goal['id']}..."}
        
        ants_count = 25 
        iterations = 15
        evaporation = 0.5
        pheromones = [[1.0 for _ in range(cols)] for _ in range(rows)]
        
        best_segment = None
        best_segment_len = float('inf')

        for it in range(iterations):
            if not active_simulations.get(run_id, {}).get("is_running", False): break
            
            paths_this_gen = []
            
            for _ in range(ants_count):
                x, y = current_pos["x"], current_pos["y"]
                path = [(x, y)]
                visited = {(x, y)}
                
                for step in range(200): 
                    if x == goal["x"] and y == goal["y"]: break
                    
                    moves = []
                    for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0 and (nx, ny) not in visited:
                            dist = math.sqrt((goal["x"]-nx)**2 + (goal["y"]-ny)**2)
                            score = (pheromones[ny][nx] ** 2) * (1.0 / (dist + 0.1))
                            moves.append((score, nx, ny))
                    
                    if not moves: break
                    moves.sort(key=lambda m: m[0], reverse=True)
                    _, x, y = random.choice(moves[:2]) 
                    path.append((x, y))
                    visited.add((x, y))

                if path[-1] == (goal["x"], goal["y"]):
                    paths_this_gen.append(path)
                    if len(path) < best_segment_len:
                        best_segment_len = len(path)
                        best_segment = path

            for r in range(rows):
                for c in range(cols): pheromones[r][c] *= evaporation
            for p in paths_this_gen:
                for px, py in p: 
                    pheromones[py][px] += (20.0 / len(p))

            speed = active_simulations.get(run_id, {}).get("speed", 50)
            await asyncio.sleep(max(0.01, (101 - speed) / 400))
            
            # --- DARKER TRAIL LOGIC ---
            # We duplicate each path 10 times in the payload. 
            # Frontend: 0.05 opacity * 10 layers = 0.5 effective opacity.
            darker_paths = []
            for path in paths_this_gen:
                formatted_path = [{"x": coord[0], "y": coord[1]} for coord in path]
                for _ in range(10): 
                    darker_paths.append(formatted_path)

            yield {
                "generationPaths": darker_paths,
                "populationPositions": [{"x": p[-1][0], "y": p[-1][1]} for p in paths_this_gen if p],
                "log": f"Gen {it}: Trail strength increasing..."
            }

        if best_segment:
            formatted_segment = [{"x": p[0], "y": p[1]} for p in best_segment]
            full_path.extend(formatted_segment[1:])
            current_pos = goal
            yield {"agentPos": goal, "visitedNode": goal}
        else:
            current_pos = goal

    yield {
        "status": "finished",
        "path": full_path,
        "log": "Optimization Complete. Strongest trail established."
    }
