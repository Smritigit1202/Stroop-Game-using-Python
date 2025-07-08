import cv2
import pygame
import time
import os

class QRInput:
    """Handle QR code input for the Stroop Effect game"""
    
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        self.cap = None
        
        # QR codes mapping - what each QR code contains
        self.qr_codes = {}
        self._load_qr_codes()

    def _load_qr_codes(self):
        """Load QR codes from the qrs directory"""
        qr_dir = "qrs"
        for color_name in ["red", "green", "blue", "yellow", "pink"]:
            path = os.path.join(qr_dir, f"qr_{color_name}.jpg")
            if os.path.exists(path):
                img = cv2.imread(path)
                if img is not None:
                    val, _, _ = self.detector.detectAndDecode(img)
                    val = val.strip().lower()
                    print(f"[CHECK] Decoded QR for '{color_name}': '{val}'")

                    if val:
                        self.qr_codes[val] = color_name
                        print(f"✔ Loaded QR code for '{color_name}' as '{val}'")
                    else:
                        print(f"[ERROR] Could not decode QR from: {path}")
                else:
                    print(f"[ERROR] Failed to read: {path}")
            else:
                print(f"[ERROR] QR file not found: {path}")
        print(f"[INFO] Total QR codes loaded: {len(self.qr_codes)} → {self.qr_codes}")

    def get_input(self, colors, screen, ui_text, fonts, timeout=10):
        """
        Get input from QR code detection
        
        Args:
            colors: List of tuples [(color_name, color_rgb), ...]
            screen: Pygame screen object
            ui_text: UI text dictionary
            fonts: Fonts dictionary
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with success, color_index, and message
        """
        if not self._init_camera():
            return {
                'success': False,
                'color_index': None,
                'message': 'camera_error'
            }

        self._show_camera_instructions(screen, ui_text, fonts)

        start_time = time.time()
        detected_qr = None

        while (time.time() - start_time) < timeout:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed

            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self._cleanup_camera()
                    return {'success': False, 'color_index': None, 'message': 'quit'}

            # Read from camera
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Couldn't read from camera")
                continue

            # Detect QR code
            val, points, _ = self.detector.detectAndDecode(frame)
            if val:
                detected_qr = val.strip().lower()
                print(f"[DEBUG] Detected QR: '{detected_qr}'")
                
                # Check if this QR code is valid
                if detected_qr in self.qr_codes:
                    detected_color = self.qr_codes[detected_qr]
                    print(f"[MATCH] QR matched to color: '{detected_color}'")
                    
                    # Find the color index in the colors list
                    color_index = self._find_color_index(detected_color, colors)
                    
                    self._cleanup_camera()
                    return {
                        'success': True,
                        'color_index': color_index,
                        'message': 'success'
                    }
                else:
                    print(f"[WARNING] QR '{detected_qr}' not in known QR codes")
                    continue

            # Update UI
            self._show_camera_instructions(screen, ui_text, fonts)
            self._show_timeout_warning(remaining, screen, ui_text, fonts)
            pygame.display.update()
            pygame.time.wait(50)

        self._cleanup_camera()

        print("[TIMEOUT] No valid QR detected in time.")
        return {
            'success': False,
            'color_index': None,
            'message': 'timeout'
        }

    def _find_color_index(self, detected_color, colors):
        """
        Find the index of the detected color in the colors list
        
        Args:
            detected_color: Color name from QR code (e.g., 'red')
            colors: List of tuples [(color_name, color_rgb), ...]
            
        Returns:
            Index of the color in the list, or -1 if not found
        """
        for i, (color_name, color_rgb) in enumerate(colors):
            # Handle both English and Hindi color names
            if color_name.lower() == detected_color.lower():
                print(f"[DEBUG] Found color '{detected_color}' at index {i}")
                return i
            
            # Handle Hindi to English mapping
            hindi_to_english = {
                'लाल': 'red',
                'हरा': 'green', 
                'नीला': 'blue',
                'पीला': 'yellow',
                'गुलाबी': 'pink'
            }
            
            if color_name in hindi_to_english and hindi_to_english[color_name] == detected_color.lower():
                print(f"[DEBUG] Found Hindi color '{color_name}' mapped to '{detected_color}' at index {i}")
                return i
        
        print(f"[ERROR] Color '{detected_color}' not found in colors list")
        return -1

    def _init_camera(self):
        """Initialize camera"""
        if self.cap and self.cap.isOpened():
            return True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[ERROR] Cannot open camera")
            return False
        print("[INFO] Camera opened successfully")
        return True

    def _cleanup_camera(self):
        """Clean up camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def _show_camera_instructions(self, screen, ui_text, fonts):
        """Show camera instructions on screen"""
        area = pygame.Rect(0, screen.get_height() - 150, screen.get_width(), 150)
        pygame.draw.rect(screen, (240, 240, 240), area)

        try:
            camera_text = fonts['english_medium'].render("📷 Camera Active - Show QR Code", True, (0, 100, 0))
        except:
            camera_text = pygame.font.Font(None, 32).render("Camera Active - Show QR Code", True, (0, 100, 0))
        screen.blit(camera_text, (50, screen.get_height() - 130))

        try:
            inst_text = "Show QR code for the COLOR you see (not the word)"
            inst_surface = fonts['english_small'].render(inst_text, True, (50, 50, 50))
        except:
            inst_surface = pygame.font.Font(None, 24).render(inst_text, True, (50, 50, 50))
        screen.blit(inst_surface, (50, screen.get_height() - 100))

        # Show available QR codes
        available_text = f"Available: {', '.join(self.qr_codes.values())}"
        try:
            available_surface = fonts['english_small'].render(available_text, True, (0, 0, 200))
        except:
            available_surface = pygame.font.Font(None, 20).render(available_text, True, (0, 0, 200))
        screen.blit(available_surface, (50, screen.get_height() - 70))

        try:
            esc_text = fonts['english_small'].render("ESC: Quit", True, (100, 100, 100))
        except:
            esc_text = pygame.font.Font(None, 20).render("ESC: Quit", True, (100, 100, 100))
        screen.blit(esc_text, (50, screen.get_height() - 40))

    def _show_timeout_warning(self, remaining_time, screen, ui_text, fonts):
        """Show timeout warning"""
        area = pygame.Rect(screen.get_width()//2 - 100, screen.get_height()//2 + 100, 200, 50)
        pygame.draw.rect(screen, (255, 255, 200), area)
        pygame.draw.rect(screen, (255, 0, 0), area, 2)

        timeout_text = f"Time: {remaining_time:.1f}s"
        try:
            timeout_surface = fonts['english_medium'].render(timeout_text, True, (255, 0, 0))
        except:
            timeout_surface = pygame.font.Font(None, 32).render(timeout_text, True, (255, 0, 0))

        text_rect = timeout_surface.get_rect(center=area.center)
        screen.blit(timeout_surface, text_rect)

    def test_qr_detection(self):
        """Test QR detection functionality"""
        print("Testing QR detection...")
        print(f"Loaded codes: {self.qr_codes}")
        if not self.is_camera_available():
            print("Camera not available")
            return False
        print("Camera ready for detection.")
        return True

    def is_camera_available(self):
        """Check if camera is available"""
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False

    def get_available_qr_codes(self):
        """Get list of available QR codes"""
        return list(self.qr_codes.keys())

    def cleanup(self):
        """Clean up resources"""
        self._cleanup_camera()
        print("[INFO] QRInput cleaned up.")