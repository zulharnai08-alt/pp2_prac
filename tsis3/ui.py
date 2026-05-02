import pygame


def draw_text(surface, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.SysFont("Verdana", size)  # создание шрифта (каждый вызов — новая инициализация)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))  # центрирование текста
    surface.blit(text_surface, text_rect)


class Button:
    def __init__(self, x, y, width, height, text, color=(200, 200, 200)):
        self.rect = pygame.Rect(x - width//2, y, width, height)  # прямоугольник кнопки (центр по X)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)  # отрисовка кнопки
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)  # рамка
        draw_text(surface, self.text, 25, self.rect.centerx, self.rect.centery)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)  # проверка клика внутри кнопки


def input_name_screen(screen, width, height):
    name = ""
    active = True

    while active:
        screen.fill((255, 255, 255))  # очистка экрана каждый кадр

        draw_text(screen, "ENTER YOUR NAME:", 30, width//2, height//2 - 50)
        draw_text(screen, name + "|", 40, width//2, height//2, (0, 0, 255))  # курсор в виде "|"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()  # полный выход из игры

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    active = False  # завершение ввода имени

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]  # удаление символа

                else:
                    if len(name) < 10 and event.unicode.isalnum():
                        name += event.unicode  # ввод только букв/цифр + лимит длины

        pygame.display.update()  # обновление экрана

    return name
