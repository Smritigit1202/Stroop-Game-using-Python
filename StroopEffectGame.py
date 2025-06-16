import pygame
import random
import cv2
import mediapipe as mp
import threading
import time
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Stroop Effect Game - Gesture Controlled")
clock = pygame.time.Clock()

# Language setup
LANGUAGES = {
    'english': {
        'colors': [
            ("Red", (255, 0, 0)), 
            ("Green", (0, 255, 0)), 
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)), 
            ("Pink", (255, 20, 147))
        ],
        'ui': {
            'title': 'STROOP EFFECT GAME',
            'language_prompt': 'Choose Language / भाषा चुनें',
            'press_1': 'Press 1 for English',
            'press_2': 'Press 2 for Hindi / हिंदी के लिए 2 दबाएं',
            'rules': 'Rules:',
            'rule1': '1. A word will appear in a COLOR',
            'rule2': '2. Ignore the WORD, focus on the COLOR',
            'rule3': '3. Show fingers to select the color:',
            'finger_mapping': [
                '   1 finger = Red',
                '   2 fingers = Green', 
                '   3 fingers = Blue',
                '   4 fingers = Yellow',
                '   5 fingers = Pink'
            ],
            'camera_check': 'Make sure your camera is working!',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'question': 'Question',
            'score': 'Score',
            'instruction': 'Show fingers for the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit',
            'fingers_text': ['finger', 'fingers', 'fingers', 'fingers', 'fingers'],
            'gesture_instruction': 'Show 1-5 fingers to select',
            'language_change': 'Press L to change language'
        }
    },
    'hindi': {
        'colors': [
            ("लाल", (255, 0, 0)),      # Red
            ("हरा", (0, 255, 0)),       # Green  
            ("नीला", (0, 0, 255)),      # Blue
            ("पीला", (255, 255, 0)),    # Yellow
            ("गुलाबी", (255, 20, 147))  # Pink
        ],
        'ui': {
            'title': 'स्ट्रूप प्रभाव खेल',
            'language_prompt': 'Choose Language / भाषा चुनें',
            'press_1': 'Press 1 for English',
            'press_2': 'Press 2 for Hindi / हिंदी के लिए 2 दबाएं',
            'rules': 'नियम:',
            'rule1': '1. एक शब्द एक रंग में दिखाई देगा',
            'rule2': '2. शब्द को नज़रअंदाज़ करें, रंग पर ध्यान दें',
            'rule3': '3. रंग चुनने के लिए उंगलियां दिखाएं:',
            'finger_mapping': [
                '   1 उंगली = लाल',
                '   2 उंगलियां = हरा', 
                '   3 उंगलियां = नीला',
                '   4 उंगलियां = पीला',
                '   5 उंगलियां = गुलाबी'
            ],
            'camera_check': 'सुनिश्चित करें कि आपका कैमरा काम कर रहा है!',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या बाहर निकलने के लिए ESC',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'instruction': 'रंग के लिए उंगलियां दिखाएं (शब्द के लिए नहीं):',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या बाहर निकलने के लिए ESC',
            'fingers_text': ['उंगली', 'उंगलियां', 'उंगलियां', 'उंगलियां', 'उंगलियां'],
            'gesture_instruction': '1-5 उंगलियां दिखाएं',
            'language_change': 'भाषा बदलने के लिए L दबाएं'
        }
    }
}

# Global variables
current_language = 'english'
colors = LANGUAGES[current_language]['colors']
ui_text = LANGUAGES[current_language]['ui']

# Font setup with Hindi support
def load_fonts():
    """Load fonts with Hindi support"""
    # Check if Mangal font exists in the current directory
    mangal_font_path = "Mangal.ttf"
    
    if os.path.exists(mangal_font_path):
        # Use Mangal font for Hindi text
        try:
            font_large_hindi = pygame.font.Font(mangal_font_path, 50)
            font_medium_hindi = pygame.font.Font(mangal_font_path, 32)
            font_small_hindi = pygame.font.Font(mangal_font_path, 22)
            font_tiny_hindi = pygame.font.Font(mangal_font_path, 18)
            print("✓ Mangal font loaded successfully for Hindi text!")
            
            # Test Hindi rendering
            test_surface = font_medium_hindi.render("भाषा", True, (0, 0, 0))
            print("✓ Hindi text rendering test passed!")
            
        except Exception as e:
            print(f"✗ Error loading Mangal font: {e}")
            print("✗ Falling back to system fonts...")
            # Try system Hindi fonts
            font_large_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 50)
            font_medium_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 32)
            font_small_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 22)
            font_tiny_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 18)
    else:
        print("✗ mangal.ttf not found in current directory.")
        print("ℹ Trying system fonts for Hindi support...")
        # Try system Hindi fonts
        font_large_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 50)
        font_medium_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 32)
        font_small_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 22)
        font_tiny_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 18)
    
    # English fonts (using system fonts)
    font_large_english = pygame.font.SysFont("arial", 50)
    font_medium_english = pygame.font.SysFont("arial", 32)
    font_small_english = pygame.font.SysFont("arial", 22)
    font_tiny_english = pygame.font.SysFont("arial", 18)
    
    return {
        'hindi': {
            'large': font_large_hindi,
            'medium': font_medium_hindi,
            'small': font_small_hindi,
            'tiny': font_tiny_hindi
        },
        'english': {
            'large': font_large_english,
            'medium': font_medium_english,
            'small': font_small_english,
            'tiny': font_tiny_english
        }
    }

# Load fonts
fonts = load_fonts()

def get_font(size):
    """Get appropriate font based on current language"""
    return fonts[current_language][size]

def render_text(text, size, color):
    """Render text with appropriate font for current language"""
    font = get_font(size)
    return font.render(text, True, color)

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

def update_language(lang):
    """Update current language and related variables"""
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[current_language]['colors']
    ui_text = LANGUAGES[current_language]['ui']

def count_fingers(landmarks):
    """Count extended fingers based on hand landmarks"""
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
    required_stable_frames = 10
    
    while camera_active:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        finger_count = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_count = count_fingers(hand_landmarks.landmark)
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
                break
        
        if finger_count == stable_count:
            stable_frames += 1
        else:
            stable_count = finger_count
            stable_frames = 0
        
        if stable_frames >= required_stable_frames:
            with gesture_lock:
                current_finger_count = finger_count
        
        # Display info on camera feed
        cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, ui_text['gesture_instruction'], (10, 70),
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
            return current_finger_count - 1
    return None

def draw_color_options():
    """Draw color selection buttons with numbers"""
    button_rects = []
    for i, (name, color) in enumerate(colors):
        x = 70 + i * 150
        y = 500
        
        # Draw button background
        pygame.draw.rect(screen, (240, 240, 240), (x, y, 140, 90))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, 140, 90), 2)
        
        # Draw color name with proper font
        text = render_text(name, 'small', color)
        text_rect = text.get_rect(center=(x + 70, y + 30))
        screen.blit(text, text_rect)
        
        # Draw finger count instruction with proper font
        finger_text = render_text(f"{i + 1} {ui_text['fingers_text'][i]}", 'tiny', (0, 0, 0))
        finger_rect = finger_text.get_rect(center=(x + 70, y + 65))
        screen.blit(finger_text, finger_rect)
        
        button_rects.append(pygame.Rect(x, y, 140, 90))
    
    return button_rects

def render_mixed_text(text, size, color, use_hindi_font=False):
    """Render text that might contain both English and Hindi characters"""
    font_to_use = fonts['hindi'][size] if use_hindi_font else fonts['english'][size]
    return font_to_use.render(text, True, color)

def select_language():
    """Language selection screen"""
    screen.fill((255, 255, 255))
    
    # Title - render separately for English and Hindi parts
    english_part = "Choose Language / "
    hindi_part = "भाषा चुनें"
    
    # Render English part
    english_text = fonts['english']['large'].render(english_part, True, (0, 0, 200))
    english_width = english_text.get_width()
    
    # Render Hindi part
    hindi_text = fonts['hindi']['large'].render(hindi_part, True, (0, 0, 200))
    hindi_width = hindi_text.get_width()
    
    # Calculate total width and center position
    total_width = english_width + hindi_width
    start_x = (900 - total_width) // 2
    
    # Blit both parts
    screen.blit(english_text, (start_x, 180))
    screen.blit(hindi_text, (start_x + english_width, 180))
    
    # Option 1 - English only
    option1 = fonts['english']['medium'].render("Press 1 for English", True, (0, 0, 0))
    option1_rect = option1.get_rect(center=(450, 300))
    screen.blit(option1, option1_rect)
    
    # Option 2 - Mixed text, render separately
    english_part2 = "Press 2 for Hindi / "
    hindi_part2 = "हिंदी के लिए 2 दबाएं"
    
    # Render English part
    english_text2 = fonts['english']['medium'].render(english_part2, True, (0, 0, 0))
    english_width2 = english_text2.get_width()
    
    # Render Hindi part
    hindi_text2 = fonts['hindi']['medium'].render(hindi_part2, True, (0, 0, 0))
    hindi_width2 = hindi_text2.get_width()
    
    # Calculate total width and center position
    total_width2 = english_width2 + hindi_width2
    start_x2 = (900 - total_width2) // 2
    
    # Blit both parts
    screen.blit(english_text2, (start_x2, 350))
    screen.blit(hindi_text2, (start_x2 + english_width2, 350))
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    update_language('english')
                    return 'english'
                elif event.key == pygame.K_2:
                    update_language('hindi')
                    return 'hindi'
                elif event.key == pygame.K_ESCAPE:
                    return None
        clock.tick(60)

def show_instructions():
    """Show game instructions"""
    screen.fill((255, 255, 255))
    
    # Title
    title = render_text(ui_text['title'], 'large', (255, 0, 0))
    title_rect = title.get_rect(center=(450, 60))
    screen.blit(title, title_rect)
    
    y_offset = 120
    
    # Rules
    rules_text = render_text(ui_text['rules'], 'medium', (0, 0, 255))
    screen.blit(rules_text, (50, y_offset))
    y_offset += 50
    
    # Rule details
    rules = [ui_text['rule1'], ui_text['rule2'], ui_text['rule3']]
    for rule in rules:
        rule_text = render_text(rule, 'small', (0, 0, 0))
        screen.blit(rule_text, (70, y_offset))
        y_offset += 35
    
    # Finger mappings
    for mapping in ui_text['finger_mapping']:
        mapping_text = render_text(mapping, 'small', (0, 0, 0))
        screen.blit(mapping_text, (90, y_offset))
        y_offset += 30
    
    y_offset += 20
    
    # Additional instructions
    camera_text = render_text(ui_text['camera_check'], 'small', (255, 100, 0))
    screen.blit(camera_text, (50, y_offset))
    y_offset += 40
    
    start_text = render_text(ui_text['start_quit'], 'small', (0, 0, 0))
    screen.blit(start_text, (50, y_offset))
    y_offset += 30
    
    lang_text = render_text(ui_text['language_change'], 'tiny', (128, 128, 128))
    screen.blit(lang_text, (50, y_offset))
    
    pygame.display.flip()

def main_game():
    """Main game loop"""
    global camera_active
    
    # Language selection
    selected_lang = select_language()
    if selected_lang is None:
        pygame.quit()
        return
    
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
                elif event.key == pygame.K_l:
                    # Change language
                    selected_lang = select_language()
                    if selected_lang is None:
                        camera_active = False
                        pygame.quit()
                        return
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
        progress_text = render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 'medium', (0, 0, 0))
        screen.blit(progress_text, (20, 20))
        
        # Show score
        score_text = render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0))
        screen.blit(score_text, (650, 20))
        
        # Language indicator
        lang_indicator = render_text(f"Language: {current_language.title()}", 'tiny', (128, 128, 128))
        screen.blit(lang_indicator, (20, 660))
        
        # Show the word in the target color
        word_surface = render_text(word_name, 'large', correct_color_rgb)
        word_rect = word_surface.get_rect(center=(450, 200))
        screen.blit(word_surface, word_rect)
        
        # Show instruction
        instruction = render_text(ui_text['instruction'], 'medium', (0, 0, 0))
        instruction_rect = instruction.get_rect(center=(450, 320))
        screen.blit(instruction, instruction_rect)
        
        # Draw color options
        draw_color_options()
        
        pygame.display.flip()
        
        # Wait for gesture input
        start_time = time.time()
        answered = False
        
        while not answered and time.time() - start_time < 5.0:
            gesture_input = get_gesture_input()
            
            if gesture_input is not None:
                if gesture_input == correct_color_index:
                    score += 1
                    feedback_text = render_text(ui_text['correct'], 'large', (0, 255, 0))
                else:
                    feedback_text = render_text(ui_text['wrong'], 'large', (255, 0, 0))
                
                screen.fill((255, 255, 255))
                feedback_rect = feedback_text.get_rect(center=(450, 350))
                screen.blit(feedback_text, feedback_rect)
                pygame.display.flip()
                time.sleep(1)
                answered = True
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    camera_active = False
                    pygame.quit()
                    return
            
            clock.tick(60)
        
        if not answered:
            screen.fill((255, 255, 255))
            timeout_text = render_text(ui_text['timeout'], 'large', (255, 165, 0))
            timeout_rect = timeout_text.get_rect(center=(450, 350))
            screen.blit(timeout_text, timeout_rect)
            pygame.display.flip()
            time.sleep(1)
        
        question_count += 1
    
    # Show final score
    screen.fill((255, 255, 255))
    final_score_text = render_text(f"{ui_text['final_score']}: {score}/{total_questions}", 'large', (0, 100, 0))
    final_rect = final_score_text.get_rect(center=(450, 250))
    screen.blit(final_score_text, final_rect)
    
    percentage = (score / total_questions) * 100
    percentage_text = render_text(f"{ui_text['accuracy']}: {percentage:.1f}%", 'medium', (0, 0, 0))
    perc_rect = percentage_text.get_rect(center=(450, 300))
    screen.blit(percentage_text, perc_rect)
    
    restart_text = render_text(ui_text['restart'], 'small', (0, 0, 0))
    restart_rect = restart_text.get_rect(center=(450, 400))
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