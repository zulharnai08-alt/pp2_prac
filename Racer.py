import pygame, sys
from pygame.locals import *
import random

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Screen
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game")

# ===== ENEMY =====
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"C:\Users\zulha\OneDrive\Immagini\Снимки экрана\Снимок экрана 2026-04-23 211027.png")
        self.image = pygame.transform.scale(self.image, (75, 75))
        self.rect = self.image.get_rect()
        self.reset()

    def move(self):
        self.rect.move_ip(0, 7)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ===== PLAYER =====
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"C:\Users\zulha\Downloads\Pygame_rects.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def update(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0:
            if pressed_keys[K_LEFT]:
                self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[K_RIGHT]:
                self.rect.move_ip(5, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ===== COIN =====
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(r"C:\Users\zulha\Downloads\OIP.webp")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.reset()

    def move(self):
        self.rect.move_ip(0, 5)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def reset(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ===== OBJECTS =====
P1 = Player()
E1 = Enemy()
C1 = Coin()

score = 0
font = pygame.font.SysFont("Arial", 30)

# ===== GAME LOOP =====
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    P1.update()
    E1.move()
    C1.move()

    # Collision with coin
    if P1.rect.colliderect(C1.rect):
        score += 1
        C1.reset()

    # Game over (enemy)
    if P1.rect.colliderect(E1.rect):
        print("GAME OVER")
        pygame.quit()
        sys.exit()

    DISPLAYSURF.fill(WHITE)

    P1.draw(DISPLAYSURF)
    E1.draw(DISPLAYSURF)
    C1.draw(DISPLAYSURF)

    # Score
    score_text = font.render("Score: " + str(score), True, BLACK)
    DISPLAYSURF.blit(score_text, (300, 10))

    pygame.display.update()
    FramePerSec.tick(FPS)
