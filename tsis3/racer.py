import pygame
import random
import os

# папка с картинками — та же где лежат скрипты
ASSET_DIR = r"C:\Users\zulha\cod\python"

def load_img(filename, size=None):
    """загружает картинку, масштабирует если нужно"""
    path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"не удалось загрузить {filename}: {e}")
        surf = pygame.Surface(size or (40, 60), pygame.SRCALPHA)
        surf.fill((200, 200, 200))
        return surf


# ===================== игрок =====================
class Player(pygame.sprite.Sprite):
    def __init__(self, color="Blue"):
        super().__init__()
        # Player.png = синяя, Player2.png = оранжевая, Player3.png = фиолетовая
        color_map = {
            "Blue":   "Player.png",
            "Orange": "Player2.png",
            "Purple": "Player3.png",
        }
        filename = color_map.get(color, "Player.png")
        self.image = load_img(filename, (40, 70))
        self.rect  = self.image.get_rect(center=(200, 520))

    def move(self):
        """движение стрелками влево/вправо"""
        keys = pygame.key.get_pressed()
        if self.rect.left > 20 and keys[pygame.K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < 380 and keys[pygame.K_RIGHT]:
            self.rect.move_ip(5, 0)


# ===================== враг =====================
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_img("Enemy.png", (40, 70))
        self.rect  = self.image.get_rect()
        self.reset()

    def move(self, speed):
        """возвращает True если враг уехал вниз (обогнал = очко)"""
        self.rect.move_ip(0, speed)
        if self.rect.top > 600:
            return True  # сигнал для main.py — нужен ресет
        return False

    def reset(self, others=None, min_dist=80):
        """спавнит врага, стараясь не ставить слишком близко к другим.
        others — список всех врагов для проверки расстояния.
        min_dist — минимальное расстояние в пикселях между центрами."""
        for _ in range(30):  # максимум 30 попыток найти свободное место
            x = random.randint(40, 360)
            y = random.randint(-500, -100)

            if others is None:
                break  # нет других врагов — просто ставим

            # проверяем расстояние до каждого другого врага
            too_close = False
            for other in others:
                if other is self:
                    continue  # пропускаем самого себя
                dist_x = abs(other.rect.centerx - x)
                dist_y = abs(other.rect.centery - y)
                if dist_x < min_dist and dist_y < min_dist:
                    too_close = True
                    break  # слишком близко — пробуем новую позицию

            if not too_close:
                break  # нашли подходящее место — выходим из цикла

        self.rect.center = (x, y)


# ===================== монеты =====================
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img_normal = load_img("coin.png",  (24, 24))   # обычная — 1 очко
        self.img_red    = load_img("coin1.png", (24, 24))   # красная — 3 очка
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600:
            self.reset()

    def reset(self):
        if random.randint(0, 3) == 0:   # 25% шанс красной монеты
            self.image  = self.img_red
            self.weight = 3
        else:
            self.image  = self.img_normal
            self.weight = 1
        self.rect = self.image.get_rect(
            center=(random.randint(40, 360), random.randint(-400, -50))
        )


# ===================== препятствие (масло) =====================
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_img("oil.png", (40, 40))
        self.rect  = self.image.get_rect()
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600:
            self.reset()

    def reset(self):
        self.rect.center = (
            random.randint(40, 360),
            random.randint(-1500, -600)
        )


# ===================== нитро полоса =====================
class NitroStrip(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_img("nitro.png", (50, 25))
        self.rect  = self.image.get_rect()
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


# ===================== бонусы =====================
class PowerUp(pygame.sprite.Sprite):
    TYPES = ["nitro", "shield", "repair"]

    def __init__(self):
        super().__init__()
        self._imgs = {
            "nitro":  load_img("nitro.png",  (32, 32)),
            "shield": load_img("shield.png", (32, 32)),
            "repair": load_img("coin1.png",  (32, 32)),  # заглушка для repair
        }
        self.kind = None
        self.reset()

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > 600:
            self.reset()

    def reset(self):
        """случайный тип бонуса при каждом сбросе"""
        self.kind  = random.choice(self.TYPES)
        self.image = self._imgs[self.kind]
        self.rect  = self.image.get_rect(
            center=(random.randint(40, 360), random.randint(-3000, -1000))
        )
