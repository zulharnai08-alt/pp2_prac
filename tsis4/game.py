import pygame
import random

# Типы объектов на поле
FOOD    = "food"
POISON  = "poison"
POWERUP = "powerup"

# Размер клетки и размеры поля
CELL  = 20
WIDTH  = 600
HEIGHT = 400

# Цвета препятствий и бонусов
COLOR_OBSTACLE = (120, 120, 120)
COLOR_FOOD     = (0, 255, 0)
COLOR_POISON   = (139, 0, 0)
COLOR_SHIELD   = (0, 180, 255)
COLOR_SPEED    = (255, 200, 0)
COLOR_SLOW     = (180, 0, 255)
COLOR_GRID     = (35, 35, 35)


class GameLogic:
    def __init__(self, settings):
        self.settings  = settings
        self.obstacles = []

    # ------------------------------------------------------------------ #
    #  Препятствия                                                         #
    # ------------------------------------------------------------------ #
    def generate_obstacles(self, level, snake_list):
        """Генерирует препятствия начиная с 3-го уровня."""
        if level < 3:
            return

        count = min(5 + level * 2, 30)   # не больше 30 блоков
        attempts = 0
        new_obstacles = []

        while len(new_obstacles) < count and attempts < 1000:
            attempts += 1
            pos = [
                random.randrange(0, WIDTH,  CELL),
                random.randrange(0, HEIGHT, CELL)
            ]
            # Не ставим вплотную к любому сегменту змейки (зона 3×3 от позиции)
            too_close = any(
                abs(pos[0] - s[0]) <= CELL * 2 and abs(pos[1] - s[1]) <= CELL * 2
                for s in snake_list
            )
            if not too_close and pos not in new_obstacles:
                new_obstacles.append(pos)

        self.obstacles = new_obstacles

    def draw_obstacles(self, screen):
        for obs in self.obstacles:
            pygame.draw.rect(screen, COLOR_OBSTACLE, [obs[0], obs[1], CELL, CELL])
            # Небольшая рамка для объёма
            pygame.draw.rect(screen, (80, 80, 80), [obs[0], obs[1], CELL, CELL], 2)

    # ------------------------------------------------------------------ #
    #  Спавн объектов                                                      #
    # ------------------------------------------------------------------ #
    def spawn_food(self, snake_list):
        """Возвращает свободную позицию для еды / яда / бонуса."""
        for _ in range(500):
            pos = [
                random.randrange(0, WIDTH,  CELL),
                random.randrange(0, HEIGHT, CELL)
            ]
            if pos not in snake_list and pos not in self.obstacles:
                return pos
        # Аварийный fallback — возвращаем любую свободную клетку
        for x in range(0, WIDTH, CELL):
            for y in range(0, HEIGHT, CELL):
                pos = [x, y]
                if pos not in snake_list and pos not in self.obstacles:
                    return pos
        return [0, 0]   # поле почти заполнено

    # ------------------------------------------------------------------ #
    #  Сетка                                                               #
    # ------------------------------------------------------------------ #
    def draw_grid(self, screen):
        if not self.settings.get("grid_overlay", True):
            return
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (WIDTH, y))

    # ------------------------------------------------------------------ #
    #  Отрисовка бонусов                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def powerup_color(ptype):
        return {
            "speed":  COLOR_SPEED,
            "slow":   COLOR_SLOW,
            "shield": COLOR_SHIELD,
        }.get(ptype, (255, 255, 255))
