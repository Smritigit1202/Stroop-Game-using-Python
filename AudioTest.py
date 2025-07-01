# -*- coding: utf-8 -*-
import pygame
import random
import speech_recognition as sr
import time
import threading
from queue import Queue
import os
import sys

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Stroop Effect Game - Voice Controlled")
clock = pygame.time.Clock()

# Languages and UI text with phonetic alternatives for Hindi
LANGUAGES = {
    'english': {
        'colors': [("red", (255, 0, 0)), ("green", (0, 255, 0)), ("blue", (0, 0, 255)),
                   ("yellow", (255, 255, 0)), ("pink", (255, 20, 147))],
        'ui': {
            'title': 'STROOP EFFECT GAME',
            'rules': 'Rules:',
            'rule1': '1. A word will appear in a COLOR',
            'rule2': '2. Ignore the WORD, focus on the COLOR',
            'instruction': 'Say the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'language_change': 'Press L to change language',
            'question': 'Question',
            'score': 'Score',
            'listening': 'Listening... Speak now!',
            'mic_error': 'Microphone error - check connection',
            'audio_test': 'Press T to test microphone'
        }
    },
    'hindi': {
        'colors': [
            ("लाल", (255, 0, 0), ["लाल", "laal", "lal", "red", "राल"]), 
            ("हरा", (0, 255, 0), ["हरा", "hara", "green", "हरी", "हरे"]), 
            ("नीला", (0, 0, 255), ["नीला", "neela", "nila", "blue", "नील", "नीली"]),
            ("पीला", (255, 255, 0), ["पीला", "peela", "pila", "yellow", "पील", "पीली"]), 
            ("गुलाबी", (255, 20, 147), ["गुलाबी", "gulabi", "pink", "गुलाब", "गुलाबे"])
        ],
        'ui': {
            'title': 'स्ट्रूप प्रभाव खेल',
            'rules': 'नियम:',
            'rule1': '1. एक शब्द एक रंग में दिखाई जाएगी',
            'rule2': '2. शब्द को नजरअंदाज करें, रंग पर ध्यान दें',
            'instruction': 'रंग का नाम बोलें (शब्द नहीं):',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या ESC दबाएं',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या बाहर निकलने के लिए ESC',
            'language_change': 'भाषा बदलने के लिए L दबाएं',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'listening': 'सुन रहे हैं... अब बोलें!',
            'mic_error': 'माइक्रोफोन त्रुटि - कनेक्शन जांचें',
            'audio_test': 'माइक्रोफोन परीक्षण के लिए T दबाएं'
        }
    }
}

# Global state
current_language = 'english'
colors = LANGUAGES[current_language]['colors']
ui_text = LANGUAGES[current_language]['ui']
language_stats = {
    'english': {'score': 0, 'times': [], 'played': False},
    'hindi': {'score': 0, 'times': [], 'played': False}
}

# Audio recognition setup
recognizer = sr.Recognizer()
microphone = None

def initialize_microphone():
    """Initialize microphone with error handling"""
    global microphone
    try:
        microphone = sr.Microphone()
        print("Calibrating microphone...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Microphone calibrated successfully!")
        return True
    except Exception as e:
        print(f"Microphone initialization failed: {e}")
        return False

# Font loading with Mangal support
def load_fonts():
    fonts = {}
    
    # Try to load Mangal font for Hindi
    mangal_paths = [
        "Mangal.ttf",
        "./Mangal.ttf",
        "fonts/Mangal.ttf",
        "C:/Windows/Fonts/mangal.ttf",
        "/System/Library/Fonts/Mangal.ttf",
        "/usr/share/fonts/truetype/mangal/Mangal.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf"
    ]
    
    mangal_font = None
    for path in mangal_paths:
        if os.path.exists(path):
            try:
                # Test if the font can be loaded
                test_font = pygame.font.Font(path, 24)
                mangal_font = path
                print(f"Found Mangal font at: {path}")
                break
            except Exception as e:
                print(f"Failed to load font from {path}: {e}")
                continue
    
    if mangal_font:
        try:
            fonts['hindi_large'] = pygame.font.Font(mangal_font, 48)
            fonts['hindi_medium'] = pygame.font.Font(mangal_font, 32)
            fonts['hindi_small'] = pygame.font.Font(mangal_font, 24)
            print("Mangal fonts loaded successfully!")
        except Exception as e:
            print(f"Failed to create Mangal fonts: {e}")
            mangal_font = None
    
    # Fallback fonts
    if not mangal_font:
        print("Mangal font not found, using system fonts...")
        # Try system fonts that might support Hindi
        hindi_fonts = ["Arial Unicode MS", "Noto Sans Devanagari", "Sanskrit 2003", "Arial", "DejaVu Sans"]
        for font_name in hindi_fonts:
            try:
                fonts['hindi_large'] = pygame.font.SysFont(font_name, 48)
                fonts['hindi_medium'] = pygame.font.SysFont(font_name, 32)
                fonts['hindi_small'] = pygame.font.SysFont(font_name, 24)
                print(f"Using {font_name} for Hindi text")
                break
            except:
                continue
        
        # If still no Hindi fonts, use default
        if 'hindi_large' not in fonts:
            fonts['hindi_large'] = pygame.font.Font(None, 48)
            fonts['hindi_medium'] = pygame.font.Font(None, 32)
            fonts['hindi_small'] = pygame.font.Font(None, 24)
            print("Using default font for Hindi (may not display correctly)")
    
    # English fonts
    fonts['english_large'] = pygame.font.SysFont("arial", 48)
    fonts['english_medium'] = pygame.font.SysFont("arial", 32)
    fonts['english_small'] = pygame.font.SysFont("arial", 24)
    
    return fonts

fonts = load_fonts()

# Helpers
def render_text(text, size, color):
    """Render text with appropriate font for current language"""
    font_key = f"{current_language}_{size}"
    if font_key in fonts:
        try:
            return fonts[font_key].render(text, True, color)
        except Exception as e:
            print(f"Font rendering error: {e}")
            # Fallback to English font
            return fonts[f"english_{size}"].render(text, True, color)
    else:
        # Fallback to English font
        return fonts[f"english_{size}"].render(text, True, color)

def update_language(lang):
    """Update current language and reload color/UI data"""
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[lang]['colors']
    ui_text = LANGUAGES[lang]['ui']

def test_microphone():
    """Test microphone functionality"""
    if not microphone:
        screen.fill((255, 255, 255))
        screen.blit(render_text("Microphone not initialized", 'medium', (255, 0, 0)), (200, 300))
        screen.blit(render_text("Press any key to continue", 'small', (100, 100, 100)), (300, 350))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
        return False
    
    print("Testing microphone...")
    screen.fill((255, 255, 255))
    screen.blit(render_text("Testing microphone...", 'medium', (0, 0, 0)), (300, 200))
    screen.blit(render_text("Say something!", 'medium', (0, 0, 255)), (350, 250))
    pygame.display.flip()
    
    try:
        with microphone as source:
            print("Listening for test...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            # Try multiple recognition services
            recognized_text = None
            
            # Try Google first
            try:
                language_code = 'hi-IN' if current_language == 'hindi' else 'en-US'
                recognized_text = recognizer.recognize_google(audio, language=language_code)
                print(f"Google recognition: {recognized_text}")
            except:
                print("Google recognition failed")
            
            # Try with alternative language codes
            if not recognized_text:
                try:
                    alt_language = 'en-IN' if current_language == 'hindi' else 'en-US'
                    recognized_text = recognizer.recognize_google(audio, language=alt_language)
                    print(f"Alternative Google recognition: {recognized_text}")
                except:
                    print("Alternative Google recognition failed")
            
            if recognized_text:
                screen.fill((255, 255, 255))
                screen.blit(render_text("Microphone working!", 'medium', (0, 200, 0)), (300, 200))
                screen.blit(render_text(f"You said: {recognized_text}", 'small', (0, 0, 0)), (150, 250))
                screen.blit(render_text("Press any key to continue", 'small', (100, 100, 100)), (300, 300))
                pygame.display.flip()
                
                # Wait for key press
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                        elif event.type == pygame.KEYDOWN:
                            waiting = False
                return True
            else:
                raise Exception("No recognition service worked")
            
    except sr.WaitTimeoutError:
        print("No speech detected during test")
        screen.fill((255, 255, 255))
        screen.blit(render_text("No speech detected", 'medium', (255, 0, 0)), (300, 200))
        screen.blit(render_text("Check microphone connection", 'small', (0, 0, 0)), (250, 250))
        screen.blit(render_text("Press any key to continue", 'small', (100, 100, 100)), (300, 300))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
        return False
    except Exception as e:
        print(f"Microphone test failed: {e}")
        screen.fill((255, 255, 255))
        screen.blit(render_text("Microphone test failed", 'medium', (255, 0, 0)), (250, 200))
        screen.blit(render_text("Check microphone permissions", 'small', (0, 0, 0)), (200, 250))
        screen.blit(render_text("Press any key to continue", 'small', (100, 100, 100)), (300, 300))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    waiting = False
        return False

def match_color_hindi(spoken_text, colors):
    """Enhanced Hindi color matching with phonetic alternatives"""
    spoken_lower = spoken_text.lower().strip()
    
    for i, color_data in enumerate(colors):
        if len(color_data) >= 3:  # Has phonetic alternatives
            color_name = color_data[0]
            alternatives = color_data[2]
            
            # Check all alternatives
            for alt in alternatives:
                if alt.lower() in spoken_lower or spoken_lower in alt.lower():
                    print(f"Matched '{spoken_text}' with '{color_name}' using alternative '{alt}'")
                    return i
    
    return None

def match_color_english(spoken_text, colors):
    """English color matching"""
    spoken_lower = spoken_text.lower().strip()
    
    for i, color_data in enumerate(colors):
        color_name = color_data[0]
        if color_name.lower() in spoken_lower or spoken_lower in color_name.lower():
            print(f"Matched '{spoken_text}' with '{color_name}'")
            return i
    
    return None

def get_voice_input_threaded(result_queue, stop_event):
    """Get voice input in a separate thread with better Hindi support"""
    if not microphone:
        result_queue.put(None)
        return
        
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening for voice input...")
            
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=4)
            
            if stop_event.is_set():
                return
            
            recognized_text = None
            
            # Try multiple recognition services for better Hindi support
            if current_language == 'hindi':
                # Try Google with Hindi
                try:
                    recognized_text = recognizer.recognize_google(audio, language='hi-IN')
                    print(f"Google Hindi recognition: {recognized_text}")
                except Exception as e:
                    print(f"Google Hindi failed: {e}")
                
                # Try Google with English as fallback (for Hindi speakers saying English words)
                if not recognized_text:
                    try:
                        recognized_text = recognizer.recognize_google(audio, language='en-IN')
                        print(f"Google English-India recognition: {recognized_text}")
                    except Exception as e:
                        print(f"Google English-India failed: {e}")
                
                # Try with US English as last resort
                if not recognized_text:
                    try:
                        recognized_text = recognizer.recognize_google(audio, language='en-US')
                        print(f"Google US English recognition: {recognized_text}")
                    except Exception as e:
                        print(f"Google US English failed: {e}")
                
                # Match with Hindi colors
                if recognized_text:
                    color_index = match_color_hindi(recognized_text, colors)
                    if color_index is not None:
                        result_queue.put(color_index)
                        return
            else:
                # English recognition
                try:
                    recognized_text = recognizer.recognize_google(audio, language='en-US')
                    print(f"English recognition: {recognized_text}")
                    
                    color_index = match_color_english(recognized_text, colors)
                    if color_index is not None:
                        result_queue.put(color_index)
                        return
                except Exception as e:
                    print(f"English recognition failed: {e}")
            
            # No match found
            print(f"No color match found for: {recognized_text}")
            result_queue.put(-1)
            
    except sr.WaitTimeoutError:
        print("No speech detected")
        result_queue.put(None)
    except sr.UnknownValueError:
        print("Could not understand audio")
        result_queue.put(-1)
    except sr.RequestError as e:
        print(f"Speech recognition error: {e}")
        result_queue.put(None)
    except Exception as e:
        print(f"Unexpected error in voice recognition: {e}")
        result_queue.put(None)

def get_voice_input(timeout=6):
    """Get voice input with better error handling"""
    result_queue = Queue()
    stop_event = threading.Event()
    
    voice_thread = threading.Thread(
        target=get_voice_input_threaded, 
        args=(result_queue, stop_event)
    )
    voice_thread.daemon = True
    voice_thread.start()
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not result_queue.empty():
            result = result_queue.get()
            stop_event.set()
            return result
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
                return None
        
        time.sleep(0.1)
    
    stop_event.set()
    return None

def get_color_name_and_rgb(color_data):
    """Extract color name and RGB from color data structure"""
    if current_language == 'hindi' and len(color_data) >= 3:
        return color_data[0], color_data[1]  # Hindi name, RGB
    else:
        return color_data[0], color_data[1]  # English name, RGB

# Comparison screen
def compare_language_stats():
    screen.fill((255, 255, 255))
    title = render_text("Comparison of Languages", 'large', (0, 0, 0))
    screen.blit(title, title.get_rect(center=(450, 60)))

    for idx, lang in enumerate(['english', 'hindi']):
        y_offset = 150 + idx * 200
        lang_title = render_text(f"{lang.title()}:", 'medium', (0, 0, 255))
        screen.blit(lang_title, (100, y_offset))

        if language_stats[lang]['played']:
            score = language_stats[lang]['score']
            times = language_stats[lang]['times']
            if times:
                avg_time = sum(times) / len(times)
                details = render_text(f"Score: {score}/10, Avg Time: {avg_time:.2f}s", 'small', (0, 0, 0))
            else:
                details = render_text(f"Score: {score}/10, No time data", 'small', (0, 0, 0))
        else:
            details = render_text("Not played yet", 'small', (128, 128, 128))
        screen.blit(details, (120, y_offset + 40))

    # Determine better language
    e, h = language_stats['english'], language_stats['hindi']
    if e['played'] and h['played']:
        if e['times'] and h['times']:
            avg_e = sum(e['times']) / len(e['times'])
            avg_h = sum(h['times']) / len(h['times'])
            winner = "English" if avg_e < avg_h else ("Hindi" if avg_h < avg_e else "Both same")
            result = render_text(f"Better Response Time: {winner}", 'medium', (0, 150, 0))
            screen.blit(result, (100, 500))
        
        score_winner = "English" if e['score'] > h['score'] else ("Hindi" if h['score'] > e['score'] else "Both same")
        score_result = render_text(f"Better Score: {score_winner}", 'medium', (0, 0, 150))
        screen.blit(score_result, (100, 530))

    prompt = render_text("Press SPACE to return", 'small', (100, 100, 100))
    screen.blit(prompt, (100, 640))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        clock.tick(60)

# Language selection screen
def select_language():
    screen.fill((255, 255, 255))
    screen.blit(render_text("Choose Language / भाषा चुनें", 'large', (0, 0, 200)), (200, 120))
    screen.blit(render_text("Press 1 for English", 'medium', (0, 0, 0)), (250, 200))
    screen.blit(render_text("Press 2 for Hindi / हिंदी के लिए 2 दबाएं", 'medium', (0, 0, 0)), (150, 250))
    screen.blit(render_text("Press 3 to Compare Results", 'medium', (0, 0, 0)), (250, 300))
    screen.blit(render_text("Press T to Test Microphone", 'medium', (200, 0, 0)), (250, 350))
    screen.blit(render_text("Press ESC to Quit", 'medium', (100, 100, 100)), (250, 400))
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
                elif event.key == pygame.K_3:
                    compare_language_stats()
                elif event.key == pygame.K_t:
                    test_microphone()
                elif event.key == pygame.K_ESCAPE:
                    return None
        clock.tick(60)

# Instructions screen
def show_instructions():
    screen.fill((255, 255, 255))
    screen.blit(render_text(ui_text['title'], 'large', (255, 0, 0)), (200, 60))
    screen.blit(render_text(ui_text['rules'], 'medium', (0, 0, 255)), (70, 130))
    screen.blit(render_text(ui_text['rule1'], 'small', (0, 0, 0)), (90, 180))
    screen.blit(render_text(ui_text['rule2'], 'small', (0, 0, 0)), (90, 210))
    screen.blit(render_text(ui_text['start_quit'], 'small', (0, 0, 0)), (90, 260))
    screen.blit(render_text(ui_text['language_change'], 'small', (100, 100, 100)), (90, 290))
    screen.blit(render_text(ui_text['audio_test'], 'small', (200, 0, 0)), (90, 320))
    
    # Show color examples for current language
    y_start = 380
    example_text = "Colors to say:" if current_language == 'english' else "बोलने वाले रंग:"
    screen.blit(render_text(example_text, 'small', (0, 0, 100)), (90, y_start))
    
    for i, color_data in enumerate(colors):
        color_name, color_rgb = get_color_name_and_rgb(color_data)
        color_surface = render_text(color_name, 'small', color_rgb)
        screen.blit(color_surface, (90 + (i * 120), y_start + 30))
    
    pygame.display.flip()

# Main game logic
def main_game():
    # Initialize microphone first
    if not initialize_microphone():
        screen.fill((255, 255, 255))
        screen.blit(render_text("Microphone initialization failed!", 'large', (255, 0, 0)), (150, 300))
        screen.blit(render_text("Please check your microphone and try again", 'medium', (0, 0, 0)), (150, 350))
        screen.blit(render_text("Press any key to exit", 'small', (100, 100, 100)), (350, 400))
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    waiting = False
        pygame.quit()
        return

    selected_lang = select_language()
    if not selected_lang:
        pygame.quit()
        return

    waiting = True
    while waiting:
        show_instructions()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: 
                    waiting = False
                elif event.key == pygame.K_l: 
                    return main_game()
                elif event.key == pygame.K_t:
                    test_microphone()
                elif event.key == pygame.K_ESCAPE: 
                    pygame.quit()
                    return
        clock.tick(60)

    score = 0
    total_questions = 10
    question_count = 0
    language_stats[current_language]['times'] = []

    while question_count < total_questions:
        # Select random word and color
        word_data = random.choice(colors)
        word_name, _ = get_color_name_and_rgb(word_data)
        
        correct_idx = random.randint(0, len(colors) - 1)
        correct_data = colors[correct_idx]
        correct_name, correct_color = get_color_name_and_rgb(correct_data)

        # Display question
        screen.fill((255, 255, 255))
        screen.blit(render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 'medium', (0, 0, 0)), (20, 20))
        screen.blit(render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0)), (650, 20))
        
        # Display the word in the target color
        word_surface = render_text(word_name, 'large', correct_color)
        screen.blit(word_surface, word_surface.get_rect(center=(450, 250)))
        
        # Show listening indicator and color options
        screen.blit(render_text(ui_text['instruction'], 'small', (0, 0, 0)), (250, 350))
        screen.blit(render_text(ui_text['listening'], 'small', (0, 200, 0)), (300, 400))
        
        # Show color options
        options_text = "Options:" if current_language == 'english' else "विकल्प:"
        screen.blit(render_text(options_text, 'small', (100, 100, 100)), (50, 450))
        for i, color_data in enumerate(colors):
            option_name, option_color = get_color_name_and_rgb(color_data)
            option_surface = render_text(option_name, 'small', option_color)
            screen.blit(option_surface, (50 + (i * 120), 480))
        
        pygame.display.flip()

        start_time = time.time()
        result = get_voice_input(timeout=7)
        
        if result is not None and result >= 0:
            # Valid response received
            time_taken = time.time() - start_time
            language_stats[current_language]['times'].append(time_taken)
            
            correct = (result == correct_idx)
            if correct:
                score += 1
            
            # Show result
            result_text = ui_text['correct'] if correct else ui_text['wrong']
            result_color = (0, 200, 0) if correct else (200, 0, 0)
            
            screen.fill((255, 255, 255))
            screen.blit(render_text(result_text, 'large', result_color), (350, 300))
            screen.blit(render_text(f"Time: {time_taken:.2f}s", 'medium', (0, 0, 0)), (350, 350))
            
            # Show what was expected vs what was said
            expected_name, _ = get_color_name_and_rgb(colors[correct_idx])
            said_name, _ = get_color_name_and_rgb(colors[result]) if result < len(colors) else ("Unknown", (0, 0, 0))
            
            expected_text = f"Expected: {expected_name}"
            said_text = f"You said: {said_name}"
            screen.blit(render_text(expected_text, 'small', (0, 0, 0)), (300, 400))
            screen.blit(render_text(said_text, 'small', (0, 0, 0)), (300, 430))
            
            pygame.display.flip()
            time.sleep(2)
            
        else:
            # Timeout or no response
            screen.fill((255, 255, 255))
            screen.blit(render_text(ui_text['timeout'], 'large', (200, 0, 0)), (350, 300))
            pygame.display.flip()
            time.sleep(2)

        question_count += 1

    # Update score and mark language as played
    language_stats[current_language]['score'] = score
    language_stats[current_language]['played'] = True

    # Show final score
    screen.fill((255, 255, 255))
    screen.blit(render_text(ui_text['final_score'], 'large', (0, 0, 255)), (300, 200))
    screen.blit(render_text(f"{ui_text['score']}: {score}/{total_questions}", 'medium', (0, 0, 0)), (320, 270))

    if language_stats[current_language]['times']:
        avg_time = sum(language_stats[current_language]['times']) / len(language_stats[current_language]['times'])
        screen.blit(render_text(f"{ui_text['accuracy']}: {avg_time:.2f}s", 'medium', (0, 0, 0)), (320, 320))
    
    screen.blit(render_text(ui_text['restart'], 'small', (100, 100, 100)), (200, 400))
    pygame.display.flip()

    # Wait for user input to restart or exit
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_game()
                    return
                elif event.key == pygame.K_ESCAPE:
                    waiting = False
                    pygame.quit()
                    return
        clock.tick(60)

if __name__ == "__main__":
    main_game()
