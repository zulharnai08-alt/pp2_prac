import pygame
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, color="Blue"):
        super().__init__() 
        # Поддержка разных цветов машин через настройки
        color_map = {"Blue": "Player.png", "Orange": "Player2.png", "Pink": "Player3.png"}
        filename = color_map.get(color, "Player.png")
        
        try:
            self.image = pygame.image.load(filename)
        except:
            self.image = pygame.Surface((40, 60))
            self.image.fill((0, 0, 255))
        
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < 400 and pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        try: self.image = pygame.image.load("Enemy.png")
        except: self.image = pygame.Surface((40, 60)); self.image.fill((255,0,0))
        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600:
            self.reset()
            return True 
        return False

    def reset(self):
        self.rect.center = (random.randint(40, 360), random.randint(-400, -100))

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.img_small = pygame.image.load("coin.png")
            self.img_red = pygame.image.load("coin1.png")
        except:
            self.img_small = pygame.Surface((20,20)); self.img_small.fill((255,255,0))
            self.img_red = pygame.Surface((20,20)); self.img_red.fill((255,0,0))
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600: self.reset()

    def reset(self):
        if random.randint(0, 1) == 1: self.image, self.weight = self.img_red, 3
        else: self.image, self.weight = self.img_small, 1
        pos_x = random.randint(40, 360)
        pos_y = random.randint(-300, -50)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try: self.image = pygame.image.load("oil.png")
        except: self.image = pygame.Surface((40,40)); self.image.fill((0,0,0))
        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600: self.reset()

    def reset(self):
        self.rect.center = (random.randint(40, 360), random.randint(-1500, -500))

class NitroStrip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try: self.image = pygame.image.load("nitro.png")
        except: self.image = pygame.Surface((40,40)); self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600: self.reset()

    def reset(self):
        self.rect.center = (random.randint(40, 360), random.randint(-2000, -800))

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        self.type = type
        try: self.image = pygame.image.load(f"{type}.png")
        except: self.image = pygame.Surface((30,30)); self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600: self.reset()

    def reset(self):
        self.rect.center = (random.randint(40, 360), random.randint(-3000, -1000))
