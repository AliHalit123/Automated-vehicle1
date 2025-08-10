import pygame
from settings import WIDTH, HEIGHT, CELL_SIZE, ROWS, COLS, WHITE
from firstgrid import initialize_grid
from pedestrian import PedestrianManager
from garbage import Garbage
from button import Button
from game_state import GameState
import callback

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 60))
pygame.display.set_caption("Autonomous Vehicle Simulation")
clock = pygame.time.Clock()

# Initial grid and other objects
grid, building_positions = initialize_grid(ROWS, COLS)
pedestrians = PedestrianManager()
garbage = Garbage()

# Gamestate object
state = GameState(grid, building_positions, pedestrians, garbage)

#Buttons and callbacks
buttons = [
    Button(160, HEIGHT + 10, 120, 40, "Initial Position", lambda: callback.set_start_mode(state)),
    Button(290, HEIGHT + 10, 120, 40, "Destination", lambda: callback.set_end_mode(state)),
    Button(420, HEIGHT + 10, 120, 40, "Pedestrian", lambda: callback.set_pedestrian_mode(state)),
    Button(710, 200, 120, 40, "Start", lambda: callback.set_start(state)),
    Button(710, 260, 120, 40, "Restart", lambda: callback.restart_callback(state)),
    Button(710, 320, 120, 40, "Clean", lambda: callback.clear_callback(state)),
    Button(710, 380, 120, 40, "Rebuild", lambda: callback.rebuild(state))
]

running = True
while running:
    clock.tick(2)
    screen.fill(WHITE)

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        for button in buttons:
            button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y < HEIGHT and state.mode is not None:
                row, col = y // CELL_SIZE, x // CELL_SIZE
                #add starting point
                if state.mode == "start" and not state.start and state.grid[row][col].type == "empty":
                    state.start = (row, col)
                    state.grid[row][col].set_type("start")
                    state.mode = None
                #add destination
                elif state.mode == "end" and state.grid[row][col].type == "empty":
                    state.end_list.append((row, col))
                    state.grid[row][col].set_type("goal")
                    if not state.vehicle and state.start:
                        from astar import astar
                        path = astar(state.start, state.end_list[0], state.grid)
                        destination_queue = state.end_list[1:] if len(state.end_list) > 1 else []
                        from vehicle import Vehicle
                        state.vehicle = Vehicle(state.start, path, destination_queue=destination_queue, initial_target=state.end_list[0])
                        state.vehicle1 = Vehicle(state.start, path, destination_queue=destination_queue.copy(), initial_target=state.end_list[0], img_type="car1")
                    elif state.vehicle:
                        state.vehicle.destinations.append((row, col))
                        state.vehicle1.destinations.append((row, col))
                    state.mode = None
                #add pedestrian
                elif state.mode == "pedestrian" and state.grid[row][col].type == "empty":
                    state.grid[row][col].set_type("pedestrian")
                    state.pedestrians.add_pedestrian((row, col))
                    state.mode = None


    state.garbage.add_garbage()

    # move pedestrians and garbage
    if state.vehicle and state.start_simulation and state.vehicle.pos != state.end_list[-1] and state.vehicle1.pos != state.end_list[-1]:
        state.pedestrians.move_pedestrians(state.grid, state.vehicle.pos)
        state.garbage.move_garbage(state.grid, state.vehicle.pos)

    # check if vehicles reached and save the time
    if state.vehicle and state.vehicle.pos == state.end_list[-1] and not state.v_reached[0]:
        state.v_reached[0] = True
        import time
        state.end_time_v1 = time.time()
        with open("record.txt", "a") as f:
            f.write(f"vehicle1:{round(state.end_time_v1 - state.start_time, 3)} ")

    if state.vehicle1 and state.vehicle1.pos == state.end_list[-1] and not state.v_reached[1]:
        state.v_reached[1] = True
        import time
        state.end_time_v2 = time.time()
        with open("record.txt", "a") as f:
            f.write(f"vehicle2:{round(state.end_time_v2 - state.start_time, 3)} \n")

    # sraw each cell on the grid
    for row in state.grid:
        for cell in row:
            cell.draw(screen, CELL_SIZE)

    #draw pedestrians and garbage
    state.pedestrians.draw(screen)
    state.garbage.draw(screen)

    #move and draw vehciles
    if state.vehicle and state.start_simulation:
        state.vehicle.move(screen, state.grid)
        state.vehicle1.move_normal(screen, state.grid)
        state.vehicle.draw(screen)
        state.vehicle1.draw(screen, False)

    #draw the buttons
    for button in buttons:
        button.draw(screen)

    if state.mode:
        font = pygame.font.SysFont(None, 28)
        info_text = f"Click on any cell on the grid to set the location of {state.mode} point"
        info_surface = font.render(info_text, True, (0, 0, 0))
        screen.blit(info_surface, (10, HEIGHT - 30))

    pygame.display.update()

pygame.quit()
