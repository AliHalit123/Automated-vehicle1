import random
from grid import Cell

def initialize_grid(rows, cols, num_buildings=8):
    grid = [[Cell(r, c) for c in range(cols)] for r in range(rows)]

    building_positions = set()
    while len(building_positions) < num_buildings:
        pos = (random.randint(0, rows - 1), random.randint(0, cols - 1))
        if pos not in building_positions:
            building_positions.add(pos)

    for (r, c) in building_positions:
        grid[r][c].set_type("building")

    return grid, building_positions
