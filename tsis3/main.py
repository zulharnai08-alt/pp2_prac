from racer import Player, Enemy, Coin, Obstacle, NitroStrip, PowerUp, ASSET_DIR  # основные игровые объекты и путь к ресурсам
from ui import Button, draw_text, input_name_screen  # UI элементы
from persistence import save_score, get_top_scores, load_settings, save_settings  # работа с сохранениями

pygame.init()
pygame.mixer.init()  # инициализация звука

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))  # создание игрового окна

current_settings = load_settings()  # загрузка пользовательских настроек

DIFF_MAP = {"Easy": 4, "Medium": 6, "Hard": 8}  # карта сложности → базовая скорость


def play_music() -> None:
    if not current_settings["sound"]:  # если звук выключен — не запускаем музыку
        return
    pygame.mixer.music.play(-1)  # бесконечное воспроизведение


def game_loop(user_name):
    pygame.mixer.music.stop()
    play_music()  # перезапуск музыки при старте игры

    base_speed = DIFF_MAP.get(current_settings["difficulty"], 5)  # скорость зависит от сложности
    FINISH_LINE = 5000  # дистанция для победы

    speed = base_speed
    score = 0
    coins = 0
    distance = 0.0

    p1 = Player(color=current_settings["car_color"])  # игрок с выбранным цветом
    e1 = Enemy()
    e2 = Enemy()
    c1 = Coin()

    while True:
        curr_t = pygame.time.get_ticks()  # текущее время (для эффектов)

        milestone = int(distance) // 1000
        if milestone > last_milestone:
            speed += 1  # постепенное увеличение сложности

        eff = speed
        if curr_t < nitro_timer:
            eff += 4  # ускорение от нитро
        if curr_t < oil_timer:
            eff -= 3  # замедление от масла

        eff = max(1, eff)  # защита от отрицательной скорости

        distance += eff * 0.1  # накопление пройденной дистанции

        for enemy in [e1, e2]:
            if enemy.move(eff):
                score += 1  # очки за обгон

        if pygame.sprite.collide_rect(p1, c1):
            coins += c1.weight  # сбор монет
            if coins // 5 > old // 5:
                speed += 1  # бонус за каждые 5 монет

        for enemy in [e1, e2]:
            if pygame.sprite.collide_rect(p1, enemy):
                if not has_shield:
                    total = coins + score
                    save_score(user_name, total, distance)  # сохранение результата
                    game_over_screen(user_name, total, int(distance))
                    return

        if distance >= FINISH_LINE:
            total = coins + score
            save_score(user_name, total, distance)  # сохранение при победе
            victory_screen(user_name, total, int(distance))
            return


def main_menu():
    btn_play = Button(WIDTH//2, 200, 200, 50, "ИГРАТЬ")  # кнопка старта игры

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.is_clicked(event.pos):
                    name = input_name_screen(SCREEN, WIDTH, HEIGHT)  # ввод имени игрока
                    game_loop(name)


if __name__ == "__main__":
    main_menu()  # точка входа в игру
