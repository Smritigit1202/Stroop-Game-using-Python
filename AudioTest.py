# -*- coding: utf-8 -*-

import pygame
import random
import speech_recognition as sr
import threading
import time
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Stroop Effect Game - Voice Controlled")
clock = pygame.time.Clock()

# Language setup (same as original, no changes needed)
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
            'rule3': '3. Speak the color name:',
            'finger_mapping': [
                '   Say "Red"', '   Say "Green"', '   Say "Blue"', '   Say "Yellow"', '   Say "Pink"'
            ],
            'camera_check': 'Make sure your microphone is working!',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'question': 'Question',
            'score': 'Score',
            'instruction': 'Say the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit',
            
            'gesture_instruction': 'Say a color name',
            'language_change': 'Press L to change language'
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
            'language_prompt': 'Choose Language / भाषा चुनें',
            'press_1': 'Press 1 for English',
            'press_2': 'Press 2 for Hindi / हिंदी के लिए 2 दबाएं',
            'rules': 'नियम:',
            'rule1': '1. एक शब्द एक रंग में दिखाई जाएगी',
            'rule2': '2. शब्द को नजरअंदाज करें, रंग पर ध्यान दें',
            'rule3': '3. रंग का नाम बोलें:',
            'finger_mapping': [
                '   लाल', 'हरा', 'नीला', 'पीला', 'गुलाबी'
            ],
            'camera_check': 'निश्चित करें कि आपका माइक्रोफोन काम कर रहा है!',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या बाहर निकाले के लिए ESC',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'instruction': 'रंग का नाम बोलें (शब्द नहीं):',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सतीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या बाहर निकाले के लिए ESC',
           
            'gesture_instruction': 'रंग का नाम बोलें',
            'language_change': 'भाषा बदलने के लिए L दबाएं'
        }
    }
}

current_language = 'english'
colors = LANGUAGES[current_language]['colors']
ui_text = LANGUAGES[current_language]['ui']

def load_fonts():
    mangal_font_path = "Mangal.ttf"

    if os.path.exists(mangal_font_path):
        try:
            font_large_hindi = pygame.font.Font(mangal_font_path, 50)
            font_medium_hindi = pygame.font.Font(mangal_font_path, 32)
            font_small_hindi = pygame.font.Font(mangal_font_path, 22)
            font_tiny_hindi = pygame.font.Font(mangal_font_path, 18)
        except:
            font_large_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 50)
            font_medium_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 32)
            font_small_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 22)
            font_tiny_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 18)
    else:
        font_large_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 50)
        font_medium_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 32)
        font_small_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 22)
        font_tiny_hindi = pygame.font.SysFont("mangal,devanagari,noto sans devanagari", 18)

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

# Same setup for fonts and UI...
# Replace get_gesture_input() with:
def get_font(size):
    """Get appropriate font based on current language"""
    return fonts[current_language][size]

def render_text(text, size, color):
    """Render text with appropriate font for current language"""
    font = get_font(size)
    return font.render(text, True, color)

def update_language(lang):
    """Update current language and related variables"""
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[current_language]['colors']
    ui_text = LANGUAGES[current_language]['ui']


def get_voice_input(timeout=5):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language='hi' if current_language == 'hindi' else 'en')
            print(f"You said: {text}")
            spoken = text.strip().lower()
            for i, (name, _) in enumerate(colors):
                if spoken in name.lower():
                    return i
        except Exception as e:
            print("Error recognizing voice:", e)
    return None
# --- Font loading setup ---
fonts = load_fonts()
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
    
    total_width = english_width + hindi_width
    start_x = (900 - total_width) // 2
    
    screen.blit(english_text, (start_x, 180))
    screen.blit(hindi_text, (start_x + english_width, 180))
    
    option1 = fonts['english']['medium'].render("Press 1 for English", True, (0, 0, 0))
    option1_rect = option1.get_rect(center=(450, 300))
    screen.blit(option1, option1_rect)
    
    english_part2 = "Press 2 for Hindi / "
    hindi_part2 = "हिंदी के लिए 2 दबाएं"
    
    english_text2 = fonts['english']['medium'].render(english_part2, True, (0, 0, 0))
    hindi_text2 = fonts['hindi']['medium'].render(hindi_part2, True, (0, 0, 0))
    
    total_width2 = english_text2.get_width() + hindi_text2.get_width()
    start_x2 = (900 - total_width2) // 2
    
    screen.blit(english_text2, (start_x2, 350))
    screen.blit(hindi_text2, (start_x2 + english_text2.get_width(), 350))
    
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
    
    title = render_text(ui_text['title'], 'large', (255, 0, 0))
    title_rect = title.get_rect(center=(450, 60))
    screen.blit(title, title_rect)
    
    y_offset = 120
    rules_text = render_text(ui_text['rules'], 'medium', (0, 0, 255))
    screen.blit(rules_text, (50, y_offset))
    y_offset += 50

    rules = [ui_text['rule1'], ui_text['rule2']]
    for rule in rules:
        rule_text = render_text(rule, 'small', (0, 0, 0))
        screen.blit(rule_text, (70, y_offset))
        y_offset += 35

    audio_instruction = render_text("🎤 Say the COLOR name loudly (not the word on screen)", 'small', (255, 100, 0))
    screen.blit(audio_instruction, (70, y_offset))
    y_offset += 40

    start_text = render_text(ui_text['start_quit'], 'small', (0, 0, 0))
    screen.blit(start_text, (50, y_offset))
    y_offset += 30
    
    lang_text = render_text(ui_text['language_change'], 'tiny', (128, 128, 128))
    screen.blit(lang_text, (50, y_offset))

    pygame.display.flip()


def main_game():
    selected_lang = select_language()
    if selected_lang is None:
        pygame.quit()
        return

    waiting_for_start = True
    while waiting_for_start:
        show_instructions()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting_for_start = False
                elif event.key == pygame.K_l:
                    selected_lang = select_language()
                    if selected_lang is None:
                        pygame.quit()
                        return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        clock.tick(60)

    score = 0
    total_questions = 20
    question_count = 0

    while question_count < total_questions:
        word_name = random.choice(colors)[0]
        correct_color_index = random.randint(0, 4)
        correct_color_name, correct_color_rgb = colors[correct_color_index]

        screen.fill((255, 255, 255))

        progress_text = render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 'medium', (0, 0, 0))
        screen.blit(progress_text, (20, 20))

        score_text = render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0))
        screen.blit(score_text, (650, 20))

        lang_indicator = render_text(f"Language: {current_language.title()}", 'tiny', (128, 128, 128))
        screen.blit(lang_indicator, (20, 660))

        word_surface = render_text(word_name, 'large', correct_color_rgb)
        word_rect = word_surface.get_rect(center=(450, 200))
        screen.blit(word_surface, word_rect)

        instruction = render_text(ui_text['instruction'], 'medium', (0, 0, 0))
        instruction_rect = instruction.get_rect(center=(450, 320))
        screen.blit(instruction, instruction_rect)

        draw_color_options()
        pygame.display.flip()

        start_time = time.time()
        answered = False

        while not answered and time.time() - start_time < 5.0:
            voice_input = get_voice_input()
            if voice_input is not None:
                if voice_input == correct_color_index:
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

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_game()
                    return
                elif event.key == pygame.K_ESCAPE:
                    waiting = False
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main_game()