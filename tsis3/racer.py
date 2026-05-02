import pygame
import random

# ===================== ИГРОК =====================
class Player(pygame.sprite.Sprite):
    def __init__(self, img_path):
        super().__init__()

        # Загружаем картинку машины
        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            # Если не загрузилось — будет синий прямоугольник
            self.image = pygame.Surface((40, 60))
            self.image.fill((0, 0, 255))

        # Позиция машины
        self.rect = self.image.get_rect()
        self.rect.center = (200, 520)

    def move(self):
        # Управление стрелками
        keys = pygame.key.get_pressed()

        if self.rect.left > 0 and keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < 400 and keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)


# ===================== ВРАГ =====================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, img_path):
        super().__init__()

        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((40, 60))
            self.image.fill((255, 0, 0))

        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        # Движение вниз
        self.rect.move_ip(0, speed)

        # Если вышел за экран — вернуть вверх
        if self.rect.top > 600:
            self.reset()
            return True  # даём очко
        return False

    def reset(self):
        # Случайная позиция сверху
        self.rect.center = (
            random.randint(40, 360),
            random.randint(-400, -100)
        )


# ===================== МОНЕТЫ =====================
class Coin(pygame.sprite.Sprite):
    def __init__(self, img1, img2):
        super().__init__()

        try:
            # Обычная монета
            self.img_small = pygame.image.load(img1).convert_alpha()
            # Красная (дороже)
            self.img_red = pygame.image.load(img2).convert_alpha()
        except:
            self.img_small = pygame.Surface((20, 20))
            self.img_small.fill((255, 255, 0))
            self.img_red = pygame.Surface((20, 20))
            self.img_red.fill((255, 0, 0))

        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > 600:
            self.reset()

    def reset(self):
        # Случайный тип монеты
        if random.randint(0, 1):
            self.image = self.img_red
            self.weight = 3  # больше очков
        else:
            self.image = self.img_small
            self.weight = 1

        self.rect = self.image.get_rect(
            center=(random.randint(40, 360), random.randint(-300, -50))
        )


# ===================== МАСЛО (препятствие) =====================
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, img_path):
        super().__init__()

        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill((0, 0, 0))

        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > 600:
            self.reset()

    def reset(self):
        self.rect.center = (
            random.randint(40, 360),
            random.randint(-1500, -500)
        )


# ===================== НИТРО =====================
class NitroStrip(pygame.sprite.Sprite):
    def __init__(self, img_path):
        super().__init__()

        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > 600:
            self.reset()

    def reset(self):
        self.rect.center = (
            random.randint(40, 360),
            random.randint(-2000, -800)
        )


# ===================== БОНУСЫ =====================
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, img_path):
        super().__init__()

        try:
            self.image = pygame.image.load(img_path).convert_alpha()
        except:
            self.image = pygame.Surface((30, 30))
            self.image.fill((255, 255, 255))

        self.rect = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)

        if self.rect.top > 600:
            self.reset()

    def reset(self):
        self.rect.center = (
            random.randint(40, 360),
            random.randint(-3000, -1000)
        )
