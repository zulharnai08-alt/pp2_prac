import pygame
import random
import sys
import numpy as np

from db import Database
from config1 import load_settings, save_settings
from game import GameLogic, CELL, WIDTH, HEIGHT

# инициализация pygame и звукового модуля
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# подключение к базе данных и загрузка настроек из файла
db       = Database()
settings = load_settings()

# создание окна игры
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake TSIS 4")

# шрифты трёх размеров для разных экранов
font_big   = pygame.font.SysFont("Arial", 28, bold=True)
font_med   = pygame.font.SysFont("Arial", 22)
font_small = pygame.font.SysFont("Arial", 18)

# объект для ограничения fps
clock = pygame.time.Clock()

# цвета в формате rgb
BLACK     = (0,   0,   0)
WHITE     = (255, 255, 255)
YELLOW    = (255, 215, 0)
GREEN     = (0,   220, 0)
DARK_RED  = (139, 0,   0)
BLUE_DARK = (20,  20,  60)
GREY_DARK = (20,  20,  20)


# частота дискретизации для генерации звука (стандарт cd-качества)
SAMPLE_RATE = 44100


def _make_tone(freq, duration, volume=0.4, wave="sine", decay=True):
    """
    генерирует один звуковой тон и возвращает pygame.Sound.
    freq     - частота в герцах (высота звука)
    duration - длительность в секундах
    volume   - громкость от 0.0 до 1.0
    wave     - форма волны: sine / square / saw
    decay    - затухание звука к концу (True = плавное угасание)
    """
    frames = int(duration * SAMPLE_RATE)
    t = np.linspace(0, duration, frames, endpoint=False)

    # выбор формы волны
    if wave == "sine":
        arr = np.sin(2 * np.pi * freq * t)           # синусоида - мягкий звук
    elif wave == "square":
        arr = np.sign(np.sin(2 * np.pi * freq * t))  # меандр - резкий пиксельный звук
    elif wave == "saw":
        arr = 2 * (t * freq - np.floor(t * freq + 0.5))  # пила - жёсткий звук
    else:
        arr = np.sin(2 * np.pi * freq * t)

    # огибающая затухания: громкость линейно падает от 1 до 0
    if decay:
        envelope = np.linspace(1.0, 0.0, frames)
        arr *= envelope

    # нормализация в диапазон int16 и перевод в стерео
    arr     = np.clip(arr * volume, -1.0, 1.0)
    arr_int = (arr * 32767).astype(np.int16)
    stereo  = np.column_stack([arr_int, arr_int])
    return pygame.sndarray.make_sound(stereo)


def _make_chord(freqs, duration, volume=0.3, decay=True):
    """
    микширует несколько тонов в один звук (аккорд).
    freqs - список частот, которые звучат одновременно.
    суммируем и делим на количество нот чтобы не было клиппинга.
    """
    frames = int(duration * SAMPLE_RATE)
    t      = np.linspace(0, duration, frames, endpoint=False)
    arr    = sum(np.sin(2 * np.pi * f * t) for f in freqs) / len(freqs)

    if decay:
        arr *= np.linspace(1.0, 0.0, frames)

    arr     = np.clip(arr * volume, -1.0, 1.0)
    arr_int = (arr * 32767).astype(np.int16)
    stereo  = np.column_stack([arr_int, arr_int])
    return pygame.sndarray.make_sound(stereo)


# звуковые эффекты - создаются один раз при запуске программы
SND_EAT     = _make_tone(880,  0.08, volume=0.35, wave="sine",   decay=True)    # съел еду
SND_POISON  = _make_tone(180,  0.35, volume=0.45, wave="saw",    decay=True)    # съел яд
SND_DEAD    = _make_chord([220, 165, 147], 0.6,   volume=0.50,   decay=True)    # смерть
SND_POWERUP = _make_chord([523, 659, 784], 0.25,  volume=0.40,   decay=True)    # подобрал бонус
SND_SHIELD  = _make_tone(660,  0.18, volume=0.35, wave="square", decay=True)    # щит отразил удар
SND_LEVELUP = _make_chord([523, 659, 784, 1047], 0.35, volume=0.45, decay=True) # новый уровень
SND_MENU    = _make_tone(440,  0.06, volume=0.20, wave="sine",   decay=False)   # клик в меню


def _make_bg_music(duration=4.0):
    """
    генерирует короткую мелодическую петлю для фоновой музыки.
    строится из арпеджио до-мажор: C4 E4 G4 C5 G4 E4 C4 B3.
    pygame зацикливает её через loops=-1 в play_bg().
    """
    frames  = int(duration * SAMPLE_RATE)
    t_full  = np.linspace(0, duration, frames, endpoint=False)
    notes   = [261, 329, 392, 523, 392, 329, 261, 196]  # частоты нот арпеджио
    seg_len = frames // len(notes)                       # длина одного звука в семплах
    arr     = np.zeros(frames)

    for i, freq in enumerate(notes):
        start = i * seg_len
        end   = start + seg_len
        t_seg = t_full[start:end]
        tone  = np.sin(2 * np.pi * freq * t_seg)
        env   = np.linspace(0.8, 0.2, seg_len)  # каждая нота затухает плавно
        arr[start:end] = tone * env

    # низкая громкость фона чтобы не перекрывать звуковые эффекты
    arr     = np.clip(arr * 0.18, -1.0, 1.0)
    arr_int = (arr * 32767).astype(np.int16)
    stereo  = np.column_stack([arr_int, arr_int])
    return pygame.sndarray.make_sound(stereo)


# фоновая музыка создаётся один раз и потом зацикливается через play_bg()
BG_MUSIC = _make_bg_music(duration=4.0)


def play_bg(enabled):
    """запускает фоновую музыку в бесконечном цикле или останавливает её."""
    if enabled:
        BG_MUSIC.play(loops=-1)
    else:
        BG_MUSIC.stop()


def play_sfx(sound, enabled):
    """воспроизводит звуковой эффект, если звук включён в настройках."""
    if enabled:
        sound.play()


# вспомогательная функция - заливка фона серым
def draw_background():
    screen.fill(GREY_DARK)


# вспомогательная функция - текст по центру экрана по оси x
def draw_text_centered(text, font, color, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))


# вспомогательная функция - текст в произвольной позиции
def draw_text(text, font, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))


def input_username():
    """
    экран ввода имени игрока.
    принимает ввод с клавиатуры, ограничение - 15 символов.
    возвращает строку с именем после нажатия enter.
    """
    username = ""
    while True:
        draw_background()
        draw_text_centered("SNAKE  TSIS 4", font_big, YELLOW, 80)
        draw_text_centered("Enter your username:", font_med, WHITE, 160)

        # рисуем поле ввода с жёлтой рамкой
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
                    play_sfx(SND_MENU, settings.get("sound", True))
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]                           # удаляем последний символ
                elif len(username) < 15 and event.unicode.isprintable() and event.unicode != "":
                    username += event.unicode                          # добавляем символ


def main_menu(username, player_id):
    """
    главное меню игры.
    показывает приветствие, личный рекорд и 4 пункта меню.
    запускает фоновую музыку при входе.
    """
    options = [
        ("1  -  Play",         pygame.K_1),
        ("2  -  Leaderboard",  pygame.K_2),
        ("3  -  Settings",     pygame.K_3),
        ("4  -  Quit",         pygame.K_4),
    ]

    # включаем фоновую музыку при входе в меню
    play_bg(settings.get("sound", True))

    while True:
        best = db.get_personal_best(player_id)  # личный рекорд из базы данных
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
                play_sfx(SND_MENU, settings.get("sound", True))
                if event.key == pygame.K_1:
                    BG_MUSIC.stop()                       # останавливаем музыку перед игрой
                    run_game(player_id, best)
                    play_bg(settings.get("sound", True))  # возобновляем после возврата в меню
                elif event.key == pygame.K_2:
                    show_leaderboard()
                elif event.key == pygame.K_3:
                    show_settings()
                    play_bg(settings.get("sound", True))  # применяем изменение звука сразу
                elif event.key == pygame.K_4:
                    BG_MUSIC.stop()
                    db.close(); pygame.quit(); sys.exit()


def show_leaderboard():
    """
    экран таблицы лидеров.
    загружает топ-10 из базы данных и отображает в виде таблицы.
    первое место подсвечивается жёлтым цветом.
    """
    records = db.get_top_10()
    while True:
        draw_background()
        draw_text_centered("TOP-10 LEADERBOARD", font_big, YELLOW, 15)

        # заголовки колонок таблицы
        headers = ["#", "Player", "Score", "Lvl", "Date"]
        col_x   = [30, 65, 290, 365, 425]
        for hx, h in zip(col_x, headers):
            draw_text(h, font_small, (180, 180, 180), hx, 55)
        pygame.draw.line(screen, (80, 80, 80), (25, 75), (575, 75))  # разделительная линия

        # строки с результатами игроков
        for i, (name, score, lvl, date) in enumerate(records):
            y         = 85 + i * 27
            row_color = YELLOW if i == 0 else WHITE  # первое место выделяем жёлтым
            for val, hx in zip([str(i+1), name, str(score), str(lvl), str(date)], col_x):
                draw_text(val, font_small, row_color, hx, y)

        draw_text_centered("ESC  -  Back", font_small, (120, 120, 120), 370)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def show_settings():
    """
    экран настроек.
    позволяет переключить: сетку, звук, цвет змейки.
    настройки сохраняются в settings1.json при выходе через esc.
    изменение звука применяется мгновенно без перезапуска.
    """
    global settings
    color_options = [
        ([0, 255, 0],     "Green"),
        ([255, 255, 255], "White"),
        ([0, 255, 255],   "Cyan"),
        ([255, 165, 0],   "Orange"),
        ([255, 50, 50],   "Red"),
    ]

    def current_color_name():
        # ищем текущий цвет в списке и возвращаем его название
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
            f"1  -  Grid overlay:  {grid_status}",
            f"2  -  Sound:         {sound_status}",
            f"3  -  Snake color:   {color_name}",
        ]
        for i, row in enumerate(rows):
            draw_text_centered(row, font_med, WHITE, 110 + i * 55)

        # маленький квадрат-превью текущего цвета змейки
        preview_color = tuple(settings.get("snake_color", [0, 255, 0]))
        pygame.draw.rect(screen, preview_color, [WIDTH // 2 + 90, 217, 20, 20])

        draw_text_centered("ESC  -  Save & Back", font_small, (120, 120, 120), 360)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(settings)  # сохраняем все настройки в json при выходе
                    return
                if event.key == pygame.K_1:
                    settings["grid_overlay"] = not settings.get("grid_overlay", True)
                if event.key == pygame.K_2:
                    settings["sound"] = not settings.get("sound", True)
                    # мгновенно применяем изменение звука без выхода из настроек
                    if settings["sound"]:
                        BG_MUSIC.play(loops=-1)
                    else:
                        BG_MUSIC.stop()
                if event.key == pygame.K_3:
                    # перебираем цвета по кругу
                    cur  = settings.get("snake_color", [0, 255, 0])
                    rgbs = [c[0] for c in color_options]
                    idx  = rgbs.index(cur) if cur in rgbs else 0
                    settings["snake_color"] = color_options[(idx + 1) % len(color_options)][0]


def run_game(player_id, best_score):
    """
    основной игровой цикл.
    управление: стрелки - движение, esc - выход в меню.
    механики: еда, яд, три вида бонусов, препятствия с 3 уровня.
    в конце автоматически сохраняет результат в базу данных.
    """
    global settings
    settings = load_settings()      # перечитываем настройки перед каждой новой игрой
    logic    = GameLogic(settings)  # объект игровой логики (препятствия, сетка, спавн еды)

    # начальное положение змейки - 3 сегмента, движение вправо
    snake     = [[260, 200], [280, 200], [300, 200]]
    direction = "RIGHT"
    change_to = "RIGHT"

    score      = 0
    level      = 1
    base_speed = 10   # базовая скорость в fps, растёт с каждым уровнем
    cur_speed  = base_speed

    food_pos   = logic.spawn_food(snake)  # позиция зелёной еды
    poison_pos = logic.spawn_food(snake)  # позиция яда (тёмно-красный)

    powerup       = None   # активный бонус на поле: [x, y, тип, тик_исчезновения]
    powerup_end   = 0      # тик, после которого временный эффект заканчивается
    shield_active = False  # флаг активного щита

    snd_on = settings.get("sound", True)  # кешируем настройку звука один раз

    running = True
    while running:
        ticks = pygame.time.get_ticks()  # миллисекунды с запуска pygame - для таймеров

        # обработка событий клавиатуры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # запрещаем разворот на 180 градусов (нельзя идти в противоположную сторону)
                if event.key == pygame.K_UP    and direction != "DOWN":  change_to = "UP"
                if event.key == pygame.K_DOWN  and direction != "UP":    change_to = "DOWN"
                if event.key == pygame.K_LEFT  and direction != "RIGHT": change_to = "LEFT"
                if event.key == pygame.K_RIGHT and direction != "LEFT":  change_to = "RIGHT"
                if event.key == pygame.K_ESCAPE:
                    running = False

        direction = change_to

        # вычисляем новую позицию головы на основе текущего направления
        head = list(snake[-1])
        if direction == "UP":      head[1] -= CELL
        elif direction == "DOWN":  head[1] += CELL
        elif direction == "LEFT":  head[0] -= CELL
        elif direction == "RIGHT": head[0] += CELL

        # проверяем все виды столкновений
        wall_hit = head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT
        self_hit = head in snake[:-1]      # голова попала в собственное тело
        obs_hit  = head in logic.obstacles  # голова попала в препятствие

        if wall_hit or self_hit or obs_hit:
            if shield_active:
                # щит поглощает одно столкновение и деактивируется
                play_sfx(SND_SHIELD, snd_on)
                shield_active = False
                # при ударе о стену возвращаем голову в границы поля
                head[0] = max(0, min(head[0], WIDTH  - CELL))
                head[1] = max(0, min(head[1], HEIGHT - CELL))
            else:
                play_sfx(SND_DEAD, snd_on)
                running = False
                break

        snake.append(head)  # добавляем новую позицию головы

        # проверяем, съела ли змея зелёную еду
        if head == food_pos:
            score += 1
            play_sfx(SND_EAT, snd_on)
            food_pos = logic.spawn_food(snake)  # спавним новую еду в случайном месте
            if score % 3 == 0:
                # каждые 3 очка - повышение уровня
                level      += 1
                base_speed  = min(base_speed + 2, 25)    # скорость растёт, максимум 25
                logic.generate_obstacles(level, snake)   # добавляем препятствия с 3 уровня
                play_sfx(SND_LEVELUP, snd_on)
        else:
            snake.pop(0)  # если еду не съели - убираем хвост (имитация движения)

        # проверяем, съела ли змея яд
        if head == poison_pos:
            play_sfx(SND_POISON, snd_on)
            snake      = snake[2:]  # укорачиваем змею на 2 сегмента
            poison_pos = logic.spawn_food(snake)
            if len(snake) < 1:
                # если змея стала слишком короткой - конец игры
                play_sfx(SND_DEAD, snd_on)
                running = False
                break

        # случайный спавн бонуса (шанс примерно 1/120 за тик)
        if powerup is None and random.randint(1, 120) == 1:
            pos    = logic.spawn_food(snake)
            ptype  = random.choice(["speed", "slow", "shield"])
            powerup = [pos[0], pos[1], ptype, ticks + 8000]  # исчезнет через 8 секунд

        # бонус исчезает если игрок не подобрал его вовремя
        if powerup and ticks > powerup[3]:
            powerup = None

        # проверяем подбор бонуса головой змейки
        if powerup and head == [powerup[0], powerup[1]]:
            ptype = powerup[2]
            play_sfx(SND_POWERUP, snd_on)
            if ptype == "speed":
                cur_speed   = base_speed + 7      # ускорение на 5 секунд
                powerup_end = ticks + 5000
            elif ptype == "slow":
                cur_speed   = max(4, base_speed - 5)  # замедление на 5 секунд
                powerup_end = ticks + 5000
            elif ptype == "shield":
                shield_active = True  # щит действует до первого столкновения
            powerup = None

        # сбрасываем временный эффект скорости после окончания таймера
        if ticks > powerup_end:
            cur_speed = base_speed

        # отрисовка текущего кадра
        screen.fill(BLACK)
        logic.draw_grid(screen)       # сетка (если включена в настройках)
        logic.draw_obstacles(screen)  # серые блоки препятствий

        # зелёная еда
        pygame.draw.rect(screen, (0, 220, 0),  [food_pos[0],   food_pos[1],   CELL, CELL])
        # тёмно-красный яд
        pygame.draw.rect(screen, (139, 0, 0),  [poison_pos[0], poison_pos[1], CELL, CELL])

        # бонус - цветной квадрат с буквой типа (s=speed, l=slow, s=shield)
        if powerup:
            color = GameLogic.powerup_color(powerup[2])
            pygame.draw.rect(screen, color, [powerup[0], powerup[1], CELL, CELL])
            lbl = font_small.render(powerup[2][0].upper(), True, BLACK)
            screen.blit(lbl, (powerup[0] + 3, powerup[1] + 1))

        # отрисовка змейки сегмент за сегментом
        snake_color = tuple(settings.get("snake_color", [0, 255, 0]))
        for i, seg in enumerate(snake):
            col = (100, 200, 255) if shield_active else snake_color  # голубой цвет при активном щите
            if i == len(snake) - 1:
                col = tuple(min(255, c + 40) for c in col)  # голова немного светлее тела
            pygame.draw.rect(screen, col, [seg[0], seg[1], CELL, CELL])

        # hud - строка статуса в верхнем левом углу
        hud = f"Score: {score}   Lvl: {level}   PB: {best_score}"
        if shield_active:
            hud += "   [SHIELD]"
        draw_text(hud, font_small, WHITE, 6, 6)

        pygame.display.flip()
        clock.tick(cur_speed)  # ограничиваем скорость: fps = cur_speed

    # игра закончена - сохраняем результат в базу данных
    db.save_session(player_id, score, level)
    return show_game_over(score, level, best_score, player_id)


def show_game_over(score, level, best_score, player_id):
    """
    экран окончания игры.
    показывает итоговый счёт, уровень и личный рекорд.
    если установлен новый рекорд - показывает поздравление.
    r - перезапуск игры, m - возврат в главное меню.
    """
    new_best      = db.get_personal_best(player_id)
    is_new_record = new_best > best_score  # сравниваем с рекордом до начала игры

    while True:
        screen.fill((50, 0, 0))  # тёмно-красный фон для экрана проигрыша
        draw_text_centered("GAME  OVER", font_big, WHITE, 60)
        draw_text_centered(f"Score: {score}     Level: {level}", font_med, WHITE, 120)

        if is_new_record:
            draw_text_centered("NEW PERSONAL BEST!", font_med, YELLOW, 160)
        else:
            draw_text_centered(f"Personal best: {new_best}", font_small, (200, 200, 200), 160)

        draw_text_centered("R  -  Restart",   font_med, (200, 255, 200), 220)
        draw_text_centered("M  -  Main Menu", font_med, (200, 255, 200), 260)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return run_game(player_id, new_best)  # перезапуск с обновлённым рекордом
                if event.key == pygame.K_m:
                    return  # возврат в main_menu


def main():
    """точка входа: ввод имени -> поиск/создание игрока в бд -> главное меню."""
    username  = input_username()
    player_id = db.get_or_create_player(username)
    main_menu(username, player_id)


if __name__ == "__main__":
    main()
