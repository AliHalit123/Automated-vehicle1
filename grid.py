import pygame
import random

class Cell:
    def __init__(self, row, col, cell_type="empty"):
        self.row = row
        self.col = col
        self.type = cell_type  # "empty", "car", "pedestrian", "wall", "goal", "start", "building"
        self.image = self.load_image() if self.should_have_image() else None

    def should_have_image(self):
        # Sadece bu tipler görsel kullanır
        return self.type in ["car", "wall", "goal", "start", "building"]

    def load_image(self):
        size = 70  # Hücre boyutu
        path_map = {
            "car": ["car.png"],
            "wall": ["assets/wall.png"],
            "goal": ["destination.jpg"],
            "start": ["starting_point.jpg"],
            "building": ["building.gif","building5.gif","building2.gif","building1.gif"],
        }

        image_path = random.choice(path_map[self.type])


        if not image_path:
            return None  # Görsel tanımlı değilse hiç yükleme

        try:
            img = pygame.image.load(image_path)
            return pygame.transform.scale(img, (size, size))
        except Exception as e:
            print(f"Resim yüklenemedi: {image_path}, Hata: {e}")
            surf = pygame.Surface((size, size))
            surf.fill((200, 200, 200))  # Gri yüzey
            return surf

    def set_type(self, new_type):
        self.type = new_type
        self.image = self.load_image() if self.should_have_image() else None

    def draw(self, surface, cell_size):
        rect = pygame.Rect(self.col * cell_size, self.row * cell_size, cell_size, cell_size)

        if self.type == "empty":
            pygame.draw.rect(surface, (255, 255, 255), rect)
        elif self.image:
            surface.blit(self.image, (self.col * cell_size, self.row * cell_size))

        pygame.draw.rect(surface, (150, 150, 150), rect, 1)
