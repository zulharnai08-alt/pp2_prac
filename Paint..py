import pygame
import sys
import math

pygame.init()

# размеры окна
a, b = 900, 600

# цвета
c = (255, 255, 255)   # белый
d = (0, 0, 0)         # чёрный

# палитра
e = [
    ("red", (220, 50, 50)),
    ("green", (50, 180, 80)),
    ("blue", (50, 100, 220)),
    ("yellow", (240, 200, 60)),
    ("purple", (160, 80, 200)),
    ("black", (20, 20, 20)),
]

f = 32   # размер квадрата палитры
g = 70   # высота верхней панели

# экран
h = pygame.display.set_mode((a, b))
pygame.display.set_caption("Paint")
i = pygame.time.Clock()

# шрифт
j = pygame.font.SysFont("Arial", 18)

# холст
k = pygame.Surface((a, b))
k.fill(c)

# режим и параметры
l = "brush"
m = (0, 0, 255)
n = 6

o = False
p = None
q = None
r = None

def s(text, x, y, color=d):
    """Рисует текст."""
    img = j.render(text, True, color)
    h.blit(img, (x, y))

def t():
    """Рисует палитру цветов."""
    x = 10
    y = 9
    for _, color in e:
        rect = pygame.Rect(x, y, f, f)
        pygame.draw.rect(h, color, rect)
        pygame.draw.rect(h, d, rect, 1)

        if color == m and l != "eraser":
            pygame.draw.rect(h, c, rect, 3)

        x += f + 8

def u(pos):
    """Проверяет, был ли клик по палитре."""
    x, y = pos
    if y > g:
        return None

    px = 10
    py = 9
    for _, color in e:
        rect = pygame.Rect(px, py, f, f)
        if rect.collidepoint(pos):
            return color
        px += f + 8

    return None

def v(surface, color, width, start, end):
    """Рисует линию."""
    pygame.draw.line(surface, color, start, end, width)
    pygame.draw.circle(surface, color, end, width // 2)

def w(surface, tool, color, width, start, end):
    """Рисует фигуру."""
    rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
    rect.normalize()

    if rect.width == 0 or rect.height == 0:
        return

    if tool == "rect":
        pygame.draw.rect(surface, color, rect, width)

    elif tool == "square":
        side = min(rect.width, rect.height)
        sq = pygame.Rect(rect.topleft, (side, side))
        pygame.draw.rect(surface, color, sq, width)

    elif tool == "circle":
        radius = min(rect.width, rect.height) // 2
        if radius > 0:
            pygame.draw.circle(surface, color, rect.center, radius, width)

    elif tool == "right_triangle":
        points = [rect.topleft, rect.bottomleft, rect.bottomright]
        pygame.draw.polygon(surface, color, points, width)

    elif tool == "equilateral_triangle":
        side = min(rect.width, int(rect.height / 0.8660254))
        side = max(1, side)
        tri_h = int(side * 0.8660254)

        top = (rect.centerx, rect.top)
        left = (rect.centerx - side // 2, rect.top + tri_h)
        right = (rect.centerx + side // 2, rect.top + tri_h)

        pygame.draw.polygon(surface, color, [top, left, right], width)

    elif tool == "rhombus":
        points = [rect.midtop, rect.midright, rect.midbottom, rect.midleft]
        pygame.draw.polygon(surface, color, points, width)

while True:
    r = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_1:
                l = "brush"
            elif event.key == pygame.K_2:
                l = "rect"
            elif event.key == pygame.K_3:
                l = "square"
            elif event.key == pygame.K_4:
                l = "right_triangle"
            elif event.key == pygame.K_5:
                l = "equilateral_triangle"
            elif event.key == pygame.K_6:
                l = "rhombus"
            elif event.key == pygame.K_7:
                l = "circle"
            elif event.key == pygame.K_8:
                l = "eraser"

            elif event.key == pygame.K_c:
                k.fill(c)

            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                n = min(50, n + 1)
            elif event.key == pygame.K_MINUS:
                n = max(1, n - 1)

            elif event.key == pygame.K_r:
                m = (220, 50, 50)
                l = "brush"
            elif event.key == pygame.K_g:
                m = (50, 180, 80)
                l = "brush"
            elif event.key == pygame.K_b:
                m = (50, 100, 220)
                l = "brush"
            elif event.key == pygame.K_k:
                m = (20, 20, 20)
                l = "brush"
            elif event.key == pygame.K_y:
                m = (240, 200, 60)
                l = "brush"

        if event.type == pygame.MOUSEBUTTONDOWN:
            color = u(event.pos)
            if color is not None:
                m = color
                l = "brush"
                continue

            if event.button == 1:
                o = True
                p = event.pos
                q = event.pos

                if l == "brush":
                    pygame.draw.circle(k, m, event.pos, n // 2)
                elif l == "eraser":
                    pygame.draw.circle(k, c, event.pos, n // 2)

        if event.type == pygame.MOUSEMOTION:
            if o and l in ("brush", "eraser"):
                color = m if l == "brush" else c
                v(k, color, n, q, event.pos)
                q = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and o:
                if l in ("rect", "square", "circle", "right_triangle", "equilateral_triangle", "rhombus"):
                    w(k, l, m, n, p, event.pos)

                o = False
                p = None
                q = None

    h.fill((230, 230, 230))
    pygame.draw.rect(h, (245, 245, 245), (0, 0, a, g))
    pygame.draw.line(h, (180, 180, 180), (0, g), (a, g), 1)

    t()

    s("1-кисть  2-прямоугольник  3-квадрат  4-пр.треуг.  5-равн.треуг.  6-ромб  7-круг  8-ластик", 10, 44)
    s("C - очистить   +/- - размер кисти", 10, 20)
    s(f"Режим: {l}", 620, 20)

    h.blit(k, (0, 0))

    if o and l in ("rect", "square", "circle", "right_triangle", "equilateral_triangle", "rhombus") and p is not None:
        temp = h.copy()
        w(temp, l, m, n, p, r)
        h.blit(temp, (0, 0))

    pygame.display.flip()
    i.tick(60)
