# -*- coding: utf-8 -*-
import sqlite3
import pygame
import random
import time
import sys
import io
import os

# Ensure UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

# Import input method modules
try:
    from audio_input import AudioRecoVorder
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("Voice input not available")

try:
    from click_input import ClickInput
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False
    print("Click input not available")

try:
    from key_input import KeyInput
    KEY_AVAILABLE = True
except ImportError:
    KEY_AVAILABLE = False
    print("Key input not available")

try:
    from finger_input import GestureInput
    GESTURE_AVAILABLE = True
except ImportError:
    GESTURE_AVAILABLE = False
    print("Gesture input not available")

try:
    from color_input import CameraInput
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    print("Camera input not available")

try:
    from qr_input import QRInput
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("QR input not available")

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Stroop Effect Game - Multi-Input Methods")
clock = pygame.time.Clock()

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'pink': (255, 20, 147),

}

# Languages and UI text
LANGUAGES = {
    'english': {
        'colors': [
            ("red", (255, 0, 0)), ("green", (0, 255, 0)), ("blue", (0, 0, 255)),
            ("yellow", (255, 255, 0)), ("pink", (255, 20, 147))
        ],
        'ui': {
            'title': 'STROOP EFFECT GAME',
            'subtitle': 'Multi-Input Methods',
            'rules': 'Rules:',
            'rule1': '1. A word will appear in a COLOR',
            'rule2': '2. Ignore the WORD, focus on the COLOR',
            'instruction': 'Select the COLOR (not the word):',
            'correct': 'Correct! +1',
            'wrong': 'Wrong!',
            'timeout': "Time's up!",
            'final_score': 'Final Score',
            'accuracy': 'Accuracy',
            'restart': 'Press SPACE to play again or ESC to quit',
            'start_quit': 'Press SPACE to start or ESC to quit',
            'language_change': 'Press L to change language',
            'compare': 'Press C to compare results',
            'question': 'Question',
            'score': 'Score',
            'input_method': 'Input Method',
            'select_method': 'Select Input Method:',
            'method_voice': '1. Voice Input',
            'method_click': '2. Click Input',
            'method_key': '3. Keyboard Input',
            'method_gesture': '4. Gesture Input',
            'method_camera': '5. Camera Color Detection',
            'method_qr': '6. QR Code Input',
            'method_test': 'Press T to Show efficiency comparison',
            'get_ready': 'Get ready...',
            'processing': 'Processing...',
            'avg_time': 'Average Time',
            'efficiency': 'Efficiency',
            'stroop_effect': 'Stroop Effect'
        }
    },
    'hindi': {
        'colors': [
            ("लाल", (255, 0, 0)), ("हरा", (0, 255, 0)), ("नीला", (0, 0, 255)),
            ("पीला", (255, 255, 0)), ("गुलाबी", (255, 20, 147))
        ],
        'ui': {
            'title': 'स्ट्रूप प्रभाव खेल',
            'subtitle': 'बहु-इनपुट विधियां',
            'rules': 'नियम:',
            'rule1': '1. एक शब्द एक रंग में दिखाई जाएगी',
            'rule2': '2. शब्द को नजरअंदाज करें, रंग पर ध्यान दें',
            'instruction': 'रंग का चयन करें (शब्द नहीं):',
            'correct': 'सही! +1',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या ESC दबाएं',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या बाहर निकलने के लिए ESC',
            'language_change': 'भाषा बदलने के लिए L दबाएं',
            'compare': 'परिणाम तुलना के लिए C दबाएं',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'input_method': 'इनपुट विधि',
            'select_method': 'इनपुट विधि चुनें:',
            'method_voice': '1. आवाज इनपुट',
            'method_click': '2. क्लिक इनपुट',
            'method_key': '3. कीबोर्ड इनपुट',
            'method_gesture': '4. हावभाव इनपुट',
            'method_camera': '5. कैमरा रंग पहचान',
            'method_qr': '6. QR कोड इनपुट',
            'method_test': 'वर्तमान विधि परीक्षण के लिए T दबाएं',
            'get_ready': 'तैयार हो जाएं...',
            'processing': 'प्रसंस्करण...',
            'avg_time': 'औसत समय',
            'efficiency': 'दक्षता',
            'stroop_effect': 'स्ट्रूप प्रभाव'
        }
    }
}

# Input method enumeration
class InputMethod:
    VOICE = "voice"
    CLICK = "click"
    KEY = "key"
    GESTURE = "gesture"
    CAMERA = "camera"
    QR = "qr"

# Global state
current_language = 'english'
current_input_method = InputMethod.VOICE
colors = LANGUAGES[current_language]['colors']
ui_text = LANGUAGES[current_language]['ui']
def init_db():
    print("[INIT] Initializing database and creating table if not exists...")
    conn = sqlite3.connect('stroop_efficiency.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS efficiency (
                    method TEXT,
                    language TEXT,
                    highest_efficiency REAL,
                    average_efficiency REAL,
                    games_played INTEGER,
                    PRIMARY KEY (method, language)
                )''')
    conn.commit()
    conn.close()

# Initialize input handlers
input_handlers = {}
if VOICE_AVAILABLE:
    input_handlers[InputMethod.VOICE] = AudioRecoVorder()
if CLICK_AVAILABLE:
    input_handlers[InputMethod.CLICK] = ClickInput()
if KEY_AVAILABLE:
    input_handlers[InputMethod.KEY] = KeyInput()
if GESTURE_AVAILABLE:
    input_handlers[InputMethod.GESTURE] = GestureInput()
if CAMERA_AVAILABLE:
    input_handlers[InputMethod.CAMERA] = CameraInput()
if QR_AVAILABLE:
    input_handlers[InputMethod.QR] = QRInput()

# Game statistics
game_stats = {
    'english': {
        'voice': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'click': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'key': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'gesture': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'camera': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'qr': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
    },
    'hindi': {
        'voice': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'click': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'key': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'gesture': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'camera': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
        'qr': {'score': 0, 'times': [], 'played': False, 'stroop_conflicts': [], 'non_conflicts': []},
    }
}

# Font management
def load_fonts():
    fonts = {}
    
    # Try to load Hindi fonts
    hindi_font_paths = [
        "Mangal.ttf", "./fonts/Mangal.ttf", "C:/Windows/Fonts/mangal.ttf",
        "/System/Library/Fonts/Mangal.ttf", "/usr/share/fonts/truetype/mangal/Mangal.ttf"
    ]
    
    hindi_font = None
    for path in hindi_font_paths:
        if os.path.exists(path):
            try:
                pygame.font.Font(path, 24)
                hindi_font = path
                break
            except:
                continue
    
    # Load fonts
    if hindi_font:
        try:
            fonts['hindi_large'] = pygame.font.Font(hindi_font, 56)
            fonts['hindi_medium'] = pygame.font.Font(hindi_font, 36)
            fonts['hindi_small'] = pygame.font.Font(hindi_font, 24)
        except:
            hindi_font = None
    
    if not hindi_font:
        fonts['hindi_large'] = pygame.font.Font(None, 56)
        fonts['hindi_medium'] = pygame.font.Font(None, 36)
        fonts['hindi_small'] = pygame.font.Font(None, 24)
    
    fonts['english_large'] = pygame.font.SysFont("arial", 56)
    fonts['english_medium'] = pygame.font.SysFont("arial", 36)
    fonts['english_small'] = pygame.font.SysFont("arial", 24)
    
    return fonts

fonts = load_fonts()
def show_efficiency_analysis():
    conn = sqlite3.connect('stroop_efficiency.db')
    c = conn.cursor()
    c.execute("SELECT * FROM efficiency ORDER BY method, language")
    data = c.fetchall()
    conn.close()

    screen.fill((255, 255, 255))
    title = render_text("Efficiency Analysis (Max / Avg)", 'large', (0, 0, 200))
    screen.blit(title, (SCREEN_WIDTH//2 - 250, 30))

    y = 100
    for row in data:
        method, lang, high, avg, played = row
        line = f"{method.upper()} | {lang.capitalize():<7} | Max: {high:.2f} | Avg: {avg:.2f} | Played: {played}"
        text = render_text(line, 'small', (0, 0, 0))
        screen.blit(text, (100, y))
        y += 30
    
    note = render_text("Press any key to return", 'small', (100, 100, 100))
    screen.blit(note, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                waiting = False

def render_text(text, size, color):
    font_key = f"{current_language}_{size}"
    if font_key in fonts:
        try:
            return fonts[font_key].render(text, True, color)
        except:
            return fonts[f"english_{size}"].render(text, True, color)
    else:
        return fonts[f"english_{size}"].render(text, True, color)

def update_language(lang):
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[lang]['colors']
    ui_text = LANGUAGES[lang]['ui']

def get_available_methods():
    """Get list of available input methods"""
    available = []
    method_names = {
        InputMethod.VOICE: (ui_text['method_voice'], VOICE_AVAILABLE),
        InputMethod.CLICK: (ui_text['method_click'], CLICK_AVAILABLE),
        InputMethod.KEY: (ui_text['method_key'], KEY_AVAILABLE),
        InputMethod.GESTURE: (ui_text['method_gesture'], GESTURE_AVAILABLE),
        InputMethod.CAMERA: (ui_text['method_camera'], CAMERA_AVAILABLE),
        InputMethod.QR: (ui_text['method_qr'], QR_AVAILABLE)
    }
    
    for method, (name, available_flag) in method_names.items():
        if available_flag:
            available.append((method, name))
    
    return available

def select_input_method():
    """Show input method selection screen"""
    global current_input_method
    
    available_methods = get_available_methods()
    
    if not available_methods:
        # Show error if no methods available
        screen.fill((255, 255, 255))
        error_text = render_text("No input methods available!", 'large', (255, 0, 0))
        error_rect = error_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(error_text, error_rect)
        pygame.display.flip()
        time.sleep(3)
        return False
    
    selected_index = 0
    
    while True:
        screen.fill((255, 255, 255))
        
        # Title
        title_text = render_text(ui_text['select_method'], 'large', (0, 0, 200))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        # Current language
        lang_text = render_text(f"Language: {'English' if current_language == 'english' else 'Hindi (हिंदी)'}", 
                               'medium', (0, 100, 0))
        lang_rect = lang_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(lang_text, lang_rect)
        
        # Method list
        start_y = 220
        for i, (method, name) in enumerate(available_methods):
            color = (0, 0, 200) if i == selected_index else (0, 0, 0)
            prefix = "► " if i == selected_index else "  "
            
            method_text = render_text(f"{prefix}{name}", 'medium', color)
            screen.blit(method_text, (300, start_y + i * 50))
        
        # Instructions
        instructions = [
            "Use UP/DOWN arrows to select",
            "Press ENTER to confirm",
            "Press L to change language",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_text = render_text(instruction, 'small', (100, 100, 100))
            screen.blit(inst_text, (300, start_y + len(available_methods) * 50 + 50 + i * 30))
        
        # Test option
        test_text = render_text(ui_text['method_test'], 'small', (0, 150, 0))
        test_rect = test_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        screen.blit(test_text, test_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(available_methods)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(available_methods)
                elif event.key == pygame.K_RETURN:
                    current_input_method = available_methods[selected_index][0]
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_l:
                    new_lang = 'hindi' if current_language == 'english' else 'english'
                    update_language(new_lang)
                    available_methods = get_available_methods()  # Update method names
                    selected_index = min(selected_index, len(available_methods) - 1)
                elif event.key == pygame.K_t:
                    show_efficiency_analysis()
        
        clock.tick(60)

def test_input_method():
    """Test the current input method"""
    if current_input_method not in input_handlers:
        return False
    
    handler = input_handlers[current_input_method]
    
    # Show test screen
    screen.fill((255, 255, 255))
    test_text = render_text(f"Testing {current_input_method} input...", 'large', (0, 0, 200))
    test_rect = test_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(test_text, test_rect)
    
    # Show a test word
    test_word = random.choice(colors)
    test_color = random.choice(colors)
    
    word_text = render_text(test_word[0], 'large', test_color[1])
    word_rect = word_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(word_text, word_rect)
    
    instruction_text = render_text("Select the color of this word", 'medium', (0, 0, 0))
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
    screen.blit(instruction_text, instruction_rect)
    
    pygame.display.flip()
    
    # Test the input method
    start_time = time.time()
    result = handler.get_input(colors, screen, ui_text, fonts)
    end_time = time.time()
    
    # Show results
    screen.fill((255, 255, 255))
    if result['success']:
        result_text = render_text("Test Successful!", 'large', (0, 200, 0))
        if result['color_index'] is not None:
            selected_color = colors[result['color_index']][0]
            detail_text = render_text(f"Selected: {selected_color}", 'medium', (0, 0, 0))
        else:
            detail_text = render_text("No color selected", 'medium', (0, 0, 0))
    else:
        result_text = render_text("Test Failed!", 'large', (255, 0, 0))
        detail_text = render_text(f"Error: {result['message']}", 'medium', (0, 0, 0))
    
    result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
    screen.blit(result_text, result_rect)
    
    detail_rect = detail_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(detail_text, detail_rect)
    
    time_text = render_text(f"Time taken: {end_time - start_time:.2f}s", 'small', (0, 0, 100))
    time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
    screen.blit(time_text, time_rect)
    
    continue_text = render_text("Press any key to continue", 'small', (100, 100, 100))
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
    screen.blit(continue_text, continue_rect)
    
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

def play_game():
    """Main game loop"""
    if current_input_method not in input_handlers:
        return False
    
    handler = input_handlers[current_input_method]
    
    question_count = 0
    total_questions = 5
    score = 0
    response_times = []
    
    # Get current stats
    current_stats = game_stats[current_language][current_input_method]
    
    while question_count < total_questions:
        # Clear screen
        screen.fill((255, 255, 255))
        
        # Show question info
        question_text = render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 'medium', (0, 0, 0))
        score_text = render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0))
        method_text = render_text(f"{ui_text['input_method']}: {current_input_method}", 'small', (0, 0, 100))
        
        screen.blit(question_text, (50, 50))
        screen.blit(score_text, (SCREEN_WIDTH - 250, 50))
        screen.blit(method_text, (50, 100))
        
        # Choose random word and color
        word_index = random.randint(0, len(colors) - 1)
        color_index = random.randint(0, len(colors) - 1)
        is_stroop_conflict = (word_index != color_index)
        
        word_name = colors[word_index][0]
        color_rgb = colors[color_index][1]
        
        # Display the word in the color
        word_surface = render_text(word_name, 'large', color_rgb)
        word_rect = word_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(word_surface, word_rect)
        
        # Show instruction
        instruction_surface = render_text(ui_text['instruction'], 'medium', (0, 0, 0))
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(instruction_surface, instruction_rect)
        
        pygame.display.flip()
        
        # Wait a moment
        time.sleep(0.5)
        
        # Get input
        start_time = time.time()
        
        result = handler.get_input(colors, screen, ui_text, fonts)
        end_time = time.time()
        
        # Handle quit
        if not result['success'] and result['message'] == 'quit':
            return False
        
        # Calculate response time
        response_time = end_time - start_time
        response_times.append(response_time)
        
        # Track stroop conflicts
        if is_stroop_conflict:
            current_stats['stroop_conflicts'].append(response_time)
        else:
            current_stats['non_conflicts'].append(response_time)
        
        # Check answer
        if result['success'] and result.get('color_index') is not None:
          is_correct = result['color_index'] == color_index
        else:
          is_correct = False

        # Show result
        screen.fill((255, 255, 255))
        screen.blit(word_surface, word_rect)
        
        if is_correct:
            score += 1
            result_text = render_text(ui_text['correct'], 'large', (0, 255, 0))
        else:
            result_text = render_text(ui_text['wrong'], 'large', (255, 0, 0))
            
            # Show correct answer
            if result['color_index'] is not None and 0 <= result['color_index'] < len(colors):
                user_answer = colors[result['color_index']][0]
                correct_answer = colors[color_index][0]
                
                user_text = render_text(f"Your answer: {user_answer}", 'medium', (0, 0, 0))
                correct_text = render_text(f"Correct answer: {correct_answer}", 'medium', (0, 0, 0))
                
                screen.blit(user_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 150))
                screen.blit(correct_text, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 190))
        
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(result_text, result_rect)
        
        # Show response time
        time_text = render_text(f"Time: {response_time:.2f}s", 'small', (0, 0, 100))
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 250))
        screen.blit(time_text, time_rect)
        
        pygame.display.flip()
        time.sleep(2)
        
        question_count += 1
    
    # Update stats
    current_stats['score'] = score
    current_stats['times'] = response_times
    current_stats['played'] = True
    
    # Show final results
    show_final_results(score, response_times)
    
    return True

def show_final_results(score, response_times):
    """Show final game results"""
    screen.fill((255, 255, 255))
    
    # Title
    title_text = render_text(ui_text['final_score'], 'large', (0, 0, 200))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Score
    score_text = render_text(f"{score}/5", 'large', (0, 0, 0))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 180))
    screen.blit(score_text, score_rect)
    
    # Accuracy
    accuracy = (score / 5) * 100
    accuracy_text = render_text(f"{ui_text['accuracy']}: {accuracy:.1f}%", 'medium', (0, 0, 0))
    accuracy_rect = accuracy_text.get_rect(center=(SCREEN_WIDTH//2, 240))
    screen.blit(accuracy_text, accuracy_rect)
    
    # Average time
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        time_text = render_text(f"{ui_text['avg_time']}: {avg_time:.2f}s", 'medium', (0, 0, 0))
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, 290))
        screen.blit(time_text, time_rect)
        
        # Efficiency
        efficiency = score / avg_time if avg_time > 0 else 0
        eff_text = render_text(f"{ui_text['efficiency']}: {efficiency:.2f}", 'medium', (0, 100, 0))
        eff_rect = eff_text.get_rect(center=(SCREEN_WIDTH//2, 340))
        screen.blit(eff_text, eff_rect)
    
    # Stroop effect analysis
    current_stats = game_stats[current_language][current_input_method]
    if current_stats['stroop_conflicts'] and current_stats['non_conflicts']:
        conflict_avg = sum(current_stats['stroop_conflicts']) / len(current_stats['stroop_conflicts'])
        non_conflict_avg = sum(current_stats['non_conflicts']) / len(current_stats['non_conflicts'])
        stroop_effect = conflict_avg - non_conflict_avg
        
        stroop_text = render_text(f"{ui_text['stroop_effect']}: +{stroop_effect:.2f}s", 'medium', (200, 0, 0))
        stroop_rect = stroop_text.get_rect(center=(SCREEN_WIDTH//2, 390))
        screen.blit(stroop_text, stroop_rect)
    
    # Instructions
    instructions = [
        ui_text['restart'],
        ui_text['language_change'],
        "Press M to change input method",
        ui_text['compare']
    ]
    
    start_y = 480
    for i, instruction in enumerate(instructions):
        inst_text = render_text(instruction, 'small', (0, 0, 0))
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 30))
        screen.blit(inst_text, inst_rect)
    
    pygame.display.flip()
    
    # Wait for input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_l:
                    new_lang = 'hindi' if current_language == 'english' else 'english'
                    update_language(new_lang)
                    return True
                elif event.key == pygame.K_m:
                    if select_input_method():
                        return True
                    return False
                elif event.key == pygame.K_c:
                    show_comparison()
                    return True
        
        clock.tick(60)
    update_efficiency_db(current_input_method, current_language, efficiency)

    return True

def show_comparison():
    """Show comparison of different methods and languages"""
    screen.fill((255, 255, 255))
    
    # Title
    title_text = render_text("Performance Comparison", 'large', (0, 0, 200))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(title_text, title_rect)
    
    # Show stats for each language and method
    y_offset = 100
    
    for lang in ['english', 'hindi']:
        lang_name = 'English' if lang == 'english' else 'Hindi (हिंदी)'
        lang_text = render_text(f"{lang_name}:", 'medium', (0, 100, 0))
        screen.blit(lang_text, (50, y_offset))
        y_offset += 40
        
        for method in ['voice', 'click', 'key', 'gesture', 'camera', 'qr']:
            stats = game_stats[lang][method]
            if stats['played']:
                # Calculate metrics
                avg_time = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
                accuracy = (stats['score'] / 5) * 100 if stats['score'] > 0 else 0
                efficiency = stats['score'] / avg_time if avg_time > 0 else 0
                
                # Calculate stroop effect
                stroop_effect = 0
                if stats['stroop_conflicts'] and stats['non_conflicts']:
                    conflict_avg = sum(stats['stroop_conflicts']) / len(stats['stroop_conflicts'])
                    non_conflict_avg = sum(stats['non_conflicts']) / len(stats['non_conflicts'])
                    stroop_effect = conflict_avg - non_conflict_avg
                
                # Display stats
                method_text = f"  {method.capitalize()}: Score={stats['score']}/5, Avg Time={avg_time:.2f}s, Accuracy={accuracy:.1f}%, Stroop Effect=+{stroop_effect:.2f}s"
                
                # Color code based on performance
                color = (0, 150, 0) if accuracy >= 80 else (150, 150, 0) if accuracy >= 60 else (150, 0, 0)
                
                stat_text = render_text(method_text, 'small', color)
                screen.blit(stat_text, (70, y_offset))
                y_offset += 25
        
        y_offset += 20
    
    # Instructions
    instruction_text = render_text("Press any key to return", 'small', (100, 100, 100))
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
    screen.blit(instruction_text, instruction_rect)
    
    pygame.display.flip()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                waiting = False
        
        clock.tick(60)
    
    return True
def update_efficiency_db(method, language, efficiency):
    conn = sqlite3.connect('stroop_efficiency.db')
    c = conn.cursor()
    
    # Fetch existing row
    c.execute("SELECT highest_efficiency, average_efficiency, games_played FROM efficiency WHERE method=? AND language=?", 
              (method, language))
    row = c.fetchone()
    
    if row:
        highest, avg, games = row
        new_highest = max(highest, efficiency)
        new_avg = (avg * games + efficiency) / (games + 1)
        c.execute("UPDATE efficiency SET highest_efficiency=?, average_efficiency=?, games_played=? WHERE method=? AND language=?",
                  (new_highest, new_avg, games + 1, method, language))
    else:
        c.execute("INSERT INTO efficiency VALUES (?, ?, ?, ?, ?)", 
                  (method, language, efficiency, efficiency, 1))
    
    conn.commit()
    conn.close()

def show_start_screen():
    """Show the start screen"""
    screen.fill((255, 255, 255))
    
    # Title
    title_text = render_text(ui_text['title'], 'large', (0, 0, 200))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
    screen.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_text = render_text(ui_text['subtitle'], 'medium', (0, 100, 0))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 200))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Current language
    lang_text = render_text(f"Language: {'English' if current_language == 'english' else 'Hindi (हिंदी)'}", 
                           'medium', (0, 0, 100))
    lang_rect = lang_text.get_rect(center=(SCREEN_WIDTH//2, 250))
    screen.blit(lang_text, lang_rect)
    
    # Current input method
    method_text = render_text(f"Input Method: {current_input_method.capitalize()}", 'medium', (0, 0, 100))
    method_rect = method_text.get_rect(center=(SCREEN_WIDTH//2, 300))
    screen.blit(method_text, method_rect)
    
    # Rules
    rules_text = render_text(ui_text['rules'], 'medium', (200, 0, 0))
    rules_rect = rules_text.get_rect(center=(SCREEN_WIDTH//2, 380))
    screen.blit(rules_text, rules_rect)
    
    rule1_text = render_text(ui_text['rule1'], 'small', (0, 0, 0))
    rule1_rect = rule1_text.get_rect(center=(SCREEN_WIDTH//2, 420))
    screen.blit(rule1_text, rule1_rect)
    
    rule2_text = render_text(ui_text['rule2'], 'small', (0, 0, 0))
    rule2_rect = rule2_text.get_rect(center=(SCREEN_WIDTH//2, 450))
    screen.blit(rule2_text, rule2_rect)
    
    # Instructions
    instructions = [
        ui_text['start_quit'],
        ui_text['language_change'],
        "Press M to change input method",
        ui_text['compare']
    ]
    
    start_y = 520
    for i, instruction in enumerate(instructions):
        inst_text = render_text(instruction, 'small', (0, 0, 0))
        inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 30))
        screen.blit(inst_text, inst_rect)
    
    pygame.display.flip()

def main():
    """Main game loop"""
    global current_language, current_input_method
    init_db()
    # Initial setup
    if not select_input_method():
        return
    
    running = True
    game_state = 'menu'  # 'menu', 'playing', 'results'
   

    while running:
        if game_state == 'menu':
            show_start_screen()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = 'playing'
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_l:
                        new_lang = 'hindi' if current_language == 'english' else 'english'
                        update_language(new_lang)
                    elif event.key == pygame.K_m:
                        if select_input_method():
                            continue
                        else:
                            running = False
                    elif event.key == pygame.K_c:
                        show_comparison()
        
        elif game_state == 'playing':
            if play_game():
                game_state = 'menu'
            else:
                running = False
        
        clock.tick(60)
    efficiency = score / total_time if total_time > 0 else 0
    update_efficiency_db(method_used, language_used, efficiency)

    # Cleanup
    for handler in input_handlers.values():
        if hasattr(handler, 'cleanup'):
            handler.cleanup()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()