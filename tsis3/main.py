import pygame
import sys
import os
import random

from racer       import Player, Enemy, Coin, Obstacle, NitroStrip, PowerUp, ASSET_DIR
from ui          import Button, draw_text, input_name_screen
from persistence import save_score, get_top_scores, load_settings, save_settings

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("racer tsis3")
clock = pygame.time.Clock()

# цвета для фона и дороги
BG_DARK   = (15, 15, 30)
ROAD_COL  = (40, 40, 50)
LINE_COL  = (200, 200, 100)

# карта сложности → базовая скорость врагов и объектов
DIFF_MAP = {"Easy": 3, "Medium": 5, "Hard": 8}

# загружаем настройки из settings.json при старте
current_settings = load_settings()


# --- функция: запуск фоновой музыки ---
def play_music():
    # не играть музыку если звук выключен в настройках
    if not current_settings.get("sound", True):
        return
    music_path = os.path.join(ASSET_DIR, "music.ogg")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # -1 = бесконечный повтор


road_y = 0  # глобальное смещение разметки для анимации прокрутки дороги

# --- функция: отрисовка дороги с движущейся разметкой ---
def draw_road(speed):
    global road_y
    SCREEN.fill(BG_DARK)
    pygame.draw.rect(SCREEN, ROAD_COL, (10, 0, 380, HEIGHT))  # полотно дороги

    road_y = (road_y + speed) % 60  # сдвигаем разметку вниз на каждом кадре
    for y in range(-60 + road_y, HEIGHT, 60):
        pygame.draw.rect(SCREEN, LINE_COL, (WIDTH // 2 - 3, y, 6, 35))  # центральная пунктирная линия


# --- функция: отрисовка интерфейс поверх игры
def draw_hud(score, coins, distance, finish, speed, active_pu, pu_timer):
    # верхняя тёмная панель с очками, монетами и дистанцией
    pygame.draw.rect(SCREEN, (0, 0, 0, 160), (0, 0, WIDTH, 40))
    draw_text(SCREEN, f"score: {score}", 18, 70,  20, (255, 255, 255))
    draw_text(SCREEN, f"coins: {coins}", 18, 200, 20, (255, 215, 0))
    draw_text(SCREEN, f"{int(distance)}/{finish}m", 18, 330, 20, (150, 220, 255))

    # текущая скорость в углу
    draw_text(SCREEN, f"spd {speed}", 15, 370, 50, (180, 180, 180))

    # активный бонус с таймером обратного отсчёта
    if active_pu:
        remaining = max(0, (pu_timer - pygame.time.get_ticks()) // 1000)
        pu_colors = {"nitro": (0, 220, 255), "shield": (200, 0, 255), "repair": (0, 255, 100)}
        col = pu_colors.get(active_pu, (255, 255, 255))
        label = f"{active_pu.upper()}"
        if active_pu != "repair":
            label += f" {remaining}s"
        draw_text(SCREEN, label, 18, WIDTH // 2, 55, col, bold=True)

    # полоса прогресса дистанции внизу экрана
    bar_w = int((distance / finish) * (WIDTH - 40))
    pygame.draw.rect(SCREEN, (60, 60, 60), (20, HEIGHT - 12, WIDTH - 40, 8))   # фон полосы
    pygame.draw.rect(SCREEN, (80, 200, 120), (20, HEIGHT - 12, bar_w, 8))      # заполненная часть


# --- функция: основной игровой цикл ---
def game_loop(user_name):
    pygame.mixer.music.stop()
    play_music()

    base_speed = DIFF_MAP.get(current_settings.get("difficulty", "Medium"), 5)
    FINISH     = 5000  # финиш через 5000 метров

    speed          = base_speed
    score          = 0
    coins          = 0
    distance       = 0.0
    last_milestone = 0  # для отслеживания каждых 1000м (повышение скорости)

    # состояние активных бонусов
    active_pu  = None   # название текущего бонуса
    pu_timer   = 0      # время окончания бонуса (в миллисекундах)
    nitro_on   = False
    shield_on  = False
    has_repair = False  # запас ремонта — поглощает одно столкновение

    # создаём все игровые объекты (спрайты из racer.py)
    player   = Player(color=current_settings.get("car_color", "Blue"))
    enemies  = [Enemy(), Enemy(), Enemy()]
    coin_obj = Coin()
    obstacle = Obstacle()   # масляное пятно
    nitro_s  = NitroStrip() # нитро-полоса на дороге
    powerup  = PowerUp()

    all_sprites = pygame.sprite.Group(player, *enemies, coin_obj, obstacle, nitro_s, powerup)

    while True:
        curr_t = pygame.time.get_ticks()  # текущее время в мс

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # выход в главное меню

        player.move()  # обрабатываем ввод и двигаем игрока

        # эффективная скорость с учётом активных бонусов
        eff = speed
        if nitro_on  and curr_t < pu_timer: eff += 5   # нитро даёт +5 к скорости
        if shield_on and curr_t < pu_timer: pass        # щит на скорость не влияет

        # сбрасываем бонусы по истечении времени
        if nitro_on  and curr_t >= pu_timer:
            nitro_on  = False
            active_pu = None
        if shield_on and curr_t >= pu_timer:
            shield_on = False
            active_pu = None
        eff = max(1, eff)  # скорость не может быть меньше 1

        # накапливаем пройденное расстояние
        distance += eff * 0.08

        # каждые 1000м увеличиваем базовую скорость на 1
        milestone = int(distance) // 1000
        if milestone > last_milestone:
            last_milestone = milestone
            speed += 1

        # двигаем врагов; если враг уехал вниз — ресетим с проверкой расстояния
        for e in enemies:
            if e.move(eff):
                e.reset(others=enemies, min_dist=80)  # минимум 80px между врагами
                score += 1

        coin_obj.move(eff)
        obstacle.move(eff)
        nitro_s.move(eff)
        powerup.move(eff)

        # --- проверка коллизий ---

        # подбор монеты
        if pygame.sprite.collide_rect(player, coin_obj):
            coins += coin_obj.weight  # вес монеты влияет на количество очков
            coin_obj.reset()

        # заезд на нитро-полосу
        if pygame.sprite.collide_rect(player, nitro_s):
            nitro_on  = True
            active_pu = "nitro"
            pu_timer  = curr_t + 4000  # 4 секунды ускорения
            nitro_s.reset()

        # подбор бонуса (powerup)
        if pygame.sprite.collide_rect(player, powerup):
            kind = powerup.kind
            if kind == "nitro":
                nitro_on  = True
                shield_on = False
                active_pu = "nitro"
                pu_timer  = curr_t + 4000
            elif kind == "shield":
                shield_on = True
                nitro_on  = False
                active_pu = "shield"
                pu_timer  = curr_t + 6000  # 6 секунд защиты
            elif kind == "repair":
                has_repair = True   # ремонт активируется при следующем столкновении
                active_pu  = "repair"
                pu_timer   = curr_t + 1
            powerup.reset()

        # столкновение с масляным пятном
        if pygame.sprite.collide_rect(player, obstacle):
            if has_repair:
                has_repair = False  # ремонт поглощает удар
                active_pu  = None
                obstacle.reset()
            else:
                obstacle.reset()  # без ремонта — просто сбрасываем препятствие

        # столкновение с врагом
        for e in enemies:
            if pygame.sprite.collide_rect(player, e):
                if shield_on and curr_t < pu_timer:
                    shield_on = False  # щит поглощает один удар
                    active_pu = None
                    e.reset(others=enemies, min_dist=80)
                elif has_repair:
                    has_repair = False  # ремонт поглощает удар
                    active_pu  = None
                    e.reset(others=enemies, min_dist=80)
                else:
                    # конец игры — сохраняем результат и показываем экран проигрыша
                    total = coins + score
                    save_score(user_name, total, distance)
                    game_over_screen(user_name, total, int(distance), False)
                    return

        # победа — игрок доехал до финиша
        if distance >= FINISH:
            total = coins + score
            save_score(user_name, total, distance)
            game_over_screen(user_name, total, int(distance), True)
            return

        # отрисовка всего на экране
        draw_road(eff)
        all_sprites.draw(SCREEN)
        draw_hud(score, coins, distance, FINISH, eff, active_pu, pu_timer)

        pygame.display.flip()
        clock.tick(60)  # ограничение 60 кадров в секунду


# --- функция: экран конца игры (победа или поражение) ---
def game_over_screen(name, score, distance, won):
    btn_retry = Button(WIDTH // 2, 380, 180, 44, "retry")
    btn_menu  = Button(WIDTH // 2, 440, 180, 44, "main menu")

    while True:
        SCREEN.fill(BG_DARK)
        title = "you won!" if won else "game over"
        col   = (80, 255, 130) if won else (255, 80, 80)  # зелёный — победа, красный — поражение
        draw_text(SCREEN, title,             36, WIDTH // 2, 140, col, bold=True)
        draw_text(SCREEN, f"player: {name}", 22, WIDTH // 2, 210)
        draw_text(SCREEN, f"score:  {score}", 22, WIDTH // 2, 250)
        draw_text(SCREEN, f"distance: {distance}m", 22, WIDTH // 2, 285)
        draw_text(SCREEN, "esc — main menu",  16, WIDTH // 2, 340, (130, 130, 130))

        btn_retry.draw(SCREEN)
        btn_menu.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.is_clicked(event.pos):
                    game_loop(name)  # перезапуск с тем же именем
                    return
                if btn_menu.is_clicked(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.flip()
        clock.tick(60)


# --- функция: экран таблицы рекордов ---
def leaderboard_screen():
    btn_back = Button(WIDTH // 2, 540, 160, 40, "back")
    scores   = get_top_scores()  # получаем топ из persistence.py

    while True:
        SCREEN.fill(BG_DARK)
        draw_text(SCREEN, "leaderboard", 30, WIDTH // 2, 40, (255, 215, 0), bold=True)
        draw_text(SCREEN, "#   name         score   dist", 14, WIDTH // 2, 80, (160, 160, 160))

        for i, s in enumerate(scores[:10]):
            rank_col = (255, 215, 0) if i == 0 else (200, 200, 200)  # золото для первого места
            line = f"{i+1:<3} {s['name']:<12} {s['score']:<7} {s.get('distance', 0)}m"
            draw_text(SCREEN, line, 16, WIDTH // 2, 110 + i * 38, rank_col)

        if not scores:
            draw_text(SCREEN, "no records yet", 22, WIDTH // 2, 300, (120, 120, 120))

        btn_back.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.is_clicked(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.flip()
        clock.tick(60)


# --- функция: экран настроек ---
def settings_screen():
    btn_back = Button(WIDTH // 2, 540, 160, 40, "back & save")

    # три цвета машины: синяя, оранжевая, фиолетовая
    colors       = ["Blue", "Orange", "Purple"]
    difficulties = ["Easy", "Medium", "Hard"]

    # защита от невалидного значения в settings.json
    if current_settings.get("car_color") not in colors:
        current_settings["car_color"] = colors[0]        # → "Blue"
    if current_settings.get("difficulty") not in difficulties:
        current_settings["difficulty"] = difficulties[1]  # → "Medium"

    while True:
        SCREEN.fill(BG_DARK)
        draw_text(SCREEN, "settings", 30, WIDTH // 2, 40, (255, 255, 255), bold=True)

        # переключатель звука
        sound_label = "sound:  on" if current_settings["sound"] else "sound:  off"
        sound_col   = (80, 255, 130) if current_settings["sound"] else (255, 80, 80)
        draw_text(SCREEN, sound_label, 22, WIDTH // 2, 130, sound_col)
        draw_text(SCREEN, "[ click to toggle ]", 15, WIDTH // 2, 158, (120, 120, 120))

        # выбор цвета машины
        draw_text(SCREEN, f"car color:  {current_settings['car_color']}", 22, WIDTH // 2, 220)
        draw_text(SCREEN, "[ < / > to change ]", 15, WIDTH // 2, 248, (120, 120, 120))

        # выбор сложности
        draw_text(SCREEN, f"difficulty:  {current_settings['difficulty']}", 22, WIDTH // 2, 310)
        draw_text(SCREEN, "[ < / > to change ]", 15, WIDTH // 2, 338, (120, 120, 120))

        btn_back.draw(SCREEN)

        # кнопки листания цвета
        btn_col_l = Button(90,  213, 36, 30, "<")
        btn_col_r = Button(310, 213, 36, 30, ">")
        btn_col_l.draw(SCREEN)
        btn_col_r.draw(SCREEN)

        # кнопки листания сложности
        btn_dif_l = Button(90,  303, 36, 30, "<")
        btn_dif_r = Button(310, 303, 36, 30, ">")
        btn_dif_l.draw(SCREEN)
        btn_dif_r.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # клик по области звука — переключаем
                if 60 < pos[0] < 340 and 115 < pos[1] < 170:
                    current_settings["sound"] = not current_settings["sound"]

                # листаем цвет машины
                if btn_col_l.is_clicked(pos):
                    idx = colors.index(current_settings["car_color"])
                    current_settings["car_color"] = colors[(idx - 1) % len(colors)]
                if btn_col_r.is_clicked(pos):
                    idx = colors.index(current_settings["car_color"])
                    current_settings["car_color"] = colors[(idx + 1) % len(colors)]

                # листаем сложность
                if btn_dif_l.is_clicked(pos):
                    idx = difficulties.index(current_settings["difficulty"])
                    current_settings["difficulty"] = difficulties[(idx - 1) % len(difficulties)]
                if btn_dif_r.is_clicked(pos):
                    idx = difficulties.index(current_settings["difficulty"])
                    current_settings["difficulty"] = difficulties[(idx + 1) % len(difficulties)]

                # сохраняем настройки в settings.json и выходим
                if btn_back.is_clicked(pos):
                    save_settings(current_settings)
                    return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(current_settings)
                return

        pygame.display.flip()
        clock.tick(60)


# --- функция: главное меню ---
def main_menu():
    btn_play  = Button(WIDTH // 2, 200, 200, 50, "play")
    btn_board = Button(WIDTH // 2, 270, 200, 50, "leaderboard")
    btn_sett  = Button(WIDTH // 2, 340, 200, 50, "settings")
    btn_quit  = Button(WIDTH // 2, 410, 200, 50, "quit")

    play_music()

    while True:
        SCREEN.fill(BG_DARK)

        draw_text(SCREEN, "racer", 52, WIDTH // 2, 90,  (255, 215, 0), bold=True)
        draw_text(SCREEN, "tsis3", 20, WIDTH // 2, 140, (150, 150, 150))

        btn_play.draw(SCREEN)
        btn_board.draw(SCREEN)
        btn_sett.draw(SCREEN)
        btn_quit.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.is_clicked(event.pos):
                    name = input_name_screen(SCREEN, WIDTH, HEIGHT)  # экран ввода имени из ui.py
                    game_loop(name)
                elif btn_board.is_clicked(event.pos):
                    leaderboard_screen()
                elif btn_sett.is_clicked(event.pos):
                    settings_screen()
                elif btn_quit.is_clicked(event.pos):
                    pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(60)


# точка входа — запускается первым при старте программы
if __name__ == "__main__":
    main_menu()
