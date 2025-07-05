import cv2
import pygame
import time
import os

class QRInput:
    """Handle QR code input for the Stroop Effect game"""
    
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
        self.cap = None
        
        # Color mapping for QR codes (maps Hindi/English color names to English QR codes)
        self.color_qr_mapping = {
            "red": "red", "green": "green", "blue": "blue", "yellow": "yellow", "pink": "pink",
            "लाल": "red", "हरा": "green", "नीला": "blue", "पीला": "yellow", "गुलाबी": "pink"
        }

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

    def get_input(self, expected_color, screen, ui_text, fonts, timeout=10):
        if not self._init_camera():
            return {
                'success': False,
                'detected_qr': None,
                'is_correct': False,
                'message': 'camera_error'
            }

        self._show_camera_instructions(screen, ui_text, fonts)

        start_time = time.time()
        detected_qr = None

        while (time.time() - start_time) < timeout:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self._cleanup_camera()
                    return {'success': False, 'detected_qr': None, 'is_correct': False, 'message': 'quit'}

            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Couldn't read from camera")
                continue

            val, points, _ = self.detector.detectAndDecode(frame)
            if val:
                detected_qr = val.strip().lower()
                print(f"[DEBUG] Detected QR: '{detected_qr}'")
                if detected_qr not in self.qr_codes:
                    print(f"[WARNING] QR '{detected_qr}' not in known QR codes")
                    continue
                print(f"[MATCH] QR matched and valid: '{detected_qr}'")
                break

            # UI update
            self._show_camera_instructions(screen, ui_text, fonts)
            self._show_timeout_warning(remaining, screen, ui_text, fonts)
            pygame.display.update()
            pygame.time.wait(50)

        self._cleanup_camera()

        if detected_qr is None:
            print("[TIMEOUT] No QR detected in time.")
            return {'success': False, 'detected_qr': None, 'is_correct': False, 'message': 'timeout'}

        print(f"[INFO] expected_color received: {expected_color}")
        expected_color_name = expected_color[0][0].lower()  # Get 'red' from [('red', (255, 0, 0)), ...]
        expected_qr = self.color_qr_mapping.get(expected_color_name, "")
        is_correct = detected_qr == expected_qr

# Get index of the expected QR color in the color list
        color_index = next(
            (i for i, (name, _) in enumerate(self.color_qr_mapping.items()) if name.lower() == expected_qr),
    -1)

        print(f"[DEBUG] Expected: '{expected_color}' → QR: '{expected_qr}', Detected: '{detected_qr}', Match: {is_correct}")

        return {
          'success': True,
        'detected_qr': detected_qr,
         'is_correct': is_correct,
    'color_index': color_index,
    'message': 'correct' if is_correct else 'incorrect'
}


    def _init_camera(self):
        if self.cap and self.cap.isOpened():
            return True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[ERROR] Cannot open camera")
            return False
        print("[INFO] Camera opened successfully")
        return True

    def _cleanup_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def _show_camera_instructions(self, screen, ui_text, fonts):
        area = pygame.Rect(0, screen.get_height() - 150, screen.get_width(), 150)
        pygame.draw.rect(screen, (240, 240, 240), area)

        try:
            camera_text = fonts['english_medium'].render("📷 Camera Active - Show QR Code", True, (0, 100, 0))
        except:
            camera_text = pygame.font.Font(None, 32).render("Camera Active - Show QR Code", True, (0, 100, 0))
        screen.blit(camera_text, (50, screen.get_height() - 130))

        try:
            inst_text = ui_text.get("show_qr", "Show QR code for the COLOR you see")
            inst_surface = fonts['english_small'].render(inst_text, True, (50, 50, 50))
        except:
            inst_surface = pygame.font.Font(None, 24).render(inst_text, True, (50, 50, 50))
        screen.blit(inst_surface, (50, screen.get_height() - 100))

        try:
            esc_text = fonts['english_small'].render("ESC: Quit", True, (100, 100, 100))
        except:
            esc_text = pygame.font.Font(None, 20).render("ESC: Quit", True, (100, 100, 100))
        screen.blit(esc_text, (50, screen.get_height() - 40))

    def _show_timeout_warning(self, remaining_time, screen, ui_text, fonts):
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
        print("Testing QR detection...")
        print(f"Loaded codes: {self.qr_codes}")
        if not self.is_camera_available():
            print("Camera not available")
            return False
        print("Camera ready for detection.")
        return True

    def is_camera_available(self):
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False

    def get_available_qr_codes(self):
        return list(self.qr_codes.keys())

    def cleanup(self):
        self._cleanup_camera()
        print("[INFO] QRInput cleaned up.")
