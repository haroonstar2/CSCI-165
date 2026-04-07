import asyncio
import random
from collections import defaultdict
from models import Point

# =========================================================
# 1. FIXED STARTS
# =========================================================
# Adjust these if needed.

BLUE_START = Point(x=6, y=56)
RED_START = Point(x=57, y=7)

# =========================================================
# 2. CAMP ID MAPPING
# =========================================================

BLUE_ID_MAP = {
    "blue_gromp": "gromp",
    "blue_blue_buff": "blue",
    "blue_wolves": "wolves",
    "blue_raptors": "raptors",
    "blue_red_buff": "red",
    "blue_krugs": "krugs",
}

RED_ID_MAP = {
    "red_gromp": "gromp",
    "red_blue_buff": "blue",
    "red_wolves": "wolves",
    "red_raptors": "raptors",
    "red_red_buff": "red",
    "red_krugs": "krugs",
}

# =========================================================
# 3. NODE REWARD DATA
# =========================================================

NODE_DATA = {
    "blue":    {"type": "resource", "clear_time": 10, "gold": 90, "xp": 110},
    "gromp":   {"type": "resource", "clear_time": 8,  "gold": 80, "xp": 100},
    "wolves":  {"type": "resource", "clear_time": 9,  "gold": 75, "xp": 95},
    "raptors": {"type": "resource", "clear_time": 11, "gold": 85, "xp": 105},
    "red":     {"type": "resource", "clear_time": 10, "gold": 90, "xp": 100},
    "krugs":   {"type": "resource", "clear_time": 12, "gold": 85, "xp": 110},
    "scuttle": {"type": "river",    "clear_time": 6,  "gold": 70, "xp": 70},
}

# =========================================================
# 4. SIDE-SPECIFIC SCUTTLE CHOICE
# =========================================================
# Backend decides scuttle automatically.

def choose_scuttle(side: str, camps: list[dict]) -> dict | None:
    wanted_id = "scuttle_bot" if side == "blue" else "scuttle_top"
    for camp in camps:
        if camp["id"] == wanted_id:
            return camp
    return None

# =========================================================
# 5. BUILD RL NODES FROM FRONTEND CAMPS
# =========================================================

def build_q_nodes(side: str, camps: list[dict], start: Point) -> dict:
    id_map = BLUE_ID_MAP if side == "blue" else RED_ID_MAP

    nodes = {
        "start": {"x": start.x, "y": start.y}
    }

    for camp in camps:
        camp_id = camp["id"]
        if camp_id in id_map:
            nodes[id_map[camp_id]] = {"x": camp["x"], "y": camp["y"]}

    scuttle = choose_scuttle(side, camps)
    if scuttle:
        nodes["scuttle"] = {"x": scuttle["x"], "y": scuttle["y"]}

    return nodes

# =========================================================
# 6. ENVIRONMENT
# =========================================================

class JungleQEnv:
    def __init__(
        self,
        grid,
        nodes,
        targets,
        node_data,
        target_pos,
        start_name="start",
        max_steps=500,
        move_penalty=1.0,
        wall_penalty=5.0,
        completion_bonus=100.0,
        gold_weight=1.0,
        xp_weight=0.8,
        clear_time_weight=2.0,
    ):
        self.grid = grid
        self.nodes = nodes
        self.targets = targets
        self.node_data = node_data
        self.start_name = start_name
        self.max_steps = max_steps

        self.move_penalty = move_penalty
        self.wall_penalty = wall_penalty
        self.completion_bonus = completion_bonus
        self.gold_weight = gold_weight
        self.xp_weight = xp_weight
        self.clear_time_weight = clear_time_weight

        self.target_pos = target_pos

        self.actions = [0, 1, 2, 3]  # up, down, left, right
        self.action_moves = {
            0: (0, -1),  # up    -> y - 1
            1: (0, 1),   # down  -> y + 1
            2: (-1, 0),  # left  -> x - 1
            3: (1, 0),   # right -> x + 1
        }

        self.target_to_bit = {name: i for i, name in enumerate(targets)}
        self.all_visited_mask = (1 << len(targets)) - 1

        self.target_positions = {name: nodes[name] for name in targets}
        self.start_pos = nodes[start_name]

        self.reset()

    def reset(self):
        self.pos = dict(self.start_pos)
        self.visited_mask = 0
        self.steps = 0
        self.total_gold = 0
        self.total_xp = 0
        self.total_clear_time = 0
        return self.get_state()

    def get_state(self):
        return (self.pos["x"], self.pos["y"], self.visited_mask)

    def in_bounds(self, pos):
        x, y = pos["x"], pos["y"]
        return 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0])

    def is_walkable(self, pos):
        x, y = pos["x"], pos["y"]
        return self.in_bounds(pos) and self.grid[y][x] == 0

    def camp_reward(self, camp_name):
        data = self.node_data[camp_name]
        return (
            self.gold_weight * data["gold"]
            + self.xp_weight * data["xp"]
            - self.clear_time_weight * data["clear_time"]
        )

    def step(self, action):
        self.steps += 1

        dx, dy = self.action_moves[action]
        next_pos = {
            "x": self.pos["x"] + dx,
            "y": self.pos["y"] + dy,
        }

        reward = -self.move_penalty

        if not self.is_walkable(next_pos):
            next_pos = dict(self.pos)
            reward = -self.wall_penalty

        self.pos = next_pos

        for target_name, target_pos in self.target_positions.items():
            if self.pos["x"] == target_pos["x"] and self.pos["y"] == target_pos["y"]:
                bit = self.target_to_bit[target_name]
                if not (self.visited_mask & (1 << bit)):
                    self.visited_mask |= (1 << bit)

                    data = self.node_data[target_name]
                    self.total_gold += data["gold"]
                    self.total_xp += data["xp"]
                    self.total_clear_time += data["clear_time"]

                    reward += self.camp_reward(target_name)

        done = False

        if (
            self.pos["x"] == self.target_pos["x"]
            and self.pos["y"] == self.target_pos["y"]
        ):
            if self.visited_mask == self.all_visited_mask:
                reward += self.completion_bonus
                done = True
            else:
                reward -= 20

        if self.steps >= self.max_steps:
            done = True

        return self.get_state(), reward, done

# =========================================================
# 7. TRAINING
# =========================================================

def epsilon_greedy(Q, state, epsilon, n_actions=4):
    if random.random() < epsilon:
        return random.randint(0, n_actions - 1)
    return max(range(n_actions), key=lambda a: Q[state][a])

def train_q_learning(
    env,
    episodes=5000,
    alpha=0.1,
    gamma=0.95,
    epsilon=1.0,
    epsilon_decay=0.999,
    epsilon_min=0.02,
):
    Q = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    rewards_per_episode = []

    for _ in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0.0

        while not done:
            action = epsilon_greedy(Q, state, epsilon)
            next_state, reward, done = env.step(action)

            best_next = max(Q[next_state]) if not done else 0.0
            td_target = reward + gamma * best_next
            td_error = td_target - Q[state][action]
            Q[state][action] += alpha * td_error

            state = next_state
            total_reward += reward

        rewards_per_episode.append(total_reward)
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    return Q, rewards_per_episode

def run_greedy_policy(env, Q):
    state = env.reset()
    done = False
    path = [dict(env.pos)]
    collected = []
    seen_masks = {env.visited_mask}

    while not done:
        action = max(range(4), key=lambda a: Q[state][a])
        next_state, _, done = env.step(action)
        state = next_state
        path.append(dict(env.pos))

        if env.visited_mask not in seen_masks:
            seen_masks.add(env.visited_mask)
            collected.append(env.visited_mask)

        if len(path) > env.max_steps:
            break

    return path

# =========================================================
# 8. MAIN ASYNC GENERATOR FOR FASTAPI SSE
# =========================================================

async def run_q_learning_simulation(run_id, start, target, side, camps, grid, active_simulations):
    target_pos = {"x": target.x, "y": target.y}
    if side not in ("blue", "red"):
        yield {
            "status": "finished",
            "path": [],
            "log": "Q-Learning failed: invalid side."
        }
        return

    nodes = build_q_nodes(side, camps,start)

    required_targets = ["gromp", "blue", "wolves", "raptors", "red", "krugs","scuttle"]
    targets = [name for name in required_targets if name in nodes]

    missing = [name for name in ["gromp", "blue", "wolves", "raptors", "red", "krugs"] if name not in nodes]
    if missing:
        yield {
            "status": "finished",
            "path": [],
            "log": f"Q-Learning failed: missing camps {missing}"
        }
        return

    env = JungleQEnv(
        grid=grid,
        nodes=nodes,
        targets=targets,
        node_data=NODE_DATA,
        target_pos = target_pos,
        start_name="start",
        max_steps=500,
        move_penalty=1.0,
        wall_penalty=5.0,
        completion_bonus=100.0,
        gold_weight=1.0,
        xp_weight=0.8,
        clear_time_weight=2.0,
    )

    yield {
        "log": f"[Q_LEARNING] Training route for {side} side with targets: {targets}"
    }

    Q, _ = train_q_learning(
        env,
        episodes=5000,
        alpha=0.1,
        gamma=0.95,
        epsilon=1.0,
        epsilon_decay=0.999,
        epsilon_min=0.1,
    )

    final_path = run_greedy_policy(env, Q)

    for step in final_path:
        if not active_simulations[run_id].get("is_running", False):
            return

        yield {
            "agentPos": {"x": step["x"], "y": step["y"]},
            "visitedNode": {"x": step["x"], "y": step["y"]},
            "log": f"[Q_LEARNING] Agent moved to ({step['x']}, {step['y']})"
        }

        slider_val = active_simulations[run_id].get("speed", 50)
        delay = max(0.01, 1.0 - (slider_val / 100.0))
        await asyncio.sleep(delay)

    yield {
        "status": "finished",
        "path": final_path,
        "log": f"Q-Learning jungle route complete for {side} side."
    }