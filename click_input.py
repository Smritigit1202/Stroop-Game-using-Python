import pygame
import pygame.freetype
import time
import os

# Test script to check Hindi font rendering capability
def test_hindi_font_rendering():
    """Test if pygame can render Hindi text properly"""
    pygame.init()
    
    # Create a small test window
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Hindi Font Test")
    
    # Hindi color names
    hindi_colors = {
        'red': 'लाल',
        'green': 'हरा', 
        'blue': 'नीला',
        'yellow': 'पीला',
        'pink': 'गुलाबी'
    }
    
    # Test different font loading methods
    fonts_to_test = []
    
    # 1. Try loading system Hindi fonts
    font_paths = [
        "fonts/NotoSansDevanagari-Regular.ttf",
        "fonts/NotoSansDevanagari.ttf", 
        "fonts/Devanagari.ttf",
        "fonts/hindi.ttf"
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = pygame.freetype.Font(font_path, 24)
                fonts_to_test.append((f"Custom: {font_path}", font))
                print(f"✓ Loaded: {font_path}")
            except Exception as e:
                print(f"✗ Failed to load {font_path}: {e}")
    
    # 2. Try system default fonts
    try:
        system_font = pygame.freetype.Font(None, 24)
        fonts_to_test.append(("System Default", system_font))
        print("✓ Loaded system default font")
    except Exception as e:
        print(f"✗ Failed to load system font: {e}")
    
    # 3. Try pygame.font (not freetype)
    try:
        regular_font = pygame.font.Font(None, 24)
        fonts_to_test.append(("Regular pygame.font", regular_font))
        print("✓ Loaded regular pygame font")
    except Exception as e:
        print(f"✗ Failed to load regular font: {e}")
    
    # Test rendering with each font
    screen.fill((255, 255, 255))
    y_offset = 50
    
    for font_name, font in fonts_to_test:
        # Test English text
        try:
            if hasattr(font, 'render') and len(font.render.__code__.co_varnames) > 3:
                # This is a freetype font
                text_surf, _ = font.render("English: Red", fgcolor=(0, 0, 0))
            else:
                # This is a regular pygame font
                text_surf = font.render("English: Red", True, (0, 0, 0))
            
            screen.blit(text_surf, (50, y_offset))
            print(f"✓ {font_name}: English text rendered")
        except Exception as e:
            print(f"✗ {font_name}: English text failed - {e}")
        
        y_offset += 30
        
        # Test Hindi text
        try:
            hindi_text = hindi_colors['red']  # 'लाल'
            
            if hasattr(font, 'render') and len(font.render.__code__.co_varnames) > 3:
                # This is a freetype font
                text_surf, _ = font.render(hindi_text, fgcolor=(255, 0, 0))
            else:
                # This is a regular pygame font  
                text_surf = font.render(hindi_text, True, (255, 0, 0))
            
            screen.blit(text_surf, (50, y_offset))
            print(f"✓ {font_name}: Hindi text rendered - {hindi_text}")
        except Exception as e:
            print(f"✗ {font_name}: Hindi text failed - {e}")
        
        y_offset += 50
    
    pygame.display.flip()
    
    # Wait for user input
    print("\nPress any key to continue or ESC to quit...")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                waiting = False
                break
            elif event.type == pygame.KEYDOWN:
                waiting = False
                break
    
    pygame.quit()
    return fonts_to_test

# Fixed ClickInput class
class ClickInput:
    def __init__(self):
        self.button_rects = []
        self.colors = []
        self.screen = None
        self.ui_text = None
        self.fonts = None
        
        # Initialize Hindi fonts with error handling
        self.hindi_font = None
        self.hindi_font_medium = None
        self.hindi_font_small = None
        
        self._load_hindi_fonts()

    def _load_hindi_fonts(self):
        """Load Hindi fonts with proper error handling."""
        font_paths = [
            "fonts/NotoSansDevanagari-Regular.ttf",
            "fonts/NotoSansDevanagari.ttf",
            "fonts/Devanagari.ttf",
            "fonts/hindi.ttf"
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    print(f"DEBUG: Loading Hindi font from: {font_path}")
                    self.hindi_font = pygame.freetype.Font(font_path, 20)
                    self.hindi_font_medium = pygame.freetype.Font(font_path, 24)
                    self.hindi_font_small = pygame.freetype.Font(font_path, 18)
                    print(f"DEBUG: Hindi font loaded successfully!")
                    return
            except Exception as e:
                print(f"DEBUG: Failed to load font {font_path}: {e}")
                continue
        
        # If no Hindi font found, use system default
        print("DEBUG: No Hindi font found, using system default")
        try:
            self.hindi_font = pygame.freetype.Font(None, 20)
            self.hindi_font_medium = pygame.freetype.Font(None, 24)
            self.hindi_font_small = pygame.freetype.Font(None, 18)
        except Exception as e:
            print(f"DEBUG: Failed to load system font: {e}")

    def _get_font(self, size_key):
        """Get font based on language and ensure proper Devanagari rendering."""
        # For Hindi, always use freetype fonts
        if hasattr(self, 'current_language') and self.current_language == 'hindi':
            if size_key == 'medium' and self.hindi_font_medium:
                return self.hindi_font_medium
            elif size_key == 'small' and self.hindi_font_small:
                return self.hindi_font_small
            elif self.hindi_font:
                return self.hindi_font
            else:
                # Fallback to system font
                return pygame.freetype.Font(None, 24)
        else:
            # For English, use regular pygame fonts
            if self.fonts:
                font = self.fonts.get(f'english_{size_key}')
                if font:
                    return font
            return pygame.font.Font(None, 24)

    def get_input(self, colors, screen, ui_text, fonts, current_language='english'):
        self.colors = colors
        self.screen = screen
        self.ui_text = ui_text
        self.fonts = fonts
        
        # Auto-detect language based on color names if not explicitly set
        if current_language == 'english':
            # Check if any color names contain Devanagari characters
            for color_name, _ in colors:
                if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in color_name):
                    current_language = 'hindi'
                    break
        
        self.current_language = current_language  # Store language
        
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
        button_height = 60  # Increased height for better text display
        button_width = 200   # Increased width for Hindi text
        
        button_spacing = 20
        total_width = min(3, len(self.colors)) * (button_width + button_spacing) - button_spacing
        start_x = (screen_width - total_width) // 2

        for i in range(len(self.colors)):
            row = i // 3
            col = i % 3
            x = start_x + col * (button_width + button_spacing)
            y = screen_height - 150 + row * (button_height + 15)
            self.button_rects.append(pygame.Rect(x, y, button_width, button_height))

    def _render_text_safe(self, text, font, color):
        """Safely render text with proper error handling for Hindi."""
        print(f"DEBUG: Rendering text: '{text}' | Language: {self.current_language}")
        
        # Check if text contains Devanagari characters
        is_hindi_text = any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in str(text))
        
        # For Hindi text, force use of freetype font
        if is_hindi_text:
            try:
                # Try to use Hindi-capable freetype font
                if self.hindi_font_medium:
                    text_surf, text_rect = self.hindi_font_medium.render(str(text), fgcolor=color)
                    return text_surf
                elif self.hindi_font:
                    text_surf, text_rect = self.hindi_font.render(str(text), fgcolor=color)
                    return text_surf
                else:
                    # Try system freetype font
                    system_font = pygame.freetype.Font(None, 24)
                    text_surf, text_rect = system_font.render(str(text), fgcolor=color)
                    return text_surf
            except Exception as e:
                print(f"DEBUG: Hindi font rendering failed: {e}")
                # Last resort - try with system font that might support Unicode
                try:
                    # Try to find a system font that supports Unicode
                    unicode_font = pygame.freetype.Font(None, 24)
                    text_surf, text_rect = unicode_font.render(str(text), fgcolor=color)
                    return text_surf
                except Exception as e2:
                    print(f"DEBUG: Unicode fallback failed: {e2}")
                    # Return error placeholder
                    placeholder_font = pygame.font.Font(None, 20)
                    return placeholder_font.render("???", True, color)
        
        # For English text, use regular rendering
        try:
            # Check if this is a freetype font
            if hasattr(font, 'render') and hasattr(font, 'get_rect'):
                # This is a freetype font - use fgcolor parameter
                text_surf, text_rect = font.render(str(text), fgcolor=color)
                return text_surf
            else:
                # This is a regular pygame font - use antialias parameter
                text_surf = font.render(str(text), True, color)
                return text_surf
        except Exception as e:
            print(f"DEBUG: Font rendering error: {e}")
            # Emergency fallback to system font
            try:
                fallback_font = pygame.font.Font(None, 24)
                return fallback_font.render(str(text), True, color)
            except Exception as e2:
                print(f"DEBUG: Emergency fallback failed: {e2}")
                # Return a placeholder surface
                placeholder_font = pygame.font.Font(None, 20)
                return placeholder_font.render("???", True, color)

    def _get_hindi_color_name(self, english_name):
        """Get Hindi color name with proper mapping."""
        # Fixed Hindi color mappings - using dictionary instead of set
        hindi_colors = {
            'red': 'लाल',
            'green': 'हरा',
            'blue': 'नीला', 
            'yellow': 'पीला',
            'pink': 'गुलाबी',
            'orange': 'नारंगी',
            'purple': 'बैंगनी',
            'black': 'काला',
            'white': 'सफ़ेद',
            'brown': 'भूरा'
        }
        
        # Convert to lowercase for matching
        english_key = english_name.lower().strip()
        
        # Return Hindi text if found, otherwise return original
        return hindi_colors.get(english_key, english_name)

    def _show_color_buttons(self):
        # Clear the button area
        button_area = pygame.Rect(0, self.screen.get_height() - 200,
                                  self.screen.get_width(), 200)
        pygame.draw.rect(self.screen, (240, 240, 240), button_area)

        # Title - detect if we need Hindi or English
        is_hindi_mode = any(any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in color_name) 
                           for color_name, _ in self.colors)
        
        if is_hindi_mode:
            title_text = "टेक्स्ट का रंग चुनें:"
            title_font = self.hindi_font_medium if self.hindi_font_medium else pygame.freetype.Font(None, 24)
        else:
            title_text = "Click the color of the text:"
            title_font = pygame.font.Font(None, 24)
        
        title_surf = self._render_text_safe(title_text, title_font, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2,
                                                 self.screen.get_height() - 180))
        self.screen.blit(title_surf, title_rect)

        # Draw buttons
        for i, (color_name, color_rgb) in enumerate(self.colors):
            if i < len(self.button_rects):
                button_rect = self.button_rects[i]
                
                # Fill button with light gray background
                pygame.draw.rect(self.screen, (245, 245, 245), button_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
                
                # The color_name is already in the correct language, just use it directly
                display_text = color_name
                
                print(f"DEBUG: Rendering button {i}: '{color_name}' -> '{display_text}'")
                
                # Render text with safe method (it will auto-detect Hindi vs English)
                text_surf = self._render_text_safe(display_text, None, (0, 0, 0))
                text_rect = text_surf.get_rect(center=button_rect.center)
                self.screen.blit(text_surf, text_rect)

        # ESC label
        try:
            if is_hindi_mode:
                esc_text_content = "ESC: बाहर निकलें"
            else:
                esc_text_content = "ESC: Quit"
            
            esc_text = self._render_text_safe(esc_text_content, None, (100, 100, 100))
            self.screen.blit(esc_text, (20, self.screen.get_height() - 25))
        except Exception as e:
            print(f"DEBUG: ESC text error: {e}")

    def _get_clicked_color(self, mouse_pos):
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return None

    def _highlight_hovered_button(self, mouse_pos):
        # Redraw all buttons with hover effects
        for i, button_rect in enumerate(self.button_rects):
            if i < len(self.colors):
                color_name, color_rgb = self.colors[i]
                is_hovered = button_rect.collidepoint(mouse_pos)
                
                # Draw button background
                if is_hovered:
                    pygame.draw.rect(self.screen, (220, 220, 220), button_rect)
                    pygame.draw.rect(self.screen, (0, 100, 200), button_rect, 3)
                else:
                    pygame.draw.rect(self.screen, (245, 245, 245), button_rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
                
                # Use the color name directly (already in correct language)
                display_text = color_name
                
                # Render text with hover color
                text_color = (0, 50, 100) if is_hovered else (0, 0, 0)
                text_surf = self._render_text_safe(display_text, None, text_color)
                text_rect = text_surf.get_rect(center=button_rect.center)
                self.screen.blit(text_surf, text_rect)

    def _show_timeout_warning(self, remaining_time):
        warning_area = pygame.Rect(self.screen.get_width() // 2 - 100,
                                   self.screen.get_height() // 2 + 100, 200, 50)
        pygame.draw.rect(self.screen, (255, 255, 200), warning_area)
        pygame.draw.rect(self.screen, (255, 0, 0), warning_area, 2)

        timeout_text = f"Time: {remaining_time:.1f}s"
        timeout_font = pygame.font.Font(None, 24)
        timeout_surf = self._render_text_safe(timeout_text, timeout_font, (255, 0, 0))
        text_rect = timeout_surf.get_rect(center=warning_area.center)
        self.screen.blit(timeout_surf, text_rect)

    def cleanup(self):
        self.button_rects = []
        self.colors = []
        self.screen = None
        self.ui_text = None
        self.fonts = None

if __name__ == "__main__":
    # Run the Hindi font test
    print("Testing Hindi font rendering capabilities...")
    test_hindi_font_rendering()
    print("Test completed!")