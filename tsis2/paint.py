import pygameimport sysimport osfrom datetime 
import datetimefrom tools 
import draw_shape, flood_fill

def main():
    pygame.init()  

    screen = pygame.display.set_mode((900, 700))  
    

    pygame.display.set_caption("Paint: P:Pencil, R:Rect, Z:Clear, Ctrl+S:Save")  
  

    canvas = pygame.Surface((900, 700))  
    # Создание поверхности (холста), на которой будем рисовать

    canvas.fill((255, 255, 255))  
    # Заливаем холст белым цветом

    clock = pygame.time.Clock()  
    # Объект для контроля FPS (частоты кадров)

    font = pygame.font.SysFont("Arial", 24)  
    # Шрифт для текста

    small_font = pygame.font.SysFont("Arial", 18)  
    # Маленький шрифт для интерфейса

    color = (0, 0, 0)  
    # Текущий цвет (по умолчанию чёрный)

    mode = 'pencil'  
    # Текущий инструмент (карандаш)

    thickness = 2  
    # Толщина линии

    drawing = False  
    # Флаг: рисуем ли сейчас

    start_pos = None  
    # Начальная позиция мыши

    last_pos = None  
    # Последняя позиция (для рисования линий)

    text_input = ""  
 

    text_pos = None  
    # Позиция текста

    typing = False  
    # Флаг режима ввода текста

    while True:  


        mouse_pos = pygame.mouse.get_pos()  
        # Получаем текущую позицию мыши

        for event in pygame.event.get():  
            # Обрабатываем все события (клавиатура, мышь и т.д.)

            if event.type == pygame.QUIT:  
                # Если нажали на крестик окна
                pygame.quit()  
                # Закрываем pygame
                sys.exit()  
                # Завершаем программу

            if event.type == pygame.KEYDOWN:  
                # Если нажата клавиша

                mods = pygame.key.get_mods()  
                # Получаем модификаторы (Ctrl, Shift и т.д.)

                # --- 1. ОЧИСТКА ЭКРАНА (Z) ---
                if event.key == pygame.K_z:  
                    # Если нажали Z
                    canvas.fill((255, 255, 255))  
                    # Очищаем холст (заливаем белым)
                    continue  
                    # Переходим к следующему событию

                # --- 2. СОХРАНЕНИЕ (Ctrl + S) ---
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):  
                    # Если нажали Ctrl+S

                    current_dir = os.path.dirname(os.path.abspath(__file__))  
                    # Получаем папку, где находится файл

                    filename = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"  
                    # Генерируем имя файла с текущим временем

                    full_path = os.path.join(current_dir, filename)  
                    # Полный путь к файлу

                    pygame.image.save(canvas, full_path)  
                    # Сохраняем изображение холста

                    print(f"Сохранено: {full_path}")  
                    # Выводим путь сохранения

                    continue  

                # --- ВВОД ТЕКСТА ---
                if typing:  
                    # Если сейчас режим ввода текста

                    if event.key == pygame.K_RETURN:  
                        # Enter — завершить ввод
                        txt_surf = font.render(text_input, True, color)  
                        # Создаём поверхность с текстом
                        canvas.blit(txt_surf, text_pos)  
                        # Рисуем текст на холсте
                        typing = False  

                    elif event.key == pygame.K_ESCAPE:  
                        # Escape — отмена
                        typing = False  

                    elif event.key == pygame.K_BACKSPACE:  
                        # Удаление символа
                        text_input = text_input[:-1]  

                    else:
                        text_input += event.unicode  
                        # Добавляем введённый символ

                    continue  

        
                if event.key == pygame.K_1: color = (255, 0, 0)  # Красный
                if event.key == pygame.K_2: color = (0, 255, 0)  # Зелёный
                if event.key == pygame.K_3: color = (0, 0, 255)  # Синий
                if event.key == pygame.K_0: color = (0, 0, 0)    # Чёрный

                # --- СМЕНА ИНСТРУМЕНТА ---
                if not (mods & pygame.KMOD_CTRL):  
                    # Если не зажат Ctrl

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

                # --- ТОЛЩИНА ---
                if event.key == pygame.K_F1: thickness = 2  
                if event.key == pygame.K_F2: thickness = 5  
                if event.key == pygame.K_F3: thickness = 10  

            # --- МЫШЬ ---
            if event.type == pygame.MOUSEBUTTONDOWN:  
                # Нажали кнопку мыши

                if mode == 'fill':  
                    flood_fill(canvas, event.pos, color)  
                    # Заливка области

                elif mode == 'text':  
                    typing = True  
                    text_pos = event.pos  
                    text_input = ""  

                else:
                    drawing = True  
                    start_pos = event.pos  
                    last_pos = event.pos  

            if event.type == pygame.MOUSEBUTTONUP:  
                # Отпустили кнопку мыши

                if drawing:  
                    draw_shape(canvas, mode, start_pos, event.pos, color, thickness)  
                    # Рисуем фигуру

                drawing = False  

            if event.type == pygame.MOUSEMOTION:  
                # Движение мыши

                if drawing and mode == 'pencil':  
                    pygame.draw.line(canvas, color, last_pos, event.pos, thickness)  
                    # Рисуем линию (карандаш)
                    last_pos = event.pos  

                elif drawing and mode == 'eraser':  
                    pygame.draw.circle(canvas, (255, 255, 255), event.pos, 20)  
                    # Ластик (рисуем белым)

        # --- ОТРИСОВКА ---
        screen.blit(canvas, (0, 0))  
        # Рисуем холст на экран

        if drawing and mode not in ['pencil', 'fill', 'text', 'eraser']:  
            draw_shape(screen, mode, start_pos, mouse_pos, color, thickness, is_preview=True)  
            # Предпросмотр фигуры

        if typing:  
            temp_txt = font.render(text_input + "|", True, color)  
            # Показываем вводимый текст
            screen.blit(temp_txt, text_pos)

        pygame.draw.rect(screen, (240, 240, 240), (0, 0, 900, 35))  
        # Панель сверху

        status_text = f"MODE: {mode.upper()}  |  SIZE: {thickness}  |  Z: CLEAR"  
        # Текст состояния

        ui_surf = small_font.render(status_text, True, (60, 60, 60))  
        # Рендер текста

        screen.blit(ui_surf, (15, 7))  
        # Отображение текста

        pygame.display.flip()  
        # Обновление экрана

        clock.tick(120)  
        

if __name__ == "__main__":  

    main()  
