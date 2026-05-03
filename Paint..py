import pygame
import sys
import math


# Настройки окна

WIDTH, HEIGHT = 900, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Палитра цветов

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


# Инициализация pygame

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 18)

# Отдельный холст, чтобы рисунок не исчезал
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# Состояние программы

mode = "brush"  # brush, rect, square, right_triangle, equilateral_triangle, rhombus, circle, eraser
current_color = (0, 0, 255)
brush_size = 6

drawing = False
start_pos = None
last_pos = None
current_mouse_pos = None

# Вспомогательные функции
def draw_text(text, x, y, color=BLACK):
    """Рисует текст на экране."""
    img = font.render(text, True, color)
    #создаёт изображение текста
    screen.blit(img, (x, y))
    #"рисует" эту картинку на экране


def draw_palette():
    """Рисует палитру цветов в верхней панели."""
    x = 10
    y = 9
    for _, color in PALETTE:
        #перебор цветов в pallette _ игнор 1 элемента 
        rect = pygame.Rect(x, y, PALETTE_BOX_SIZE, PALETTE_BOX_SIZE)
        # рисуем прямоугольник: поз х у а размер: PALETTE_BOX_SIZE × PALETTE_BOX_SIZE   # 
        pygame.draw.rect(screen, color, rect)
        # цветной квадрат
        pygame.draw.rect(screen, BLACK, rect, 1)
        # рамка квдарта толщина 1 см 

        # Подсветка выбранного цвета
        if color == current_color and mode != "eraser":
            # если выбран солар и режим не кисточко 
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)
            # рисуем рамку белаю размер 3 

        x += PALETTE_BOX_SIZE + 8
        # сдвиг к след фигуре


def get_palette_color(pos):
    """Возвращает цвет, если клик был по палитре."""
    x, y = pos
    if y > TOP_PANEL_H:
        # если унас поз у выще чем нашо экран делаю ничего
        return None

    px = 10
    py = 9
    for _, color in PALETTE:
        # также перебор цветов кроме 1
        rect = pygame.Rect(px, py, PALETTE_BOX_SIZE, PALETTE_BOX_SIZE)
        # рисуем квадрат на поз рх ру а размер с сиайзе
        if rect.collidepoint(pos):
            #проверяет: попал ли клик внутрь квадрата если да ретун цвет
            return color
        px += PALETTE_BOX_SIZE + 8
        #Переходим к следующему квадрату справа.

    return None
#если клик не попал в политру


def draw_free_line(surface, color, width, start, end):
    """Рисует линию между двумя точками."""
    pygame.draw.line(surface, color, start, end, width)
    # линия между 2 точками
    pygame.draw.circle(surface, color, end, width // 2)
    # в конце для красивого вида делаем кружок 


def draw_shape(surface, tool, color, width, start, end):
    """Рисует выбранную фигуру по двум точкам: start и end."""
    rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
    #создаётся прямоугольник от start до end
    rect.normalize()
    #исправляет ситуацию, если ты тянул мышь “в обратную сторону”

    # Если размер нулевой, рисовать нечего
    if rect.width == 0 or rect.height == 0:
        return
    # Обычный прямоугольник по размеру rect.
    if tool == "rect":
        pygame.draw.rect(surface, color, rect, width)
        # рисуем его 
    # 
    elif tool == "square":
        # Берётся меньшая сторона, чтобы получился ровный квадрат. 
        side = min(rect.width, rect.height)
        square_rect = pygame.Rect(rect.topleft, (side, side))
        # это координаты верхнего левого угла исходного прямоугольника 
        pygame.draw.rect(surface, color, square_rect, width)
        #рисуем его 

    elif tool == "circle":
        # Круг вписываем в прямоугольник центр = центр прямоугольника 
        radius = min(rect.width, rect.height) // 2
        if radius > 0:
            pygame.draw.circle(surface, color, rect.center, radius, width)
            # рисуем его 

    elif tool == "right_triangle":
        # Прямоугольный треугольник
        points = [rect.topleft, rect.bottomleft, rect.bottomright]
        # берем верхний левый  правый угола 
        pygame.draw.polygon(surface, color, points, width)
        # Рисуем треугольник прямой 

    elif tool == "equilateral_triangle":
        # Равносторонний треугольник
        # Высота равностороннего треугольника = side * sqrt(3) / 2
        max_side_by_height = int(rect.height / 0.8660254)
        side = max(1, min(rect.width, max_side_by_height))
        # Берём минимальное из: ширины прямоугольника максимально допустимой стороны по высоте  max(1) — защита от нуля
        tri_h = int(side * 0.8660254)
        # Вычисление высоты треугольника 

        top = (rect.centerx, rect.top)
        # Определение вершин верхняя вершина — по центру сверху основание — симметрично относительно центра
        left = (rect.centerx - side // 2, rect.top + tri_h)
        right = (rect.centerx + side // 2, rect.top + tri_h)

        pygame.draw.polygon(surface, color, [top, left, right], width)
        #рисуется треугольник 

    elif tool == "rhombus":
        # Ромб
        points = [rect.midtop, rect.midright, rect.midbottom, rect.midleft]
        # используешь 4 ключевые точки прямоугольника  середина верхней правой  нижней левой сторон
        pygame.draw.polygon(surface, color, points, width)
        # Рисуется многоугольник по этим 4 точкам



running = True
while running:
    current_mouse_pos = pygame.mouse.get_pos()
    #   текущие координаты курсора мыши в окне

    for event in pygame.event.get():
        # если событие закрыт окно оно закрывает 
        if event.type == pygame.QUIT:
            running = False

        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:    
                running = False

            # если нажал на пример 1 унас мод кисточка и т д 
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

            # если с очистка 
            elif event.key == pygame.K_c:
                canvas.fill(WHITE)

            # увелечение и уменьшений кисти 
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                brush_size = min(50, brush_size + 1)
            elif event.key == pygame.K_MINUS:
                brush_size = max(1, brush_size - 1)

            # если нажал на на эти кнопи утебя менятеся цвета фигур 
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

        #
        if event.type == pygame.MOUSEBUTTONDOWN:
            # попал ли клик в палитру проверька 
            chosen_color = get_palette_color(event.pos)
            #  если кликнул меняется цвет кисти 
            if chosen_color is not None:
                current_color = chosen_color
                mode = "brush"
                continue

            
            if event.button == 1:
                # провеька кнопки мыша на  левую стоитли
                drawing = True
                start_pos = event.pos
                last_pos = event.pos

                # Для кисти и ластика сразу ставим точку 
                if mode == "brush":
                    pygame.draw.circle(canvas, current_color, event.pos, brush_size // 2)
                elif mode == "eraser":
                    pygame.draw.circle(canvas, WHITE, event.pos, brush_size // 2)

        if event.type == pygame.MOUSEMOTION:
            # Рисуем только когда: кисточко и ластик 
            if drawing and mode in ("brush", "eraser"):
                # Для кисти и ластика рисуем линию
                color = current_color if mode == "brush" else WHITE
                # кисть текущий цвет ластик белый 
                draw_free_line(canvas, color, brush_size, last_pos, event.pos)
                # линию от прошлой позиции к новой 
                last_pos = event.pos
                # текущая точка станет предыдущей

        if event.type == pygame.MOUSEBUTTONUP:
            # именно левая кнопка и мы в процессе рисования
            if event.button == 1 and drawing:
                if mode in ("rect", "square", "circle", "right_triangle", "equilateral_triangle", "rhombus"):
                    # стар поз где нажали енд поз где отпустили и фигура появляется только после отпускания 
                    draw_shape(canvas, mode, current_color, brush_size, start_pos, event.pos)
                # ниже зброс состояние рисовки 
                drawing = False
                start_pos = None
                last_pos = None
            # Заливка фона
        screen.fill((230, 230, 230))

        # Верхняя панел инструментов рисуется прямоугольник 
        pygame.draw.rect(screen, (245, 245, 245), (0, 0, WIDTH, TOP_PANEL_H))
        # Разделительная линия горизонтальная    
        pygame.draw.line(screen, (180, 180, 180), (0, TOP_PANEL_H), (WIDTH, TOP_PANEL_H), 1)

        draw_palette()

    # Подсказки
    draw_text("1-кисть  2-прямоугольник  3-квадрат  4-пр.треуг.  5-равн.треуг.  6-ромб  7-круг  8-ластик", 10, 44)
    draw_text("C - очистить   +/- - размер кисти", 10, 20)

    # Холст
    screen.blit(canvas, (0, 0))

    # выбор инструмент-фигура 
    if drawing and mode in ("rect", "square", "circle", "right_triangle", "equilateral_triangle", "rhombus") and start_pos is not None:
        # копию текущего экрана
        temp = screen.copy()
        # фигура на копий
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
    # текущий инструмент на экране
    draw_text(mode_text[mode], 620, 20)

    pygame.display.flip()
    # Обновление экрана
    clock.tick(60)
    #фпс60

pygame.quit()
sys.exit()
# корректное закрытие 
