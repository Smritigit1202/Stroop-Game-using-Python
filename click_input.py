import pygame
import pygame.freetype
import time
from MainFile import current_language  # Ensure this is defined globally

class ClickInput:
    def __init__(self):
        self.button_rects = []
        self.colors = []
        self.screen = None
        self.ui_text = None
        self.fonts = None
        self.hindi_font = pygame.freetype.Font("fonts/NotoSansDevanagari-Regular.ttf", 24)

    def _get_font(self, size_key):
     """Get font based on language and ensure proper Devanagari rendering."""
     if current_language == 'hindi':
        # Always return the freetype Hindi font
        return self.hindi_font
     else:
        if self.fonts:
            font = self.fonts.get(f'english_{size_key}')
            if font:
                return font
        return pygame.font.Font(None, 24)  # Fallback for English only

    def get_input(self, colors, screen, ui_text, fonts):
        self.colors = colors
        self.screen = screen
        self.ui_text = ui_text
        self.fonts = fonts

        self._create_color_buttons()
        self._show_color_buttons()

        start_time = time.time()
        timeout = 10.0

        while True:
            current_time = time.time()
            if current_time - start_time > timeout:
                return {'success': False, 'color_index': None, 'message': 'timeout'}

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {'success': False, 'color_index': None, 'message': 'quit'}
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return {'success': False, 'color_index': None, 'message': 'quit'}
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    color_index = self._get_clicked_color(mouse_pos)
                    if color_index is not None:
                        return {'success': True, 'color_index': color_index, 'message': 'success'}

            remaining_time = timeout - (current_time - start_time)
            if remaining_time <= 3:
                self._show_timeout_warning(remaining_time)

            self._highlight_hovered_button(pygame.mouse.get_pos())
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def _create_color_buttons(self):
        self.button_rects = []
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        button_width = 160
        button_height = 50
        button_spacing = 20
        total_width = min(3, len(self.colors)) * (button_width + button_spacing) - button_spacing
        start_x = (screen_width - total_width) // 2

        for i in range(len(self.colors)):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + button_spacing)
            y = screen_height - 150 + row * (button_height + 15)
            self.button_rects.append(pygame.Rect(x, y, button_width, button_height))

    def _show_color_buttons(self):
        button_area = pygame.Rect(0, self.screen.get_height() - 200,
                                  self.screen.get_width(), 200)
        pygame.draw.rect(self.screen, (240, 240, 240), button_area)

        # Title
        title_font = self._get_font('medium')
        if isinstance(title_font, pygame.freetype.Font):
            title_surf, _ = title_font.render("Click the color of the text:", (0, 0, 0))
        else:
            title_surf = title_font.render("Click the color of the text:", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2,
                                                 self.screen.get_height() - 180))
        self.screen.blit(title_surf, title_rect)

        # Draw buttons and labels
        for i, (color_name, color_rgb) in enumerate(self.colors):
            if i < len(self.button_rects):
                button_rect = self.button_rects[i]
                pygame.draw.rect(self.screen, (255, 255, 255), button_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)

                # Always use appropriate font based on current language
                font = self._get_font('small')
                if isinstance(font, pygame.freetype.Font):
                    text_surf, _ = font.render(str(color_name), fgcolor=color_rgb)
                else:
                   text_surf = font.render(str(color_name), True, color_rgb)

                text_rect = text_surf.get_rect(center=button_rect.center)
                self.screen.blit(text_surf, text_rect)

        # ESC label
        esc_font = self._get_font('small')
        if isinstance(esc_font, pygame.freetype.Font):
            esc_text, _ = esc_font.render("ESC: Quit", (100, 100, 100))
        else:
            esc_text = esc_font.render("ESC: Quit", True, (100, 100, 100))
        self.screen.blit(esc_text, (20, self.screen.get_height() - 25))

    def _get_clicked_color(self, mouse_pos):
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None

    def _highlight_hovered_button(self, mouse_pos):
        for i, button_rect in enumerate(self.button_rects):
            color_name, color_rgb = self.colors[i]
            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, (220, 220, 220), button_rect)
                pygame.draw.rect(self.screen, color_rgb, button_rect, 3)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), button_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)

            font = self._get_font('small')
            if isinstance(font, pygame.freetype.Font):
                text_surf, _ = font.render(str(color_name), fgcolor=color_rgb)
            else:
                text_surf = font.render(str(color_name), True, color_rgb)

            text_rect = text_surf.get_rect(center=button_rect.center)
            self.screen.blit(text_surf, text_rect)

    def _show_timeout_warning(self, remaining_time):
        warning_area = pygame.Rect(self.screen.get_width() // 2 - 100,
                                   self.screen.get_height() // 2 + 100, 200, 50)
        pygame.draw.rect(self.screen, (255, 255, 200), warning_area)
        pygame.draw.rect(self.screen, (255, 0, 0), warning_area, 2)

        timeout_text = f"Time: {remaining_time:.1f}s"
        timeout_font = self._get_font('medium')
        if isinstance(timeout_font, pygame.freetype.Font):
            timeout_surf, _ = timeout_font.render(timeout_text, (255, 0, 0))
        else:
            timeout_surf = timeout_font.render(timeout_text, True, (255, 0, 0))
        text_rect = timeout_surf.get_rect(center=warning_area.center)
        self.screen.blit(timeout_surf, text_rect)

    def cleanup(self):
        self.button_rects = []
        self.colors = []
        self.screen = None
        self.ui_text = None
        self.fonts = None

    def test_input(self):
        print("Testing mouse click input...")
        print("Click functionality:")
        print("- Left mouse button: Select color")
        print("- Hover effects: Button highlighting")
        print("- ESC key: Quit")
        print("- Timeout: 10 seconds")
        return True
