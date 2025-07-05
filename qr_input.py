import cv2
import pygame
import time
import os
import sys
import math
import random

class QRInput:
    """Handle QR code input for the Stroop Effect game"""
    
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        self.cap = None
        
        # Color mapping for QR codes (maps Hindi/English color names to English QR codes)
        self.color_qr_mapping = {
            # English
            "red": "red",
            "green": "green", 
            "blue": "blue",
            # Hindi
            "लाल": "red",
            "हरा": "green",
            "नीला": "blue"
        }
        
        # Load and validate QR codes
        self.qr_codes = {}
        self._load_qr_codes()
    
    def _load_qr_codes(self):
        """Load QR codes from the qrs directory"""
        qr_dir = "qrs"
        
        for color_name in ["red", "green", "blue"]:
            path = os.path.join(qr_dir, f"qr_{color_name}.jpg")
            if os.path.exists(path):
                img = cv2.imread(path)
                if img is not None:
                    val, _, _ = self.detector.detectAndDecode(img)
                    if val.strip().lower() == color_name:
                        self.qr_codes[val.lower()] = color_name
                        print(f"Loaded QR code for {color_name}")
                    else:
                        print(f"QR for {color_name} not recognized or mismatched!")
                else:
                    print(f"Failed to load: {path}")
            else:
                print(f"QR file not found: {path}")
        
        print(f"Total QR codes loaded: {len(self.qr_codes)}")
    
    def get_input(self, expected_color, screen, ui_text, fonts, timeout=7):
        """
        Get QR code input from camera
        
        Args:
            expected_color: The expected color name (string)
            screen: Pygame screen object
            ui_text: UI text dictionary
            fonts: Font dictionary
            timeout: Timeout in seconds (default 7)
            
        Returns:
            dict: {'success': bool, 'detected_qr': str or None, 'is_correct': bool, 'message': str}
        """
        # Initialize camera
        if not self._init_camera():
            return {
                'success': False,
                'detected_qr': None,
                'is_correct': False,
                'message': 'camera_error'
            }
        
        # Show camera input instructions
        self._show_camera_instructions(screen, ui_text, fonts)
        
        start_time = time.time()
        detected_qr = None
        
        while (time.time() - start_time) < timeout:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._cleanup_camera()
                    return {
                        'success': False,
                        'detected_qr': None,
                        'is_correct': False,
                        'message': 'quit'
                    }
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._cleanup_camera()
                        return {
                            'success': False,
                            'detected_qr': None,
                            'is_correct': False,
                            'message': 'quit'
                        }
            
            # Time tracking
            elapsed = time.time() - start_time
            time_left = max(0, timeout - elapsed)
            
            # Update timeout display
            if time_left <= 3:  # Show countdown in last 3 seconds
                self._show_timeout_warning(time_left, screen, ui_text, fonts)
            
            # Read frame from camera
            ret, frame = self.cap.read()
            if ret:
                val, points, _ = self.detector.detectAndDecode(frame)
                if val:
                    detected_qr = val.strip().lower()
                    print(f"[DEBUG] Detected QR: '{detected_qr}'")
                    break  # QR found, exit loop
                
                # Show camera feed (optional - comment out if not needed)
                # cv2.imshow("QR Scanner", frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
            
            pygame.display.flip()
            pygame.time.wait(50)  # Small delay to prevent high CPU usage
        
        # Cleanup camera
        self._cleanup_camera()
        
        # Check if we got a result
        if detected_qr is None:
            return {
                'success': False,
                'detected_qr': None,
                'is_correct': False,
                'message': 'timeout'
            }
        
        # Check if answer is correct
        expected_qr = self.color_qr_mapping.get(expected_color.lower(), "")
        is_correct = detected_qr == expected_qr
        
        return {
            'success': True,
            'detected_qr': detected_qr,
            'is_correct': is_correct,
            'message': 'correct' if is_correct else 'incorrect'
        }
    
    def _init_camera(self):
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def _cleanup_camera(self):
        """Clean up camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
    
    def _show_camera_instructions(self, screen, ui_text, fonts):
        """Show camera input instructions"""
        # Clear area for instructions
        instruction_area = pygame.Rect(0, screen.get_height() - 150, screen.get_width(), 150)
        pygame.draw.rect(screen, (240, 240, 240), instruction_area)
        
        # Camera status
        try:
            camera_text = fonts['english_medium'].render("📷 Camera Active - Show QR Code", True, (0, 100, 0))
            screen.blit(camera_text, (50, screen.get_height() - 130))
        except:
            camera_text = pygame.font.Font(None, 32).render("Camera Active - Show QR Code", True, (0, 100, 0))
            screen.blit(camera_text, (50, screen.get_height() - 130))
        
        # Instructions
        instruction_text = ui_text.get("show_qr", "Show QR code for the COLOR you see")
        try:
            inst_surface = fonts['english_small'].render(instruction_text, True, (50, 50, 50))
            screen.blit(inst_surface, (50, screen.get_height() - 100))
        except:
            inst_surface = pygame.font.Font(None, 24).render(instruction_text, True, (50, 50, 50))
            screen.blit(inst_surface, (50, screen.get_height() - 100))
        
        # ESC to quit
        try:
            esc_text = fonts['english_small'].render("ESC: Quit", True, (100, 100, 100))
            screen.blit(esc_text, (50, screen.get_height() - 40))
        except:
            esc_text = pygame.font.Font(None, 20).render("ESC: Quit", True, (100, 100, 100))
            screen.blit(esc_text, (50, screen.get_height() - 40))
    
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
    
    def validate_qr_code(self, qr_value, expected_color):
        """Validate if QR code matches expected color"""
        expected_qr = self.color_qr_mapping.get(expected_color.lower(), "")
        return qr_value.lower() == expected_qr
    
    def cleanup(self):
        """Clean up all resources"""
        self._cleanup_camera()
        print("QR Input cleanup completed")
    
    def test_qr_detection(self):
        """Test QR code detection functionality"""
        print("Testing QR code detection...")
        print(f"Loaded QR codes: {self.qr_codes}")
        print(f"Color mappings: {self.color_qr_mapping}")
        
        if not self.is_camera_available():
            print("Camera not available for testing")
            return False
        
        print("Camera available for QR detection")
        return True