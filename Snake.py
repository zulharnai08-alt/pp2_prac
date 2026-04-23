
import pygame
import random
import sys



CELL_SIZE = 20                  # Размер одной клетки
GRID_WIDTH = 30                 # Ширина поля в клетках
GRID_HEIGHT = 20                # Высота поля в клетках

WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE + 60   # +60 — место под счет и уровень

START_FPS = 8                   # Начальная скорость
SPEED_UP = 2                    # Увеличение скорости при переходе на уровень выше
FOODS_FOR_NEXT_LEVEL = 3        # Сколько еды нужно для нового уровня

# Цвета
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GREEN = (80, 180, 80)
DARK_GREEN = (30, 120, 50)
RED = (220, 70, 70)
BLUE = (40, 100, 180)
GRAY = (230, 230, 230)



pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("Arial", 22)
font_big = pygame.font.SysFont("Arial", 40)


def draw_text(text, font, color, x, y):
    """Рисует текст на экране."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def grid_to_px(cell):
    """Перевод координат клетки (x, y) в пиксели."""
    x, y = cell
    return x * CELL_SIZE, y * CELL_SIZE + 60  # +60 — сдвиг вниз из-за HUD

def is_out_of_bounds(cell):
    """Проверка выхода за пределы игрового поля."""
    x, y = cell
    return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT

def spawn_food(snake):
    """
    Создает еду в случайной свободной клетке.
    Еда не должна попадать на змейку.
    """
    free_cells = []

    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if (x, y) not in snake:
                free_cells.append((x, y))

    # Если свободных клеток нет, вернуть None
    if not free_cells:
        return None

    return random.choice(free_cells)

def reset_game():
    """Сбрасывает игру в начальное состояние."""
    snake = [(5, 5), (4, 5), (3, 5)]   # Голова — первый элемент списка
    direction = "RIGHT"
    next_direction = "RIGHT"

    food = spawn_food(snake)

    score = 0
    level = 1
    foods_eaten = 0
    fps = START_FPS
    game_over = False

    return snake, direction, next_direction, food, score, level, foods_eaten, fps, game_over

def get_new_head(head, direction):
    """Вычисляет новую позицию головы змейки."""
    x, y = head

    if direction == "UP":
        return (x, y - 1)
    elif direction == "DOWN":
        return (x, y + 1)
    elif direction == "LEFT":
        return (x - 1, y)
    elif direction == "RIGHT":
        return (x + 1, y)

def draw_grid():
    """Рисует сетку игрового поля."""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE + 60, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_snake(snake):
    """Рисует змейку."""
    for i, cell in enumerate(snake):
        x, y = grid_to_px(cell)
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

        if i == 0:
            pygame.draw.rect(screen, DARK_GREEN, rect)  # Голова
        else:
            pygame.draw.rect(screen, GREEN, rect)       # Тело

def draw_food(food):
    """Рисует еду."""
    if food is None:
        return

    x, y = grid_to_px(food)
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, rect)

def draw_hud(score, level, fps):
    """Рисует верхнюю панель со счетом и уровнем."""
    hud_rect = pygame.Rect(0, 0, WIDTH, 60)
    pygame.draw.rect(screen, BLUE, hud_rect)

    draw_text(f"Score: {score}", font_small, WHITE, 20, 18)
    draw_text(f"Level: {level}", font_small, WHITE, 150, 18)
    draw_text(f"Speed: {fps}", font_small, WHITE, 260, 18)

def draw_game_over(score):
    """Экран после проигрыша."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    msg1 = font_big.render("GAME OVER", True, WHITE)
    msg2 = font_small.render(f"Final score: {score}", True, WHITE)
    msg3 = font_small.render("Press R to restart or ESC to quit", True, WHITE)

    screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 - 10))
    screen.blit(msg3, (WIDTH // 2 - msg3.get_width() // 2, HEIGHT // 2 + 25))



snake, direction, next_direction, food, score, level, foods_eaten, fps, game_over = reset_game()



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Выход из игры
            if event.key == pygame.K_ESCAPE:
                running = False

            # Перезапуск после проигрыша
            if game_over and event.key == pygame.K_r:
                snake, direction, next_direction, food, score, level, foods_eaten, fps, game_over = reset_game()

            # Изменение направления
            if not game_over:
                if event.key == pygame.K_UP:
                    next_direction = "UP"
                elif event.key == pygame.K_DOWN:
                    next_direction = "DOWN"
                elif event.key == pygame.K_LEFT:
                    next_direction = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    next_direction = "RIGHT"

   
    if not game_over:
        # Запрещаем прямой разворот на 180 градусов
        opposite = {
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT": "RIGHT",
            "RIGHT": "LEFT"
        }

        if next_direction != opposite[direction]:
            direction = next_direction

        # Считаем новую голову змейки
        new_head = get_new_head(snake[0], direction)

        # Проверка на столкновение со стеной
        if is_out_of_bounds(new_head):
            game_over = True

        # Проверка на столкновение с собой
        elif new_head in snake:
            game_over = True

        else:
            # Добавляем новую голову в начало списка
            snake.insert(0, new_head)

            # Если голова попала на еду
            if new_head == food:
                score += 10
                foods_eaten += 1

                # Переход на новый уровень каждые 3 еды
                if foods_eaten % FOODS_FOR_NEXT_LEVEL == 0:
                    level += 1
                    fps += SPEED_UP   # Увеличиваем скорость

                # Создаем новую еду
                food = spawn_food(snake)
            else:
                # Если еда не съедена, убираем хвост
                snake.pop()

   
    screen.fill(WHITE)

    draw_hud(score, level, fps)
    draw_grid()
    draw_food(food)
    draw_snake(snake)

    if game_over:
        draw_game_over(score)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
sys.exit()
