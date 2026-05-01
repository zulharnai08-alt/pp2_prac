import pygame, random, time, sys

pygame.init()

# размеры
a = 20
b = 30
c = 20

d = b * a
e = c * a + 60

# скорость
f = 8
g = 2
h = 3

# цвета
w = (255, 255, 255)
er = (0, 0, 0)
g1 = (0, 200, 0)
t = (200, 0, 0)
y = (150, 0, 150)
o = (0, 0, 200)

# цвета для клетчатого фона
bg1 = (245, 245, 245)
bg2 = (230, 230, 230)

# экран
sc = pygame.display.set_mode((d, e))
cl = pygame.time.Clock()

# шрифт
font = pygame.font.SysFont("Arial", 22)

# еда (случайная + вес + таймер)
def q(s):
    r = [(i, j) for i in range(b) for j in range(c) if (i, j) not in s]
    if not r:
        return None

    p = random.choice(r)

    if random.randint(0, 1):
        return {"p": p, "v": 10, "c": t, "tm": time.time(), "l": 5}
    else:
        return {"p": p, "v": 30, "c": y, "tm": time.time(), "l": 3}

# старт игры
def u():
    s = [(5, 5), (4, 5), (3, 5)]
    d1 = "R"
    d2 = "R"
    f1 = q(s)
    sc1 = 0
    lv = 1
    fe = 0
    sp = f
    go = False
    return s, d1, d2, f1, sc1, lv, fe, sp, go

# движение головы
def m(hh, d1):
    x, y = hh
    if d1 == "U": return (x, y - 1)
    if d1 == "D": return (x, y + 1)
    if d1 == "L": return (x - 1, y)
    if d1 == "R": return (x + 1, y)

# границы
def z(p):
    x, y = p
    return x < 0 or x >= b or y < 0 or y >= c

# фон
def bg():
    for i in range(b):
        for j in range(c):
            col = bg1 if (i + j) % 2 == 0 else bg2
            pygame.draw.rect(sc, col, (i * a, j * a + 60, a, a))

# змейка
def s1(s):
    for x, y in s:
        pygame.draw.rect(sc, g1, (x * a, y * a + 60, a, a))

# еда
def f2(f1):
    if f1:
        x, y = f1["p"]
        pygame.draw.rect(sc, f1["c"], (x * a, y * a + 60, a, a))

# hud
def h1(sc1, lv):
    pygame.draw.rect(sc, o, (0, 0, d, 60))

    coins_text = font.render(f"Coins: {sc1}", True, er)
    level_text = font.render(f"Level: {lv}", True, er)

    sc.blit(level_text, (20, 18))
    sc.blit(coins_text, (d - coins_text.get_width() - 20, 18))

# запуск
s, d1, d2, f1, sc1, lv, fe, sp, go = u()

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP: d2 = "U"
            if ev.key == pygame.K_DOWN: d2 = "D"
            if ev.key == pygame.K_LEFT: d2 = "L"
            if ev.key == pygame.K_RIGHT: d2 = "R"

    if not go:
        op = {"U": "D", "D": "U", "L": "R", "R": "L"}
        if d2 != op[d1]:
            d1 = d2

        nh = m(s[0], d1)

        if z(nh) or nh in s:
            go = True
        else:
            s.insert(0, nh)

            if f1 and nh == f1["p"]:
                sc1 += f1["v"]
                fe += 1

                if fe % h == 0:
                    lv += 1
                    sp += g

                f1 = q(s)
            else:
                s.pop()

        if f1 and time.time() - f1["tm"] > f1["l"]:
            f1 = q(s)

    sc.fill(w)
    h1(sc1, lv)
    bg()
    f2(f1)
    s1(s)

    # GAME OVER
    if go:
        sc.fill((255, 0, 0))

        font_big = pygame.font.SysFont("Arial", 50)
        text = font_big.render("GAME OVER", True, (0, 0, 0))

        sc.blit(text, (d//2 - text.get_width()//2, e//2 - 30))

        pygame.display.update()
        pygame.time.delay(2000)

        pygame.quit()
        sys.exit()

    pygame.display.update()
    cl.tick(sp)

#if fe % h == 0:
#lv += 1
#sp += g это измененик скорости начальная 8
