import pygame
import random
import sys

from db import Database
from config1 import load_settings, save_settings
from game import GameLogic, CELL, WIDTH, HEIGHT

pygame.init()

db       = Database()         # подключение к БД (создаёт таблицы)
settings = load_settings()    # загрузка настроек

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # окно игры
clock  = pygame.time.Clock()


def input_username():
    username = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()  # жёсткий выход

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(username) > 0:
                    return username.strip()  # возврат имени
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]  # удаление символа
                elif len(username) < 15 and event.unicode.isprintable():
                    username += event.unicode  # ввод текста


def main_menu(username, player_id):
    while True:
        best = db.get_personal_best(player_id)  # запрос к БД (может быть частым)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    run_game(player_id, best)
                elif event.key == pygame.K_4:
                    db.close()  # важно закрыть соединение
                    pygame.quit(); sys.exit()


def run_game(player_id, best_score):
    global settings
    settings = load_settings()   # перезагрузка настроек перед игрой

    logic = GameLogic(settings)  # вся игровая логика вынесена в отдельный класс

    snake = [[260, 200], [280, 200], [300, 200]]
    direction = "RIGHT"

    score = 0
    level = 1
    base_speed = 10
    cur_speed  = base_speed

    food_pos   = logic.spawn_food(snake)
    poison_pos = logic.spawn_food(snake)

    powerup       = None
    powerup_end   = 0
    shield_active = False

    while True:
        ticks = pygame.time.get_ticks()  # таймер для бонусов и эффектов

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # --- движение ---
        head = list(snake[-1])  # копия головы (важно, иначе баги со ссылками)

        # --- столкновения ---
        wall_hit = head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT
        self_hit = head in snake[:-1]
        obs_hit  = head in logic.obstacles

        if wall_hit or self_hit or obs_hit:
            if not shield_active:
                break  # завершение игры
            shield_active = False  # щит спасает один раз

        snake.append(head)

        # --- еда ---
        if head == food_pos:
            score += 1
            food_pos = logic.spawn_food(snake)

            if score % 3 == 0:
                level += 1
                base_speed = min(base_speed + 2, 25)  # ограничение скорости
                logic.generate_obstacles(level, snake)
        else:
            snake.pop(0)  # движение змеи

        # --- яд ---
        if head == poison_pos:
            snake = snake[2:]  # укорачиваем (может убить сразу)
            if len(snake) < 1:
                break

        # --- бонусы ---
        if powerup is None and random.randint(1, 120) == 1:
            pos   = logic.spawn_food(snake)
            ptype = random.choice(["speed", "slow", "shield"])
            powerup = [pos[0], pos[1], ptype, ticks + 8000]  # время жизни бонуса

        if powerup and ticks > powerup[3]:
            powerup = None  # исчезновение бонуса

        if powerup and head == [powerup[0], powerup[1]]:
            if powerup[2] == "speed":
                cur_speed   = base_speed + 7
                powerup_end = ticks + 5000
            elif powerup[2] == "slow":
                cur_speed   = max(4, base_speed - 5)
                powerup_end = ticks + 5000
            elif powerup[2] == "shield":
                shield_active = True
            powerup = None

        if ticks > powerup_end:
            cur_speed = base_speed  # сброс эффекта

        clock.tick(cur_speed)  # управление FPS = скорость игры

    db.save_session(player_id, score, level)  # сохранение результата в БД
    return show_game_over(score, level, best_score, player_id)


def main():
    username  = input_username()
    player_id = db.get_or_create_player(username)  # создание/получение игрока из БД
    main_menu(username, player_id)


if __name__ == "__main__":
    main()  # точка входа
