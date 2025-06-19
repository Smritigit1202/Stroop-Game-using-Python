# -*- coding: utf-8 -*-

import pygame
import random
import cv2
import pytesseract
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
            'rule3': '3. Draw letters to select the color:',
            'finger_mapping': [
                'R = Red', 'G = Green', 'B = Blue', 'Y = Yellow', 'P = Pink'
            ],
            'camera_check': 'Make sure your camera is working!',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'question': 'Question',
            'score': 'Score',
            'instruction': 'Draw letter for the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit'
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
            'rule3': '3. रंग चुनने के लिए अक्षर बनाएं:',
            'finger_mapping': [
                'R = लाल', 'G = हरा', 'B = नीला', 'Y = पीला', 'P = गुलाबी'
            ],
            'camera_check': 'सुनिश्चित करें कि आपका कैमरा काम कर रहा है!',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या ESC दबाएं बाहर निकलने के लिए',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'instruction': 'शब्द नहीं, रंग के लिए अक्षर बनाएं:',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या ESC दबाएं'
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

def detect_letter_from_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    text = pytesseract.image_to_string(gray, config='--psm 8 -c tessedit_char_whitelist=RGBYP')
    letter = text.strip().upper()
    return letter[0] if letter else None

def detect_letter():
    global detected_letter, camera_active
    cap = cv2.VideoCapture(0)
    if not cap.isOpened(): return
    stable_letter = None
    stable_frames = 0
    required_stable_frames = 10
    while camera_active:
        ret, frame = cap.read()
        if not ret: continue
        frame = cv2.flip(frame, 1)
        letter = detect_letter_from_frame(frame)
        if letter == stable_letter:
            stable_frames += 1
        else:
            stable_letter = letter
            stable_frames = 0
        if stable_frames >= required_stable_frames:
            with gesture_lock:
                detected_letter = letter
        cv2.putText(frame, f"Letter: {letter}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Letter Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
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
    y = 60
    screen.blit(render_text(ui_text['title'], 'large', (255, 0, 0)), (200, y))
    y += 80
    for key in ['rules', 'rule1', 'rule2', 'rule3']:
        screen.blit(render_text(ui_text[key], 'medium', (0, 0, 0)), (50, y))
        y += 40
    for line in ui_text['finger_mapping']:
        screen.blit(render_text(line, 'small', (0, 0, 0)), (70, y))
        y += 30
    screen.blit(render_text(ui_text['camera_check'], 'small', (255, 100, 0)), (50, y))
    y += 40
    screen.blit(render_text(ui_text['start_quit'], 'small', (0, 0, 0)), (50, y))
    pygame.display.flip()

def main_game():
    global camera_active
    selected_lang = select_language()
    if selected_lang is None:
        pygame.quit()
        return

    letter_thread = threading.Thread(target=detect_letter, daemon=True)
    letter_thread.start()

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

    score = 0
    total_questions = 10

    for question_count in range(total_questions):
        word_name = random.choice(colors)[0]
        correct_color_index = random.randint(0, 4)
        correct_color_name, correct_color_rgb = colors[correct_color_index]

        screen.fill((255, 255, 255))
        screen.blit(render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 'medium', (0, 0, 0)), (20, 20))
        screen.blit(render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0)), (650, 20))
        word_surface = render_text(word_name, 'large', correct_color_rgb)
        screen.blit(word_surface, word_surface.get_rect(center=(450, 250)))
        screen.blit(render_text(ui_text['instruction'], 'medium', (0, 0, 0)), (100, 350))
        pygame.display.flip()

        start_time = time.time()
        answered = False

        while not answered and time.time() - start_time < 5.0:
            with gesture_lock:
                letter = detected_letter
            if letter and letter == correct_color_name[0].upper():
                score += 1
                feedback = render_text(ui_text['correct'], 'large', (0, 255, 0))
                answered = True
            elif letter:
                feedback = render_text(ui_text['wrong'], 'large', (255, 0, 0))
                answered = True
            if answered:
                screen.fill((255, 255, 255))
                screen.blit(feedback, feedback.get_rect(center=(450, 350)))
                pygame.display.flip()
                time.sleep(1)
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    camera_active = False
                    pygame.quit()
                    return
            clock.tick(60)

        if not answered:
            screen.fill((255, 255, 255))
            timeout_text = render_text(ui_text['timeout'], 'large', (255, 165, 0))
            screen.blit(timeout_text, timeout_text.get_rect(center=(450, 350)))
            pygame.display.flip()
            time.sleep(1)

    screen.fill((255, 255, 255))
    screen.blit(render_text(f"{ui_text['final_score']}: {score}/{total_questions}", 'large', (0, 100, 0)), (200, 250))
    perc = (score / total_questions) * 100
    screen.blit(render_text(f"{ui_text['accuracy']}: {perc:.1f}%", 'medium', (0, 0, 0)), (300, 320))
    screen.blit(render_text(ui_text['restart'], 'small', (0, 0, 0)), (200, 400))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_game()
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

if __name__ == "__main__":
    main_game()