import pygame
import sys
import os

from racer import Player, Enemy, Coin, Obstacle, NitroStrip, PowerUp, ASSET_DIR
from ui import Button, draw_text, input_name_screen
from persistence import save_score, get_top_scores, load_settings, save_settings

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer Pro")
clock = pygame.time.Clock()


def asset(filename: str) -> str:
    """Возвращает полный путь к файлу в папке скрипта."""
    return os.path.join(ASSET_DIR, filename)


# ── Звуки ─────────────────────────────────────────────────────────────────────
try:
    crash_sound = pygame.mixer.Sound(asset("TSIS3_crash.wav"))
    print("[OK] Загружен crash sound")
except Exception as e:
    print(f"[WARN] crash sound не загружен: {e}")
    crash_sound = None

# ── Фон ───────────────────────────────────────────────────────────────────────
try:
    bg_image = pygame.image.load(asset("AnimatedStreet.png")).convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    print("[OK] Загружен фон AnimatedStreet.png")
except Exception as e:
    print(f"[WARN] Фон не загружен: {e}")
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((80, 80, 80))

current_settings = load_settings()
DIFF_MAP = {"Easy": 4, "Medium": 6, "Hard": 8}


# ── Вспомогательная функция воспроизведения музыки ───────────────────────────
def play_music() -> None:
    if not current_settings["sound"]:
        return
    try:
        pygame.mixer.music.load(asset("music.wav"))
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
        print("[OK] Музыка запущена")
    except Exception as e:
        print(f"[WARN] Музыка не загружена: {e}")


# ── Экраны ────────────────────────────────────────────────────────────────────
def victory_screen(name: str, score: int, dist: int) -> None:
    btn_menu  = Button(WIDTH // 2, 410, 160, 50, "МЕНЮ")
    btn_retry = Button(WIDTH // 2, 475, 160, 50, "ИГРАТЬ СНОВА")
    while True:
        SCREEN.fill((0, 80, 0))
        draw_text(SCREEN, "ПОБЕДА!", 55, WIDTH // 2, 140, (255, 230, 0))
        draw_text(SCREEN, f"Счёт: {score}", 30, WIDTH // 2, 240, (255, 255, 255))
        draw_text(SCREEN, f"Дистанция: {dist} м", 24, WIDTH // 2, 285, (200, 255, 200))
        btn_menu.draw(SCREEN)
        btn_retry.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_menu.is_clicked(event.pos):
                    return
                if btn_retry.is_clicked(event.pos):
                    game_loop(name); return
        pygame.display.update()
        clock.tick(60)


def game_over_screen(name: str, score: int, dist: int) -> None:
    btn_retry = Button(WIDTH // 2, 370, 160, 50, "ЕЩЁ РАЗ")
    btn_menu  = Button(WIDTH // 2, 440, 160, 50, "МЕНЮ")
    while True:
        SCREEN.fill((100, 0, 0))
        draw_text(SCREEN, "ИГРА ОКОНЧЕНА", 44, WIDTH // 2, 150, (255, 255, 255))
        draw_text(SCREEN, f"Счёт: {score}", 30, WIDTH // 2, 245, (255, 255, 255))
        draw_text(SCREEN, f"Дистанция: {dist} м", 24, WIDTH // 2, 293, (255, 200, 200))
        btn_retry.draw(SCREEN)
        btn_menu.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.is_clicked(event.pos):
                    game_loop(name); return
                if btn_menu.is_clicked(event.pos):
                    return
        pygame.display.update()
        clock.tick(60)


def leaderboard_screen() -> None:
    scores   = get_top_scores()
    btn_back = Button(WIDTH // 2, 545, 150, 45, "НАЗАД")
    while True:
        SCREEN.fill((30, 30, 60))
        draw_text(SCREEN, "ТОП 10", 38, WIDTH // 2, 50, (255, 230, 0))
        for i, entry in enumerate(scores):
            y_pos = 115 + i * 38
            line  = f"{i+1:>2}. {entry['name'][:10]:<10}  {entry['score']}"
            color = (255, 215, 0) if i == 0 else (220, 220, 220)
            draw_text(SCREEN, line, 19, WIDTH // 2, y_pos, color)
        btn_back.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn_back.is_clicked(event.pos):
                return
        pygame.display.update()
        clock.tick(60)


def settings_screen() -> None:
    def diff_label():  return f"Сложность: {current_settings['difficulty']}"
    def color_label(): return f"Цвет машины: {current_settings['car_color']}"
    def sound_label(): return f"Звук: {'ВКЛ' if current_settings['sound'] else 'ВЫКЛ'}"

    btn_diff  = Button(WIDTH // 2, 175, 240, 50, diff_label())
    btn_color = Button(WIDTH // 2, 245, 240, 50, color_label())
    btn_sound = Button(WIDTH // 2, 315, 240, 50, sound_label())
    btn_back  = Button(WIDTH // 2, 430, 150, 50, "НАЗАД")

    while True:
        SCREEN.fill((50, 50, 80))
        draw_text(SCREEN, "НАСТРОЙКИ", 40, WIDTH // 2, 90, (255, 255, 255))
        for b in [btn_diff, btn_color, btn_sound, btn_back]:
            b.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_diff.is_clicked(event.pos):
                    lvls = ["Easy", "Medium", "Hard"]
                    current_settings["difficulty"] = lvls[
                        (lvls.index(current_settings["difficulty"]) + 1) % 3
                    ]
                    btn_diff.text = diff_label()
                if btn_color.is_clicked(event.pos):
                    cols = ["Blue", "Orange", "Pink"]
                    current_settings["car_color"] = cols[
                        (cols.index(current_settings["car_color"]) + 1) % 3
                    ]
                    btn_color.text = color_label()
                if btn_sound.is_clicked(event.pos):
                    current_settings["sound"] = not current_settings["sound"]
                    btn_sound.text = sound_label()
                    if current_settings["sound"]:
                        play_music()
                    else:
                        pygame.mixer.music.stop()
                if btn_back.is_clicked(event.pos):
                    save_settings(current_settings)
                    return
        pygame.display.update()
        clock.tick(60)


# ── Главный игровой цикл ─────────────────────────────────────────────────────
def game_loop(user_name: str) -> None:
    pygame.mixer.music.stop()
    play_music()

    base_speed   = DIFF_MAP.get(current_settings["difficulty"], 5)
    FINISH_LINE  = 5000

    speed        = base_speed
    score        = 0
    coins        = 0
    distance     = 0.0
    has_shield   = False
    nitro_timer  = 0
    oil_timer    = 0
    bg_y         = 0
    last_milestone = 0

    # Спрайты
    p1          = Player(color=current_settings["car_color"])
    e1          = Enemy()
    e2          = Enemy()
    c1          = Coin()
    o1          = Obstacle()
    n1          = NitroStrip()
    shield_item = PowerUp("shield")
    repair_item = PowerUp("repair")

    running = True
    while running:
        curr_t = pygame.time.get_ticks()

        # ── Динамическая сложность: +1 скорость каждые 1000 м ───────────────
        milestone = int(distance) // 1000
        if milestone > last_milestone:
            last_milestone = milestone
            speed += 1

        # ── Итоговая скорость ────────────────────────────────────────────────
        eff = speed
        if curr_t < nitro_timer: eff += 4
        if curr_t < oil_timer:   eff -= 3
        eff = max(1, eff)

        distance += eff * 0.1

        # ── Фон ─────────────────────────────────────────────────────────────
        bg_y = (bg_y + eff) % HEIGHT
        SCREEN.blit(bg_image, (0, bg_y))
        SCREEN.blit(bg_image, (0, bg_y - HEIGHT))

        # ── Отрисовка и обновление спрайтов ─────────────────────────────────
        for sprite in [o1, n1, c1, shield_item, repair_item]:
            sprite.move(eff)
            SCREEN.blit(sprite.image, sprite.rect)

        p1.move()
        SCREEN.blit(p1.image, p1.rect)

        for enemy in [e1, e2]:
            if enemy.move(eff):
                score += 1
            SCREEN.blit(enemy.image, enemy.rect)

        # ── Коллизии ─────────────────────────────────────────────────────────
        if pygame.sprite.collide_rect(p1, o1):
            oil_timer = curr_t + 2000

        if pygame.sprite.collide_rect(p1, n1):
            nitro_timer = curr_t + 2000

        if pygame.sprite.collide_rect(p1, shield_item):
            has_shield = True
            shield_item.reset()

        if pygame.sprite.collide_rect(p1, repair_item):
            speed       = base_speed + int(distance) // 1000
            oil_timer   = 0
            nitro_timer = 0
            repair_item.reset()

        if pygame.sprite.collide_rect(p1, c1):
            old = coins
            coins += c1.weight
            if coins // 5 > old // 5:
                speed += 1
            c1.reset()

        for enemy in [e1, e2]:
            if pygame.sprite.collide_rect(p1, enemy):
                if has_shield:
                    has_shield = False
                    enemy.reset()
                else:
                    pygame.mixer.music.stop()
                    if current_settings["sound"] and crash_sound:
                        crash_sound.play()
                    total = coins + score
                    save_score(user_name, total, distance)
                    game_over_screen(user_name, total, int(distance))
                    return

        # ── Финишная черта ───────────────────────────────────────────────────
        if distance >= FINISH_LINE:
            pygame.mixer.music.stop()
            total = coins + score
            save_score(user_name, total, distance)
            victory_screen(user_name, total, int(distance))
            return

        # ── HUD ──────────────────────────────────────────────────────────────
        # Полоса прогресса
        pygame.draw.rect(SCREEN, (50, 50, 50),  (10, 8,  WIDTH - 20, 14), border_radius=7)
        fill_w = int((WIDTH - 20) * min(distance / FINISH_LINE, 1.0))
        pygame.draw.rect(SCREEN, (50, 200, 80), (10, 8,  fill_w, 14), border_radius=7)
        draw_text(SCREEN, f"{int(distance)}/{FINISH_LINE} м", 15, WIDTH // 2, 29, (255, 255, 255))

        draw_text(SCREEN, f"Монеты: {coins}",    18, 60,         58, (255, 230, 0))
        draw_text(SCREEN, f"Счёт: {coins+score}", 18, WIDTH - 65, 58, (255, 255, 255))
        draw_text(SCREEN, f"Скорость x{speed}",  15, WIDTH // 2,  58, (200, 200, 255))

        if has_shield:
            draw_text(SCREEN, "ЩИТ АКТИВЕН", 15, WIDTH - 68, 82, (0, 200, 255))

        if curr_t < oil_timer:
            draw_text(SCREEN, "МАСЛО! ТОРМОЗИ", 26, WIDTH // 2, HEIGHT // 2, (255, 60, 60))
        if curr_t < nitro_timer:
            draw_text(SCREEN, "НИТРО БУСТ!", 26, WIDTH // 2, HEIGHT // 2 - 44, (0, 255, 80))

        # ── События ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        pygame.display.update()
        clock.tick(60)


# ── Главное меню ─────────────────────────────────────────────────────────────
def main_menu() -> None:
    btn_play     = Button(WIDTH // 2, 200, 200, 50, "ИГРАТЬ")
    btn_lead     = Button(WIDTH // 2, 268, 200, 50, "ТАБЛИЦА ЛИДЕРОВ")
    btn_settings = Button(WIDTH // 2, 336, 200, 50, "НАСТРОЙКИ")
    btn_quit     = Button(WIDTH // 2, 404, 200, 50, "ВЫХОД")

    while True:
        SCREEN.blit(bg_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))

        draw_text(SCREEN, "RACER PRO", 54, WIDTH // 2, 110, (255, 230, 0)
        for b in [btn_play, btn_lead, btn_settings, btn_quit]:
            b.draw(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.is_clicked(event.pos):
                    name = input_name_screen(SCREEN, WIDTH, HEIGHT)
                    game_loop(name)
                elif btn_lead.is_clicked(event.pos):
                    leaderboard_screen()
                elif btn_settings.is_clicked(event.pos):
                    settings_screen()
                elif btn_quit.is_clicked(event.pos):
                    pygame.quit(); sys.exit()

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
