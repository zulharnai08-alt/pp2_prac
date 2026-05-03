def draw_shape(surface, mode, start, end, color, thickness, is_preview=False):
    x1, y1 = start  # координаты начала
    x2, y2 = end    # координаты конца (где отпустили мышь)
    
    thick = 1 if is_preview else thickness  # при превью толщина 1, иначе выбранная

    if mode == 'line':
        # прямая линия между двумя точками
        pygame.draw.line(surface, color, start, end, thickness)

    elif mode == 'rect':
        # прямоугольник — min/abs чтобы работало в любую сторону
        pygame.draw.rect(
            surface, color,
            (min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2)),
            thick
        )

    elif mode == 'square':
        # квадрат — берём большую сторону чтобы он был ровным
        side = max(abs(x1-x2), abs(y1-y2))
        rect_x = x1 if x2 > x1 else x1 - side  # направление по x
        rect_y = y1 if y2 > y1 else y1 - side  # направление по y
        pygame.draw.rect(surface, color, (rect_x, rect_y, side, side), thick)

    elif mode == 'circle':
        # радиус = расстояние от начальной точки до текущей
        rad = int(math.hypot(x2-x1, y2-y1))
        if rad > 0:
            pygame.draw.circle(surface, color, start, rad, thick)

    elif mode == 'right_tri':
        # прямоугольный треугольник — прямой угол в точке start
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, thick)

    elif mode == 'equilat_tri':
        # равносторонний треугольник — высота по формуле h = a * sqrt(3) / 2
        height = (x2 - x1) * math.sqrt(3) / 2
        points = [
            (x1, y2),
            (x2, y2),
            ((x1 + x2) / 2, y2 - height)  # верхняя точка по центру
        ]
        pygame.draw.polygon(surface, color, points, thick)

    elif mode == 'rhombus':
        # ромб — 4 точки через центр и середины сторон
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        points = [
            (mid_x, y1),  # верх
            (x2, mid_y),  # право
            (mid_x, y2),  # низ
            (x1, mid_y)   # лево
        ]
        pygame.draw.polygon(surface, color, points, thick)


def flood_fill(surface, pos, new_color):
    target_color = surface.get_at(pos)  # цвет пикселя на который кликнули
    if target_color == new_color:       # если цвет уже такой — ничего не делаем
        return
    
    w, h = surface.get_size()  # размеры холста для проверки границ
    queue = [pos]               # очередь пикселей для обхода (алгоритм bfs)
    surface.set_at(pos, new_color)  # закрашиваем стартовый пиксель

    while queue:
        curr_x, curr_y = queue.pop(0)  # берём следующий пиксель из очереди

        # проверяем 4 соседа: вниз, вверх, вправо, влево
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x, y = curr_x + dx, curr_y + dy
            if 0 <= x < w and 0 <= y < h:  # не выходим за границы холста
                if surface.get_at((x, y)) == target_color:  # цвет совпадает с исходным
                    surface.set_at((x, y), new_color)  # закрашиваем
                    queue.append((x, y))               # добавляем в очередь

        if len(queue) > 50000:  # защита от зависания на больших областях
            break
