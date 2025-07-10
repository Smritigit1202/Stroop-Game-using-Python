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
        self.hindi_font = pygame.freetype.Font("fonts/NotoSansDevanagari-Regular.ttf", 20)
        self.hindi_font_medium = pygame.freetype.Font("fonts/NotoSansDevanagari-Regular.ttf", 24)
        self.hindi_font_small = pygame.freetype.Font("fonts/NotoSansDevanagari-Regular.ttf", 18)

    def _get_font(self, size_key):
        """Get font based on language and ensure proper Devanagari rendering."""
        if current_language == 'hindi':
            # Return appropriate Hindi font based on size
            if size_key == 'medium':
                return self.hindi_font_medium
            elif size_key == 'small':
                return self.hindi_font_small
            else:
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
        
        # DEBUG: Print what colors are being received
        print(f"DEBUG: ClickInput received {len(colors)} colors:")
        for i, (color_name, color_rgb) in enumerate(colors):
            print(f"  Color {i}: '{color_name}' -> {color_rgb}")
        print(f"DEBUG: Current language: {current_language}")

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
        button_height = 40  # Height of each button
        button_width = 160
        
        button_spacing = 20
        total_width = min(3, len(self.colors)) * (button_width + button_spacing) - button_spacing
        start_x = (screen_width - total_width) // 2

        for i in range(len(self.colors)):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + button_spacing)
            y = screen_height - 150 + row * (button_height + 15)
            self.button_rects.append(pygame.Rect(x, y, button_width, button_height))

    def _render_text(self, text, font, color):
        """Helper method to render text with proper font handling."""
        # Debug print to see what text is being rendered
        print(f"DEBUG: Rendering text: '{text}' | Language: {current_language} | Font type: {type(font)}")
        
        if isinstance(font, pygame.freetype.Font):
            text_surf, _ = font.render(str(text), fgcolor=color)
        else:
            text_surf = font.render(str(text), True, color)
        return text_surf

    def _show_color_buttons(self):
        # Clear the button area
        button_area = pygame.Rect(0, self.screen.get_height() - 200,
                                  self.screen.get_width(), 200)
        pygame.draw.rect(self.screen, (240, 240, 240), button_area)

        # Title
        title_font = self._get_font('medium')
        title_text = "Click the color of the text:" if current_language == 'english' else "टेक्स्ट का रंग चुनें:"
        title_surf = self._render_text(title_text, title_font, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2,
                                                 self.screen.get_height() - 180))
        self.screen.blit(title_surf, title_rect)

        # Draw buttons with solid colors
        for i, (color_name, color_rgb) in enumerate(self.colors):
            if i < len(self.button_rects):
                button_rect = self.button_rects[i]
                
                # Fill button completely with the color
                pygame.draw.rect(self.screen, color_rgb, button_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 3)  # Thicker border for visibility

        # ESC label
        esc_font = self._get_font('small')
        esc_text_content = "ESC: Quit" if current_language == 'english' else "ESC: बाहर निकलें"
        esc_text = self._render_text(esc_text_content, esc_font, (100, 100, 100))
        self.screen.blit(esc_text, (20, self.screen.get_height() - 25))

    def _get_clicked_color(self, mouse_pos):
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None

    def _highlight_hovered_button(self, mouse_pos):
        # First redraw all buttons in normal state
        for i, button_rect in enumerate(self.button_rects):
            if i < len(self.colors):
                color_name, color_rgb = self.colors[i]
                
                # Check if this button is hovered
                is_hovered = button_rect.collidepoint(mouse_pos)
                
                # Fill button with color
                pygame.draw.rect(self.screen, color_rgb, button_rect)
                
                # Draw border - thicker/different color if hovered
                if is_hovered:
                    pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 5)  # White thick border when hovered
                else:
                    pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 3)  # Black border normally

    def _show_timeout_warning(self, remaining_time):
        warning_area = pygame.Rect(self.screen.get_width() // 2 - 100,
                                   self.screen.get_height() // 2 + 100, 200, 50)
        pygame.draw.rect(self.screen, (255, 255, 200), warning_area)
        pygame.draw.rect(self.screen, (255, 0, 0), warning_area, 2)

        timeout_text = f"Time: {remaining_time:.1f}s"
        timeout_font = self._get_font('medium')
        timeout_surf = self._render_text(timeout_text, timeout_font, (255, 0, 0))
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