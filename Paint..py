
import pygame
import sys



WIDTH, HEIGHT = 900, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Цвета палитры
PALETTE = [
    ("red", (220, 50, 50)),
    ("green", (50, 180, 80)),
    ("blue", (50, 100, 220)),
    ("yellow", (240, 200, 60)),
    ("purple", (160, 80, 200)),
    ("black", (20, 20, 20)),
]

PALETTE_BOX_SIZE = 32
PALETTE_MARGIN = 10
TOP_PANEL_H = 50



pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 14)

# Отдельная поверхность для рисования, чтобы линии не исчезали
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)



mode = "brush"          # brush, rect, circle, eraser
current_color = (0, 0, 255)
brush_size = 6

drawing = False
start_pos = None
last_pos = None
current_mouse_pos = None



def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_palette():
    """Рисует палитру цветов в верхней панели."""
    x = 10
    y = 9
    for name, color in PALETTE:
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

def draw_preview_shape(surface, tool, color, width, start, end):
    """Рисует временный предпросмотр фигуры."""
    rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
    rect.normalize()

    if tool == "rect":
        pygame.draw.rect(surface, color, rect, width)
    elif tool == "circle":
        # Радиус круга берём по большей стороне прямоугольника
        radius = max(rect.width, rect.height) // 2
        center = rect.center
        pygame.draw.circle(surface, color, center, radius, width)

def draw_free_line(surface, color, width, start, end):
    """Рисует линию между двумя точками."""
    pygame.draw.line(surface, color, start, end, width)
    pygame.draw.circle(surface, color, end, width // 2)



running = True
while running:
    current_mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Выход
            if event.key == pygame.K_ESCAPE:
                running = False

            # Выбор инструмента
            elif event.key == pygame.K_1:
                mode = "brush"
            elif event.key == pygame.K_2:
                mode = "rect"
            elif event.key == pygame.K_3:
                mode = "circle"
            elif event.key == pygame.K_4:
                mode = "eraser"

            # Очистка холста
            elif event.key == pygame.K_c:
                canvas.fill(WHITE)

            # Изменение размера кисти
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                brush_size = min(50, brush_size + 1)
            elif event.key == pygame.K_MINUS:
                brush_size = max(1, brush_size - 1)

            # Быстрый выбор цветов с клавиатуры
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

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Клик по палитре меняет цвет
            chosen_color = get_palette_color(event.pos)
            if chosen_color is not None:
                current_color = chosen_color
                mode = "brush"
                continue

            # Левый клик — начинаем рисование
            if event.button == 1:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

                # Для кисти и ластика сразу ставим точку
                if mode == "brush":
                    pygame.draw.circle(canvas, current_color, event.pos, brush_size // 2)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, WHITE, event.pos, brush_size // 2)

        if event.type == pygame.MOUSEMOTION:
            if drawing and mode in ("brush", "eraser"):
                # Для кисти и ластика рисуем линию между предыдущей точкой и текущей
                color = current_color if mode == "brush" else WHITE
                draw_free_line(canvas, color, brush_size, last_pos, event.pos)
                last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                # Для фигур рисуем их только после отпускания кнопки мыши
                if mode == "rect":
                    draw_preview_shape(canvas, "rect", current_color, brush_size, start_pos, event.pos)
                elif mode == "circle":
                    draw_preview_shape(canvas, "circle", current_color, brush_size, start_pos, event.pos)

                drawing = False
                start_pos = None
                last_pos = None

   

    screen.fill((230, 230, 230))

    # Верхняя панель
    pygame.draw.rect(screen, (245, 245, 245), (0, 0, WIDTH, TOP_PANEL_H))
    pygame.draw.line(screen, (180, 180, 180), (0, TOP_PANEL_H), (WIDTH, TOP_PANEL_H), 1)

    draw_palette()

    # Подсказки
    draw_text("1 - кисть   2 - прямоугольник   3 - круг   4 - ластик   C - очистить", 420, 16)
    draw_text(f"Размер: {brush_size}", 420, 32)

    # Основной холст
    screen.blit(canvas, (0, 0))

    # Предпросмотр фигуры во время перетаскивания мыши
    if drawing and mode in ("rect", "circle") and start_pos is not None:
        temp = screen.copy()
        draw_preview_shape(temp, mode, current_color, brush_size, start_pos, current_mouse_pos)
        screen.blit(temp, (0, 0))

    # Небольшая метка текущего режима
    mode_text = {
        "brush": "Режим: кисть",
        "rect": "Режим: прямоугольник",
        "circle": "Режим: круг",
        "eraser": "Режим: ластик"
    }
    draw_text(mode_text[mode], 650, 32)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit() 
import pygame
import sys


WIDTH, HEIGHT = 900, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Цвета палитры
PALETTE = [
    ("red", (220, 50, 50)),
    ("green", (50, 180, 80)),
    ("blue", (50, 100, 220)),
    ("yellow", (240, 200, 60)),
    ("purple", (160, 80, 200)),
    ("black", (20, 20, 20)),
]

PALETTE_BOX_SIZE = 32
PALETTE_MARGIN = 10
TOP_PANEL_H = 50


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 18)
small_font = pygame.font.SysFont("Arial", 14)

# Отдельная поверхность для рисования, чтобы линии не исчезали
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)



mode = "brush"          # brush, rect, circle, eraser
current_color = (0, 0, 255)
brush_size = 6

drawing = False
start_pos = None
last_pos = None
current_mouse_pos = None



def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_palette():
    """Рисует палитру цветов в верхней панели."""
    x = 10
    y = 9
    for name, color in PALETTE:
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

def draw_preview_shape(surface, tool, color, width, start, end):
    """Рисует временный предпросмотр фигуры."""
    rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
    rect.normalize()

    if tool == "rect":
        pygame.draw.rect(surface, color, rect, width)
    elif tool == "circle":
        # Радиус круга берём по большей стороне прямоугольника
        radius = max(rect.width, rect.height) // 2
        center = rect.center
        pygame.draw.circle(surface, color, center, radius, width)

def draw_free_line(surface, color, width, start, end):
    """Рисует линию между двумя точками."""
    pygame.draw.line(surface, color, start, end, width)
    pygame.draw.circle(surface, color, end, width // 2)



running = True
while running:
    current_mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Выход
            if event.key == pygame.K_ESCAPE:
                running = False

            # Выбор инструмента
            elif event.key == pygame.K_1:
                mode = "brush"
            elif event.key == pygame.K_2:
                mode = "rect"
            elif event.key == pygame.K_3:
                mode = "circle"
            elif event.key == pygame.K_4:
                mode = "eraser"

            # Очистка холста
            elif event.key == pygame.K_c:
                canvas.fill(WHITE)

            # Изменение размера кисти
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                brush_size = min(50, brush_size + 1)
            elif event.key == pygame.K_MINUS:
                brush_size = max(1, brush_size - 1)

            # Быстрый выбор цветов с клавиатуры
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

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Клик по палитре меняет цвет
            chosen_color = get_palette_color(event.pos)
            if chosen_color is not None:
                current_color = chosen_color
                mode = "brush"
                continue

            # Левый клик — начинаем рисование
            if event.button == 1:
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

                # Для кисти и ластика сразу ставим точку
                if mode == "brush":
                    pygame.draw.circle(canvas, current_color, event.pos, brush_size // 2)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, WHITE, event.pos, brush_size // 2)

        if event.type == pygame.MOUSEMOTION:
            if drawing and mode in ("brush", "eraser"):
                # Для кисти и ластика рисуем линию между предыдущей точкой и текущей
                color = current_color if mode == "brush" else WHITE
                draw_free_line(canvas, color, brush_size, last_pos, event.pos)
                last_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                # Для фигур рисуем их только после отпускания кнопки мыши
                if mode == "rect":
                    draw_preview_shape(canvas, "rect", current_color, brush_size, start_pos, event.pos)
                elif mode == "circle":
                    draw_preview_shape(canvas, "circle", current_color, brush_size, start_pos, event.pos)

                drawing = False
                start_pos = None
                last_pos = None

  

    screen.fill((230, 230, 230))

    # Верхняя панель
    pygame.draw.rect(screen, (245, 245, 245), (0, 0, WIDTH, TOP_PANEL_H))
    pygame.draw.line(screen, (180, 180, 180), (0, TOP_PANEL_H), (WIDTH, TOP_PANEL_H), 1)

    draw_palette()

    # Подсказки
    draw_text("1 - кисть   2 - прямоугольник   3 - круг   4 - ластик   C - очистить", 420, 16)
    draw_text(f"Размер: {brush_size}", 420, 32)

    # Основной холст
    screen.blit(canvas, (0, 0))

    # Предпросмотр фигуры во время перетаскивания мыши
    if drawing and mode in ("rect", "circle") and start_pos is not None:
        temp = screen.copy()
        draw_preview_shape(temp, mode, current_color, brush_size, start_pos, current_mouse_pos)
        screen.blit(temp, (0, 0))

    # Небольшая метка текущего режима
    mode_text = {
        "brush": "Режим: кисть",
        "rect": "Режим: прямоугольник",
        "circle": "Режим: круг",
        "eraser": "Режим: ластик"
    }
    draw_text(mode_text[mode], 650, 32)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
