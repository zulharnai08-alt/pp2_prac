import pygame
import sys
import os
from datetime import datetime
from tools import draw_shape, flood_fill  # функции рисования из tools.py

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 700))  # окно 900x700
    pygame.display.set_caption("Paint: P:Pencil, R:Rect, Z:Clear, Ctrl+S:Save")
    
    canvas = pygame.Surface((900, 700))  # отдельный слой для рисования
    canvas.fill((255, 255, 255))         # белый фон
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)       # шрифт для текстового инструмента
    small_font = pygame.font.SysFont("Arial", 18) # шрифт для статус-бара
    
    color = (0, 0, 0)   # текущий цвет (по умолчанию чёрный)
    mode = 'pencil'     # текущий инструмент
    thickness = 2       # толщина линии
    drawing = False     # зажата ли кнопка мыши
    start_pos = None    # точка начала фигуры
    last_pos = None     # предыдущая позиция мыши (для карандаша)
    
    text_input = ""     # текст который печатает пользователь
    text_pos = None     # куда кликнули для текста
    typing = False      # режим ввода текста активен

    while True:
        mouse_pos = pygame.mouse.get_pos()  # позиция мыши каждый кадр (для превью фигур)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()  # проверяем зажат ли Ctrl/Shift/Alt

                # z — очистить холст
                if event.key == pygame.K_z:
                    canvas.fill((255, 255, 255))
                    continue

                # ctrl+s — сохранить в png с временем в названии файла
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    filename = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    full_path = os.path.join(current_dir, filename)
                    pygame.image.save(canvas, full_path)
                    print(f"Сохранено: {full_path}")
                    continue

                # обработка ввода текста когда typing=True
                if typing:
                    if event.key == pygame.K_RETURN:
                        txt_surf = font.render(text_input, True, color)
                        canvas.blit(txt_surf, text_pos)  # печатаем текст на холст
                        typing = False
                    elif event.key == pygame.K_ESCAPE:
                        typing = False                   # отмена
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]     # удаляем последний символ
                    else:
                        text_input += event.unicode      # добавляем символ
                    continue

                # переключение цвета: 0=чёрный, 1=красный, 2=зелёный, 3=синий
                if event.key == pygame.K_1: color = (255, 0, 0)
                if event.key == pygame.K_2: color = (0, 255, 0)
                if event.key == pygame.K_3: color = (0, 0, 255)
                if event.key == pygame.K_0: color = (0, 0, 0)

                # переключение инструментов (только если ctrl не зажат)
                if not (mods & pygame.KMOD_CTRL):
                    if event.key == pygame.K_p: mode = 'pencil'
                    if event.key == pygame.K_l: mode = 'line'
                    if event.key == pygame.K_g: mode = 'fill'
                    if event.key == pygame.K_w: mode = 'text'
                    if event.key == pygame.K_r: mode = 'rect'
                    if event.key == pygame.K_s: mode = 'square'
                    if event.key == pygame.K_c: mode = 'circle'
                    if event.key == pygame.K_e: mode = 'eraser'
                    if event.key == pygame.K_t: mode = 'right_tri'
                    if event.key == pygame.K_u: mode = 'equilat_tri'
                    if event.key == pygame.K_d: mode = 'rhombus'
                
                # f1/f2/f3 — толщина линии
                if event.key == pygame.K_F1: thickness = 2
                if event.key == pygame.K_F2: thickness = 5
                if event.key == pygame.K_F3: thickness = 10

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mode == 'fill':
                    flood_fill(canvas, event.pos, color)  # заливка по клику
                elif mode == 'text':
                    typing = True
                    text_pos = event.pos  # запоминаем куда кликнули
                    text_input = ""
                else:
                    drawing = True
                    start_pos = event.pos  # запоминаем начало фигуры
                    last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    draw_shape(canvas, mode, start_pos, event.pos, color, thickness)  # рисуем финальную фигуру
                drawing = False

            if event.type == pygame.MOUSEMOTION:
                if drawing and mode == 'pencil':
                    pygame.draw.line(canvas, color, last_pos, event.pos, thickness)  # карандаш — линия между позициями
                    last_pos = event.pos
                elif drawing and mode == 'eraser':
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, 20)  # ластик — белый круг

        screen.blit(canvas, (0, 0))  # выводим холст на экран
        
        # превью фигуры пока тянем мышку (рисуется на screen, не на canvas)
        if drawing and mode not in ['pencil', 'fill', 'text', 'eraser']:
            draw_shape(screen, mode, start_pos, mouse_pos, color, thickness, is_preview=True)
            
        # курсор "|" при вводе текста
        if typing:
            temp_txt = font.render(text_input + "|", True, color)
            screen.blit(temp_txt, text_pos)

        # статус-бар сверху
        pygame.draw.rect(screen, (240, 240, 240), (0, 0, 900, 35))
        status_text = f"mode: {mode}  |  size: {thickness}  |  z: clear"
        ui_surf = small_font.render(status_text, True, (60, 60, 60))
        screen.blit(ui_surf, (15, 7))

        pygame.display.flip()  # обновляем экран
        clock.tick(120)        # 120 кадров в секунду

if __name__ == "__main__":
    main()
# Инструменты:
# P — карандаш (рисует линию пока зажата мышь)
# L — прямая линия (от точки до точки)
# R — прямоугольник
# S — квадрат
# C — круг
# T — прямоугольный треугольник
# U — равносторонний треугольник
# D — ромб
# G — заливка (закрашивает область)
# W — текст (кликаешь на холст и печатаешь)
# E — ластик (стирает белым кругом)

# Цвета:
# 0 — чёрный
# 1 — красный
# 2 — зелёный
# 3 — синий

# Толщина линии:
# F1 — тонкая (2px)
# F2 — средняя (5px)
# F3 — толстая (10px)

# Прочее:
# Z      — очистить весь холст (белый фон)
# Ctrl+S — сохранить холст как .png файл с датой в названии

# Во время ввода текста (W):
# Enter     — подтвердить и напечатать текст на холст
# Escape    — отменить ввод
# Backspace — удалить последний символ
