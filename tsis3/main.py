import pygame
import sys
import os

from racer import Player, Enemy, Coin, Obstacle, NitroStrip, PowerUp

# Папка с ресурсами
BASE_DIR = r"C:\Users\zulha\cod\python"

# Функция для получения пути
def get_res(name):
    return os.path.join(BASE_DIR, name)

pygame.init()

WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()

# ===================== ФОН =====================
bg = pygame.image.load(get_res("AnimatedStreet.png"))
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
bg_y = 0  # для движения

# ===================== СОЗДАНИЕ ОБЪЕКТОВ =====================
player = Player(get_res("Player.png"))
enemy = Enemy(get_res("Enemy.png"))

# две монеты (обычная + редкая)
coin = Coin(get_res("coin.png"), get_res("coin1.png"))

oil = Obstacle(get_res("oil.png"))
nitro = NitroStrip(get_res("nitro.png"))
shield = PowerUp(get_res("shield.png"))

# все объекты в одной группе
all_sprites = pygame.sprite.Group(
    player, enemy, coin, oil, nitro, shield
)

speed = 5
score = 0

# ===================== ИГРОВОЙ ЦИКЛ =====================
while True:

    # --- события ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- движение фона ---
    bg_y += speed
    if bg_y >= HEIGHT:
        bg_y = 0

    SCREEN.blit(bg, (0, bg_y))
    SCREEN.blit(bg, (0, bg_y - HEIGHT))

    # --- движение объектов ---
    for sprite in all_sprites:
        SCREEN.blit(sprite.image, sprite.rect)

        if sprite == player:
            sprite.move()

        elif isinstance(sprite, Enemy):
            if sprite.move(speed):
                score += 1  # очки за уклонение

        else:
            sprite.move(speed)

    # --- столкновения ---
    if pygame.sprite.collide_rect(player, coin):
        score += coin.weight
        coin.reset()

    if pygame.sprite.collide_rect(player, enemy):
        print("GAME OVER")
        pygame.quit()
        sys.exit()

    # --- обновление экрана ---
    pygame.display.update()
    clock.tick(60)
