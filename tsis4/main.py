import pygame
import random
import sys

from db import Database
from config1 import load_settings, save_settings
from game import GameLogic, CELL, WIDTH, HEIGHT

# ------------------------------------------------------------------ #
#  Инициализация                                                       #
# ------------------------------------------------------------------ #
pygame.init()

db       = Database()
settings = load_settings()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake TSIS 4")

font_big  = pygame.font.SysFont("Arial", 28, bold=True)
font_med  = pygame.font.SysFont("Arial", 22)
font_small= pygame.font.SysFont("Arial", 18)
clock     = pygame.time.Clock()

# ------------------------------------------------------------------ #
#  Цвета                                                               #
# ------------------------------------------------------------------ #
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 215, 0)
GREEN      = (0,   220, 0)
DARK_RED   = (139, 0,   0)
BLUE_DARK  = (20,  20,  60)
GREY_DARK  = (20,  20,  20)


# ------------------------------------------------------------------ #
#  Вспомогательные функции                                             #
# ------------------------------------------------------------------ #
def draw_background():
    screen.fill(GREY_DARK)


def draw_text_centered(text, font, color, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


def draw_text(text, font, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))


# ------------------------------------------------------------------ #
#  Экран ввода имени                                                   #
# ------------------------------------------------------------------ #
def input_username():
    username = ""
    while True:
        draw_background()
        draw_text_centered("SNAKE  TSIS 4", font_big, YELLOW, 80)
        draw_text_centered("Enter your username:", font_med, WHITE, 160)

        # Поле ввода
        box_rect = pygame.Rect(WIDTH // 2 - 120, 195, 240, 36)
        pygame.draw.rect(screen, (50, 50, 50), box_rect, border_radius=6)
        pygame.draw.rect(screen, YELLOW, box_rect, 2, border_radius=6)
        draw_text(username + "|", font_med, YELLOW, box_rect.x + 8, box_rect.y + 5)

        draw_text_centered("Press ENTER to continue", font_small, (150, 150, 150), 260)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(username) > 0:
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 15 and event.unicode.isprintable() and event.unicode != "":
                    username += event.unicode


# ------------------------------------------------------------------ #
#  Главное меню                                                        #
# ------------------------------------------------------------------ #
def main_menu(username, player_id):
    options = [
        ("1  —  Play",         pygame.K_1),
        ("2  —  Leaderboard",  pygame.K_2),
        ("3  —  Settings",     pygame.K_3),
        ("4  —  Quit",         pygame.K_4),
    ]
    while True:
        best = db.get_personal_best(player_id)
        draw_background()
        draw_text_centered("S N A K E", font_big, GREEN, 40)
        draw_text_centered(f"Welcome,  {username}!", font_med, YELLOW, 85)
        draw_text_centered(f"Personal best:  {best}", font_small, (150, 220, 150), 115)

        for i, (label, _) in enumerate(options):
            draw_text_centered(label, font_med, WHITE, 165 + i * 45)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    run_game(player_id, best)
                elif event.key == pygame.K_2:
                    show_leaderboard()
                elif event.key == pygame.K_3:
                    show_settings()
                elif event.key == pygame.K_4:
                    db.close(); pygame.quit(); sys.exit()


# ------------------------------------------------------------------ #
#  Таблица лидеров                                                     #
# ------------------------------------------------------------------ #
def show_leaderboard():
    records = db.get_top_10()
    while True:
        draw_background()
        draw_text_centered("TOP-10 LEADERBOARD", font_big, YELLOW, 15)

        # Заголовок таблицы
        headers = ["#", "Player", "Score", "Lvl", "Date"]
        col_x   = [30, 65, 290, 365, 425]
        for hx, h in zip(col_x, headers):
            draw_text(h, font_small, (180, 180, 180), hx, 55)
        pygame.draw.line(screen, (80, 80, 80), (25, 75), (575, 75))

        for i, (name, score, lvl, date) in enumerate(records):
            y   = 85 + i * 27
            row_color = YELLOW if i == 0 else WHITE
            for val, hx in zip([str(i+1), name, str(score), str(lvl), str(date)], col_x):
                draw_text(val, font_small, row_color, hx, y)

        draw_text_centered("ESC  —  Back", font_small, (120, 120, 120), 370)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


# ------------------------------------------------------------------ #
#  Настройки                                                           #
# ------------------------------------------------------------------ #
def show_settings():
    global settings
    color_options = [
        ([0, 255, 0],   "Green"),
        ([255, 255, 255], "White"),
        ([0, 255, 255], "Cyan"),
        ([255, 165, 0], "Orange"),
        ([255, 50, 50], "Red"),
    ]

    def current_color_name():
        for rgb, name in color_options:
            if settings.get("snake_color") == rgb:
                return name
        return "Custom"

    while True:
        draw_background()
        draw_text_centered("SETTINGS", font_big, YELLOW, 30)

        grid_status  = "ON"  if settings.get("grid_overlay") else "OFF"
        sound_status = "ON"  if settings.get("sound")        else "OFF"
        color_name   = current_color_name()

        rows = [
            f"1  —  Grid overlay:  {grid_status}",
            f"2  —  Sound:         {sound_status}",
            f"3  —  Snake color:   {color_name}",
        ]
        for i, row in enumerate(rows):
            draw_text_centered(row, font_med, WHITE, 110 + i * 55)

        # Предпросмотр цвета змейки
        preview_color = tuple(settings.get("snake_color", [0, 255, 0]))
        pygame.draw.rect(screen, preview_color, [WIDTH // 2 + 90, 217, 20, 20])

        draw_text_centered("ESC  —  Save & Back", font_small, (120, 120, 120), 360)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    return
                if event.key == pygame.K_1:
                    settings["grid_overlay"] = not settings.get("grid_overlay", True)
                if event.key == pygame.K_2:
                    settings["sound"] = not settings.get("sound", True)
                if event.key == pygame.K_3:
                    cur = settings.get("snake_color", [0, 255, 0])
                    rgbs = [c[0] for c in color_options]
                    idx  = rgbs.index(cur) if cur in rgbs else 0
                    settings["snake_color"] = color_options[(idx + 1) % len(color_options)][0]


# ------------------------------------------------------------------ #
#  Игровой процесс                                                     #
# ------------------------------------------------------------------ #
def run_game(player_id, best_score):
    global settings
    settings = load_settings()   # обновим настройки перед стартом
    logic = GameLogic(settings)

    # Начальные значения
    snake      = [[260, 200], [280, 200], [300, 200]]
    direction  = "RIGHT"
    change_to  = "RIGHT"
    score      = 0
    level      = 1
    base_speed = 10
    cur_speed  = base_speed

    food_pos   = logic.spawn_food(snake)
    poison_pos = logic.spawn_food(snake)

    powerup       = None   # [x, y, type, expire_ticks]
    powerup_end   = 0      # когда заканчивается эффект бонуса
    shield_active = False

    running = True
    while running:
        ticks = pygame.time.get_ticks()

        # --- Ввод ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direction != "DOWN":  change_to = "UP"
                if event.key == pygame.K_DOWN  and direction != "UP":    change_to = "DOWN"
                if event.key == pygame.K_LEFT  and direction != "RIGHT": change_to = "LEFT"
                if event.key == pygame.K_RIGHT and direction != "LEFT":  change_to = "RIGHT"
                if event.key == pygame.K_ESCAPE:
                    running = False

        direction = change_to

        # --- Движение ---
        head = list(snake[-1])
        if direction == "UP":    head[1] -= CELL
        elif direction == "DOWN":  head[1] += CELL
        elif direction == "LEFT":  head[0] -= CELL
        elif direction == "RIGHT": head[0] += CELL

        # --- Проверка столкновений ---
        wall_hit = head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT
        self_hit = head in snake[:-1]
        obs_hit  = head in logic.obstacles

        if wall_hit or self_hit or obs_hit:
            if shield_active:
                # Щит поглощает одно столкновение
                shield_active = False
                # Телепортируем голову обратно внутрь поля при ударе о стену
                head[0] = max(0, min(head[0], WIDTH  - CELL))
                head[1] = max(0, min(head[1], HEIGHT - CELL))
            else:
                running = False
                break

        snake.append(head)

        # --- Еда ---
        if head == food_pos:
            score += 1
            food_pos = logic.spawn_food(snake)
            if score % 3 == 0:
                level     += 1
                base_speed = min(base_speed + 2, 25)
                logic.generate_obstacles(level, snake)

        else:
            snake.pop(0)   # убираем хвост только если не съели еду

        # --- Яд ---
        if head == poison_pos:
            remove = 2
            snake  = snake[remove:]   # укорачиваем змею на 2
            poison_pos = logic.spawn_food(snake)
            if len(snake) < 1:
                running = False
                break

        # --- Бонус: появление ---
        if powerup is None and random.randint(1, 120) == 1:
            pos    = logic.spawn_food(snake)
            ptype  = random.choice(["speed", "slow", "shield"])
            powerup = [pos[0], pos[1], ptype, ticks + 8000]

        # --- Бонус: истечение времени ---
        if powerup and ticks > powerup[3]:
            powerup = None

        # --- Бонус: подбор ---
        if powerup and head == [powerup[0], powerup[1]]:
            ptype = powerup[2]
            if ptype == "speed":
                cur_speed   = base_speed + 7
                powerup_end = ticks + 5000
            elif ptype == "slow":
                cur_speed   = max(4, base_speed - 5)
                powerup_end = ticks + 5000
            elif ptype == "shield":
                shield_active = True
            powerup = None

        # --- Сброс эффекта бонуса скорости ---
        if ticks > powerup_end:
            cur_speed = base_speed

        # ========== ОТРИСОВКА ==========
        screen.fill(BLACK)
        logic.draw_grid(screen)
        logic.draw_obstacles(screen)

        # Еда
        pygame.draw.rect(screen, (0, 220, 0),   [food_pos[0],   food_pos[1],   CELL, CELL])
        pygame.draw.rect(screen, (139, 0, 0),   [poison_pos[0], poison_pos[1], CELL, CELL])

        # Бонус
        if powerup:
            color = GameLogic.powerup_color(powerup[2])
            pygame.draw.rect(screen, color, [powerup[0], powerup[1], CELL, CELL])
            # Иконка-буква
            lbl = font_small.render(powerup[2][0].upper(), True, BLACK)
            screen.blit(lbl, (powerup[0] + 3, powerup[1] + 1))

        # Змейка
        snake_color = tuple(settings.get("snake_color", [0, 255, 0]))
        for i, seg in enumerate(snake):
            col = (100, 200, 255) if shield_active else snake_color
            # Голова чуть светлее
            if i == len(snake) - 1:
                col = tuple(min(255, c + 40) for c in col)
            pygame.draw.rect(screen, col, [seg[0], seg[1], CELL, CELL])

        # HUD
        hud = f"Score: {score}   Lvl: {level}   PB: {best_score}"
        if shield_active:
            hud += "   [SHIELD]"
        draw_text(hud, font_small, WHITE, 6, 6)

        pygame.display.flip()
        clock.tick(cur_speed)

    # Сохраняем результат
    db.save_session(player_id, score, level)
    return show_game_over(score, level, best_score, player_id)


# ------------------------------------------------------------------ #
#  Экран Game Over                                                     #
# ------------------------------------------------------------------ #
def show_game_over(score, level, best_score, player_id):
    new_best = db.get_personal_best(player_id)
    is_new_record = new_best > best_score

    while True:
        screen.fill((50, 0, 0))
        draw_text_centered("GAME  OVER", font_big, WHITE, 60)
        draw_text_centered(f"Score: {score}     Level: {level}", font_med, WHITE, 120)
        if is_new_record:
            draw_text_centered("🏆  NEW PERSONAL BEST!", font_med, YELLOW, 160)
        else:
            draw_text_centered(f"Personal best: {new_best}", font_small, (200, 200, 200), 160)

        draw_text_centered("R  —  Restart", font_med, (200, 255, 200), 220)
        draw_text_centered("M  —  Main Menu", font_med, (200, 255, 200), 260)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return run_game(player_id, new_best)
                if event.key == pygame.K_m:
                    return   # вернёмся в main_menu


# ------------------------------------------------------------------ #
#  Точка входа                                                         #
# ------------------------------------------------------------------ #
def main():
    username  = input_username()
    player_id = db.get_or_create_player(username)
    main_menu(username, player_id)


if __name__ == "__main__":
    main()
