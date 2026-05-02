def draw_shape(surface, mode, start, end, color, thickness, is_preview=False):
    x1, y1 = start
    x2, y2 = end
    
    # Если это предпросмотр (когда тянем мышкой), рисуем тонкой линией
    thick = 1 if is_preview else thickness

    if mode == 'line':
        pygame.draw.line(surface, color, start, end, thickness)
        # Рисуем обычную линию между двумя точками


    elif mode == 'rect':
        # Прямоугольник: считаем левый верхний угол и размеры
        pygame.draw.rect(
            surface, color,
            (min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2)),
            thick
        )

    elif mode == 'square':
        # Квадрат: берём максимальную сторону, чтобы сохранить пропорции
        side = max(abs(x1-x2), abs(y1-y2))
        
        # Корректируем позицию, чтобы квадрат рисовался в нужную сторону
        rect_x = x1 if x2 > x1 else x1 - side
        rect_y = y1 if y2 > y1 else y1 - side
        
        pygame.draw.rect(surface, color, (rect_x, rect_y, side, side), thick)

    elif mode == 'circle':
        # Радиус считаем по расстоянию между начальной и текущей точкой
        rad = int(math.hypot(x2-x1, y2-y1))
        
        if rad > 0:
            pygame.draw.circle(surface, color, start, rad, thick)

    elif mode == 'right_tri':
        # Прямоугольный треугольник (угол в точке x1,y1)
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, thick)

    elif mode == 'equilat_tri':
        # Равносторонний треугольник
        # Высота считается через формулу h = a * sqrt(3) / 2
        height = (x2 - x1) * math.sqrt(3) / 2
        
        points = [
            (x1, y2),
            (x2, y2),
            ((x1 + x2) / 2, y2 - height)
        ]
        pygame.draw.polygon(surface, color, points, thick)

    elif mode == 'rhombus':
        # Ромб строится через центр и середины сторон
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        
        points = [
            (mid_x, y1),
            (x2, mid_y),
            (mid_x, y2),
            (x1, mid_y)
        ]
        pygame.draw.polygon(surface, color, points, thick)


def flood_fill(surface, pos, new_color):
    # Получаем цвет пикселя, с которого начинается заливка
    target_color = surface.get_at(pos)

    # Если цвет уже такой же — ничего не делаем
    if target_color == new_color:
        return
    
    w, h = surface.get_size()
    # Размер поверхности

    queue = [pos]
    # Очередь для обхода (алгоритм BFS)

    surface.set_at(pos, new_color)
    # Закрашиваем стартовую точку
    
    while queue:
        curr_x, curr_y = queue.pop(0)
        # Берём текущий пиксель

        # Проверяем 4 соседей (вверх, вниз, влево, вправо)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x, y = curr_x + dx, curr_y + dy

            # Проверяем, что не вышли за границы
            if 0 <= x < w and 0 <= y < h:

                # Если цвет совпадает с исходным — закрашиваем
                if surface.get_at((x, y)) == target_color:
                    surface.set_at((x, y), new_color)
                    queue.append((x, y))

        # Ограничение очереди, чтобы программа не зависла
        if len(queue) > 50000:
            break
