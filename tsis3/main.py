import pygame, sys
from racer import Player, Enemy, Coin, Obstacle, NitroStrip, PowerUp
from ui import Button, draw_text, input_name_screen
from persistence import save_score, get_top_scores, load_settings, save_settings

pygame.init()
pygame.mixer.init() # Инициализация звука

WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Загрузка звуков
try:
    crash_sound = pygame.mixer.Sound("crash.wav")
except:
    crash_sound = None

# Загрузка и подготовка фона
try:
    bg_image = pygame.image.load("AnimatedStreet.png").convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((100, 100, 100))

current_settings = load_settings()

def game_loop(user_name):
    # Фоновая музыка
    if current_settings["sound"]:
        try:
            pygame.mixer.music.load("music.wav")
            pygame.mixer.music.play(-1) # Зацикливание
        except:
            pass

    diff_map = {"Easy": 4, "Medium": 6, "Hard": 8}
    base_speed = diff_map.get(current_settings["difficulty"], 5)
    
    speed = base_speed
    score, coins, distance = 0, 0, 0
    finish_line = 5000
    has_shield = False
    nitro_timer = 0
    oil_timer = 0
    bg_y = 0

    p1 = Player(color=current_settings["car_color"])
    e1 = Enemy(); c1 = Coin(); o1 = Obstacle()
    n1 = NitroStrip()
    shield_item = PowerUp("shield"); repair_item = PowerUp("repair")
    
    layer_bottom = pygame.sprite.Group(o1, n1)
    layer_mid = pygame.sprite.Group(c1, shield_item, repair_item)
    layer_top = pygame.sprite.Group(p1, e1)

    running = True
    while running:
        curr_t = pygame.time.get_ticks()
        
        move_speed = speed + (4 if curr_t < nitro_timer else 0) - (3 if curr_t < oil_timer else 0)
        distance += move_speed * 0.1

        bg_y += move_speed
        if bg_y >= HEIGHT: bg_y = 0
        SCREEN.blit(bg_image, (0, bg_y))
        SCREEN.blit(bg_image, (0, bg_y - HEIGHT))

        for g in [layer_bottom, layer_mid, layer_top]:
            for sprite in g:
                SCREEN.blit(sprite.image, sprite.rect)
                if sprite == p1: sprite.move()
                else: 
                    if isinstance(sprite, Enemy):
                        if sprite.move(move_speed): score += 1
                    else: sprite.move(move_speed)

        # Обработка Масла и Нитро
        if pygame.sprite.collide_rect(p1, o1): 
            oil_timer = curr_t + 2000 # Замедление на 2 сек
        if pygame.sprite.collide_rect(p1, n1): 
            nitro_timer = curr_t + 2000 # Ускорение на 2 сек
        
        # Power-ups
        if pygame.sprite.collide_rect(p1, shield_item): 
            has_shield = True; shield_item.reset()
        if pygame.sprite.collide_rect(p1, repair_item): 
            speed, oil_timer, nitro_timer = base_speed, 0, 0
            repair_item.reset()
        if pygame.sprite.collide_rect(p1, c1):
            old_c = coins
            coins += c1.weight
            if coins // 5 > old_c // 5: speed += 1
            c1.reset()

        # Столкновение с врагом
        if pygame.sprite.collide_rect(p1, e1):
            if has_shield: 
                has_shield = False; e1.reset()
            else:
                pygame.mixer.music.stop()
                if current_settings["sound"] and crash_sound:
                    crash_sound.play()
                save_score(user_name, coins + score, distance)
                game_over_screen(user_name, coins + score, int(distance))
                running = False

        # Надписи OIL и NITRO
        if curr_t < oil_timer:
            draw_text(SCREEN, "OIL! SLOW DOWN", 30, WIDTH//2, HEIGHT//2, (255, 0, 0))
        if curr_t < nitro_timer:
            draw_text(SCREEN, "NITRO BOOST!", 30, WIDTH//2, HEIGHT//2 - 50, (0, 255, 0))

        # UI
        draw_text(SCREEN, f"Dist: {int(distance)}/{finish_line}", 18, WIDTH//2, 50, (255,255,255))
        draw_text(SCREEN, f"Coins: {coins}", 18, 50, 20, (255,255,0))
        if has_shield: draw_text(SCREEN, "SHIELD ACTIVE", 15, WIDTH-70, 40, (0,200,255))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        pygame.display.update()
        clock.tick(60)

def leaderboard_screen():
    scores = get_top_scores()
    btn_back = Button(WIDTH//2, 530, 150, 50, "BACK")
    while True:
        SCREEN.fill((255, 255, 255))
        draw_text(SCREEN, "TOP 10 SCORES", 40, WIDTH//2, 50)
        for i, entry in enumerate(scores):
            y_pos = 150 + (i * 35)
            text = f"{i+1}. {entry['name'][:8]} - {entry['score']} pts"
            draw_text(SCREEN, text, 20, WIDTH//2, y_pos)
        btn_back.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and btn_back.is_clicked(event.pos): return
        pygame.display.update()

def settings_screen():
    btn_diff = Button(WIDTH//2, 200, 220, 50, f"Diff: {current_settings['difficulty']}")
    btn_color = Button(WIDTH//2, 270, 220, 50, f"Car: {current_settings['car_color']}")
    btn_sound = Button(WIDTH//2, 340, 220, 50, f"Sound: {'ON' if current_settings['sound'] else 'OFF'}")
    btn_back = Button(WIDTH//2, 450, 150, 50, "BACK")

    while True:
        SCREEN.fill((200, 200, 200))
        for b in [btn_diff, btn_color, btn_sound, btn_back]: b.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_diff.is_clicked(event.pos):
                    lvls = ["Easy", "Medium", "Hard"]
                    current_settings["difficulty"] = lvls[(lvls.index(current_settings["difficulty"]) + 1) % 3]
                    btn_diff.text = f"Diff: {current_settings['difficulty']}"
                if btn_color.is_clicked(event.pos):
                    # Переключение цветов: Синий (default), Оранжевый (2), Розовый (3)
                    cols = ["Blue", "Orange", "Pink"]
                    current_settings["car_color"] = cols[(cols.index(current_settings["car_color"]) + 1) % 3]
                    btn_color.text = f"Car: {current_settings['car_color']}"
                if btn_sound.is_clicked(event.pos):
                    current_settings["sound"] = not current_settings["sound"]
                    btn_sound.text = f"Sound: {'ON' if current_settings['sound'] else 'OFF'}"
                if btn_back.is_clicked(event.pos):
                    save_settings(current_settings)
                    return
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()

def game_over_screen(name, score, dist):
    btn_retry = Button(WIDTH//2, 400, 150, 50, "RETRY")
    btn_menu = Button(WIDTH//2, 480, 150, 50, "MENU")
    while True:
        SCREEN.fill((100, 0, 0))
        draw_text(SCREEN, "GAME OVER", 50, WIDTH//2, 150, (255,255,255))
        draw_text(SCREEN, f"Score: {score} | Dist: {dist}m", 25, WIDTH//2, 250, (255,255,255))
        btn_retry.draw(SCREEN); btn_menu.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.is_clicked(event.pos): game_loop(name)
                if btn_menu.is_clicked(event.pos): return
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()

def main_menu():
    btn_play = Button(WIDTH//2, 200, 200, 50, "PLAY")
    btn_lead = Button(WIDTH//2, 280, 200, 50, "LEADERBOARD")
    btn_settings = Button(WIDTH//2, 360, 200, 50, "SETTINGS")
    btn_quit = Button(WIDTH//2, 440, 200, 50, "QUIT")
    while True:
        SCREEN.fill((255, 255, 255))
        draw_text(SCREEN, "RACER PRO", 50, WIDTH//2, 100)
        for b in [btn_play, btn_lead, btn_settings, btn_quit]: b.draw(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.is_clicked(event.pos): 
                    name = input_name_screen(SCREEN, WIDTH, HEIGHT)
                    game_loop(name)
                if btn_lead.is_clicked(event.pos): leaderboard_screen()
                if btn_settings.is_clicked(event.pos): settings_screen()
                if btn_quit.is_clicked(event.pos): pygame.quit(); sys.exit()
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.update()

if __name__ == "__main__":
    main_menu()
