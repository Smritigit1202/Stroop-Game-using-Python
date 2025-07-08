# -*- coding: utf-8 -*-

import cv2
import numpy as np
import pygame
import time

class CameraInput:
    """Handle camera color detection input for the Stroop Effect game"""
    
    def __init__(self):
        self.cap = None
        self.camera_initialized = False
        self.detection_threshold = 0.15  # Adjusted threshold for better detection
        
        # Color detection ranges in HSV - mapped to match game colors
        self.color_ranges = {
            'red': {
                'hsv_ranges': [
                    (np.array([0, 120, 100]), np.array([10, 255, 255])),
                    (np.array([170, 120, 100]), np.array([179, 255, 255]))
                ],
                'bgr_color': (0, 0, 255)
            },
            'green': {
                'hsv_ranges': [
                    (np.array([40, 100, 100]), np.array([80, 255, 255]))
                ],
                'bgr_color': (0, 255, 0)
            },
            'blue': {
                'hsv_ranges': [
                    (np.array([100, 100, 100]), np.array([130, 255, 255]))
                ],
                'bgr_color': (255, 0, 0)
            },
            'yellow': {
                'hsv_ranges': [
                    (np.array([20, 100, 100]), np.array([35, 255, 255]))
                ],
                'bgr_color': (0, 255, 255)
            },
            'pink': {
                'hsv_ranges': [
                    (np.array([140, 50, 100]), np.array([170, 255, 255]))
                ],
                'bgr_color': (255, 20, 147)
            }
        }
    
    def initialize_camera(self, camera_index=0):
        """Initialize the camera"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                print(f"Warning: Could not open camera {camera_index}")
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Test camera
            ret, frame = self.cap.read()
            if not ret:
                print("Warning: Could not read from camera")
                return False
            
            self.camera_initialized = True
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def detect_color(self, frame):
        """
        Detect color in the center region of the frame
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            str: Color name (None if no color detected)
        """
        if frame is None:
            return None
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width, _ = frame.shape
        
        # Define center region for color detection (larger area)
        center_size = min(height, width) // 3
        center_y = height // 2
        center_x = width // 2
        
        y1 = max(0, center_y - center_size // 2)
        y2 = min(height, center_y + center_size // 2)
        x1 = max(0, center_x - center_size // 2)
        x2 = min(width, center_x + center_size // 2)
        
        center_region = hsv[y1:y2, x1:x2]
        
        if center_region.size == 0:
            return None
        
        total_pixels = center_region.shape[0] * center_region.shape[1]
        
        # Calculate color ratios
        color_ratios = {}
        for color_name, color_info in self.color_ranges.items():
            total_mask = np.zeros(center_region.shape[:2], dtype=np.uint8)
            
            # Combine all HSV ranges for this color
            for hsv_range in color_info['hsv_ranges']:
                mask = cv2.inRange(center_region, hsv_range[0], hsv_range[1])
                total_mask = cv2.bitwise_or(total_mask, mask)
            
            color_ratios[color_name] = np.sum(total_mask > 0) / total_pixels
        
        # Find the dominant color
        max_ratio = max(color_ratios.values())
        if max_ratio >= self.detection_threshold:
            detected_color = max(color_ratios, key=color_ratios.get)
            return detected_color
        
        return None

    def show_camera_feed(self, frame, detected_color=None):
        """
        Display camera feed with detection overlay
        
        Args:
            frame: OpenCV frame
            detected_color: Currently detected color name (None if none)
        """
        if frame is None:
            return
        
        height, width, _ = frame.shape
        overlay = frame.copy()
        
        # Draw detection rectangle
        center_size = min(height, width) // 3
        center_y = height // 2
        center_x = width // 2
        
        y1 = max(0, center_y - center_size // 2)
        y2 = min(height, center_y + center_size // 2)
        x1 = max(0, center_x - center_size // 2)
        x2 = min(width, center_x + center_size // 2)
        
        rect_color = (255, 255, 255)  # Default white
        label = "No Color"
        
        if detected_color and detected_color in self.color_ranges:
            rect_color = self.color_ranges[detected_color]['bgr_color']
            label = detected_color.capitalize()
        
        # Draw rectangle
        cv2.rectangle(overlay, (x1, y1), (x2, y2), rect_color, 3)
        
        # Add detection label with background
        label_text = f"Detected: {label}"
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        
        # Draw background for text
        cv2.rectangle(overlay, (10, 10), (label_size[0] + 20, label_size[1] + 20), (0, 0, 0), -1)
        cv2.putText(overlay, label_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, rect_color, 2)
        
        # Show instructions
        instructions = [
            "Show colored object in center box",
            "Keep object steady for detection",
            "Press 'q' to quit or ESC to cancel"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = height - 80 + i * 25
            cv2.rectangle(overlay, (10, y_pos - 5), (len(instruction) * 10 + 10, y_pos + 20), (0, 0, 0), -1)
            cv2.putText(overlay, instruction, (15, y_pos + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Camera - Color Detection", overlay)


    
    def map_to_detection_color(self, color_name):
     hindi_to_english = {
        'लाल': 'red',
        'हरा': 'green',
        'नीला': 'blue',
        'पीला': 'yellow',
        'गुलाबी': 'pink'
    }
     color_name = color_name.strip().lower()
     return color_name if color_name in self.color_ranges else hindi_to_english.get(color_name)

    def get_input(self, colors, screen, ui_text, fonts):
        """
        Get color input from camera
        
        Args:
            colors: List of (color_name, color_rgb) tuples from the game
            screen: Pygame screen object
            ui_text: UI text dictionary
            fonts: Font dictionary
            
        Returns:
            dict: {'success': bool, 'color_index': int or None, 'message': str}
        """
        if not self.camera_initialized:
            if not self.initialize_camera():
                return {
                    'success': False,
                    'color_index': None,
                    'message': 'Camera not available'
                }
        
        # Show camera instructions on pygame screen
        self._show_camera_instructions(screen, ui_text, fonts)
        pygame.display.flip()
        
        start_time = time.time()
        timeout = 15.0  # 15 seconds timeout
        last_stable_detection = None
        stable_count = 0
        required_stable_frames = 8  # Require 8 consecutive detections for stability
        
        # Create a mapping of game colors to detection colors
        # Hindi-to-English mapping handled here
        color_mapping = {}
        for i, (color_name, color_rgb) in enumerate(colors):
          mapped_color = self.map_to_detection_color(color_name)
          if mapped_color:
            color_mapping[mapped_color] = i

        
        while True:
            current_time = time.time()
            if current_time - start_time > timeout:
                cv2.destroyAllWindows()
                return {
                    'success': False,
                    'color_index': None,
                    'message': 'timeout'
                }
            
            # Check for pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cv2.destroyAllWindows()
                    return {
                        'success': False,
                        'color_index': None,
                        'message': 'quit'
                    }
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        cv2.destroyAllWindows()
                        return {
                            'success': False,
                            'color_index': None,
                            'message': 'quit'
                        }
            
            # Read camera frame
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect color
            detected_color = self.detect_color(frame)
            
            # Check if detection is stable
            if detected_color == last_stable_detection and detected_color is not None:
                stable_count += 1
            else:
                stable_count = 0
                last_stable_detection = detected_color
            
            # Show camera feed
            self.show_camera_feed(frame, detected_color)
            
            # Check if we have a stable detection that matches one of the available colors
            if stable_count >= required_stable_frames and detected_color:
                if detected_color.lower() in color_mapping:
                    color_index = color_mapping[detected_color.lower()]
                    cv2.destroyAllWindows()
                    return {
                        'success': True,
                        'color_index': color_index,
                        'message': 'success'
                    }
            
            # Update timeout display on pygame screen
            remaining_time = timeout - (current_time - start_time)
            if remaining_time <= 5:  # Show countdown in last 5 seconds
                self._show_timeout_warning(remaining_time, screen, ui_text, fonts)
                pygame.display.flip()
            
            # Check for 'q' key press to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC key
                cv2.destroyAllWindows()
                return {
                    'success': False,
                    'color_index': None,
                    'message': 'quit'
                }
            
            # Limit frame rate
            time.sleep(0.033)  # ~30 FPS
    
    def _show_camera_instructions(self, screen, ui_text, fonts):
        """Show camera instructions on pygame screen"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), 200))
        overlay.set_alpha(220)
        overlay.fill((50, 50, 50))
        screen.blit(overlay, (0, screen.get_height() - 200))
        
        instructions = [
            "Camera Color Detection Mode",
            "• Position colored object in center of camera view",
            "• Keep object steady for detection",
            "• Available colors: Red, Green, Blue, Yellow, Pink",
            "• Press 'q' in camera window or ESC to quit"
        ]
        
        y_offset = screen.get_height() - 190
        for i, instruction in enumerate(instructions):
            try:
                if i == 0:
                    text_surface = fonts['english_medium'].render(instruction, True, (255, 255, 255))
                else:
                    text_surface = fonts['english_small'].render(instruction, True, (200, 200, 200))
            except:
                # Fallback font
                font_size = 32 if i == 0 else 24
                font = pygame.font.Font(None, font_size)
                color = (255, 255, 255) if i == 0 else (200, 200, 200)
                text_surface = font.render(instruction, True, color)
            
            screen.blit(text_surface, (20, y_offset + i * 30))
    
    def _show_timeout_warning(self, remaining_time, screen, ui_text, fonts):
        """Show timeout warning"""
        # Create warning box
        warning_width = 250
        warning_height = 80
        warning_x = screen.get_width() // 2 - warning_width // 2
        warning_y = screen.get_height() // 2 + 150
        
        # Draw warning background
        warning_rect = pygame.Rect(warning_x, warning_y, warning_width, warning_height)
        pygame.draw.rect(screen, (255, 255, 200), warning_rect)
        pygame.draw.rect(screen, (255, 0, 0), warning_rect, 3)
        
        # Draw timeout text
        timeout_text = f"Time remaining: {remaining_time:.1f}s"
        try:
            timeout_surface = fonts['english_medium'].render(timeout_text, True, (255, 0, 0))
        except:
            timeout_surface = pygame.font.Font(None, 28).render(timeout_text, True, (255, 0, 0))
        
        text_rect = timeout_surface.get_rect(center=(warning_x + warning_width // 2, warning_y + 25))
        screen.blit(timeout_surface, text_rect)
        
        # Draw warning message
        warning_msg = "Show color to camera!"
        try:
            warning_surface = fonts['english_small'].render(warning_msg, True, (200, 0, 0))
        except:
            warning_surface = pygame.font.Font(None, 24).render(warning_msg, True, (200, 0, 0))
        
        msg_rect = warning_surface.get_rect(center=(warning_x + warning_width // 2, warning_y + 55))
        screen.blit(warning_surface, msg_rect)
    
    def cleanup(self):
        """Clean up camera resources"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        self.camera_initialized = False
    
    def test_camera(self):
        """Test the camera functionality"""
        print("Testing camera input...")
        if not self.initialize_camera():
            print("Failed to initialize camera")
            return False
        
        print("Camera initialized successfully")
        print("Available colors for detection:")
        for color_name in self.color_ranges.keys():
            print(f"  - {color_name.capitalize()}")
        
        print("\nShow different colored objects to the camera to test detection")
        print("Press 'q' to quit test")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error reading from camera")
                    break
                
                frame = cv2.flip(frame, 1)
                detected_color = self.detect_color(frame)
                self.show_camera_feed(frame, detected_color)
                
                if detected_color:
                    print(f"Detected: {detected_color}")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                    
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        except Exception as e:
            print(f"Error during test: {e}")
        finally:
            self.cleanup()
        
        return True
    
    def set_detection_threshold(self, threshold):
        """Set the detection threshold (0.0 to 1.0)"""
        self.detection_threshold = max(0.0, min(1.0, threshold))
        print(f"Detection threshold set to: {self.detection_threshold}")
    
    def get_available_colors(self):
        """Get list of available colors for detection"""
        return list(self.color_ranges.keys())


# Test function for standalone testing
if __name__ == "__main__":
    print("Testing Camera Input Module")
    camera_input = CameraInput()
    
    # Test camera initialization
    if camera_input.test_camera():
        print("Camera test completed successfully")
    else:
        print("Camera test failed")