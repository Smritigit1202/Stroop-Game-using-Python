# -*- coding: utf-8 -*-

import pygame
import random
import cv2
import numpy as np
import threading
import time
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Stroop Effect Game - Letter Controlled")
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
            'rules': 'Rules:',
            'rule1': '1. A word will appear in a COLOR',
            'rule2': '2. Ignore the WORD, focus on the COLOR',
            'rule3': '3. Draw letters clearly on paper to select the color:',
            'finger_mapping': [
                'R = Red', 'G = Green', 'B = Blue', 'Y = Yellow', 'P = Pink'
            ],
            'camera_check': 'Make sure your camera is working and you have paper ready!',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'question': 'Question',
            'score': 'Score',
            'instruction': 'Draw letter for the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit',
            'drawing_tips': 'Tips: Draw letters BIG and CLEAR on white paper'
        }
    },
    'hindi': {
        'colors': [
            ("लाल", (255, 0, 0)),
            ("हरा", (0, 255, 0)),
            ("नीला", (0, 0, 255)),
            ("पीला", (255, 255, 0)),
            ("गुलाबी", (255, 20, 147))
        ],
        'ui': {
            'title': 'स्ट्रूप प्रभाव खेल',
            'rules': 'नियम:',
            'rule1': '1. एक शब्द एक रंग में दिखाई देगा',
            'rule2': '2. शब्द को नज़रअंदाज करें, रंग पर ध्यान दें',
            'rule3': '3. रंग चुनने के लिए कागज़ पर अक्षर स्पष्ट रूप से बनाएं:',
            'finger_mapping': [
                'R = लाल', 'G = हरा', 'B = नीला', 'Y = पीला', 'P = गुलाबी'
            ],
            'camera_check': 'सुनिश्चित करें कि आपका कैमरा काम कर रहा है और कागज़ तैयार है!',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या ESC दबाएं बाहर निकलने के लिए',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'instruction': 'शब्द नहीं, रंग के लिए अक्षर बनाएं:',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या ESC दबाएं',
            'drawing_tips': 'सुझाव: सफेद कागज़ पर बड़े और स्पष्ट अक्षर बनाएं'
        }
    }
}

current_language = 'english'
colors = LANGUAGES[current_language]['colors']
ui_text = LANGUAGES[current_language]['ui']

fonts = {
    'large': pygame.font.SysFont("arial", 50),
    'medium': pygame.font.SysFont("arial", 32),
    'small': pygame.font.SysFont("arial", 22),
    'tiny': pygame.font.SysFont("arial", 18)
}

def render_text(text, size, color):
    return fonts[size].render(text, True, color)

detected_letter = None
gesture_lock = threading.Lock()
camera_active = True

def preprocess_frame(frame):
    """Preprocess frame for better letter detection"""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive threshold to handle different lighting conditions
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Apply morphological operations to clean up the image
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    
    return cleaned

def analyze_contour_for_letter(contour):
    """Analyze contour shape to determine which letter it might be"""
    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    
    # Filter out very small contours - made more lenient
    if w < 20 or h < 20:
        return None
    
    # Calculate aspect ratio
    aspect_ratio = float(w) / h
    
    # Calculate contour area and perimeter
    area = cv2.contourArea(contour)
    perimeter = cv2.arcLength(contour, True)
    
    if perimeter == 0:
        return None
    
    # Calculate circularity (how close to a circle)
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    
    # Get convex hull
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    
    # Calculate solidity (contour area / convex hull area)
    solidity = float(area) / hull_area if hull_area > 0 else 0
    
    # Approximate contour to polygon
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Debug print for testing
    print(f"Contour analysis - Area: {area:.0f}, Aspect: {aspect_ratio:.2f}, Solidity: {solidity:.2f}, Vertices: {len(approx)}")
    
    # Simplified letter classification - more permissive
    # Just detect any reasonable letter-like shape first
    
    # Basic shape filtering
    if area < 200:  # Very small shapes
        return None
    
    # Very wide shapes (likely not letters)
    if aspect_ratio > 2.0:
        return None
    
    # Very flat shapes (likely not letters)  
    if aspect_ratio < 0.2:
        return None
    
    # For now, let's classify based on aspect ratio and return the most likely letters
    # This is a simplified approach for testing
    
    if 0.3 < aspect_ratio < 0.7:  # Tall letters
        if len(approx) < 8:  # Simple shapes
            return 'R'  # Default to R for tall simple shapes
        else:
            return 'P'  # More complex tall shapes
    elif 0.7 < aspect_ratio < 1.3:  # Square-ish letters
        return 'G'  # Square-ish shapes
    elif aspect_ratio > 1.3:  # Wide letters
        return 'Y'  # Wide shapes
    else:
        return 'B'  # Default fallback
    
    return None

def detect_letter_from_frame(frame):
    """Detect hand-drawn letters using computer vision"""
    processed = preprocess_frame(frame)
    
    # Find contours
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Found {len(contours)} contours")
    
    # Filter and analyze contours
    detected_letters = []
    
    for i, contour in enumerate(contours):
        # Filter by area (remove very small contours)
        area = cv2.contourArea(contour)
        print(f"Contour {i}: area = {area}")
        
        if area < 100:  # Reduced minimum area threshold
            continue
        
        letter = analyze_contour_for_letter(contour)
        if letter:
            detected_letters.append(letter)
            print(f"Contour {i} classified as: {letter}")
    
    print(f"Detected letters: {detected_letters}")
    
    # Return the most common detected letter, or None
    if detected_letters:
        most_common = max(set(detected_letters), key=detected_letters.count)
        print(f"Most common letter: {most_common}")
        return most_common
    
    return None

def detect_letter():
    """Main letter detection function running in separate thread"""
    global detected_letter, camera_active
    
    print("Starting camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open camera!")
        print("Make sure no other application is using the camera")
        return
    
    print("Camera started successfully!")
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    stable_letter = None
    stable_frames = 0
    required_stable_frames = 5  # Reduced for testing
    
    while camera_active:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera")
            continue
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Show both original and processed frames
        # Original frame
        original_display = frame.copy()
        
        # Detect letter
        letter = detect_letter_from_frame(frame)
        
        # Stability check
        if letter == stable_letter and letter is not None:
            stable_frames += 1
        else:
            stable_letter = letter
            stable_frames = 0
        
        # Update detected letter if stable
        if stable_frames >= required_stable_frames:
            with gesture_lock:
                detected_letter = letter
                print(f"Letter detected and confirmed: {letter}")
        
        # Display processed frame with detection info
        processed = preprocess_frame(frame)
        
        # Create side-by-side display
        # Resize frames for side-by-side display
        original_small = cv2.resize(original_display, (320, 240))
        processed_small = cv2.resize(processed, (320, 240))
        processed_color = cv2.cvtColor(processed_small, cv2.COLOR_GRAY2BGR)
        
        # Combine frames horizontally
        combined = np.hstack((original_small, processed_color))
        
        # Add detection info to display
        current_detected = None
        with gesture_lock:
            current_detected = detected_letter
        
        status_text = f"Instant: {letter if letter else 'None'}"
        stable_text = f"Confirmed: {current_detected if current_detected else 'None'}"
        
        cv2.putText(combined, "ORIGINAL", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, "PROCESSED", (330, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(combined, status_text, (10, 260), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(combined, stable_text, (10, 285), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(combined, "Draw BIG letters: R, G, B, Y, P", (10, 310), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(combined, "Use BLACK pen on WHITE paper", (10, 330), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(combined, "Press 'q' to close", (450, 330), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Show the window (make sure it's visible)
        cv2.namedWindow("Letter Recognition", cv2.WINDOW_NORMAL)
        cv2.imshow("Letter Recognition", combined)
        
        # Force window to front (platform dependent)
        try:
            cv2.setWindowProperty("Letter Recognition", cv2.WND_PROP_TOPMOST, 1)
        except:
            pass
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    print("Closing camera...")
    cap.release()
    cv2.destroyAllWindows()

def update_language(lang):
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[lang]['colors']
    ui_text = LANGUAGES[lang]['ui']

def select_language():
    selecting = True
    while selecting:
        screen.fill((255, 255, 255))
        screen.blit(render_text("Press 1 for English", 'medium', (0, 0, 0)), (250, 250))
        screen.blit(render_text("Press 2 for Hindi / हिंदी के लिए 2 दबाएं", 'medium', (0, 0, 0)), (130, 300))
        pygame.display.flip()
        
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

def show_instructions():
    screen.fill((255, 255, 255))
    y = 40
    
    # Title
    screen.blit(render_text(ui_text['title'], 'large', (255, 0, 0)), (200, y))
    y += 80
    
    # Rules
    for key in ['rules', 'rule1', 'rule2', 'rule3']:
        screen.blit(render_text(ui_text[key], 'medium', (0, 0, 0)), (50, y))
        y += 40
    
    # Letter mappings
    for line in ui_text['finger_mapping']:
        screen.blit(render_text(line, 'small', (0, 0, 0)), (70, y))
        y += 30
    
    # Important instructions
    screen.blit(render_text(ui_text['drawing_tips'], 'small', (255, 100, 0)), (50, y))
    y += 30
    screen.blit(render_text(ui_text['camera_check'], 'small', (255, 100, 0)), (50, y))
    y += 40
    screen.blit(render_text(ui_text['start_quit'], 'small', (0, 0, 0)), (50, y))
    
    pygame.display.flip()

def main_game():
    global camera_active, detected_letter
    
    # Language selection
    selected_lang = select_language()
    if selected_lang is None:
        pygame.quit()
        return

    # Start camera thread
    camera_active = True
    letter_thread = threading.Thread(target=detect_letter, daemon=True)
    letter_thread.start()
    
    # Wait for user to start the game
    while True:
        show_instructions()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                camera_active = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    break
                elif event.key == pygame.K_ESCAPE:
                    camera_active = False
                    pygame.quit()
                    return
        else:
            clock.tick(60)
            continue
        break

    # Game variables
    score = 0
    total_questions = 10

    # Main game loop
    for question_count in range(total_questions):
        # Reset detected letter for new question
        with gesture_lock:
            detected_letter = None
        
        # Choose random word and color
        word_name = random.choice(colors)[0]
        correct_color_index = random.randint(0, 4)
        correct_color_name, correct_color_rgb = colors[correct_color_index]
        
        # Determine correct answer letter
        correct_letter = correct_color_name[0].upper()
        if current_language == 'english':
            # Map color names to letters
            color_to_letter = {
                'Red': 'R', 'Green': 'G', 'Blue': 'B', 
                'Yellow': 'Y', 'Pink': 'P'
            }
            correct_letter = color_to_letter.get(correct_color_name, correct_color_name[0].upper())
        
        # Display question
        screen.fill((255, 255, 255))
        screen.blit(render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 
                               'medium', (0, 0, 0)), (20, 20))
        screen.blit(render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0)), (650, 20))
        
        # Display the word in the color (Stroop effect)
        word_surface = render_text(word_name, 'large', correct_color_rgb)
        word_rect = word_surface.get_rect(center=(450, 250))
        screen.blit(word_surface, word_rect)
        
        # Display instruction
        instruction_surface = render_text(ui_text['instruction'], 'medium', (0, 0, 0))
        screen.blit(instruction_surface, (100, 350))
        
        # Show correct letter needed
        answer_text = f"Draw letter: {correct_letter}"
        screen.blit(render_text(answer_text, 'small', (100, 100, 100)), (100, 400))
        
        pygame.display.flip()

        # Wait for answer or timeout
        start_time = time.time()
        answered = False
        answer_timeout = 8.0  # Increased timeout for hand drawing

        while not answered and time.time() - start_time < answer_timeout:
            # Check for detected letter
            with gesture_lock:
                current_detected = detected_letter
            
            if current_detected and current_detected == correct_letter:
                score += 1
                feedback = render_text(ui_text['correct'], 'large', (0, 255, 0))
                answered = True
            elif current_detected and current_detected in ['R', 'G', 'B', 'Y', 'P']:
                # Wrong letter detected
                feedback = render_text(ui_text['wrong'], 'large', (255, 0, 0))
                answered = True
            
            # Show feedback if answered
            if answered:
                screen.fill((255, 255, 255))
                feedback_rect = feedback.get_rect(center=(450, 350))
                screen.blit(feedback, feedback_rect)
                pygame.display.flip()
                time.sleep(1.5)
                break
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    camera_active = False
                    pygame.quit()
                    return
            
            clock.tick(60)

        # Handle timeout
        if not answered:
            screen.fill((255, 255, 255))
            timeout_text = render_text(ui_text['timeout'], 'large', (255, 165, 0))
            timeout_rect = timeout_text.get_rect(center=(450, 350))
            screen.blit(timeout_text, timeout_rect)
            pygame.display.flip()
            time.sleep(1.5)

    # Show final results
    screen.fill((255, 255, 255))
    final_score_text = f"{ui_text['final_score']}: {score}/{total_questions}"
    screen.blit(render_text(final_score_text, 'large', (0, 100, 0)), (200, 250))
    
    accuracy_percentage = (score / total_questions) * 100
    accuracy_text = f"{ui_text['accuracy']}: {accuracy_percentage:.1f}%"
    screen.blit(render_text(accuracy_text, 'medium', (0, 0, 0)), (300, 320))
    
    screen.blit(render_text(ui_text['restart'], 'small', (0, 0, 0)), (200, 400))
    pygame.display.flip()

    # Wait for restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                camera_active = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Restart game
                    main_game()
                    return
                elif event.key == pygame.K_ESCAPE:
                    camera_active = False
                    pygame.quit()
                    return

if __name__ == "__main__":
    try:
        main_game()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()