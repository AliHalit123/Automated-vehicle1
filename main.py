import pygame
import random
from settings import WIDTH, HEIGHT, CELL_SIZE, ROWS, COLS, WHITE
from grid import Cell
from astar import astar
from vehicle import Vehicle
from pedestrian import PedestrianManager

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT + 60))
pygame.display.set_caption("Automated Vehicle Simulation")
clock = pygame.time.Clock()

grid = [[Cell(r, c) for c in range(COLS)] for r in range(ROWS)]


building_positions = set()
while len(building_positions) < 6:
    pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
    if pos not in building_positions:
        building_positions.add(pos)

for (r, c) in building_positions:
    grid[r][c].set_type("building")

start = None
end = None
vehicle = None
pedestrians = PedestrianManager()
path = []
mode = None


class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        pygame.draw.rect(screen, (180, 180, 180), self.rect)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2)
        txt = self.font.render(self.text, True, (0, 0, 0))
        text_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

def set_start_mode():
    global mode
    mode = "start"

def set_end_mode():
    global mode
    mode = "end"

def set_pedestrian_mode():
    global mode
    mode = "pedestrian"

buttons = [
    Button(10, HEIGHT + 10, 120, 40, " Starting point ", set_start_mode),
    Button(140, HEIGHT + 10, 120, 40, " Destination ", set_end_mode),
    Button(270, HEIGHT + 10, 120, 40, " Pedestrian", set_pedestrian_mode)
]

running = True
while running:
    clock.tick(2)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        for button in buttons:
            button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y < HEIGHT:
                row, col = y // CELL_SIZE, x // CELL_SIZE
                cell = grid[row][col]

                if mode == "start" and not start and cell.type == "empty":
                    start = (row, col)
                    cell.set_type("start")
                    mode = None

                elif mode == "end" and not end and cell.type == "empty":
                    end = (row, col)
                    cell.set_type("goal")
                    path = astar(start, end, grid)
                    vehicle = Vehicle(start, path)
                    mode = None

                elif mode == "pedestrian" and cell.type == "empty":
                    cell.set_type("pedestrian")
                    pedestrians.add_pedestrian((row, col))
                    mode = None

    if vehicle:
        pedestrians.move_pedestrians(grid, vehicle.pos)

    for row in grid:
        for cell in row:
            cell.draw(screen, CELL_SIZE)

    pedestrians.draw(screen)

    if vehicle:
        vehicle.move(screen)
        vehicle.draw(screen)

    for button in buttons:
        button.draw(screen)

    if mode:
        font = pygame.font.SysFont(None, 28)
        info_text = f"Mode: {mode} - click any position to set"
        info_surface = font.render(info_text, True, (0, 0, 0))
        screen.blit(info_surface, (10, HEIGHT - 30))

    pygame.display.update()


pygame.quit()
