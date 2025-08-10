import pygame
import random
from settings import CELL_SIZE

class Cell:
    """
    Represents a single cell in the grid.
    Each cell has a row and column index, a type (e.g., empty, car, building),
    and optionally an associated image for rendering.
    """
    def __init__(self, row, col, cell_type="empty"):
        self.row = row                  # Row index in the grid
        self.col = col                  # Column index in the grid
        self.type = cell_type           # Cell type: "empty", "car", "building", etc.
        # Load image only if the cell type has a visual representation
        self.image = self.load_image() if self.should_have_image() else None

    def should_have_image(self):
        """
        Returns True if this cell type should have an image,
        e.g., vehicles, goals, buildings, start points.
        """
        return self.type in ["car", "goal", "start", "building", "car1"]

    def load_image(self):
        """
        Loads and returns the image surface corresponding to the cell type.
        If multiple image options exist, selects one randomly for variety.
        If loading fails, returns a plain colored surface as fallback.
        """
        path_map = {
            "car": ["images/car.png"],
            "car1": ["images/car1.jpg"],
            "goal": ["images/destination.jpg"],
            "start": ["images/starting_point.jpg"],
            "building": [
                "images/building.gif", "images/building1.jpg",
                "images/building5.gif", "images/building2.gif", "images/building1.gif"
            ],
        }

        image_path = random.choice(path_map.get(self.type, []))

        if not image_path:
            return None

        try:
            img = pygame.image.load(image_path)
            return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except Exception as e:
            print(f"Image couldn't load {image_path}, Error: {e}")
            # Return a simple gray surface as a fallback
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
            surf.fill((200, 200, 200))
            return surf

    def set_type(self, new_type):
        """
        Changes the cell's type and reloads the corresponding image if necessary.
        """
        self.type = new_type
        self.image = self.load_image() if self.should_have_image() else None

    def draw(self, surface, cell_size):
        """
        Draws the cell on the given surface.
        If the cell is empty, draws a white rectangle with a border.
        If the cell has an image, draws the image.
        """
        rect = pygame.Rect(self.col * cell_size, self.row * cell_size, cell_size, cell_size)

        if self.type == "empty":
            pygame.draw.rect(surface, (255, 255, 255), rect)
        elif self.image:
            surface.blit(self.image, (self.col * cell_size, self.row * cell_size))

        # Draw a border around each cell
        pygame.draw.rect(surface, (150, 150, 150), rect, 1)
