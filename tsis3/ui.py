import pygame


def draw_text(surface, text, size, x, y, color=(255, 255, 255), bold=False):
    """рисует текст по центру координаты x,y"""
    font = pygame.font.SysFont("Verdana", size, bold=bold)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    surface.blit(surf, rect)


class Button:
    def __init__(self, x, y, width, height, text,
                 color=(60, 60, 80), hover_color=(100, 100, 130), text_color=(255, 255, 255)):
        # rect по центру x
        self.rect        = pygame.Rect(x - width // 2, y, width, height)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.text_color  = text_color

    def draw(self, surface):
        """рисует кнопку, подсвечивает при наведении мыши"""
        mouse = pygame.mouse.get_pos()
        col   = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=8)  # рамка
        draw_text(surface, self.text, 22, self.rect.centerx, self.rect.centery, self.text_color)

    def is_clicked(self, pos):
        """возвращает True если кликнули на кнопку"""
        return self.rect.collidepoint(pos)


def input_name_screen(screen, width, height):
    """экран ввода имени перед игрой, возвращает строку с именем"""
    name  = ""
    clock = pygame.time.Clock()

    while True:
        screen.fill((20, 20, 40))
        draw_text(screen, "enter your name:", 30, width // 2, height // 2 - 60)
        # отображаем введённое имя с курсором
        draw_text(screen, name + "|", 42, width // 2, height // 2, (80, 180, 255), bold=True)
        draw_text(screen, "press enter to start", 18, width // 2, height // 2 + 60, (150, 150, 150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()  # подтверждение
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]  # удаление последнего символа
                elif len(name) < 12 and event.unicode.isalnum():
                    name += event.unicode  # только буквы и цифры, лимит 12

        pygame.display.flip()
        clock.tick(60)
