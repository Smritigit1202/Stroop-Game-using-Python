import pygame
import random
import cv2
import mediapipe as mp
import threading
import time

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Stroop Effect Game - Gesture Controlled")
clock = pygame.time.Clock()

# Game color setup
colors = [
    ("Red", (255, 0, 0)), 
    ("Green", (0, 255, 0)), 
    ("Blue", (0, 0, 255)),
    ("Yellow", (255, 255, 0)), 
    ("Pink", (255, 20, 147))
]

# Fonts
font_large = pygame.font.SysFont("arial", 60)
font_medium = pygame.font.SysFont("arial", 36)
font_small = pygame.font.SysFont("arial", 24)

# MediaPipe Gesture Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Global variables for gesture detection
current_finger_count = 0
gesture_lock = threading.Lock()
camera_active = True

def count_fingers(landmarks):
    """Count extended fingers based on hand landmarks"""
    # Finger tip and pip landmarks
    finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
    finger_pips = [6, 10, 14, 18]
    
    fingers_up = 0
    
    # Count fingers (excluding thumb for simplicity)
    for tip, pip in zip(finger_tips, finger_pips):
        if landmarks[tip].y < landmarks[pip].y:
            fingers_up += 1
    
    # Add thumb (different logic due to thumb orientation)
    if landmarks[4].x > landmarks[3].x:  # Thumb tip vs thumb ip
        fingers_up += 1
    
    return fingers_up

def detect_gesture():
    """Background thread for gesture detection"""
    global current_finger_count, camera_active
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    stable_count = 0
    stable_frames = 0
    required_stable_frames = 10  # Need 10 consistent frames
    
    while camera_active:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        finger_count = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_count = count_fingers(hand_landmarks.landmark)
                
                # Draw hand landmarks for visual feedback
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
                break
        
        # Stabilize gesture recognition
        if finger_count == stable_count:
            stable_frames += 1
        else:
            stable_count = finger_count
            stable_frames = 0
        
        if stable_frames >= required_stable_frames:
            with gesture_lock:
                current_finger_count = finger_count
        
        # Display finger count on camera feed
        cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Show 1-5 fingers to select", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Gesture Control (Press 'q' to quit)", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            camera_active = False
            break
    
    cap.release()
    cv2.destroyAllWindows()

def get_gesture_input():
    """Get current gesture input (1-5 fingers = index 0-4)"""
    with gesture_lock:
        if 1 <= current_finger_count <= 5:
            return current_finger_count - 1  # Convert to 0-based index
    return None

def draw_color_options():
    """Draw color selection buttons with numbers"""
    button_rects = []
    for i, (name, color) in enumerate(colors):
        x = 50 + i * 140
        y = 450
        
        # Draw button background
        pygame.draw.rect(screen, (240, 240, 240), (x, y, 130, 80))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, 130, 80), 2)
        
        # Draw color name
        text = font_small.render(name, True, color)
        text_rect = text.get_rect(center=(x + 65, y + 25))
        screen.blit(text, text_rect)
        
        # Draw finger count instruction
        finger_text = font_small.render(f"{i + 1} finger{'s' if i > 0 else ''}", True, (0, 0, 0))
        finger_rect = finger_text.get_rect(center=(x + 65, y + 55))
        screen.blit(finger_text, finger_rect)
        
        button_rects.append(pygame.Rect(x, y, 130, 80))
    
    return button_rects

def show_instructions():
    """Show game instructions"""
    screen.fill((255, 255, 255))
    
    instructions = [
        "STROOP EFFECT GAME",
        "",
        "Rules:",
        "1. A word will appear in a COLOR",
        "2. Ignore the WORD, focus on the COLOR",
        "3. Show fingers to select the color:",
        "   1 finger = Red",
        "   2 fingers = Green", 
        "   3 fingers = Blue",
        "   4 fingers = Yellow",
        "   5 fingers = Pink",
        "",
        "Make sure your camera is working!",
        "Press SPACE to start or ESC to quit"
    ]
    
    y_offset = 50
    for line in instructions:
        if line.startswith("STROOP"):
            text = font_large.render(line, True, (255, 0, 0))
        elif line.startswith("Rules:"):
            text = font_medium.render(line, True, (0, 0, 255))
        else:
            text = font_small.render(line, True, (0, 0, 0))
        
        text_rect = text.get_rect(center=(400, y_offset))
        screen.blit(text, text_rect)
        y_offset += 30
    
    pygame.display.flip()

def main_game():
    """Main game loop"""
    global camera_active
    
    # Start gesture detection thread
    gesture_thread = threading.Thread(target=detect_gesture, daemon=True)
    gesture_thread.start()
    
    # Show instructions
    waiting_for_start = True
    while waiting_for_start:
        show_instructions()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                camera_active = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting_for_start = False
                elif event.key == pygame.K_ESCAPE:
                    camera_active = False
                    pygame.quit()
                    return
        clock.tick(60)
    
    # Game variables
    score = 0
    total_questions = 20
    question_count = 0
    
    while question_count < total_questions:
        # Generate random word and color
        word_name = random.choice(colors)[0]
        correct_color_index = random.randint(0, 4)
        correct_color_name, correct_color_rgb = colors[correct_color_index]
        
        # Display question
        screen.fill((255, 255, 255))
        
        # Show progress
        progress_text = font_medium.render(f"Question {question_count + 1}/{total_questions}", True, (0, 0, 0))
        screen.blit(progress_text, (20, 20))
        
        # Show score
        score_text = font_medium.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (600, 20))
        
        # Show the word in the target color
        word_surface = font_large.render(word_name, True, correct_color_rgb)
        word_rect = word_surface.get_rect(center=(400, 200))
        screen.blit(word_surface, word_rect)
        
        # Show instruction
        instruction = font_medium.render("Show fingers for the COLOR (not the word):", True, (0, 0, 0))
        instruction_rect = instruction.get_rect(center=(400, 300))
        screen.blit(instruction, instruction_rect)
        
        # Draw color options
        draw_color_options()
        
        pygame.display.flip()
        
        # Wait for gesture input
        start_time = time.time()
        answered = False
        
        while not answered and time.time() - start_time < 5.0:  # 5 second timeout
            gesture_input = get_gesture_input()
            
            if gesture_input is not None:
                if gesture_input == correct_color_index:
                    score += 1
                    # Show correct feedback
                    feedback_text = font_large.render("Correct! +1", True, (0, 255, 0))
                else:
                    # Show incorrect feedback
                    feedback_text = font_large.render("Wrong!", True, (255, 0, 0))
                
                screen.fill((255, 255, 255))
                feedback_rect = feedback_text.get_rect(center=(400, 300))
                screen.blit(feedback_text, feedback_rect)
                pygame.display.flip()
                time.sleep(1)
                answered = True
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    camera_active = False
                    pygame.quit()
                    return
            
            clock.tick(60)
        
        if not answered:
            # Timeout
            screen.fill((255, 255, 255))
            timeout_text = font_large.render("Time's up!", True, (255, 165, 0))
            timeout_rect = timeout_text.get_rect(center=(400, 300))
            screen.blit(timeout_text, timeout_rect)
            pygame.display.flip()
            time.sleep(1)
        
        question_count += 1
    
    # Show final score
    screen.fill((255, 255, 255))
    final_score_text = font_large.render(f"Final Score: {score}/{total_questions}", True, (0, 100, 0))
    final_rect = final_score_text.get_rect(center=(400, 250))
    screen.blit(final_score_text, final_rect)
    
    percentage = (score / total_questions) * 100
    percentage_text = font_medium.render(f"Accuracy: {percentage:.1f}%", True, (0, 0, 0))
    perc_rect = percentage_text.get_rect(center=(400, 300))
    screen.blit(percentage_text, perc_rect)
    
    restart_text = font_small.render("Press SPACE to play again or ESC to quit", True, (0, 0, 0))
    restart_rect = restart_text.get_rect(center=(400, 400))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    # Wait for restart or quit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_game()  # Restart game
                    return
                elif event.key == pygame.K_ESCAPE:
                    waiting = False
        clock.tick(60)
    
    camera_active = False
    pygame.quit()

if __name__ == "__main__":
    main_game()