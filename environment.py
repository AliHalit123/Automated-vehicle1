import random
from settings import ROWS, COLS
from grid import Cell
from pedestrian import PedestrianManager
from vehicle import Vehicle
from astar import astar

class HybridEnvironment:
    def __init__(self):
        self.grid = None
        self.pedestrian_manager = PedestrianManager()
        self.vehicle = None
        self.start = None
        self.end_list = []
        self.done = False
        self.wait_counter = 0
        self.max_steps = 100
        self.current_step = 0

    def reset(self):
        self.grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]
        self._place_random_buildings(8)
        self._set_start_and_goals()
        self._place_pedestrians(random.randint(3, 6))

        if self.end_list:
            path = astar(self.start, self.end_list[0], self.grid)
            self.vehicle = Vehicle(self.start, path, self.end_list[1:])

        self.done = False
        self.wait_counter = 0
        self.current_step = 0
        return self.get_state()

    def step(self, action):
        reward = 0
        self.current_step += 1

        self.pedestrian_manager.move_pedestrians(self.grid, self.vehicle.pos)

        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) in self.pedestrian_manager.positions:
                    self.grid[r][c].set_type("pedestrian")
                elif self.grid[r][c].type == "pedestrian":
                    self.grid[r][c].set_type("empty")

        moved = False

        if self.wait_counter >= 3 and action == 0:
            action = random.choice([1, 2, 3])

        if action == 0:  # Wait
            self.wait_counter += 1
            reward -= 0.1

        elif action == 1:  # Forward
            moved = self._follow_path()
            if moved:
                reward += 0.5
                self.wait_counter = 0
            else:
                reward -= 1

        elif action == 2:  # Right
            moved = self._change_lane(1)
            self.wait_counter = 0
            if moved:
                reward -= 0.2

        elif action == 3:  # Left
            moved = self._change_lane(-1)
            self.wait_counter = 0
            if moved:
                reward -= 0.2

        if self.vehicle.pos in self.end_list:
            self.done = True
            reward += 10

        r, c = self.vehicle.pos
        if self.grid[r][c].type == "pedestrian":
            self.done = True
            reward -= 20

        if self.current_step >= self.max_steps:
            self.done = True
            reward -= 5

        return self.get_state(), reward, self.done, {}

    def get_state(self):
        r, c = self.vehicle.pos
        dr, dc = self.get_direction()

        if (dr, dc) == (0, 0):
            dr, dc = (-1, 0)

        front = [
            (r + dr - dc, c + dc + dr),
            (r + dr, c + dc),
            (r + dr + dc, c + dc - dr)
        ]

        state = []
        for (i, j) in front:
            if 0 <= i < ROWS and 0 <= j < COLS and self.grid[i][j].type == "pedestrian":
                state.append(1)
            else:
                state.append(0)

        return tuple(state)  # (left, front, right)

    def get_direction(self):
        if self.vehicle and self.vehicle.step < len(self.vehicle.path):
            r, c = self.vehicle.pos
            nr, nc = self.vehicle.path[self.vehicle.step]
            return (nr - r, nc - c)
        return (0, 0)

    def _follow_path(self):
        if self.vehicle.step < len(self.vehicle.path):
            next_pos = self.vehicle.path[self.vehicle.step]
            if self._is_free(next_pos):
                self.vehicle.pos = next_pos
                self.vehicle.step += 1
                return True
        return False

    def _change_lane(self, direction):  # +1: sağ, -1: sol
        r, c = self.vehicle.pos
        dr, dc = self.get_direction()
        if (dr, dc) == (0, 0):
            return False

        perp_r, perp_c = (-dc, dr) if direction == -1 else (dc, -dr)
        new_pos = (r + perp_r, c + perp_c)

        if self._is_free(new_pos):
            self.vehicle.pos = new_pos
            if self.vehicle.destinations:
                target = self.vehicle.destinations[0]
                new_path = astar(self.vehicle.pos, target, self.grid)
                if new_path:
                    self.vehicle.path = new_path
                    self.vehicle.step = 0
            return True
        return False

    def _is_free(self, pos):
        r, c = pos
        return 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c].type not in ["pedestrian", "building"]

    def _place_random_buildings(self, count):
        added = 0
        while added < count:
            r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            if self.grid[r][c].type == "empty":
                self.grid[r][c].set_type("building")
                added += 1

    def _set_start_and_goals(self):
        while True:
            r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            if self.grid[r][c].type == "empty":
                self.start = (r, c)
                self.grid[r][c].set_type("start")
                break

        self.end_list = []
        while len(self.end_list) < random.randint(1, 3):
            r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            if self.grid[r][c].type == "empty" and (r, c) != self.start:
                self.end_list.append((r, c))
                self.grid[r][c].set_type("goal")

    def _place_pedestrians(self, count):
        self.pedestrian_manager.positions.clear()
        self.pedestrian_manager.directions.clear()
        added = 0
        while added < count:
            r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
            if self.grid[r][c].type == "empty":
                self.pedestrian_manager.add_pedestrian((r, c))
                self.grid[r][c].set_type("pedestrian")
                added += 1
