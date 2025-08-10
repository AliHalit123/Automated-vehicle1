import random
import pygame
from settings import ROWS, COLS, DIRECTIONS, CELL_SIZE

class Garbage:
    def __init__(self):
        self.positions = []
        self.initial_positions = []
        self.directions = []

    def add_garbage(self):
        while len(self.positions) < 4:
            pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
            if pos not in self.positions:
                image_path = random.choice([
                    "images/garbage.jpg","images/garbage2.gif"
                ])
                self.positions.append((pos[0], pos[1], image_path))
                self.initial_positions.append((pos[0], pos[1], image_path))
                self.directions.append(random.choice(DIRECTIONS))

    def reset_positions(self):
        self.positions = self.initial_positions.copy()
        self.directions = [random.choice(DIRECTIONS) for _ in self.positions]

    def move_garbage(self, grid_matrix, car_pos):
        new_positions = []
        new_directions = []

        occupied_positions = {(p[0], p[1]) for p in self.positions}
        occupied_positions.add(car_pos)

        for idx, (r, c, img_path) in enumerate(self.positions):
            grid_matrix[r][c].set_type("empty")

            dr, dc = self.directions[idx]

            if random.random() > 0.8:

                mr, mc = random.choice(DIRECTIONS)
                if mr!=-dr and mc!=dc:
                    dr,dc = mr,mc

            nr, nc = r + dr, c + dc

            if (0 <= nr < ROWS and 0 <= nc < COLS and
                grid_matrix[nr][nc].type == "empty" and
                (nr, nc) not in occupied_positions):

                new_positions.append((nr, nc, img_path))
                new_directions.append((dr, dc))
                occupied_positions.add((nr, nc))
            else:
                new_positions.append((r, c, img_path))
                new_directions.append((dr, dc))
                occupied_positions.add((r, c))

        for r, c, _ in new_positions:
            grid_matrix[r][c].set_type("garbage")

        self.positions = new_positions
        self.directions = new_directions

    def draw(self, surface):
        for r, c, img_path in self.positions:
            try:
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            except Exception:
                img = pygame.Surface((CELL_SIZE, CELL_SIZE))
                img.fill((200, 200, 200))
            surface.blit(img, (c * CELL_SIZE, r * CELL_SIZE))
