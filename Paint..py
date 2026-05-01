import pygame
import sys
import math

# -----------------------------
# Настройки окна
# -----------------------------
WIDTH, HEIGHT = 900, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -----------------------------
# Палитра цветов
# -----------------------------
PALETTE = [
    ("red", (220, 50, 50)),
    ("green", (50, 180, 80)),
    ("blue", (50, 100, 220)),
    ("yellow", (240, 200, 60)),
    ("purple", (160, 80, 200)),
    ("black", (20, 20, 20)),
]

PALETTE_BOX_SIZE = 32
TOP_PANEL_H = 70

# -----------------------------
# Инициализация pygame
# -----------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 18)

# Отдельный холст, чтобы рисунок не исчезал
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# -----------------------------
# Состояние программы
# -----------------------------
mode = "brush"  # brush, rect, square, right_triangle, equilateral_triangle, rhombus, circle, eraser
current_color = (0, 0, 255)
brush_size = 6

drawing = False
start_pos = None
last_pos = None
current_mouse_pos = None


# -----------------------------
# Вспомогательные функции
# -----------------------------
def draw_text(text, x, y, color=BLACK):
    """Рисует текст на экране."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_palette():
    """Рисует палитру цветов в верхней панели."""
    x = 10
    y = 9
    for _, color in PALETTE:
        rect = pygame.Rect(x, y, PALETTE_BOX_SIZE, PALETTE_BOX_SIZE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

        # Подсветка выбранного цвета
        if color == current_color and mode != "eraser":
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)

        x += PALETTE_BOX_SIZE + 8


def get_palette_color(pos):
    """Возвращает цвет, если клик был по палитре."""
    x, y = pos
    if y > TOP_PANEL_H:
        return None

    px = 10
    py = 9
    for _, color in PALETTE:
        rect = pygame.Rect(px, py, PALETTE_BOX_SIZE, PALETTE_BOX_SIZE)
        if rect.collidepoint(pos):
            return color
        px += PALETTE_BOX_SIZE + 8

    return None


def draw_free_line(surface, color, width, start, end):
    """Рисует линию между двумя точками."""
    pygame.draw.line(surface, color, start, end, width)
    pygame.draw.circle(surface, color, end, width // 2)


def draw_shape(surface, tool, color, width, start, end):
    """Рисует выбранную фигуру по двум точкам: start и end."""
    rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
    rect.normalize()

    # Если размер нулевой, рисовать нечего
    if rect.width == 0 or rect.height == 0:
        return

    if tool == "rect":
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "square":
        # Квадрат: берём меньшую сторону прямоугольника
        side = min(rect.width, rect.height)
        square_rect = pygame.Rect(rect.topleft, (side, side))
        pygame.draw.rect(surface, color, square_rect, width)

    elif tool == "circle":
        # Круг вписываем в прямоугольник
        radius = min(rect.width, rect.height) // 2
        if radius > 0:
            pygame.draw.circle(surface, color, rect.center, radius, width)

    elif tool == "right_triangle":
        # Прямоугольный треугольник
        points = [rect.topleft, rect.bottomleft, rect.bottomright]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "equilateral_triangle":
        # Равносторонний треугольник
        # Высота равностороннего треугольника = side * sqrt(3) / 2
        max_side_by_height = int(rect.height / 0.8660254)
        side = max(1, min(rect.width, max_side_by_height))
        tri_h = int(side * 0.8660254)

        top = (rect.centerx, rect.top)
        left = (rect.centerx - side // 2, rect.top + tri_h)
        right = (rect.centerx + side // 2, rect.top + tri_h)

        pygame.draw.polygon(surface, color, [top, left, right], width)

    elif tool == "rhombus":
        # Ромб
        points = [rect.midtop, rect.midright, rect.midbottom, rect.midleft]
        pygame.draw.polygon(surface, color, points, width)


# -----------------------------
# Главный цикл
# -----------------------------
running = True
while running:
    current_mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # -----------------------------
        # Управление с клавиатуры
        # -----------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # Инструменты
            elif event.key == pygame.K_1:
                mode = "brush"
            elif event.key == pygame.K_2:
                mode = "rect"
            elif event.key == pygame.K_3:
                mode = "square"
            elif event.key == pygame.K_4:
                mode = "right_triangle"
            elif event.key == pygame.K_5:
                mode = "equilateral_triangle"
            elif event.key == pygame.K_6:
                mode = "rhombus"
            elif event.key == pygame.K_7:
                mode = "circle"
            elif event.key == pygame.K_8:
                mode = "eraser"

            # Очистка холста
            elif event.key == pygame.K_c:
                canvas.fill(WHITE)

            # Размер кисти
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                brush_size = min(50, brush_size + 1)
            elif event.key == pygame.K_MINUS:
                brush_size = max(1, brush_size - 1)

            # Быстрый выбор цвета с клавиатуры
            elif event.key == pygame.K_r:
                current_color = (220, 50, 50)
                mode = "brush"
            elif event.key == pygame.K_g:
                current_color = (50, 180, 80)
                mode = "brush"
            elif event.key == pygame.K_b:
                current_color = (50, 100, 220)
                mode = "brush"
            elif event.key == pygame.K_k:
                current_color = (20, 20, 20)
                mode = "brush"
            elif event.key == pygame.K_y:
                current_color = (240, 200, 60)
                mode = "brush"

        # -----------------------------
        # Нажатие мыши
        # -----------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Если кликнули по палитре — меняем цвет
            chosen_color = get_palette_color(event.pos)
            if chosen_color is not None:
                current_color = chosen_color
                mode = "brush"
                continue

            # ЛКМ — начинаем рисование
            if event.button == 1:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

                # Для кисти и ластика сразу ставим точку
                if mode == "brush":
                    pygame.draw.circle(canvas, current_color, event.pos, brush_size // 2)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, WHITE, event.pos, brush_size // 2)

        # -----------------------------
        # Движение мыши
        # -----------------------------
        if event.type == pygame.MOUSEMOTION:
            if drawing and mode in ("brush", "eraser"):
                # Для кисти и ластика рисуем линию
                color = current_color if mode == "brush" else WHITE
                draw_free_line(canvas, color, brush_size, last_pos, event.pos)
                last_pos = event.pos

        # -----------------------------
        # Отпускание мыши
        # -----------------------------
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                # Фигуры рисуем только после отпускания кнопки мыши
                if mode in ("rect", "square", "circle", "right_triangle", "equilateral_triangle", "rhombus"):
                    draw_shape(canvas, mode, current_color, brush_size, start_pos, event.pos)

                drawing = False
                start_pos = None
                last_pos = None

    # -----------------------------
    # Отрисовка интерфейса
    # -----------------------------
    screen.fill((230, 230, 230))

    # Верхняя панель
    pygame.draw.rect(screen, (245, 245, 245), (0, 0, WIDTH, TOP_PANEL_H))
    pygame.draw.line(screen, (180, 180, 180), (0, TOP_PANEL_H), (WIDTH, TOP_PANEL_H), 1)

    draw_palette()

    # Подсказки
    draw_text("1-кисть  2-прямоугольник  3-квадрат  4-пр.треуг.  5-равн.треуг.  6-ромб  7-круг  8-ластик", 10, 44)
    draw_text("C - очистить   +/- - размер кисти", 10, 20)

    # Холст
    screen.blit(canvas, (0, 0))

    # Предпросмотр фигуры при перетаскивании мыши
    if drawing and mode in ("rect", "square", "circle", "right_triangle", "equilateral_triangle", "rhombus") and start_pos is not None:
        temp = screen.copy()
        draw_shape(temp, mode, current_color, brush_size, start_pos, current_mouse_pos)
        screen.blit(temp, (0, 0))

    # Текущий режим
    mode_text = {
        "brush": "Режим: кисть",
        "rect": "Режим: прямоугольник",
        "square": "Режим: квадрат",
        "right_triangle": "Режим: прямоугольный треугольник",
        "equilateral_triangle": "Режим: равносторонний треугольник",
        "rhombus": "Режим: ромб",
        "circle": "Режим: круг",
        "eraser": "Режим: ластик"
    }
    draw_text(mode_text[mode], 620, 20)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
