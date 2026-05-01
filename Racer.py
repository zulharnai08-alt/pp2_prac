import pygame
import sys
import random
import time
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# размеры окна
a = 400
b = 600

# FPS и таймер
c = 60
d = pygame.time.Clock()

# скорость врага
g = 5

# счётчики
t = 0   # Score
y = 0   # Coins
u = 5   # Каждые 5 монет скорость увеличивается

# цвета
w = (0, 0, 0)
x = (255, 255, 255)
z = (255, 0, 0)

# шрифты
i = pygame.font.SysFont("Verdana", 20)
o = pygame.font.SysFont("Verdana", 60)

# тексты
p = o.render("Game Over", True, w)

# пути к картинкам
v = r"C:\Users\zulha\Downloads\AnimatedStreet.png"
k = r"C:\Users\zulha\Downloads\Enemy.png"
l = r"C:\Users\zulha\Downloads\Player.png"
m = r"C:\Users\zulha\Downloads\coin.png"
n = r"C:\Users\zulha\Downloads\coin1.png"

# окно игры
s = pygame.display.set_mode((a, b))
pygame.display.set_caption("Racer")

# фон
f = pygame.image.load(v)

# враг
class A(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(k)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, a - 40), -100)

    def move(self):
        global t

        self.rect.move_ip(0, g)

        if self.rect.top > b:
            t += 1
            self.reset()

    def reset(self):
        self.rect.top = -100
        self.rect.center = (random.randint(40, a - 40), -100)

# игрок
class B(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(l)
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        key = pygame.key.get_pressed()

        if key[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)

        if key[K_RIGHT] and self.rect.right < a:
            self.rect.move_ip(5, 0)

# монета
class C(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.a1 = pygame.image.load(m)   # обычная монета
        self.b1 = pygame.image.load(n)   # красная монета
        self.image = self.a1
        self.weight = 1
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        r = random.randint(0, 1)

        if r == 1:
            self.image = self.b1
            self.weight = 3
        else:
            self.image = self.a1
            self.weight = 1

        self.rect = self.image.get_rect()
        self.rect.top = -50
        self.rect.center = (random.randint(40, a - 40), -50)

    def move(self):
        self.rect.move_ip(0, g)

        if self.rect.top > b:
            self.reset()

# объекты
j = B()
q = A()
r = C()

# группы
e = pygame.sprite.Group()
e.add(q)

all_sprites = pygame.sprite.Group()
all_sprites.add(j, q, r)

# цикл игры
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # фон
    s.blit(f, (0, 0))

    # счёт
    score_text = i.render(f"Score: {t}", True, w)
    coin_text = i.render(f"Coins: {y}", True, w)
    s.blit(score_text, (10, 10))
    s.blit(coin_text, (a - 120, 10))

    # движение всех объектов
    for item in all_sprites:
        s.blit(item.image, item.rect)
        item.move()

    # сбор монеты
    if pygame.sprite.collide_rect(j, r):
        old_coins = y
        y += r.weight

        old_level = old_coins // u
        new_level = y // u

        if new_level > old_level:
            g += (new_level - old_level)

        r.reset()

    # столкновение с врагом
    if pygame.sprite.spritecollideany(j, e):
        try:
            pygame.mixer.Sound('crash.wav').play()
        except:
            pass

        time.sleep(0.5)
        s.fill(z)
        s.blit(p, (30, 250))
        pygame.display.update()
        time.sleep(2)

        pygame.quit()
        sys.exit()

    pygame.display.update()
    d.tick(c)
