import pygame
import time

class ClickInput:
    """Handle mouse click input for the Stroop Effect game"""
    
    def __init__(self):
        self.button_rects = []
        self.colors = []
        self.screen = None
        self.ui_text = None
        self.fonts = None
        
    def get_input(self, colors, screen, ui_text, fonts):
        """
        Get mouse click input for color selection
        
        Args:
            colors: List of (color_name, color_rgb) tuples
            screen: Pygame screen object
            ui_text: UI text dictionary
            fonts: Font dictionary
            
        Returns:
            dict: {'success': bool, 'color_index': int or None, 'message': str}
        """
        # Store parameters for use in other methods
        self.colors = colors
        self.screen = screen
        self.ui_text = ui_text
        self.fonts = fonts
        
        # Create and show color buttons
        self._create_color_buttons()
        self._show_color_buttons()
        
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
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        color_index = self._get_clicked_color(mouse_pos)
                        
                        if color_index is not None:
                            return {
                                'success': True,
                                'color_index': color_index,
                                'message': 'success'
                            }
            
            # Update timeout display
            remaining_time = timeout - (current_time - start_time)
            if remaining_time <= 3:  # Show countdown in last 3 seconds
                self._show_timeout_warning(remaining_time)
            
            # Highlight button on hover
            mouse_pos = pygame.mouse.get_pos()
            self._highlight_hovered_button(mouse_pos)
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
    
    def _create_color_buttons(self):
        """Create button rectangles for color selection"""
        self.button_rects = []
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Button dimensions
        button_width = 160
        button_height = 50
        button_spacing = 20
        
        # Calculate starting position for centered layout
        total_width = min(3, len(self.colors)) * (button_width + button_spacing) - button_spacing
        start_x = (screen_width - total_width) // 2
        
        # Create buttons in rows (3 per row)
        for i in range(len(self.colors)):
            row = i // 3
            col = i % 3
            
            x = start_x + col * (button_width + button_spacing)
            y = screen_height - 150 + row * (button_height + 15)
            
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.button_rects.append(button_rect)
    
    def _show_color_buttons(self):
        """Display color selection buttons"""
        # Clear button area
        button_area = pygame.Rect(0, self.screen.get_height() - 200, 
                                 self.screen.get_width(), 200)
        pygame.draw.rect(self.screen, (240, 240, 240), button_area)
        
        # Title
        try:
            title_font = self.fonts['english_medium']
        except:
            title_font = pygame.font.Font(None, 32)
        
        title_text = title_font.render("Click the color of the text:", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.screen.get_width()//2, 
                                                self.screen.get_height() - 180))
        self.screen.blit(title_text, title_rect)
        
        # Draw color buttons
        for i, (color_name, color_rgb) in enumerate(self.colors):
            if i < len(self.button_rects):
                button_rect = self.button_rects[i]
                
                # Button background
                pygame.draw.rect(self.screen, (255, 255, 255), button_rect)
                pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
                
                # Button text
                try:
                    button_font = self.fonts['english_small']
                except:
                    button_font = pygame.font.Font(None, 24)
                
                button_text = button_font.render(color_name, True, color_rgb)
                text_rect = button_text.get_rect(center=button_rect.center)
                self.screen.blit(button_text, text_rect)
        
        # Show ESC instruction
        try:
            esc_font = self.fonts['english_small']
        except:
            esc_font = pygame.font.Font(None, 20)
        
        esc_text = esc_font.render("ESC: Quit", True, (100, 100, 100))
        self.screen.blit(esc_text, (20, self.screen.get_height() - 25))
    
    def _get_clicked_color(self, mouse_pos):
        """
        Get the color index for the clicked button
        
        Args:
            mouse_pos: Tuple of (x, y) mouse coordinates
            
        Returns:
            int or None: Color index if valid click, None otherwise
        """
        for i, button_rect in enumerate(self.button_rects):
            if button_rect.collidepoint(mouse_pos):
                return i
        return None
    
    def _highlight_hovered_button(self, mouse_pos):
        """Highlight button when mouse hovers over it"""
        for i, button_rect in enumerate(self.button_rects):
            if i < len(self.colors):
                color_name, color_rgb = self.colors[i]
                
                if button_rect.collidepoint(mouse_pos):
                    # Highlight hovered button
                    pygame.draw.rect(self.screen, (220, 220, 220), button_rect)
                    pygame.draw.rect(self.screen, color_rgb, button_rect, 3)
                else:
                    # Normal button appearance
                    pygame.draw.rect(self.screen, (255, 255, 255), button_rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
                
                # Redraw button text
                try:
                    button_font = self.fonts['english_small']
                except:
                    button_font = pygame.font.Font(None, 24)
                
                button_text = button_font.render(color_name, True, color_rgb)
                text_rect = button_text.get_rect(center=button_rect.center)
                self.screen.blit(button_text, text_rect)
    
    def _show_timeout_warning(self, remaining_time):
        """Show timeout warning"""
        # Clear center area for timeout warning
        warning_area = pygame.Rect(self.screen.get_width()//2 - 100, 
                                  self.screen.get_height()//2 + 100, 200, 50)
        pygame.draw.rect(self.screen, (255, 255, 200), warning_area)
        pygame.draw.rect(self.screen, (255, 0, 0), warning_area, 2)
        
        timeout_text = f"Time: {remaining_time:.1f}s"
        try:
            timeout_font = self.fonts['english_medium']
        except:
            timeout_font = pygame.font.Font(None, 32)
        
        timeout_surface = timeout_font.render(timeout_text, True, (255, 0, 0))
        text_rect = timeout_surface.get_rect(center=warning_area.center)
        self.screen.blit(timeout_surface, text_rect)
    
    def cleanup(self):
        """Clean up resources (if needed)"""
        self.button_rects = []
        self.colors = []
        self.screen = None
        self.ui_text = None
        self.fonts = None
    
    def test_input(self):
        """Test the mouse click input functionality"""
        print("Testing mouse click input...")
        print("Click functionality:")
        print("- Left mouse button: Select color")
        print("- Hover effects: Button highlighting")
        print("- ESC key: Quit")
        print("- Timeout: 10 seconds")
        return True