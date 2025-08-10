from grid import Cell
from yolo import contains_human
from settings import CELL_SIZE
from astar import astar
import pygame
import pickle
import numpy as np


class Vehicle:
    """
    Represents an autonomous vehicle navigating on a grid.
    Handles movement, path following, RL decision-making, and rendering.
    """
    def __init__(self, start_pos, path, destination_queue=None, initial_target=None, img_type="car"):
        self.pos = start_pos  # Current position (row, col)
        self.path = path      # List of grid cells representing the planned path
        self.step = 0         # Index in the path list for next move
        self.angle = 0        # Rotation angle for rendering orientation
        self.y_initial = 0    # Y coordinate for drawing info panel text
        self.warnings = []    # Log of warnings and RL decisions for display
        self.original_image = Cell(self.pos[0], self.pos[1], img_type).image  # Vehicle sprite
        self.destinations = destination_queue or []  # Queue of subsequent targets
        self.current_target = initial_target or (self.destinations[0] if self.destinations else start_pos)
        self.wait_counter = 0  # Counts how long vehicle has been waiting (e.g., for humans)
        self.q_table = self.load_q_table("off.pkl")  # Pretrained Q-table for RL agent

    def get_next_position(self):
        """Returns the next position in the path or None if at the end."""
        if self.step < len(self.path):
            return self.path[self.step]
        return None

    def get_front_cells(self):
        """
        Returns a list of grid cells directly in front and diagonally front-left/right
        relative to the vehicle's current position and movement direction.
        """
        if not self.get_next_position():
            return []
        r, c = self.pos
        nr, nc = self.get_next_position()
        dr, dc = nr - r, nc - c

        if dr == -1:
            return [(r - 1, c), (r - 1, c - 1), (r - 1, c + 1)]
        elif dr == 1:
            return [(r + 1, c), (r + 1, c - 1), (r + 1, c + 1)]
        elif dc == -1:
            return [(r, c - 1), (r - 1, c - 1), (r + 1, c - 1)]
        elif dc == 1:
            return [(r, c + 1), (r - 1, c + 1), (r + 1, c + 1)]
        return []

    def check_front_for_humans(self, screen):
        """
        Scans the cells in front of the vehicle to detect humans using YOLO.
        Returns True if a human is detected, False otherwise.
        """
        front_cells = self.get_front_cells()
        for r, c in front_cells:
            if 0 <= r < 10 and 0 <= c < 10:
                sub_surface = screen.subsurface(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE).copy()
                confidence = contains_human(sub_surface)
                if confidence:
                    self.warnings.append(f"--->Human detected: {r},{c} with confidence: {round(confidence, 2)}")
                    return True
        return False

    def move(self, screen, grid):
        """
        Moves the vehicle  along the path if no human detected.
        If humans detected, waits for 3 seconds and then uses RL agent to decide next action.
        """
        if not self.check_front_for_humans(screen):
            self.wait_counter = 0
            self.follow_path(grid)
        else:
            self.wait_counter += 1
            self.warnings.append(f"--> waited for {self.wait_counter} seconds .")
            if self.wait_counter >= 3:
                state = self.get_rl_state(screen)
                action = self.get_best_action(state)
                action_names = ["Wait", "Forward", "Right", "Left"]
                self.warnings.append(f"--> RL agent for the state {state}  choose the action'{action_names[action]}'")
                self.apply_rl_action(action, grid)
                self.wait_counter = 0

    def move_normal(self, screen, grid):
        """
        Moves the vehicle normally forward if no human detected.
        Does not use reinforcement learning.
        """
        if not self.check_front_for_humans(screen):
            self.wait_counter = 0
            self.follow_path(grid)

    def follow_path(self, grid):
        """
        Advances the vehicle one step along the current path,
        updating position and rotation angle accordingly.
        If path ends and destinations remain, calculates new path.
        """
        next_pos = self.get_next_position()
        if next_pos:
            dx = next_pos[1] - self.pos[1]
            dy = next_pos[0] - self.pos[0]

            # Update angle for rendering vehicle orientation
            if dx == 1:
                self.angle = -90
            elif dx == -1:
                self.angle = 90
            elif dy == 1:
                self.angle = 180
            elif dy == -1:
                self.angle = 0

            self.pos = next_pos
            self.step += 1
        elif self.step >= len(self.path):
            if self.destinations:
                self.current_target = self.destinations.pop(0)
            next_destination = self.current_target or self.pos
            new_path = astar(self.pos, next_destination, grid)
            if new_path and len(new_path) > 1:
                self.path = new_path
                self.step = 0

    def front_right_is_building(self, grid):
        """
        Checks if the cell diagonally front-right to the vehicle contains a building.
        Used for decision making when changing lanes.
        """
        if self.step >= len(self.path):
            return False

        r, c = self.pos
        nr, nc = self.path[self.step]
        dr, dc = nr - r, nc - c

        # Calculate front-right cell coordinates using perpendicular vector
        fr = r + dr + dc
        fc = c + dc - dr

        # Boundary check and return True if building present
        if 0 <= fr < len(grid) and 0 <= fc < len(grid[0]):
            cell_type = grid[fr][fc].type
            print(f"DEBUG: front-right cell ({fr}, {fc}) = {cell_type}")
            return cell_type == "building"
        return False

    def apply_rl_action(self, action, grid):
        """
        Applies the action decided by the RL agent.
        Actions: 0=Wait, 1=Forward, 2=Turn Right, 3=Turn Left
        """
        if action == 0:
            self.warnings.append("--> Car is waiting")
        elif action == 1:
            self.warnings.append("--> Car is trying to go forward")
            self.follow_path(grid)
        elif action == 2:
            # Check if right lane is blocked before turning right
            if self.front_right_is_building(grid):
                self.warnings.append("--> Right blocked by building, trying left")
                self.change_lane(grid, direction=-1)  # Change lane left
            else:
                self.warnings.append("--> Car is trying to go right")
                self.change_lane(grid, direction=1)   # Change lane right
        elif action == 3:
            self.warnings.append("--> Car is trying to go left")
            self.change_lane(grid, direction=-1)      # Change lane left

    def change_lane(self, grid, direction):
        """
        Changes lane to the left or right if possible.
        Recalculates path from new position to current target.
        """
        r, c = self.pos
        if self.step >= len(self.path):
            return

        nr, nc = self.path[self.step]
        dr, dc = nr - r, nc - c
        perp_r, perp_c = (-dc, dr) if direction == -1 else (dc, -dr)
        new_pos = (r + perp_r, c + perp_c)

        # Check boundaries and cell type to avoid collision
        if 0 <= new_pos[0] < len(grid) and 0 <= new_pos[1] < len(grid[0]):
            if grid[new_pos[0]][new_pos[1]].type not in ["pedestrian", "building"]:
                self.pos = new_pos
                target = self.current_target

                if target == self.pos:
                    return

                new_path = astar(self.pos, target, grid)
                if new_path and len(new_path) > 1:
                    self.path = new_path
                    self.step = 0
                    self.warnings.append("--> New path calculated.")

    def get_rl_state(self, screen):
        """
        Constructs a state tuple representing presence of humans in
        front-left, front, and front-right cells detected by YOLO.
        Used as input to the RL agent.
        """
        if self.step >= len(self.path):
            return (0, 0, 0)

        r, c = self.pos
        nr, nc = self.path[self.step]
        dr, dc = nr - r, nc - c
        if dr == 0 and dc == 0:
            dr, dc = -1, 0

        front = [
            (r + dr - dc, c + dc + dr),  # front-left
            (r + dr, c + dc),            # front
            (r + dr + dc, c + dc - dr)   # front-right
        ]

        state = []
        for i, j in front:
            if 0 <= i < 10 and 0 <= j < 10:
                sub_surface = screen.subsurface(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE).copy()
                confidence = contains_human(sub_surface)
                state.append(1 if confidence else 0)
            else:
                state.append(0)
        return tuple(state)

    def get_best_action(self, state):
        """
        Maps the RL state tuple to an index and returns the best action
        from the loaded Q-table.
        """
        idx = state[0] * 4 + state[1] * 2 + state[2] * 1
        return int(np.argmax(self.q_table[idx]))

    def load_q_table(self, path):
        """Loads the pretrained Q-table for RL from file."""
        with open(path, 'rb') as f:
            return pickle.load(f)

    def draw(self, surface, draw_info=True):
        """
        Draws the vehicle image rotated according to its orientation.
        Optionally draws an information panel with recent warnings and decisions.
        """
        self.y_initial = 20
        rotated = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(rotated, (self.pos[1] * CELL_SIZE, self.pos[0] * CELL_SIZE))

        if draw_info:
            box_x, box_y = 840, 10
            box_width, box_height = 300, 35
            pygame.draw.rect(surface, (0, 102, 102), (box_x, box_y, box_width, box_height), border_radius=6)
            pygame.draw.rect(surface, (0, 51, 51), (box_x, box_y, box_width, box_height), 2, border_radius=6)

            font_title = pygame.font.SysFont(None, 24, bold=True)
            title_text = font_title.render("Vehicle Information Panel", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(box_x + box_width // 2, box_y + box_height // 2))
            surface.blit(title_text, title_rect)

            font = pygame.font.SysFont(None, 22)
            self.y_initial = box_y + box_height + 10
            for sentence in self.warnings[-25:]:
                text = font.render(sentence, True, (0, 153, 153))
                surface.blit(text, (box_x + 10, self.y_initial))
                self.y_initial += 20
