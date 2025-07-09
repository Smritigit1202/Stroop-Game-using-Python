# -*- coding: utf-8 -*-
import sqlite3
import pygame
import random
import time
import sys
import io
import os
import pygame.freetype
import math
# Global color list: (Display Text, RGB)

def get_localized_colors():
    if current_language == 'hindi':
        return [
            ("लाल", (255, 0, 0)),
            ("हरा", (0, 255, 0)),
            ("नीला", (0, 0, 255)),
            ("पीला", (255, 255, 0)),
            ("गुलाबी", (255, 105, 180))
        ]
    else:
        return [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)),
            ("Pink", (255, 105, 180))
        ]

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

# UI Colors and gradients
UI_COLORS = {
    'primary': (70, 130, 180),        # Steel blue
    'secondary': (100, 149, 237),     # Cornflower blue
    'accent': (255, 215, 0),          # Gold
    'success': (50, 205, 50),         # Lime green
    'error': (220, 20, 60),           # Crimson
    'warning': (255, 140, 0),         # Dark orange
    'background': (240, 248, 255),    # Alice blue
    'text': (25, 25, 112),            # Midnight blue
    'light_text': (100, 100, 100),    # Gray
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'dark_bg': (30, 30, 50),
    'game_bg': (245, 245, 250)
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
            'stroop_effect': 'Stroop Effect',
            'your_answer': 'Your answer',
            'correct_answer': 'Correct answer'
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
            'rule1': '१. एक शब्द एक रंग में दिखाई देगा',
            'rule2': '२. शब्द को नजरअंदाज करें, रंग पर ध्यान दें',
            'instruction': 'रंग का चयन करें (शब्द नहीं):',
            'correct': 'सही! +१',
            'wrong': 'गलत!',
            'timeout': 'समय समाप्त!',
            'final_score': 'अंतिम स्कोर',
            'accuracy': 'सटीकता',
            'restart': 'फिर से खेलने के लिए SPACE दबाएं या ESC दबाएं',
            'start_quit': 'शुरू करने के लिए SPACE दबाएं या बाहर निकलने के लिए ESC',
            'language_change': 'भाषा बदलने के लिए [L] दबाएं',
            'compare': 'परिणाम तुलना के लिए [C] दबाएं',
            'question': 'प्रश्न',
            'score': 'स्कोर',
            'input_method': 'इनपुट विधि',
            'select_method': 'इनपुट विधि चुनें:',
            'method_voice': '१. आवाज इनपुट',
            'method_click': '२. क्लिक इनपुट',
            'method_key': '३. कीबोर्ड इनपुट',
            'method_gesture': '४. हाव-भाव इनपुट',
            'method_camera': '५. कैमरा रंग पहचान',
            'method_qr': '६. QR कोड इनपुट',
            'method_test': 'दक्षता तुलना के लिए T दबाएं',
            'get_ready': 'तैयार हो जाएं...',
            'processing': 'प्रसंस्करण...',
            'avg_time': 'औसत समय',
            'efficiency': 'दक्षता',
            'stroop_effect': 'स्ट्रूप प्रभाव',
            'your_answer': 'आपका उत्तर',
            'correct_answer': 'सही उत्तर'
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

# Enhanced Font management with better Hindi support
def load_fonts():
    fonts = {
    "small": pygame.freetype.Font("fonts/OpenSans-Regular.ttf", 20),
    "medium": pygame.freetype.Font("fonts/OpenSans-Regular.ttf", 28),
    "large": pygame.freetype.Font("fonts/OpenSans-Regular.ttf", 36),
    "title": pygame.freetype.Font("fonts/OpenSans-Regular.ttf", 48)
 }

    if current_language == 'hindi':
     devanagari_font = "fonts/NotoSansDevanagari-Regular.ttf"
     fonts["small"] = pygame.freetype.Font(devanagari_font, 20)
     fonts["medium"] = pygame.freetype.Font(devanagari_font, 28)
     fonts["large"] = pygame.freetype.Font(devanagari_font, 36)
     fonts["title"] = pygame.freetype.Font(devanagari_font, 48)

    # Enhanced Hindi font paths - more comprehensive search
    hindi_font_paths = [
    "./fonts/NotoSansDevanagari-Regular.ttf",     # ✅ Highest priority
    "NotoSansDevanagari-Regular.ttf",
    "C:/Windows/Fonts/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    
    
]

    
    hindi_font = None
    for path in hindi_font_paths:
        if os.path.exists(path):
            try:
                # Test if the font can render Hindi text
                test_font = pygame.font.Font(path, 24)
                test_surface = test_font.render("हिंदी", True, (0, 0, 0))
                if test_surface.get_width() > 0:  # Check if text was rendered
                    hindi_font = path
                    print(f"[FONT] Using Hindi font: {path}")
                    break
            except Exception as e:
                print(f"[FONT] Failed to load font {path}: {e}")
                continue
    
    if not hindi_font:
        print("[FONT] Warning: No Hindi font found, using default font")
        print("[FONT] Hindi text may not display correctly")
        print("[FONT] Please install Mangal or Noto Sans Devanagari font")
    
    # Load fonts with different sizes
    font_sizes = {
        'large': 56,
        'medium': 36,
        'small': 24,
        'title': 72,
        'subtitle': 28
    }
    
    for size_name, size in font_sizes.items():
        if hindi_font:
            try:
                fonts[f'hindi_{size_name}'] = pygame.font.Font(hindi_font, size)
            except Exception as e:
                print(f"[FONT] Failed to create Hindi font size {size}: {e}")
                fonts[f'hindi_{size_name}'] = pygame.font.Font(None, size)
        else:
            fonts[f'hindi_{size_name}'] = pygame.font.Font(None, size)
        
        # English fonts
        try:
            fonts[f'english_{size_name}'] = pygame.font.SysFont("arial", size, bold=(size_name in ['title', 'large']))
        except:
            fonts[f'english_{size_name}'] = pygame.font.Font(None, size)
    
    return fonts

fonts = load_fonts()

def draw_gradient_rect(surface, start_color, end_color, rect, vertical=True):
    """Draw a gradient rectangle"""
    if vertical:
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))
    else:
        for x in range(rect.width):
            ratio = x / rect.width
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x + x, rect.y), 
                           (rect.x + x, rect.y + rect.height))

def draw_button(surface, text, rect, color, text_color, font_size='medium', hover=False):
    """Draw a modern button with gradient and shadow"""
    # Shadow
    shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
    pygame.draw.rect(surface, (0, 0, 0, 50), shadow_rect, border_radius=10)
    
    # Button background
    if hover:
        button_color = tuple(min(255, c + 20) for c in color)
    else:
        button_color = color
    
    pygame.draw.rect(surface, button_color, rect, border_radius=10)
    pygame.draw.rect(surface, tuple(max(0, c - 40) for c in color), rect, 2, border_radius=10)
    
    # Button text
    button_text = render_text(text, font_size, text_color)
    text_rect = button_text.get_rect(center=rect.center)
    surface.blit(button_text, text_rect)

def draw_animated_background(surface, time_offset=0):
    """Draw animated background with particles"""
    surface.fill(UI_COLORS['game_bg'])
    
    # Draw floating particles
    for i in range(20):
        x = (200 + i * 60 + math.sin(time_offset + i) * 30) % SCREEN_WIDTH
        y = (100 + i * 40 + math.cos(time_offset + i * 0.5) * 20) % SCREEN_HEIGHT
        size = 3 + math.sin(time_offset + i * 0.3) * 2
        alpha = int(50 + math.sin(time_offset + i * 0.7) * 30)
        
        color = (*UI_COLORS['primary'], alpha)
        pygame.draw.circle(surface, color[:3], (int(x), int(y)), int(size))

import csv

def show_efficiency_analysis():
    """Efficiency analysis UI with export notification on screen"""
    conn = sqlite3.connect('stroop_efficiency.db')
    c = conn.cursor()
    c.execute("SELECT * FROM efficiency ORDER BY method, language")
    data = c.fetchall()
    conn.close()

    def draw_ui():
        draw_animated_background(screen)

        # Title
        title_rect = pygame.Rect(0, 20, SCREEN_WIDTH, 80)
        draw_gradient_rect(screen, UI_COLORS['primary'], UI_COLORS['secondary'], title_rect)
        title = render_text("Efficiency Analysis", 'title', UI_COLORS['white'])
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        # Table Header
        y = 140
        row_height = 42
        col_x = [60, 220, 400, 600, 790]
        col_titles = ["Method", "Language", "Max Efficiency", "Avg Efficiency", "Games Played"]

        pygame.draw.rect(screen, UI_COLORS['secondary'], (50, y, SCREEN_WIDTH - 100, row_height), border_radius=6)
        for i, title in enumerate(col_titles):
            header = render_text(title, 'medium', UI_COLORS['white'])
            screen.blit(header, (col_x[i], y + 10))
        y += row_height + 10

        for i, row in enumerate(data):
            method, lang, high, avg, played = row
            row_color = UI_COLORS['white'] if i % 2 == 0 else UI_COLORS['background']
            pygame.draw.rect(screen, row_color, (50, y, SCREEN_WIDTH - 100, row_height), border_radius=4)

            values = [
                method.capitalize(),
                "English" if lang == 'english' else "Hindi",
                f"{high:.2f}",
                f"{avg:.2f}",
                str(played)
            ]

            for j, val in enumerate(values):
                text = render_text(val, 'small', UI_COLORS['text'])
                screen.blit(text, (col_x[j], y + 10))

            y += row_height + 5

        # Instructions
        instruction_rect = pygame.Rect(0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 40)
        pygame.draw.rect(screen, UI_COLORS['accent'], instruction_rect)
        
        note = render_text("Press E to export as CSV | Press any other key to return to menu", 
                          'medium', UI_COLORS['text'])
        screen.blit(note, note.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))

    draw_ui()
    pygame.display.flip()

    waiting = True
    show_export_msg = False

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    export_efficiency_to_csv(data)
                    show_export_msg = True

                    # Redraw UI + show export confirmation
                    draw_ui()
                    export_note = render_text("CSV Exported Successfully!", 'medium', UI_COLORS['success'])
                    screen.blit(export_note, export_note.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 110)))
                    pygame.display.flip()
                    pygame.time.wait(2000)  # Show for 2 seconds

                else:
                    waiting = False


def export_efficiency_to_csv(data):
    """Exports efficiency data to CSV"""
    filename = "efficiency_export.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Method", "Language", "Max Efficiency", "Avg Efficiency", "Games Played"])
        for row in data:
            method, lang, high, avg, played = row
            writer.writerow([method.capitalize(), lang.capitalize(), f"{high:.2f}", f"{avg:.2f}", played])
    print(f"Efficiency data exported to {filename}")


def render_text(text, size, color):
    """Render Hindi-English mixed text with proper fonts"""
    import re
    hindi_font = fonts.get(f'hindi_{size}', fonts["english_medium"])
    english_font = fonts.get(f'english_{size}', fonts["english_medium"])
    
    # Split into Hindi and English parts
    segments = re.findall(r'[A-Za-z0-9]+|[^A-Za-z0-9]+', text)
    
    rendered_segments = []
    for segment in segments:
        if re.match(r'[A-Za-z0-9]', segment):
            surf = english_font.render(segment, True, color)
        else:
            surf = hindi_font.render(segment, True, color)
        rendered_segments.append(surf)
    
    # Combine all segments horizontally
    total_width = sum(s.get_width() for s in rendered_segments)
    max_height = max(s.get_height() for s in rendered_segments)
    final_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)
    
    x_offset = 0
    for seg in rendered_segments:
        final_surface.blit(seg, (x_offset, 0))
        x_offset += seg.get_width()
    
    return final_surface

def update_language(lang):
    """Update language with proper text refresh"""
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[lang]['colors']
    ui_text = LANGUAGES[lang]['ui']
    print(f"[LANG] Language changed to: {lang}")

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
    """Enhanced input method selection with modern UI"""
    global current_input_method
    
    available_methods = get_available_methods()
    
    if not available_methods:
        # Enhanced error display
        draw_animated_background(screen)
        
        error_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 50, 600, 100)
        pygame.draw.rect(screen, UI_COLORS['error'], error_rect, border_radius=15)
        
        error_text = render_text("No input methods available!", 'large', UI_COLORS['white'])
        error_text_rect = error_text.get_rect(center=error_rect.center)
        screen.blit(error_text, error_text_rect)
        
        pygame.display.flip()
        time.sleep(3)
        return False
    
    selected_index = 0
    animation_time = 0
    
    while True:
        animation_time += 0.1
        draw_animated_background(screen, animation_time)
        
        # Title with gradient background
        title_rect = pygame.Rect(0, 30, SCREEN_WIDTH, 100)
        draw_gradient_rect(screen, UI_COLORS['primary'], UI_COLORS['secondary'], title_rect)
        
        title_text = render_text(ui_text['select_method'], 'title', UI_COLORS['white'])
        title_text_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        screen.blit(title_text, title_text_rect)
        
        # Current language display
        lang_display = "English" if current_language == 'english' else "हिंदी"
        lang_text = render_text(f"Language/'भाषा: {lang_display}", 'medium', UI_COLORS['text'])
        lang_rect = lang_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        screen.blit(lang_text, lang_rect)
        
        # Method selection with modern buttons
        start_y = 220
        button_height = 50
        button_width = 500
        
        for i, (method, name) in enumerate(available_methods):
            button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, 
                                    start_y + i * (button_height + 10), 
                                    button_width, button_height)
            
            is_selected = (i == selected_index)
            button_color = UI_COLORS['accent'] if is_selected else UI_COLORS['secondary']
            text_color = UI_COLORS['text'] if is_selected else UI_COLORS['white']
            
            draw_button(screen, name, button_rect, button_color, text_color, 'medium', is_selected)
        
        # Instructions panel
        instruction_y = start_y + len(available_methods) * (button_height + 10) + 30
        instruction_rect = pygame.Rect(50, instruction_y, SCREEN_WIDTH - 100, 180)
        pygame.draw.rect(screen, UI_COLORS['white'], instruction_rect, border_radius=10)
        pygame.draw.rect(screen, UI_COLORS['primary'], instruction_rect, 2, border_radius=10)
        
        if current_language == 'hindi':
            instructions = [
                "चुनने के लिए 'UP/DOWN' तीर का उपयोग करें",
                "पुष्टि के लिए 'ENTER' दबाएं",
                "भाषा बदलने के लिए 'L' दबाएं",
                "बाहर निकलने के लिए 'ESC' दबाएं"
            ]
        else:
         instructions = [
        "Use UP/DOWN arrows to select",
        "Press ENTER to confirm",
        "Press L to change language",
        "Press ESC to quit"
    ]

        
        for i, instruction in enumerate(instructions):
            inst_text = render_text(instruction, 'small', UI_COLORS['text'])
            screen.blit(inst_text, (70, instruction_y + 20 + i * 30))
        
        # Test option
        test_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 120, 400, 40)
        draw_button(screen, ui_text['method_test'], test_rect, UI_COLORS['success'], UI_COLORS['white'], 'small')
        
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
                    available_methods = get_available_methods()
                    selected_index = min(selected_index, len(available_methods) - 1)
                elif event.key == pygame.K_t:
                    show_efficiency_analysis()
        
        clock.tick(60)


def test_input_method():
    """Test the current input method with enhanced UI"""
    if current_input_method not in input_handlers:
        return False
    
    handler = input_handlers[current_input_method]
    
    # Enhanced test screen with animated background
    animation_time = 0
    
    # Show initial test screen
    for frame in range(60):  # 1 second animation
        animation_time += 0.1
        draw_animated_background(screen, animation_time)
        
        # Main container with gradient background
        container_rect = pygame.Rect(100, 150, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 300)
        draw_gradient_rect(screen, UI_COLORS['primary'], UI_COLORS['secondary'], container_rect)
        pygame.draw.rect(screen, UI_COLORS['white'], container_rect, 3, border_radius=15)
        
        # Title with shadow effect
        title_shadow = render_text(f"Testing {current_input_method.capitalize()} Input", 'large', (50, 50, 50))  # darker gray as shadow
        title_text = render_text(f"Testing {current_input_method.capitalize()} Input", 'large', UI_COLORS['white'])
        
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 2, 222))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 220))
        
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_text, title_rect)
        
        # Animated loading indicator
        loading_text = render_text("Initializing test environment...", 'medium', UI_COLORS['white'])
        loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        screen.blit(loading_text, loading_rect)
        
        # Progress bar
        progress_width = 300
        progress_rect = pygame.Rect(SCREEN_WIDTH//2 - progress_width//2, 320, progress_width, 20)
        pygame.draw.rect(screen, UI_COLORS['white'], progress_rect, border_radius=10)
        
        fill_width = int((frame / 60) * progress_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, 20)
            pygame.draw.rect(screen, UI_COLORS['accent'], fill_rect, border_radius=10)
        
        pygame.display.flip()
        clock.tick(60)
    
    colors = get_localized_colors()
    test_word = random.choice(colors)

    test_color = random.choice(colors)
    
    # Main test interface
    draw_animated_background(screen, animation_time)
    
    # Main container
    container_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
    draw_gradient_rect(screen, UI_COLORS['white'], UI_COLORS['background'], container_rect)
    pygame.draw.rect(screen, UI_COLORS['primary'], container_rect, 3, border_radius=15)
    
    # Header section
    header_rect = pygame.Rect(container_rect.x, container_rect.y, container_rect.width, 80)
    draw_gradient_rect(screen, UI_COLORS['secondary'], UI_COLORS['primary'], header_rect)
    
    header_text = render_text("INPUT METHOD TEST", 'large', UI_COLORS['white'])
    header_text_rect = header_text.get_rect(center=(SCREEN_WIDTH//2, header_rect.centery))
    screen.blit(header_text, header_text_rect)
    
    # Method badge
    method_badge = pygame.Rect(container_rect.x + 20, container_rect.y + 100, 200, 40)
    pygame.draw.rect(screen, UI_COLORS['accent'], method_badge, border_radius=20)
    
    method_text = render_text(f"Method: {current_input_method.capitalize()}", 'small', UI_COLORS['text'])
    method_text_rect = method_text.get_rect(center=method_badge.center)
    screen.blit(method_text, method_text_rect)
    
    # Test word container with shadow
    word_container = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 150)
    shadow_container = pygame.Rect(word_container.x + 5, word_container.y + 5, word_container.width, word_container.height)
    
    pygame.draw.rect(screen, (0, 0, 0, 50), shadow_container, border_radius=15)
    pygame.draw.rect(screen, UI_COLORS['white'], word_container, border_radius=15)
    pygame.draw.rect(screen, test_color[1], word_container, 3, border_radius=15)
    
    # Test word with enhanced styling
    word_text = render_text(test_word[0], 'title', test_color[1])
    word_rect = word_text.get_rect(center=word_container.center)
    screen.blit(word_text, word_rect)
    
    # Instruction panel
    instruction_panel = pygame.Rect(container_rect.x + 50, container_rect.y + container_rect.height - 120, 
                                   container_rect.width - 100, 80)
    pygame.draw.rect(screen, UI_COLORS['background'], instruction_panel, border_radius=10)
    pygame.draw.rect(screen, UI_COLORS['secondary'], instruction_panel, 2, border_radius=10)
    
    instruction_text = render_text("Select the COLOR of the word above", 'medium', UI_COLORS['text'])
    instruction_rect = instruction_text.get_rect(center=(instruction_panel.centerx, instruction_panel.centery - 10))
    screen.blit(instruction_text, instruction_rect)
    
    hint_text = render_text("(Focus on the color, not the word itself)", 'small', UI_COLORS['light_text'])
    hint_rect = hint_text.get_rect(center=(instruction_panel.centerx, instruction_panel.centery + 15))
    screen.blit(hint_text, hint_rect)
    
    pygame.display.flip()
    
    # Test the input method
    start_time = time.time()
    result = handler.get_input(colors, screen, ui_text, fonts)
    end_time = time.time()
    
    # Enhanced results screen
    response_time = end_time - start_time
    
    # Results background
    draw_animated_background(screen, animation_time + 2)
    
    # Results container
    results_rect = pygame.Rect(150, 120, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 240)
    draw_gradient_rect(screen, UI_COLORS['white'], UI_COLORS['background'], results_rect)
    pygame.draw.rect(screen, UI_COLORS['primary'], results_rect, 3, border_radius=15)
    
    # Results header
    if result['success']:
        header_color = UI_COLORS['success']
        header_text = "TEST SUCCESSFUL!"
        status_icon = ""
    else:
        header_color = UI_COLORS['error']
        header_text = "TEST FAILED!"
        status_icon = ""
    
    header_rect = pygame.Rect(results_rect.x, results_rect.y, results_rect.width, 80)
    pygame.draw.rect(screen, header_color, header_rect, border_radius=15)
    
    header_surface = render_text(header_text, 'large', UI_COLORS['white'])
    header_surface_rect = header_surface.get_rect(center=(SCREEN_WIDTH//2, header_rect.centery))
    screen.blit(header_surface, header_surface_rect)
    
    # Results content area
    content_y = results_rect.y + 100
    
    # Response time card
    time_card = pygame.Rect(results_rect.x + 50, content_y, results_rect.width - 100, 60)
    pygame.draw.rect(screen, UI_COLORS['background'], time_card, border_radius=10)
    pygame.draw.rect(screen, UI_COLORS['secondary'], time_card, 2, border_radius=10)
    
    time_label = render_text("Response Time:", 'medium', UI_COLORS['text'])
    time_value = render_text(f"{response_time:.2f} seconds", 'medium', UI_COLORS['primary'])
    
    screen.blit(time_label, (time_card.x + 20, time_card.y + 15))
    screen.blit(time_value, (time_card.x + 250, time_card.y + 15))
    
    content_y += 80
    
    # Selection details card
    if result['success'] and result['color_index'] is not None:
        selection_card = pygame.Rect(results_rect.x + 50, content_y, results_rect.width - 100, 60)
        pygame.draw.rect(screen, UI_COLORS['background'], selection_card, border_radius=10)
        pygame.draw.rect(screen, UI_COLORS['success'], selection_card, 2, border_radius=10)
        
        selected_color = colors[result['color_index']][0]
        selection_text = render_text(f"Selected Color: {selected_color}", 'medium', UI_COLORS['text'])
        screen.blit(selection_text, (selection_card.x + 20, selection_card.y + 20))
        
        content_y += 80
    
    # Error details if applicable
    if not result['success']:
        error_card = pygame.Rect(results_rect.x + 50, content_y, results_rect.width - 100, 60)
        pygame.draw.rect(screen, UI_COLORS['background'], error_card, border_radius=10)
        pygame.draw.rect(screen, UI_COLORS['error'], error_card, 2, border_radius=10)
        
        error_text = render_text(f"Error: {result['message']}", 'medium', UI_COLORS['text'])
        screen.blit(error_text, (error_card.x + 20, error_card.y + 20))
        
        content_y += 80
    
    # Performance indicator
    if result['success']:
        if response_time < 2.0:
            performance_text = "Excellent Response Time!"
            performance_color = UI_COLORS['success']
        elif response_time < 4.0:
            performance_text = " Good Response Time"
            performance_color = UI_COLORS['warning']
        else:
            performance_text = "Consider Optimizing Response Time"
            performance_color = UI_COLORS['error']
        
        performance_surface = render_text(performance_text, 'medium', performance_color)
        performance_rect = performance_surface.get_rect(center=(SCREEN_WIDTH//2, content_y + 30))
        screen.blit(performance_surface, performance_rect)
    
    # Continue button
    continue_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, results_rect.y + results_rect.height - 80, 200, 50)
    draw_button(screen, "Continue", continue_btn, UI_COLORS['accent'], UI_COLORS['text'], 'medium')
    
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
    """Main game loop with enhanced UI"""
    if current_input_method not in input_handlers:
        return False
    
    handler = input_handlers[current_input_method]
    
    question_count = 0
    total_questions = 5
    score = 0
    response_times = []
    animation_time = 0
    
    # Get current stats
    current_stats = game_stats[current_language][current_input_method]
    
    # Game start animation
    for frame in range(90):  # 1.5 second countdown
        animation_time += 0.1
        draw_animated_background(screen, animation_time)
        
        # Main container
        container_rect = pygame.Rect(200, 200, SCREEN_WIDTH - 400, SCREEN_HEIGHT - 400)
        draw_gradient_rect(screen, UI_COLORS['primary'], UI_COLORS['secondary'], container_rect)
        pygame.draw.rect(screen, UI_COLORS['white'], container_rect, 3, border_radius=20)
        
        # Countdown number
        countdown_num = 3 - (frame // 30)
        if countdown_num > 0:
            countdown_text = render_text(str(countdown_num), 'title', UI_COLORS['accent'])
            countdown_rect = countdown_text.get_rect(center=container_rect.center)
            screen.blit(countdown_text, countdown_rect)
        else:
            ready_text = render_text("Let's Play!", 'large', UI_COLORS['white'])
            ready_rect = ready_text.get_rect(center=container_rect.center)
            screen.blit(ready_text, ready_rect)
        
        # Game info
        info_text = render_text(f"Method: {current_input_method.capitalize()} | Language: {current_language.capitalize()}", 
                               'medium', UI_COLORS['white'])
        info_rect = info_text.get_rect(center=(container_rect.centerx, container_rect.centery + 80))
        screen.blit(info_text, info_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    while question_count < total_questions:
        animation_time += 0.1
        
        # Enhanced game interface
        draw_animated_background(screen, animation_time)
        
        # Top status bar
        status_bar = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        draw_gradient_rect(screen, UI_COLORS['dark_bg'], UI_COLORS['primary'], status_bar)
        
        # Progress indicators
        progress_width = 300
        progress_x = SCREEN_WIDTH//2 - progress_width//2
        progress_rect = pygame.Rect(progress_x, 25, progress_width, 30)
        pygame.draw.rect(screen, UI_COLORS['white'], progress_rect, border_radius=15)
        
        # Fill progress
        fill_width = int((question_count / total_questions) * progress_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(progress_rect.x, progress_rect.y, fill_width, 30)
            pygame.draw.rect(screen, UI_COLORS['accent'], fill_rect, border_radius=15)
        
        # Question counter
        question_text = render_text(f"Question {question_count + 1}/{total_questions}", 'medium', UI_COLORS['white'])
        screen.blit(question_text, (50, 25))
        
        # Score with animated background
        score_bg = pygame.Rect(SCREEN_WIDTH - 200, 15, 150, 50)
        pygame.draw.rect(screen, UI_COLORS['accent'], score_bg, border_radius=25)
        
        score_text = render_text(f"Score: {score}", 'medium', UI_COLORS['text'])
        score_rect = score_text.get_rect(center=score_bg.center)
        screen.blit(score_text, score_rect)
        
        # Input method badge
        method_badge = pygame.Rect(20, SCREEN_HEIGHT - 100, 200, 40)
        pygame.draw.rect(screen, UI_COLORS['secondary'], method_badge, border_radius=20)
        
        method_text = render_text(f" {current_input_method.capitalize()}", 'small', UI_COLORS['white'])
        method_text_rect = method_text.get_rect(center=method_badge.center)
        screen.blit(method_text, method_text_rect)
        
        # Choose random word and color
        word_index = random.randint(0, len(colors) - 1)
        color_index = random.randint(0, len(colors) - 1)
        is_stroop_conflict = (word_index != color_index)
        
        word_name = colors[word_index][0]
        color_rgb = colors[color_index][1]
        
        # Main word display with enhanced styling
        word_container = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 120, 400, 200)
        
        # Shadow effect
        shadow_container = pygame.Rect(word_container.x + 8, word_container.y + 8, 
                                      word_container.width, word_container.height)
        pygame.draw.rect(screen, (50, 50, 50), shadow_container, border_radius=20)

        # Main container
        pygame.draw.rect(screen, UI_COLORS['white'], word_container, border_radius=20)
        pygame.draw.rect(screen, color_rgb, word_container, 5, border_radius=20)
        
        # Stroop conflict indicator
        if is_stroop_conflict:
            conflict_indicator = pygame.Rect(word_container.x + 10, word_container.y + 10, 30, 30)
            pygame.draw.circle(screen, UI_COLORS['warning'], conflict_indicator.center, 15)
            conflict_text = render_text("!", 'small', UI_COLORS['white'])
            conflict_text_rect = conflict_text.get_rect(center=conflict_indicator.center)
            screen.blit(conflict_text, conflict_text_rect)
        
        # Display the word with glow effect
        word_surface = render_text(word_name, 'title', color_rgb)
        word_rect = word_surface.get_rect(center=word_container.center)
        
        # Glow effect
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_surface = render_text(word_name, 'title', tuple(min(255, c + 50) for c in color_rgb))
            glow_rect = word_surface.get_rect(center=(word_container.center[0] + offset[0], 
                                                     word_container.center[1] + offset[1]))
            screen.blit(glow_surface, glow_rect)
        
        screen.blit(word_surface, word_rect)
        
        # Instruction panel with animation
        instruction_panel = pygame.Rect(100, SCREEN_HEIGHT//2 + 120, SCREEN_WIDTH - 200, 100)
        panel_alpha = int(200 + 55 * math.sin(animation_time * 2))
        instruction_color = (*UI_COLORS['background'], panel_alpha)
        
        pygame.draw.rect(screen, instruction_color[:3], instruction_panel, border_radius=15)
        pygame.draw.rect(screen, UI_COLORS['primary'], instruction_panel, 3, border_radius=15)
        
        # Main instruction
        instruction_text = render_text(" " + ui_text['instruction'], 'large', UI_COLORS['text'])
        instruction_rect = instruction_text.get_rect(center=(instruction_panel.centerx, instruction_panel.centery - 15))
        screen.blit(instruction_text, instruction_rect)
        
        # Hint text
        hint_text = render_text("(Ignore the word, focus on the COLOR)", 'small', UI_COLORS['light_text'])
        hint_rect = hint_text.get_rect(center=(instruction_panel.centerx, instruction_panel.centery + 20))
        screen.blit(hint_text, hint_rect)
        
        pygame.display.flip()
        
        # Wait a moment with animated loading
        for i in range(30):  # 0.5 second
            # Add subtle loading animation
            loading_dots = "." * ((i // 10) + 1)
            loading_text = render_text(f"Get ready{loading_dots}", 'small', UI_COLORS['light_text'])
            loading_rect = loading_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            
            # Clear just the loading area
            clear_rect = pygame.Rect(loading_rect.x - 50, loading_rect.y - 10, 
                                   loading_rect.width + 100, loading_rect.height + 20)
            pygame.draw.rect(screen, UI_COLORS['game_bg'], clear_rect)
            screen.blit(loading_text, loading_rect)
            
            pygame.display.update(clear_rect)
            clock.tick(60)
        
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
        
        # Enhanced result display
        draw_animated_background(screen, animation_time)
        
        # Result container
        result_container = pygame.Rect(150, 150, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 300)
        
        if is_correct:
            result_color = UI_COLORS['success']
            result_text = "" + ui_text['correct']
            result_icon = ""
            score += 1
        else:
            result_color = UI_COLORS['error']
            result_text = " " + ui_text['wrong']
            result_icon = ""
        
        # Shadow
        shadow_rect = pygame.Rect(result_container.x + 5, result_container.y + 5, 
                                 result_container.width, result_container.height)
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=20)
        
        # Main container
        pygame.draw.rect(screen, UI_COLORS['white'], result_container, border_radius=20)
        pygame.draw.rect(screen, result_color, result_container, 5, border_radius=20)
        
        # Result header
        header_rect = pygame.Rect(result_container.x, result_container.y, 
                                 result_container.width, 80)
        pygame.draw.rect(screen, result_color, header_rect, border_radius=20)
        
        result_surface = render_text(result_text, 'large', UI_COLORS['white'])
        result_surface_rect = result_surface.get_rect(center=(result_container.centerx, header_rect.centery))
        screen.blit(result_surface, result_surface_rect)
        
        # Show the word again
        word_display_rect = pygame.Rect(result_container.x + 50, result_container.y + 100, 
                                       result_container.width - 100, 80)
        pygame.draw.rect(screen, UI_COLORS['background'], word_display_rect, border_radius=10)
        pygame.draw.rect(screen, color_rgb, word_display_rect, 3, border_radius=10)
        
        word_again = render_text(word_name, 'large', color_rgb)
        word_again_rect = word_again.get_rect(center=word_display_rect.center)
        screen.blit(word_again, word_again_rect)
        
        # Answer details
        details_y = result_container.y + 200
        
        if not is_correct and result['color_index'] is not None and 0 <= result['color_index'] < len(colors):
            user_answer = colors[result['color_index']][0]
            correct_answer = colors[color_index][0]
            
            # Your answer
            user_card = pygame.Rect(result_container.x + 50, details_y, 
                                   result_container.width - 100, 40)
            pygame.draw.rect(screen, UI_COLORS['error'], user_card, border_radius=10)
            
            user_text = render_text(f"Your: {user_answer}", 'medium', UI_COLORS['white'])
            user_text_rect = user_text.get_rect(center=user_card.center)
            screen.blit(user_text, user_text_rect)
            
            # Correct answer
            correct_card = pygame.Rect(result_container.x + 50, details_y + 50, 
                                      result_container.width - 100, 40)
            pygame.draw.rect(screen, UI_COLORS['success'], correct_card, border_radius=10)
            
            correct_text = render_text(f"Correct: {correct_answer}", 'medium', UI_COLORS['white'])
            correct_text_rect = correct_text.get_rect(center=correct_card.center)
            screen.blit(correct_text, correct_text_rect)
            
            details_y += 100
        
        # Response time with performance indicator
        time_card = pygame.Rect(result_container.x + 50, details_y, 
                               result_container.width - 100, 50)
        
        # Color code based on response time
        if response_time < 2.0:
            time_color = UI_COLORS['success']
            time_icon = ""
        elif response_time < 4.0:
            time_color = UI_COLORS['warning']
            time_icon = ""
        else:
            time_color = UI_COLORS['error']
            time_icon = ""
        
        pygame.draw.rect(screen, time_color, time_card, border_radius=10)
        
        time_text = render_text(f"{time_icon} Time: {response_time:.2f}s", 'medium', UI_COLORS['white'])
        time_text_rect = time_text.get_rect(center=time_card.center)
        screen.blit(time_text, time_text_rect)
        
        pygame.display.flip()
        time.sleep(2.5)
        
        question_count += 1
    
    # Update stats
    current_stats['score'] = score
    current_stats['times'] = response_times
    current_stats['played'] = True
    
    # Show final results
    show_final_results(score, response_times)
    
    # Calculate and store efficiency
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        efficiency = score / avg_time if avg_time > 0 else 0
        update_efficiency_db(current_input_method, current_language, efficiency)
    
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
   
    # Cleanup
    for handler in input_handlers.values():
        if hasattr(handler, 'cleanup'):
            handler.cleanup()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()