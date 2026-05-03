import pygame
import sys
import random
import time
from pygame.locals import *

pygame.init()
pygame.mixer.init()
# звуковую систему
FPS = 60
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

BASE_SPEED = 5      # Начальная скорость врага
SPEED = BASE_SPEED  # Текущая скорость врага
SCORE = 0           # Сколько врагов пропущено
COINS = 0           # Количество набранных монет
N = 5               # Каждые N монет скорость увеличивается

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Шифры
font_small = pygame.font.SysFont("Verdana", 20)
font_big = pygame.font.SysFont("Verdana", 60)
game_over_text = font_big.render("Game Over", True, BLACK)

# пути изоброжение
BACKGROUND_PATH = "AnimatedStreet.png"
ENEMY_PATH = "Enemy.png"
PLAYER_PATH = "Player.png"
COIN_PATH = "coin.png"
RED_COIN_PATH = "coin1.png" 
# окно
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer - Practice 11")

# загрузка фона
background = pygame.image.load(BACKGROUND_PATH)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # изоброжание
        self.image = pygame.image.load(ENEMY_PATH)
        # получение прямоугольника изображения
        self.rect = self.image.get_rect()
        # устоновка позиции
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)

    def move(self):
        # глобалная перемменая
        global SCORE

        # Двигаем врага вниз
        self.rect.move_ip(0, SPEED)

        # Если враг ушел за экран, увеличиваем счет пропущенных
        # и возвращаем его наверх в случайную позицию
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset()

    def reset(self):
        # объект выше экрана 
        self.rect.top = -100
        # перезапис позитций
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # загруска изоб
        self.image = pygame.image.load(PLAYER_PATH)
        # получение прямоугольника изображения
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        #состояние клавиш

        # Движение влево и не даёт выйти за левую границу
        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-5, 0)
            #движение на 5 пикселей влево

        # Движение вправо и ограничение по правой границе 
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            #движение на 5 пикселей вправо
            self.rect.move_ip(5, 0)


# Монеты бывают двух типов:
# 1) обычная монета — вес 1
# 2) красная монета — вес 3
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Загружаем оба изображения заранее
        self.image_small = pygame.image.load(COIN_PATH)
        self.image_red = pygame.image.load(RED_COIN_PATH)
        self.image = self.image_small
        self.weight = 1
        self.rect = self.image.get_rect()
        self.reset()
        # Сброс позиции

    def reset(self):
        # Случайно выбираем тип монеты
        # 0 -> обычная монета, 1 -> красная монета
        coin_type = random.randint(0, 1)
        # Если выпала красная монета
        if coin_type == 1:
            self.image = self.image_red
            self.weight = 3
        # Иначе — обычная монета
        else:
            self.image = self.image_small
            self.weight = 1

        # Сбрасываем монету наверх в случайную позицию
        self.rect = self.image.get_rect()
        self.rect.top = -50
        # Случайная позиция
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

    def move(self):
        # Монета движется вниз со скоростью врага
        self.rect.move_ip(0, SPEED)

        # Если монета ушла за экран, создаем новую
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

# обьекты
P1 = Player()
E1 = Enemy()
C1 = Coin()

# спрайты

enemies = pygame.sprite.Group()
enemies.add(E1)

coins_group = pygame.sprite.Group()
coins_group.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, C1)


while True:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Фон
    DISPLAYSURF.blit(background, (0, 0))


    scores = font_small.render(f"Score: {SCORE}", True, BLACK)
    #создание изображения с текстом 
    coin_scores = font_small.render(f"Coins: {COINS}", True, BLACK)
    #создание изображения c текстом
    DISPLAYSURF.blit(scores, (10, 10))
    # Отрисовка на экран
    DISPLAYSURF.blit(coin_scores, (SCREEN_WIDTH - 120, 10))
    # Отрисовка на экран 

    # Проход по всем спрайтам 
    for entity in all_sprites:
        #Отрисовка
        DISPLAYSURF.blit(entity.image, entity.rect)
        #  Движение 
        entity.move()

    # Проверка столкновения
    if pygame.sprite.collide_rect(P1, C1):
        #Сохранение старого значения
        old_coins = COINS
        # Добавление монет
        COINS += C1.weight

        # Увеличиваем скорость врага каждый раз,
        # когда игрок пересекает границу N монет
        old_level = old_coins // N
        new_level = COINS // N

        # Если за одну монету игрок перепрыгнул сразу несколько уровней,
        # увеличим скорость на нужное количество
        if new_level > old_level:
            SPEED += (new_level - old_level)

        # После сбора монеты создаем новую
        C1.reset()

   # Проверка столкновения 
    if pygame.sprite.spritecollideany(P1, enemies):
        # Пауза перед экраном поражения
        time.sleep(0.5)
        # Красный экран
        DISPLAYSURF.fill(RED)
        #Текст Game Over
        DISPLAYSURF.blit(game_over_text, (30, 250))
        # Обновление экрана
        pygame.display.update()
        # Пауза перед выходом
        time.sleep(2)
        pygame.quit()
        sys.exit()

    # Обновление экрана
    pygame.display.update()
    FramePerSec.tick(FPS)
