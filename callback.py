# callbacks.py
import random
import time
from astar import astar
from vehicle import Vehicle
from settings import ROWS, COLS


def set_start_mode(state):
    """Switch to start point selection mode."""
    state.mode = "start"


def set_end_mode(state):
    """Switch to destination point selection mode."""
    state.mode = "end"


def set_pedestrian_mode(state):
    """Switch to pedestrian adding mode."""
    state.mode = "pedestrian"


def clear_callback(state):
    """Clear start, goal, and pedestrians on the map."""
    state.k += 1
    state.v_reached = [False, False]

    for row in state.grid:
        for cell in row:
            if cell.type in ["start", "goal", "pedestrian"]:
                cell.set_type("empty")

    state.start = None
    state.end_list.clear()
    state.vehicle = None
    state.vehicle1 = None
    state.path.clear()
    state.pedestrians.reset_positions()
    state.start_simulation = False
    state.mode = None


def restart_callback(state):
    """Reset vehicles and pedestrians and start the simulation."""
    state.j += 1
    state.v_reached = [False, False]

    with open("record.txt", "a") as f:
        f.write(f"Here we have map {state.i}, run {state.j}, version {state.k}\n")

    if state.start and len(state.end_list) >= 1:
        initial_path = astar(state.start, state.end_list[0], state.grid)
        fallback_queue = state.end_list[1:] if len(state.end_list) > 1 else []
        state.vehicle = Vehicle(state.start, initial_path, destination_queue=fallback_queue,
                                initial_target=state.end_list[0])
        state.vehicle1 = Vehicle(state.start, initial_path, destination_queue=fallback_queue.copy(),
                                 initial_target=state.end_list[0], img_type="car1")
    else:
        state.vehicle = None
        state.vehicle1 = None

    state.pedestrians.reset_positions()
    state.garbage.reset_positions()
    state.start_simulation = True
    state.mode = None


def set_start(state):
    """Start the simulation."""
    with open("record.txt", "a") as f:
        f.write(f"Here we have map {state.i}, run {state.j}, version {state.k}\n")
    if state.vehicle:
        state.start_simulation = True
        state.start_time = time.time()


def rebuild(state):
    """Rebuild the map and add random buildings."""
    state.i += 1
    state.j = 0
    state.k = 0

    for row in state.grid:
        for cell in row:
            if cell.type in ["start", "goal", "pedestrian", "building"]:
                cell.set_type("empty")

    state.start = None
    state.end_list.clear()
    state.vehicle = None
    state.vehicle1 = None
    state.v_reached = [False, False]
    state.path.clear()
    state.pedestrians.reset_positions()
    state.building_positions.clear()

    # Place 8 random buildings
    while len(state.building_positions) < 8:
        pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
        if pos not in state.building_positions:
            state.building_positions.add(pos)

    for (r, c) in state.building_positions:
        state.grid[r][c].set_type("building")

    state.start_simulation = False
    state.mode = None
