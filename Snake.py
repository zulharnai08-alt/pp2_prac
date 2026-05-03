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
    # свободных позиций
    r = [(i, j) for i in range(b) for j in range(c) if (i, j) not in s]
    if not r:
        return None
    # Выбор случайной позиции
    p = random.choice(r)
    # Случайный выбор типа объекта
    if random.randint(0, 1):
        # обычный объект
        return {"p": p, "v": 10, "c": t, "tm": time.time(), "l": 5}
    else:
        # редкий объект
        return {"p": p, "v": 30, "c": y, "tm": time.time(), "l": 3}

# старт игры
def u():
    #Начальное положение
    s = [(5, 5), (4, 5), (3, 5)]
    #Направления
    d1 = "R"
    d2 = "R"
    #Создание объекта
    f1 = q(s)
    # Счёт
    sc1 = 0
    # Уровень
    lv = 1
    # Счётчик еды
    fe = 0
    # Скорость
    sp = f
    #окончания игры
    go = False

    return s, d1, d2, f1, sc1, lv, fe, sp, go

# движение головы
def m(hh, d1):
    # координаты
    x, y = hh
    # Движение 
    if d1 == "U": return (x, y - 1)
    if d1 == "D": return (x, y + 1)
    if d1 == "L": return (x - 1, y)
    if d1 == "R": return (x + 1, y)

# границы
def z(p):
    #координаты
    x, y = p
    #Проверка границ
    return x < 0 or x >= b or y < 0 or y >= c

# фон
def bg():
    # двойной цикл: i  по ширине j по высоте
    for i in range(b):
        for j in range(c):
            #Выбор цвета клетки
            col = bg1 if (i + j) % 2 == 0 else bg2
            # Рисование клетки 
            pygame.draw.rect(sc, col, (i * a, j * a + 60, a, a))

# змейка
def s1(s):
    #Проход по всем координатам
    for x, y in s:
        # Рисование
        pygame.draw.rect(sc, g1, (x * a, y * a + 60, a, a))

# еда
def f2(f1):
    if f1:
        #Получение координат
        x, y = f1["p"]
        # Рисование
        pygame.draw.rect(sc, f1["c"], (x * a, y * a + 60, a, a))

def h1(sc1, lv):
    #Рисуем верхнюю панель
    pygame.draw.rect(sc, o, (0, 0, d, 60))
    # Создание текста
    coins_text = font.render(f"Coins: {sc1}", True, er)
    # Уровень
    level_text = font.render(f"Level: {lv}", True, er)
    # Отрисовка текста и кол монет слева и вправо
    sc.blit(level_text, (20, 18))
    sc.blit(coins_text, (d - coins_text.get_width() - 20, 18))

# запуск
s, d1, d2, f1, sc1, lv, fe, sp, go = u()

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Управление
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_UP: d2 = "U"
            if ev.key == pygame.K_DOWN: d2 = "D"
            if ev.key == pygame.K_LEFT: d2 = "L"
            if ev.key == pygame.K_RIGHT: d2 = "R"

    if not go:
        #Запрет разворота назад
        op = {"U": "D", "D": "U", "L": "R", "R": "L"}
        if d2 != op[d1]:
            #противоположные направления
            d1 = d2
        # Новая голова змейки
        nh = m(s[0], d1)
        #Проверка столкновений
        if z(nh) or nh in s:
            go = True
        else:
            #Движение змейки
            s.insert(0, nh)
            #съел еду
            if f1 and nh == f1["p"]:
                #Очки
                sc1 += f1["v"]
                #Счётчик еды
                fe += 1
                #Уровень и скорость
                if fe % h == 0:
                    lv += 1
                    sp += g
                # Новая еда
                f1 = q(s)
                #Если не съели
            else:
                s.pop()
        #Проверка времени еды
        if f1 and time.time() - f1["tm"] > f1["l"]:
            f1 = q(s)
    #Отрисовка
    sc.fill(w)
    #Интерфейс
    h1(sc1, lv)
    #Фон
    bg()
    #Еда
    f2(f1)
    #Змейка
    s1(s)

    # oevr
    if go:
        #Красный экран
        sc.fill((255, 0, 0))
        # Создание текста
        font_big = pygame.font.SysFont("Arial", 50)
        # создаём текст
        text = font_big.render("GAME OVER", True, (0, 0, 0))
        #в центр текст
        sc.blit(text, (d//2 - text.get_width()//2, e//2 - 30))
        #Обновление экрана
        pygame.display.update()
        # пауза перед текстом 2 сек
        pygame.time.delay(2000)

        pygame.quit()
        sys.exit()
    #Обновление экрана
    pygame.display.update()
    cl.tick(sp)

#if fe % h == 0:
#lv += 1
#sp += g это измененик скорости начальная 8
