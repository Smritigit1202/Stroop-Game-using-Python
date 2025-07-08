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
                min_detection_confidence=0.5,  # Lowered for better detection
                min_tracking_confidence=0.3    # Lowered for better tracking
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
            self.required_stable_frames = 10  # Reduced for faster response
            
            # Input timeout settings
            self.timeout_duration = 15.0  # Increased timeout
            self.gesture_hold_time = 1.5  # Reduced hold time
            
            # Last valid gesture tracking
            self.last_valid_gesture = None
            self.last_gesture_time = 0
            self.gesture_start_time = 0
            self.gesture_confirmed = False
            
            # Camera initialization flag
            self.camera_initialized = False
            
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
        
        print("Starting camera...")
        
        try:
            # Try different camera indices with more thorough testing
            camera_found = False
            for camera_index in [0, 1, 2, -1]:  # Added -1 as fallback
                print(f"Testing camera index {camera_index}...")
                try:
                    test_cap = cv2.VideoCapture(camera_index)
                    
                    # Set camera properties before testing
                    test_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    test_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    test_cap.set(cv2.CAP_PROP_FPS, 30)
                    test_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    # Wait a moment for camera to initialize
                    time.sleep(0.5)
                    
                    if test_cap.isOpened():
                        # Try to read multiple frames to ensure camera is working
                        successful_reads = 0
                        for _ in range(5):
                            ret, frame = test_cap.read()
                            if ret and frame is not None and frame.size > 0:
                                successful_reads += 1
                            time.sleep(0.1)
                        
                        if successful_reads >= 3:
                            print(f"Camera {camera_index} is working properly ({successful_reads}/5 frames read)")
                            test_cap.release()
                            self.camera_index = camera_index
                            camera_found = True
                            break
                        else:
                            print(f"Camera {camera_index} opened but unstable ({successful_reads}/5 frames read)")
                    else:
                        print(f"Camera {camera_index} failed to open")
                    
                    test_cap.release()
                    
                except Exception as e:
                    print(f"Error testing camera {camera_index}: {e}")
                    try:
                        test_cap.release()
                    except:
                        pass
                    continue
            
            if not camera_found:
                print("ERROR: No working camera found!")
                print("Please check:")
                print("1. Camera is connected and not used by another application")
                print("2. Camera permissions are granted")
                print("3. Camera drivers are installed")
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
            self.camera_initialized = False
            
            # Start gesture detection thread
            self.gesture_thread = threading.Thread(target=self._detect_gesture, daemon=True)
            self.gesture_thread.start()
            
            # Wait for camera to fully initialize
            print("Waiting for camera to initialize...")
            for i in range(50):  # Wait up to 5 seconds
                if self.camera_initialized:
                    break
                time.sleep(0.1)
            
            if not self.camera_initialized:
                print("Warning: Camera initialization timeout, but proceeding...")
            
            print("Camera started successfully!")
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
        
        self.camera_initialized = False
        print("Camera stopped")
    
    def _count_fingers(self, landmarks):
        """Count extended fingers based on hand landmarks"""
        if not landmarks:
            return 0
        
        # Landmark indices for finger tips and reference points
        finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        finger_pips = [3, 6, 10, 14, 18]  # Reference points
        
        fingers_up = 0
        
        try:
            # Check thumb (different logic - compare x coordinates)
            if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
                fingers_up += 1
            
            # Check other fingers (compare y coordinates - tip should be above pip)
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
        
        print("Starting gesture detection thread...")
        
        try:
            # Initialize camera in the thread
            self.cap = cv2.VideoCapture(self.camera_index)
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Additional camera settings for better performance
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            
            if not self.cap.isOpened():
                print("ERROR: Could not open camera in detection thread")
                self.camera_active = False
                return
            
            # Wait for camera to stabilize
            print("Camera warming up...")
            for _ in range(10):
                ret, frame = self.cap.read()
                if ret:
                    break
                time.sleep(0.1)
            
            print("Camera ready for gesture detection!")
            self.camera_initialized = True
            
        except Exception as e:
            print(f"Error opening camera in detection thread: {e}")
            self.camera_active = False
            return
        
        consecutive_failures = 0
        max_failures = 20
        frame_count = 0
        
        while self.camera_active:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    consecutive_failures += 1
                    print(f"Failed to read frame (attempt {consecutive_failures})")
                    if consecutive_failures >= max_failures:
                        print(f"Too many consecutive frame read failures ({consecutive_failures})")
                        break
                    time.sleep(0.1)
                    continue
                
                consecutive_failures = 0
                frame_count += 1
                
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
                        old_count = self.current_finger_count
                        self.current_finger_count = finger_count
                        if old_count != finger_count and finger_count > 0:
                            print(f"GESTURE DETECTED: {finger_count} fingers")  # Fixed message
                
                # Display information on frame
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Stable: {self.stable_frames}/{self.required_stable_frames}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, f"Current: {self.current_finger_count}", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, "Show 1-5 fingers to select color", (10, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Hold gesture for confirmation", (10, 180),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to close camera", (10, 210),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Show the frame
                cv2.imshow("Gesture Control - Stroop Game", frame)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("User pressed 'q' to quit camera")
                    self.camera_active = False
                    break
                elif key == ord('r'):
                    print("Resetting gesture detection...")
                    with self.gesture_lock:
                        self.current_finger_count = 0
                        self.stable_count = 0
                        self.stable_frames = 0
                
                # Debug output every 30 frames
                if frame_count % 30 == 0:
                    print(f"Frame {frame_count}: Fingers={finger_count}, Stable={self.stable_frames}, Current={self.current_finger_count}")
                    
            except Exception as e:
                print(f"Error in gesture detection loop: {e}")
                consecutive_failures += 1
                if consecutive_failures >= max_failures:
                    print("Too many consecutive errors, stopping camera")
                    break
                time.sleep(0.1)
        
        # Cleanup
        print("Cleaning up gesture detection thread...")
        if self.cap:
            self.cap.release()
            self.cap = None
        
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        self.camera_active = False
        self.camera_initialized = False
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
        
        print("Starting gesture input process...")
        
        # Start camera if not already started
        if not self.camera_active:
            print("Camera not active, starting...")
            if not self.start_camera():
                return {
                    'success': False,
                    'color_index': None,
                    'message': 'Failed to start camera'
                }
        
        # Wait for camera to be ready
        wait_time = 0
        while not self.camera_initialized and wait_time < 5.0:
            time.sleep(0.1)
            wait_time += 0.1
        
        if not self.camera_initialized:
            print("Warning: Camera not fully initialized, proceeding anyway...")
        
        # Reset gesture state
        with self.gesture_lock:
            self.gesture_confirmed = False
            self.gesture_start_time = 0
            self.current_finger_count = 0
        
        start_time = time.time()
        current_gesture = None
        gesture_hold_start = 0
        
        # Show initial instructions
        self._show_gesture_instructions(screen, ui_text, fonts, colors)
        pygame.display.flip()
        
        print("Waiting for gesture input...")
        print("Available gestures:")
        for i, (color_name, _) in enumerate(colors):
            print(f"  {i+1} fingers = {color_name}")
        
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
                    color_name = colors[detected_gesture][0]
                    print(f"Gesture detected: {detected_gesture + 1} fingers ({color_name})")
                else:
                    # Same gesture, check if held long enough
                    hold_duration = time.time() - gesture_hold_start
                    if hold_duration >= self.gesture_hold_time:
                        color_name = colors[detected_gesture][0]
                        print(f"Gesture confirmed: {detected_gesture + 1} fingers ({color_name})")
                        # Don't stop camera here - let the main game handle it
                        return {
                            'success': True,
                            'color_index': detected_gesture,
                            'message': f'Selected {color_name}'
                        }
            else:
                # No valid gesture
                if current_gesture is not None:
                    print("Gesture lost")
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
            if remaining_time <= 5.0:
                self._show_timeout_warning(remaining_time, screen, ui_text, fonts)
            
            pygame.display.flip()
            time.sleep(0.05)  # Small delay to prevent excessive CPU usage
        
        # Timeout reached
        print("Gesture input timeout reached")
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
            ]
            
            # Add color mappings
            for i, (color_name, _) in enumerate(colors):
                instructions.append(f"{i+1} finger{'s' if i > 0 else ''} = {color_name}")
            
            instructions.extend([
                "",
                f"Hold gesture for {self.gesture_hold_time} seconds to confirm",
                "Camera window shows live feed",
                "Press ESC to quit"
            ])
            
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
        progress_area = pygame.Rect(screen.get_width()//2 - 150, 100, 300, 30)
        pygame.draw.rect(screen, (200, 200, 200), progress_area)
        
        # Progress fill
        fill_width = int(progress_area.width * progress)
        fill_area = pygame.Rect(progress_area.x, progress_area.y, fill_width, progress_area.height)
        
        # Color the progress bar based on selection
        if gesture_index < len(colors):
            color_rgb = colors[gesture_index][1]
            pygame.draw.rect(screen, color_rgb, fill_area)
        else:
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
        print("Cleaning up gesture input...")
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
        print(f"Hold gesture for {self.gesture_hold_time} seconds to confirm")
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