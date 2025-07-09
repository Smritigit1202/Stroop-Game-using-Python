import pygame
import time

class KeyInput:
    """Handle keyboard input for the Stroop Effect game"""
    
    def __init__(self):
        self.key_mappings = {
            pygame.K_r: 0,  # Red
            pygame.K_g: 1,  # Green
            pygame.K_b: 2,  # Blue
            pygame.K_y: 3,  # Yellow
            pygame.K_p: 4,  # Pink
            pygame.K_o: 5,  # Orange
            pygame.K_u: 6,  # Purple (U for purple to avoid conflict)
        }
        
        # Alternative number key mappings
        self.number_mappings = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
            pygame.K_6: 5,
            pygame.K_7: 6,
        }
    
    def get_input(self, colors, screen, ui_text, fonts):
        """
        Get keyboard input for color selection
        
        Args:
            colors: List of (color_name, color_rgb) tuples
            screen: Pygame screen object
            ui_text: UI text dictionary
            fonts: Font dictionary
            
        Returns:
            dict: {'success': bool, 'color_index': int or None, 'message': str}
        """
        # Show keyboard mapping
        self._show_keyboard_help(colors, screen, ui_text, fonts)
        
        start_time = time.time()
        timeout = 10.0  # 10 seconds timeout
        
        while True:
            current_time = time.time()
            if current_time - start_time > timeout:
                return {
                    'success': False,
                    'color_index': None,
                    'message': 'timeout'
                }
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {
                        'success': False,
                        'color_index': None,
                        'message': 'quit'
                    }
                
                elif event.type == pygame.KEYDOWN:
                    # Check for ESC key to quit
                    if event.key == pygame.K_ESCAPE:
                        return {
                            'success': False,
                            'color_index': None,
                            'message': 'quit'
                        }
                    
                    # Check letter key mappings
                    if event.key in self.key_mappings:
                        color_index = self.key_mappings[event.key]
                        if 0 <= color_index < len(colors):
                            return {
                                'success': True,
                                'color_index': color_index,
                                'message': 'success'
                            }
                    
                    # Check number key mappings
                    if event.key in self.number_mappings:
                        color_index = self.number_mappings[event.key]
                        if 0 <= color_index < len(colors):
                            return {
                                'success': True,
                                'color_index': color_index,
                                'message': 'success'
                            }
            
            # Update timeout display
            remaining_time = timeout - (current_time - start_time)
            if remaining_time <= 3:  # Show countdown in last 3 seconds
                self._show_timeout_warning(remaining_time, screen, ui_text, fonts)
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
    
    def _show_keyboard_help(self, colors, screen, ui_text, fonts):
     """Show keyboard mapping help"""
    # Clear lower part of screen for help
     help_area = pygame.Rect(0, screen.get_height() - 200, screen.get_width(), 200)
     pygame.draw.rect(screen, (240, 240, 240), help_area)

    # Title
     try:
        help_title = fonts['english_small'].render("Keyboard Controls:", True, (0, 0, 0))
        screen.blit(help_title, (50, screen.get_height() - 190))
     except:
        help_title = pygame.font.Font(None, 24).render("Keyboard Controls:", True, (0, 0, 0))
        screen.blit(help_title, (50, screen.get_height() - 190))

    # Show color mappings
     y_offset = screen.get_height() - 160
     col_width = screen.get_width() // 4

     for i, (color_name, color_rgb) in enumerate(colors):
        if i >= 7:
            break

        x_pos = 50 + (i % 4) * col_width
        if i >= 4:
            y_pos = y_offset + 30
        else:
            y_pos = y_offset

        key_letter = self._get_key_letter(i)
        key_number = str(i + 1)

        # Split rendering (mixed fonts for Hindi/English)
        try:
            # Render "R/1 = "
            eng_font = fonts.get('english_small', pygame.font.Font(None, 24))
            left_text = eng_font.render(f"{key_letter}/{key_number} = ", True, (0, 0, 0))
            screen.blit(left_text, (x_pos, y_pos))

            # Render color name (Hindi or English)
            if all('\u0900' <= c <= '\u097F' for c in color_name):  # Hindi detection
                color_font = fonts.get('hindi_small', pygame.font.Font(None, 24))
            else:
                color_font = eng_font

            color_text = color_font.render(color_name, True, color_rgb)
            screen.blit(color_text, (x_pos + left_text.get_width(), y_pos))

        except Exception as e:
            print(f"Error rendering mapping: {e}")
            fallback = pygame.font.Font(None, 20).render(f"{key_letter}/{key_number}: {color_name}", True, color_rgb)
            screen.blit(fallback, (x_pos, y_pos))

    # ESC mapping
     try:
        esc_text = fonts['english_small'].render("ESC: Quit", True, (100, 100, 100))
        screen.blit(esc_text, (50, screen.get_height() - 40))
     except:
        esc_text = pygame.font.Font(None, 20).render("ESC: Quit", True, (100, 100, 100))
        screen.blit(esc_text, (50, screen.get_height() - 40))

    def _get_key_letter(self, index):
        """Get the letter key for a given color index"""
        key_letters = ['R', 'G', 'B', 'Y', 'P', 'O', 'U']
        return key_letters[index] if index < len(key_letters) else '?'
    
    def _show_timeout_warning(self, remaining_time, screen, ui_text, fonts):
        """Show timeout warning"""
        # Clear center area for timeout warning
        warning_area = pygame.Rect(screen.get_width()//2 - 100, screen.get_height()//2 + 100, 200, 50)
        pygame.draw.rect(screen, (255, 255, 200), warning_area)
        pygame.draw.rect(screen, (255, 0, 0), warning_area, 2)
        
        timeout_text = f"Time: {remaining_time:.1f}s"
        try:
            timeout_surface = fonts['english_medium'].render(timeout_text, True, (255, 0, 0))
        except:
            timeout_surface = pygame.font.Font(None, 32).render(timeout_text, True, (255, 0, 0))
        
        text_rect = timeout_surface.get_rect(center=warning_area.center)
        screen.blit(timeout_surface, text_rect)
    
    def cleanup(self):
        """Clean up resources (if needed)"""
        pass
    
    def test_input(self):
        """Test the keyboard input functionality"""
        print("Testing keyboard input...")
        print("Key mappings:")
        print("Letter keys: R=Red, G=Green, B=Blue, Y=Yellow, P=Pink, O=Orange, U=Purple")
        print("Number keys: 1-7 for colors 1-7")
        print("ESC key: Quit")
        return True
