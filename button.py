import pygame

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        color = (140, 164, 111)
        if self.text in ["Start", "Restart", "Clean", "Rebuild"]:
            color = (244, 96, 111)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2)
        txt = self.font.render(self.text, True, (0, 0, 0))
        text_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
