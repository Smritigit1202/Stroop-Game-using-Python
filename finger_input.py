import pygame
import threading
import time
import sys

# Try to import computer vision libraries
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Install with: pip install opencv-python")

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False
    print("Warning: MediaPipe not available. Install with: pip install mediapipe")

class GestureInput:
    """Handle finger gesture input for the Stroop Effect game"""
    
    def __init__(self):
        # Check if required libraries are available
        if not CV2_AVAILABLE or not MP_AVAILABLE:
            self.available = False
            print("Gesture input unavailable: Missing required libraries")
            return
        
        try:
            # MediaPipe setup
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            
            # Gesture detection variables
            self.current_finger_count = 0
            self.gesture_lock = threading.Lock()
            self.camera_active = False
            self.gesture_thread = None
            self.cap = None
            self.camera_index = 0
            
            # Gesture stability settings
            self.stable_count = 0
            self.stable_frames = 0
            self.required_stable_frames = 15  # Frames needed for stable gesture
            
            # Input timeout settings
            self.timeout_duration = 10.0  # seconds
            self.gesture_hold_time = 1.0  # seconds to hold gesture
            
            # Last valid gesture tracking
            self.last_valid_gesture = None
            self.last_gesture_time = 0
            self.gesture_start_time = 0
            self.gesture_confirmed = False
            
            self.available = True
            print("Gesture input initialized successfully")
            
        except Exception as e:
            self.available = False
            print(f"Error initializing gesture input: {e}")
    
    def is_available(self):
        """Check if gesture input is available"""
        return hasattr(self, 'available') and self.available
    
    def start_camera(self):
        """Start the camera and gesture detection thread"""
        if not self.is_available():
            print("Gesture input not available")
            return False
            
        if self.camera_active:
            print("Camera already active")
            return True
            
        try:
            # Try different camera indices
            camera_found = False
            for camera_index in [0, 1, 2]:
                print(f"Trying camera index {camera_index}...")
                try:
                    test_cap = cv2.VideoCapture(camera_index)
                    if test_cap.isOpened():
                        # Set a reasonable resolution
                        test_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        test_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        
                        ret, frame = test_cap.read()
                        if ret and frame is not None:
                            print(f"Camera {camera_index} is working")
                            test_cap.release()
                            self.camera_index = camera_index
                            camera_found = True
                            break
                        else:
                            print(f"Camera {camera_index} opened but can't read frames")
                    else:
                        print(f"Camera {camera_index} failed to open")
                    test_cap.release()
                except Exception as e:
                    print(f"Error testing camera {camera_index}: {e}")
                    continue
            
            if not camera_found:
                print("No working camera found")
                return False
            
            # Reset gesture state
            with self.gesture_lock:
                self.current_finger_count = 0
                self.stable_count = 0
                self.stable_frames = 0
                self.last_valid_gesture = None
                self.last_gesture_time = 0
                self.gesture_confirmed = False
            
            self.camera_active = True
            self.gesture_thread = threading.Thread(target=self._detect_gesture, daemon=True)
            self.gesture_thread.start()
            
            # Wait for camera to initialize
            time.sleep(1)
            
            print("Camera started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            self.camera_active = False
            return False
    
    def stop_camera(self):
        """Stop the camera and gesture detection"""
        if not self.is_available():
            return
            
        print("Stopping camera...")
        self.camera_active = False
        
        if self.gesture_thread and self.gesture_thread.is_alive():
            self.gesture_thread.join(timeout=3.0)
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        try:
            cv2.destroyAllWindows()
        except:
            pass
            
        print("Camera stopped")
    
    def _count_fingers(self, landmarks):
        """Count extended fingers based on hand landmarks"""
        if not landmarks:
            return 0
        
        # Landmark indices for finger tips and PIPs
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18]  # Thumb IP, Index PIP, Middle PIP, Ring PIP, Pinky PIP
        
        fingers_up = 0
        
        try:
            # Check thumb (different logic due to orientation)
            if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
                fingers_up += 1
            
            # Check other fingers (tip higher than PIP)
            for i in range(1, 5):
                if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
                    fingers_up += 1
                    
        except (IndexError, AttributeError) as e:
            print(f"Error counting fingers: {e}")
            return 0
        
        return fingers_up
    
    def _detect_gesture(self):
        """Background thread for gesture detection"""
        if not self.is_available():
            return
            
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not self.cap.isOpened():
                print("Error: Could not open camera in detection thread")
                self.camera_active = False
                return
                
            print("Camera opened successfully in detection thread")
            
        except Exception as e:
            print(f"Error opening camera in detection thread: {e}")
            self.camera_active = False
            return
        
        consecutive_failures = 0
        max_failures = 10
        
        while self.camera_active:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        print(f"Too many consecutive frame read failures ({consecutive_failures})")
                        break
                    continue
                
                consecutive_failures = 0
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                finger_count = 0
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        finger_count = self._count_fingers(hand_landmarks.landmark)
                        
                        # Draw hand landmarks
                        self.mp_drawing.draw_landmarks(
                            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )
                        break
                
                # Gesture stability logic
                if finger_count == self.stable_count:
                    self.stable_frames += 1
                else:
                    self.stable_count = finger_count
                    self.stable_frames = 0
                
                # Update current gesture only if stable
                if self.stable_frames >= self.required_stable_frames:
                    with self.gesture_lock:
                        self.current_finger_count = finger_count
                
                # Display information on frame
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Stable: {self.stable_frames}/{self.required_stable_frames}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, "Show 1-5 fingers to select color", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Hold gesture for 1 second", (10, 140),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to close camera", (10, 170),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Show the frame
                cv2.imshow("Gesture Control", frame)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("User pressed 'q' to quit camera")
                    self.camera_active = False
                    break
                    
            except Exception as e:
                print(f"Error in gesture detection loop: {e}")
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    print("Too many consecutive errors, stopping camera")
                    break
                time.sleep(0.1)
        
        # Cleanup
        if self.cap:
            self.cap.release()
            self.cap = None
            
        try:
            cv2.destroyAllWindows()
        except:
            pass
            
        self.camera_active = False
        print("Gesture detection thread ended")
    
    def get_current_gesture(self):
        """Get current stable gesture (1-5 fingers = index 0-4)"""
        if not self.is_available() or not self.camera_active:
            return None
            
        with self.gesture_lock:
            if 1 <= self.current_finger_count <= 5:
                return self.current_finger_count - 1
        return None
    
    def get_input(self, colors, screen, ui_text, fonts):
        """
        Get finger gesture input for color selection
        
        Args:
            colors: List of (color_name, color_rgb) tuples
            screen: Pygame screen object
            ui_text: UI text dictionary
            fonts: Font dictionary
            
        Returns:
            dict: {'success': bool, 'color_index': int or None, 'message': str}
        """
        if not self.is_available():
            return {
                'success': False,
                'color_index': None,
                'message': 'Gesture input not available'
            }
        
        # Start camera if not already started
        if not self.camera_active:
            if not self.start_camera():
                return {
                    'success': False,
                    'color_index': None,
                    'message': 'Failed to start camera'
                }
        
        # Reset gesture state
        with self.gesture_lock:
            self.gesture_confirmed = False
            self.gesture_start_time = 0
        
        start_time = time.time()
        current_gesture = None
        gesture_hold_start = 0
        
        # Show initial instructions
        self._show_gesture_instructions(screen, ui_text, fonts, colors)
        pygame.display.flip()
        
        print("Waiting for gesture input...")
        
        while time.time() - start_time < self.timeout_duration:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {
                        'success': False,
                        'color_index': None,
                        'message': 'quit'
                    }
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return {
                            'success': False,
                            'color_index': None,
                            'message': 'quit'
                        }
            
            # Get current gesture
            detected_gesture = self.get_current_gesture()
            
            if detected_gesture is not None and 0 <= detected_gesture < len(colors):
                if current_gesture != detected_gesture:
                    # New gesture detected
                    current_gesture = detected_gesture
                    gesture_hold_start = time.time()
                    print(f"Gesture detected: {detected_gesture + 1} fingers")
                else:
                    # Same gesture, check if held long enough
                    hold_duration = time.time() - gesture_hold_start
                    if hold_duration >= self.gesture_hold_time:
                        print(f"Gesture confirmed: {detected_gesture + 1} fingers")
                        return {
                            'success': True,
                            'color_index': detected_gesture,
                            'message': f'Selected color {detected_gesture + 1}'
                        }
            else:
                # No valid gesture
                current_gesture = None
                gesture_hold_start = 0
            
            # Update display
            self._show_gesture_instructions(screen, ui_text, fonts, colors)
            
            # Show current gesture status
            if current_gesture is not None:
                hold_duration = time.time() - gesture_hold_start
                progress = min(hold_duration / self.gesture_hold_time, 1.0)
                self._show_gesture_progress(screen, current_gesture, progress, colors, fonts)
            
            # Show timeout warning
            remaining_time = self.timeout_duration - (time.time() - start_time)
            if remaining_time <= 3.0:
                self._show_timeout_warning(remaining_time, screen, ui_text, fonts)
            
            pygame.display.flip()
            time.sleep(0.05)  # Small delay to prevent excessive CPU usage
        
        # Timeout reached
        return {
            'success': False,
            'color_index': None,
            'message': 'Timeout - no gesture detected'
        }
    
    def _show_gesture_instructions(self, screen, ui_text, fonts, colors):
        """Show gesture input instructions"""
        # Clear the screen area for instructions
        instruction_area = pygame.Rect(50, 150, screen.get_width() - 100, 400)
        pygame.draw.rect(screen, (240, 240, 240), instruction_area)
        pygame.draw.rect(screen, (0, 0, 0), instruction_area, 2)
        
        # Title
        try:
            if 'english_medium' in fonts:
                title_font = fonts['english_medium']
            else:
                title_font = pygame.font.Font(None, 36)
            
            title_text = title_font.render("Gesture Input", True, (0, 0, 200))
            screen.blit(title_text, (instruction_area.x + 10, instruction_area.y + 10))
            
            # Instructions
            instructions = [
                "Show fingers to select colors:",
                "",
                "1 finger = " + colors[0][0] if len(colors) > 0 else "1 finger = Color 1",
                "2 fingers = " + colors[1][0] if len(colors) > 1 else "2 fingers = Color 2",
                "3 fingers = " + colors[2][0] if len(colors) > 2 else "3 fingers = Color 3",
                "4 fingers = " + colors[3][0] if len(colors) > 3 else "4 fingers = Color 4",
                "5 fingers = " + colors[4][0] if len(colors) > 4 else "5 fingers = Color 5",
                "",
                "Hold gesture for 1 second to confirm",
                "Camera window shows live feed",
                "Press ESC to quit"
            ]
            
            small_font = fonts.get('english_small', pygame.font.Font(None, 24))
            
            y_offset = 60
            for instruction in instructions:
                if instruction:  # Skip empty lines
                    text_surface = small_font.render(instruction, True, (0, 0, 0))
                    screen.blit(text_surface, (instruction_area.x + 20, instruction_area.y + y_offset))
                y_offset += 30
                
        except Exception as e:
            print(f"Error showing instructions: {e}")
            # Fallback text
            fallback_font = pygame.font.Font(None, 24)
            fallback_text = fallback_font.render("Show 1-5 fingers to select color", True, (0, 0, 0))
            screen.blit(fallback_text, (instruction_area.x + 20, instruction_area.y + 20))
    
    def _show_gesture_progress(self, screen, gesture_index, progress, colors, fonts):
        """Show gesture confirmation progress"""
        # Progress bar area
        progress_area = pygame.Rect(screen.get_width()//2 - 100, 100, 200, 30)
        pygame.draw.rect(screen, (200, 200, 200), progress_area)
        
        # Progress fill
        fill_width = int(progress_area.width * progress)
        fill_area = pygame.Rect(progress_area.x, progress_area.y, fill_width, progress_area.height)
        pygame.draw.rect(screen, (0, 255, 0), fill_area)
        
        # Progress border
        pygame.draw.rect(screen, (0, 0, 0), progress_area, 2)
        
        # Progress text
        try:
            font = fonts.get('english_small', pygame.font.Font(None, 24))
            color_name = colors[gesture_index][0] if gesture_index < len(colors) else f"Color {gesture_index + 1}"
            progress_text = f"Selecting {color_name}: {progress * 100:.0f}%"
            text_surface = font.render(progress_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(screen.get_width()//2, 80))
            screen.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error showing progress: {e}")
    
    def _show_timeout_warning(self, remaining_time, screen, ui_text, fonts):
        """Show timeout warning"""
        # Warning area
        warning_area = pygame.Rect(screen.get_width()//2 - 100, screen.get_height() - 100, 200, 50)
        pygame.draw.rect(screen, (255, 255, 200), warning_area)
        pygame.draw.rect(screen, (255, 0, 0), warning_area, 2)
        
        timeout_text = f"Time: {remaining_time:.1f}s"
        try:
            font = fonts.get('english_medium', pygame.font.Font(None, 32))
            timeout_surface = font.render(timeout_text, True, (255, 0, 0))
        except:
            timeout_surface = pygame.font.Font(None, 32).render(timeout_text, True, (255, 0, 0))
        
        text_rect = timeout_surface.get_rect(center=warning_area.center)
        screen.blit(timeout_surface, text_rect)
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_available():
            self.stop_camera()
            if hasattr(self, 'hands'):
                self.hands.close()
    
    def test_input(self):
        """Test the finger input functionality"""
        if not self.is_available():
            print("Gesture input not available - missing dependencies")
            print("Please install required packages:")
            print("pip install opencv-python mediapipe")
            return False
            
        print("Testing finger input...")
        print("Gesture mappings:")
        print("1 finger = Color 1")
        print("2 fingers = Color 2")
        print("3 fingers = Color 3")
        print("4 fingers = Color 4")
        print("5 fingers = Color 5")
        print("Hold gesture for 1 second to confirm")
        print("ESC key: Quit")
        print("Camera window: Press 'q' to quit camera")
        
        # Test camera initialization
        try:
            if self.start_camera():
                print("Camera initialized successfully!")
                print("You should see a camera window. Test your gestures there.")
                
                # Keep camera running for testing
                input("Press Enter to stop the test...")
                
                self.stop_camera()
                print("Camera test completed!")
                return True
            else:
                print("Camera initialization failed!")
                return False
        except Exception as e:
            print(f"Camera test failed: {e}")
            return False

# Test function that can be run directly
def test_gesture_input():
    """Test the gesture input system"""
    print("Testing Gesture Input System")
    print("=" * 40)
    
    gesture_input = GestureInput()
    
    if gesture_input.is_available():
        print("✓ Gesture input system is available")
        return gesture_input.test_input()
    else:
        print("✗ Gesture input system is not available")
        print("Please install required dependencies:")
        print("pip install opencv-python mediapipe")
        return False

# Run test if this file is executed directly
if __name__ == "__main__":
    test_gesture_input()