import pygame
import math

def draw_shape(surface, mode, start, end, color, thickness, is_preview=False):
    x1, y1 = start
    x2, y2 = end
    # Для превью всегда используем толщину 1, чтобы видеть контур
    thick = 1 if is_preview else thickness

    if mode == 'line':
        pygame.draw.line(surface, color, start, end, thickness)
    
    elif mode == 'rect':
        pygame.draw.rect(surface, color, (min(x1, x2), min(y1, y2), abs(x1-x2), abs(y1-y2)), thick)
    
    elif mode == 'square':
        side = max(abs(x1-x2), abs(y1-y2))
        rect_x = x1 if x2 > x1 else x1 - side
        rect_y = y1 if y2 > y1 else y1 - side
        pygame.draw.rect(surface, color, (rect_x, rect_y, side, side), thick)

    elif mode == 'circle':
        rad = int(math.hypot(x2-x1, y2-y1))
        if rad > 0:
            pygame.draw.circle(surface, color, start, rad, thick)

    elif mode == 'right_tri':
        points = [(x1, y1), (x1, y2), (x2, y2)]
        pygame.draw.polygon(surface, color, points, thick)

    elif mode == 'equilat_tri':
        height = (x2 - x1) * math.sqrt(3) / 2
        points = [(x1, y2), (x2, y2), ((x1 + x2) / 2, y2 - height)]
        pygame.draw.polygon(surface, color, points, thick)

    elif mode == 'rhombus':
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        points = [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        pygame.draw.polygon(surface, color, points, thick)

def flood_fill(surface, pos, new_color):
    target_color = surface.get_at(pos)
    if target_color == new_color: return
    
    w, h = surface.get_size()
    queue = [pos]
    surface.set_at(pos, new_color)
    
    while queue:
        curr_x, curr_y = queue.pop(0)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            x, y = curr_x + dx, curr_y + dy
            if 0 <= x < w and 0 <= y < h:
                if surface.get_at((x, y)) == target_color:
                    surface.set_at((x, y), new_color)
                    queue.append((x, y))
        if len(queue) > 50000: break # Защита от зависания
