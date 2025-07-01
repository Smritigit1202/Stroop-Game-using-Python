import cv2
import pygame
import time
import random
import os
import math
import sys

# Initialize pygame
pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stroop QR Challenge")

# Fonts
title_font = pygame.font.SysFont("Arial", 48, bold=True)
large_font = pygame.font.SysFont("Arial", 64, bold=True)
medium_font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)
score_font = pygame.font.SysFont("Arial", 28, bold=True)

# Enhanced Hindi font loading with multiple fallbacks
# Enhanced Hindi font loading with your specific path
def load_hindi_fonts():
    """Try multiple methods to load Hindi fonts"""
    hindi_fonts = {
        'large': None,
        'medium': None,
        'small': None,
        'title': None
    }
    
    # Font sizes
    sizes = {'large': 64, 'medium': 36, 'small': 24, 'title': 48}
    
    print("Attempting to load Hindi fonts...")
    
    # First try your specific Mangal.ttf path
    your_mangal_path = r"C:\Users\abhis\OneDrive\Desktop\Game Making\STROOOP_GAME\Stroop-Game-using-Python\Mangal.ttf"
    
    if os.path.exists(your_mangal_path):
        try:
            print(f"Found Mangal font at: {your_mangal_path}")
            # Test the font first
            test_font = pygame.font.Font(your_mangal_path, 32)
            test_text = "हिंदी"
            test_surface = test_font.render(test_text, True, (0, 0, 0))
            
            # If test passes, load all sizes
            for size_key, size_val in sizes.items():
                hindi_fonts[size_key] = pygame.font.Font(your_mangal_path, size_val)
            
            print("Successfully loaded Hindi font from your specified path!")
            return hindi_fonts
            
        except Exception as e:
            print(f"Failed to load font from your path: {e}")
    else:
        print(f"Font file not found at: {your_mangal_path}")
    
    # List of Hindi fonts to try (in order of preference) - system fonts
    hindi_font_names = [
        "Mangal",           # Windows default Hindi font
        "Noto Sans Devanagari",  # Google Noto font
        "Lohit Devanagari", # Linux common font
        "Kalpurush",        # Bengali/Hindi font
        "FreeSans",         # Free font with Devanagari support
        "DejaVu Sans",      # Has some Devanagari support
        "Arial Unicode MS", # Windows font with Unicode support
        "Lucida Sans Unicode" # Another Unicode font
    ]
    
    # Try each system font name
    for font_name in hindi_font_names:
        try:
            # Try system font first
            test_large = pygame.font.SysFont(font_name, 64)
            
            # Test if the font can render Hindi text properly
            test_text = "हिंदी"
            test_surface = test_large.render(test_text, True, (0, 0, 0))
            
            # If we get here without error, the font works
            for size_key, size_val in sizes.items():
                hindi_fonts[size_key] = pygame.font.SysFont(font_name, size_val, bold=(size_key in ['large', 'title']))
            
            print(f"Successfully loaded Hindi system font: {font_name}")
            return hindi_fonts
            
        except Exception as e:
            print(f"Failed to load system font {font_name}: {e}")
            continue
    
    # Try other common font file paths as fallback
    possible_font_paths = [
        "C:/Windows/Fonts/mangal.ttf",
        "C:/Windows/Fonts/MANGAL.TTF", 
        "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "./fonts/mangal.ttf",  # Local font file
        "./fonts/NotoSansDevanagari-Regular.ttf",
        "./Mangal.ttf",  # Current directory
        "fonts/Mangal.ttf"  # fonts subdirectory
    ]
    
    for font_path in possible_font_paths:
        if os.path.exists(font_path):
            try:
                for size_key, size_val in sizes.items():
                    hindi_fonts[size_key] = pygame.font.Font(font_path, size_val)
                print(f"Successfully loaded Hindi font from: {font_path}")
                return hindi_fonts
            except Exception as e:
                print(f"Failed to load font from {font_path}: {e}")
                continue
    
    # Last resort: use default fonts with Unicode support
    print("Using fallback fonts for Hindi text")
    try:
        for size_key, size_val in sizes.items():
            # Try to get a font with better Unicode support
            hindi_fonts[size_key] = pygame.font.Font(None, size_val)
    except:
        # Ultimate fallback
        for size_key, size_val in sizes.items():
            hindi_fonts[size_key] = pygame.font.SysFont("Arial", size_val, bold=(size_key in ['large', 'title']))
    
    return hindi_fonts

# Load Hindi fonts
hindi_fonts = load_hindi_fonts()

# Test Hindi rendering
def test_hindi_rendering():
    """Test if Hindi text renders properly"""
    test_text = "हिंदी परीक्षण"
    try:
        test_surface = hindi_fonts['medium'].render(test_text, True, (0, 0, 0))
        # Check if the surface has reasonable dimensions
        if test_surface.get_width() > 10 and test_surface.get_height() > 10:
            print("Hindi text rendering test: PASSED")
            return True
        else:
            print("Hindi text rendering test: FAILED (empty surface)")
            return False
    except Exception as e:
        print(f"Hindi text rendering test: FAILED ({e})")
        return False

# Run the test
hindi_works = test_hindi_rendering()

# Colors - Lighter theme
COLORS = {
    "background": (240, 245, 250),
    "card_bg": (255, 255, 255),
    "white": (255, 255, 255),
    "black": (30, 30, 30),
    "green": (34, 197, 94),
    "red": (239, 68, 68),
    "blue": (59, 130, 246),
    "orange": (251, 146, 60),
    "purple": (168, 85, 247),
    "gray": (107, 114, 128),
    "dark_gray": (75, 85, 99),
    "light_gray": (229, 231, 235),
    "text_primary": (17, 24, 39),
    "text_secondary": (75, 85, 99)
}

# Language configurations
LANGUAGES = {
    "english": {
        "name": "English",
        "colors": [("Red", (255, 50, 50)), ("Green", (50, 255, 50)), ("Blue", (50, 50, 255))],
        "ui": {
            "title": "STROOP QR CHALLENGE",
            "subtitle": "Test your cognitive flexibility!",
            "start_game": "START GAME",
            "quit": "QUIT",
            "select_language": "SELECT LANGUAGE",
            "instructions": [
                "1. Read the COLOR, not the word",
                "2. Show correct QR code to camera",
                "3. You have 7 seconds per question"
            ],
            "score": "Score",
            "question": "Question",
            "show_qr": "Show QR code for the COLOR you see",
            "camera_active": "📷 Camera Active - Show QR Code",
            "correct": "CORRECT!",
            "incorrect": "INCORRECT!",
            "timeout": "TIME OUT!",
            "game_complete": "GAME COMPLETE!",
            "excellent": "Excellent work!",
            "good": "Good job!",
            "practice": "Keep practicing!",
            "play_again": "PLAY AGAIN",
            "main_menu": "MAIN MENU",
            "font_warning": ""
        },
        "fonts": {
            "title": title_font,
            "large": large_font,
            "medium": medium_font,
            "small": small_font
        }
    },
    "hindi": {
        "name": "हिंदी",
        "colors": [("लाल", (255, 50, 50)), ("हरा", (50, 255, 50)), ("नीला", (50, 50, 255))],
        "ui": {
            "title": "स्ट्रूप QR चुनौती",
            "subtitle": "अपनी संज्ञानात्मक लचीलेपन का परीक्षण करें!",
            "start_game": "खेल शुरू करें",
            "quit": "बाहर निकलें",
            "select_language": "भाषा चुनें",
            "instructions": [
                "1. शब्द नहीं, रंग पढ़ें",
                "2. कैमरे को सही QR कोड दिखाएं",
                "3. आपके पास प्रति प्रश्न 7 सेकंड हैं"
            ],
            "score": "स्कोर",
            "question": "प्रश्न",
            "show_qr": "आपको दिखाई देने वाले रंग के लिए QR कोड दिखाएं",
            "camera_active": "📷 कैमरा सक्रिय - QR कोड दिखाएं",
            "correct": "सही!",
            "incorrect": "गलत!",
            "timeout": "समय समाप्त!",
            "game_complete": "खेल पूरा!",
            "excellent": "बहुत बढ़िया!",
            "good": "अच्छा काम!",
            "practice": "अभ्यास जारी रखें!",
            "play_again": "फिर से खेलें",
            "main_menu": "मुख्य मेनू",
            "font_warning": "हिंदी फॉन्ट लोड नहीं हो सका - अंग्रेजी का उपयोग करें" if not hindi_works else ""
        },
        "fonts": {
            "title": hindi_fonts['title'],
            "large": hindi_fonts['large'],
            "medium": hindi_fonts['medium'],
            "small": hindi_fonts['small']
        }
    }
}

# Add font fallback warning
if not hindi_works:
    print("\n" + "="*50)
    print("WARNING: Hindi fonts may not display properly!")
    print("To fix this, install a Hindi font like:")
    print("- Windows: Mangal (usually pre-installed)")
    print("- Linux: sudo apt-get install fonts-lohit-deva")
    print("- Or download Noto Sans Devanagari from Google Fonts")
    print("="*50 + "\n")

# Color mapping for QR codes (maps Hindi/English color names to English QR codes)
COLOR_QR_MAPPING = {
    # English
    "red": "red",
    "green": "green", 
    "blue": "blue",
    # Hindi
    "लाल": "red",
    "हरा": "green",
    "नीला": "blue"
}

# Global language setting
current_language = "english"

# Load QR codes
qr_codes = {}
qr_dir = "qrs"
detector = cv2.QRCodeDetector()

for color_name in ["red", "green", "blue"]:
    path = os.path.join(qr_dir, f"qr_{color_name}.jpg")
    if os.path.exists(path):
        img = cv2.imread(path)
        if img is not None:
            val, _, _ = detector.detectAndDecode(img)
            if val.strip().lower() == color_name:
                qr_codes[val.lower()] = color_name
            else:
                print(f"QR for {color_name} not recognized or mismatched!")
        else:
            print(f"Failed to load: {path}")
    else:
        print(f"File not found: {path}")

print("Loaded QR codes:", qr_codes)

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=COLORS["white"], font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font or medium_font
        self.hovered = False
        
    def draw(self, surface):
        # Draw button with hover effect and shadow
        if self.hovered:
            # Shadow effect
            shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, COLORS["gray"], shadow_rect, border_radius=12)
            button_color = tuple(min(255, c + 30) for c in self.color)
        else:
            button_color = self.color
            
        pygame.draw.rect(surface, button_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, COLORS["light_gray"], self.rect, 2, border_radius=12)
        
        # Draw text with error handling
        try:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error rendering button text '{self.text}': {e}")
            # Fallback to ASCII approximation if needed
            fallback_text = "?" * len(self.text)
            text_surface = medium_font.render(fallback_text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def safe_render_text(font, text, color, fallback_font=None):
    """Safely render text with fallback options"""
    try:
        return font.render(text, True, color)
    except Exception as e:
        print(f"Error rendering text '{text}': {e}")
        if fallback_font:
            try:
                return fallback_font.render(text, True, color)
            except:
                pass
        # Last resort: render placeholder
        return medium_font.render("???", True, color)

def draw_gradient_background(surface):
    """Draw a light gradient background"""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(COLORS["background"][0] * (1 - ratio * 0.1))
        g = int(COLORS["background"][1] * (1 - ratio * 0.1))
        b = int(COLORS["background"][2] * (1 - ratio * 0.1))
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def draw_card(surface, x, y, width, height, color=COLORS["card_bg"], border_color=COLORS["light_gray"]):
    """Draw a modern card-style container with shadow"""
    # Shadow
    shadow_offset = 4
    pygame.draw.rect(surface, COLORS["gray"], 
                    (x + shadow_offset, y + shadow_offset, width, height), 
                    border_radius=20)
    # Main card
    pygame.draw.rect(surface, color, (x, y, width, height), border_radius=20)
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2, border_radius=20)

def draw_progress_bar(surface, x, y, width, height, progress, bg_color=COLORS["dark_gray"], fill_color=COLORS["blue"]):
    """Draw a progress bar"""
    pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=height//2)
    if progress > 0:
        fill_width = int(width * progress)
        pygame.draw.rect(surface, fill_color, (x, y, fill_width, height), border_radius=height//2)

def draw_timer_circle(surface, x, y, radius, time_left, total_time):
    """Draw a circular timer"""
    center = (x, y)
    progress = time_left / total_time
    
    # Background circle
    pygame.draw.circle(surface, COLORS["light_gray"], center, radius, 6)
    
    # Progress arc
    if progress > 0:
        color = COLORS["green"] if progress > 0.5 else COLORS["orange"] if progress > 0.3 else COLORS["red"]
        end_angle = -90 + (360 * progress)
        # Draw arc segments for smooth circle
        for i in range(int(360 * progress)):
            angle = math.radians(-90 + i)
            start_pos = (center[0] + (radius - 3) * math.cos(angle), 
                        center[1] + (radius - 3) * math.sin(angle))
            end_pos = (center[0] + (radius + 3) * math.cos(angle), 
                      center[1] + (radius + 3) * math.sin(angle))
            pygame.draw.line(surface, color, start_pos, end_pos, 6)
    
    # Timer text
    timer_text = safe_render_text(LANGUAGES[current_language]["fonts"]["large"], 
                                 str(int(time_left)), COLORS["text_primary"], large_font)
    timer_rect = timer_text.get_rect(center=center)
    surface.blit(timer_text, timer_rect)

def show_language_selection():
    """Display language selection screen"""
    global current_language
    clock = pygame.time.Clock()
    
    english_button = Button(SCREEN_WIDTH//2 - 250, 350, 200, 80, "English", COLORS["blue"], font=large_font)
    hindi_button = Button(SCREEN_WIDTH//2 + 50, 350, 200, 80, "हिंदी", COLORS["green"], font=hindi_fonts['large'])
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if english_button.handle_event(event):
                current_language = "english"
                return "menu"
            if hindi_button.handle_event(event):
                current_language = "hindi"
                return "menu"
        
        # Draw background
        draw_gradient_background(screen)
        
        # Title card
        draw_card(screen, SCREEN_WIDTH//2 - 300, 100, 600, 150)
        
        # Title
        title_text = safe_render_text(title_font, "SELECT LANGUAGE", COLORS["text_primary"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 140))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = safe_render_text(hindi_fonts['medium'], "भाषा चुनें", COLORS["text_secondary"], medium_font)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Font warning if needed
        if not hindi_works:
            warning_text = safe_render_text(small_font, "Hindi fonts may not display properly", COLORS["red"])
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, 230))
            screen.blit(warning_text, warning_rect)
        
        # Draw buttons
        english_button.draw(screen)
        hindi_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    return "quit"

def show_menu():
    """Display the main menu"""
    lang = LANGUAGES[current_language]
    clock = pygame.time.Clock()
    
    start_button = Button(SCREEN_WIDTH//2 - 120, 420, 240, 60, lang["ui"]["start_game"], 
                         COLORS["green"], font=lang["fonts"]["medium"])
    language_button = Button(SCREEN_WIDTH//2 - 120, 500, 240, 60, lang["ui"]["select_language"], 
                           COLORS["blue"], font=lang["fonts"]["medium"])
    quit_button = Button(SCREEN_WIDTH//2 - 120, 580, 240, 60, lang["ui"]["quit"], 
                        COLORS["red"], font=lang["fonts"]["medium"])
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if start_button.handle_event(event):
                return "start"
            if language_button.handle_event(event):
                return "language"
            if quit_button.handle_event(event):
                return "quit"
        
        # Draw background
        draw_gradient_background(screen)
        
        # Title card
        draw_card(screen, SCREEN_WIDTH//2 - 350, 80, 700, 200)
        
        # Title
        title_text = safe_render_text(lang["fonts"]["title"], lang["ui"]["title"], 
                                    COLORS["text_primary"], title_font)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 140))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = safe_render_text(lang["fonts"]["medium"], lang["ui"]["subtitle"], 
                                       COLORS["text_secondary"], medium_font)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 190))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions card
        draw_card(screen, SCREEN_WIDTH//2 - 350, 300, 700, 100)
        
        for i, instruction in enumerate(lang["ui"]["instructions"]):
            inst_text = safe_render_text(lang["fonts"]["small"], instruction, 
                                       COLORS["text_primary"], small_font)
            screen.blit(inst_text, (SCREEN_WIDTH//2 - 320, 320 + i * 25))
        
        # Font warning for Hindi
        if current_language == "hindi" and not hindi_works:
            warning_text = safe_render_text(small_font, "Note: Hindi display may be limited", COLORS["orange"])
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, 280))
            screen.blit(warning_text, warning_rect)
        
        # Draw buttons
        start_button.draw(screen)
        language_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    return "quit"

def show_game_screen(word, color, score, question_num, total_questions, time_left):
    """Display the main game screen"""
    lang = LANGUAGES[current_language]
    draw_gradient_background(screen)
    
    # Header card
    draw_card(screen, 30, 20, SCREEN_WIDTH - 60, 80)
    
    # Score
    score_text = safe_render_text(score_font, f"{lang['ui']['score']}: {score}/{total_questions}", 
                                COLORS["text_primary"], score_font)
    screen.blit(score_text, (60, 45))
    
    # Question counter
    question_text = safe_render_text(score_font, f"{lang['ui']['question']} {question_num}/{total_questions}", 
                                   COLORS["text_primary"], score_font)
    question_rect = question_text.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(question_text, question_rect)
    
    # Progress bar
    progress = (question_num - 1) / total_questions
    draw_progress_bar(screen, SCREEN_WIDTH - 280, 35, 200, 30, progress)
    
    # Main game area card
    draw_card(screen, SCREEN_WIDTH//2 - 400, 130, 800, 350)
    
    # Word display
    word_text = safe_render_text(lang["fonts"]["large"], word, color, large_font)
    word_rect = word_text.get_rect(center=(SCREEN_WIDTH//2, 230))
    screen.blit(word_text, word_rect)
    
    # Instruction
    instruction_text = safe_render_text(lang["fonts"]["medium"], lang["ui"]["show_qr"], 
                                      COLORS["text_secondary"], medium_font)
    instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 300))
    screen.blit(instruction_text, instruction_rect)
    
    # Camera status card
    draw_card(screen, SCREEN_WIDTH//2 - 250, 360, 500, 60, COLORS["blue"])
    camera_text = safe_render_text(lang["fonts"]["medium"], lang["ui"]["camera_active"], 
                                 COLORS["white"], medium_font)
    camera_rect = camera_text.get_rect(center=(SCREEN_WIDTH//2, 390))
    screen.blit(camera_text, camera_rect)
    
    # Timer circle
    draw_timer_circle(screen, SCREEN_WIDTH//2, 550, 60, time_left, 7)
    
    pygame.display.flip()

def show_feedback(feedback_text, is_correct):
    """Show feedback for correct/incorrect answers"""
    lang = LANGUAGES[current_language]
    color = COLORS["green"] if is_correct else COLORS["red"]
    
    # Feedback card
    draw_card(screen, SCREEN_WIDTH//2 - 200, 300, 400, 100, color)
    
    feedback_surface = safe_render_text(lang["fonts"]["large"], feedback_text, 
                                      COLORS["white"], large_font)
    feedback_rect = feedback_surface.get_rect(center=(SCREEN_WIDTH//2, 350))
    screen.blit(feedback_surface, feedback_rect)
    
    pygame.display.flip()

def show_final_score(score, total_questions):
    """Display final score screen"""
    lang = LANGUAGES[current_language]
    clock = pygame.time.Clock()
    percentage = (score / total_questions) * 100
    
    # Properly positioned buttons with no overlap
    play_again_button = Button(SCREEN_WIDTH//2 - 250, 480, 200, 60, lang["ui"]["play_again"], 
                              COLORS["green"], font=lang["fonts"]["medium"])
    menu_button = Button(SCREEN_WIDTH//2 + 50, 480, 200, 60, lang["ui"]["main_menu"], 
                        COLORS["blue"], font=lang["fonts"]["medium"])
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if play_again_button.handle_event(event):
                return "play_again"
            if menu_button.handle_event(event):
                return "menu"
        
        draw_gradient_background(screen)
        
        # Results card - properly centered
        draw_card(screen, SCREEN_WIDTH//2 - 350, 120, 700, 300)
        
        # Title
        title_text = safe_render_text(lang["fonts"]["title"], lang["ui"]["game_complete"], 
                                    COLORS["text_primary"], title_font)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        screen.blit(title_text, title_rect)
        
        # Score - large and prominent
        score_text = safe_render_text(lang["fonts"]["large"], f"{score}/{total_questions}", 
                                    COLORS["text_primary"], large_font)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(score_text, score_rect)
        
        # Percentage
        percent_text = safe_render_text(lang["fonts"]["medium"], f"{percentage:.1f}%", 
                                      COLORS["text_secondary"], medium_font)
        percent_rect = percent_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        screen.blit(percent_text, percent_rect)
        
        # Performance message
        if percentage >= 80:
            message = lang["ui"]["excellent"]
            message_color = COLORS["green"]
        elif percentage >= 60:
            message = lang["ui"]["good"]
            message_color = COLORS["blue"]
        else:
            message = lang["ui"]["practice"]
            message_color = COLORS["orange"]
        
        message_text = safe_render_text(lang["fonts"]["medium"], message, 
                                      message_color, medium_font)
        message_rect = message_text.get_rect(center=(SCREEN_WIDTH//2, 360))
        screen.blit(message_text, message_rect)
        
        # Buttons - properly spaced
        play_again_button.draw(screen)
        menu_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    return "quit"

def get_qr_from_camera(timeout=7):
    """Camera function to detect QR codes"""
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    start = time.time()
    result = None
    
    while time.time() - start < timeout:
        current_time = time.time()
        time_left = timeout - (current_time - start)
        
        ret, frame = cap.read()
        if not ret:
            continue

        val, points, _ = detector.detectAndDecode(frame)
        if val:
            print(f"[DEBUG] Detected QR from camera: '{val}'")
            result = val.strip().lower()
            break
        
        cv2.imshow("Show QR to Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return result

def game():
    """Main game function with enhanced UI"""
    lang = LANGUAGES[current_language]
    score = 0
    total_questions = 10
    
    for q in range(1, total_questions + 1):
        word, word_color = random.choice(lang["colors"])
        display_color_name, display_color_rgb = random.choice(lang["colors"])
        # Continue from where the code was cut off
        while word == display_color_name:
            display_color_name, display_color_rgb = random.choice(lang["colors"])
        
        # Show game screen with timer
        start_time = time.time()
        timeout = 7
        answered = False
        
        while not answered and (time.time() - start_time) < timeout:
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Calculate remaining time
            elapsed = time.time() - start_time
            time_left = max(0, timeout - elapsed)
            
            # Show game screen
            show_game_screen(word, display_color_rgb, score, q, total_questions, time_left)
            
            # Small delay to prevent excessive CPU usage
            pygame.time.wait(50)
            
            # Check if time is up
            if time_left <= 0:
                break
        
        # Get QR code from camera
        print(f"Question {q}: Word='{word}', DisplayColor='{display_color_name}'")
        print(f"Expected QR: '{COLOR_QR_MAPPING.get(display_color_name, 'unknown')}'")
        
        detected_qr = get_qr_from_camera(timeout=max(1, int(time_left)))
        
        # Check answer
        expected_color = COLOR_QR_MAPPING.get(display_color_name.lower(), "")
        is_correct = False
        
        if detected_qr:
            print(f"[DEBUG] Detected: '{detected_qr}', Expected: '{expected_color}'")
            if detected_qr == expected_color:
                is_correct = True
                score += 1
                show_feedback(lang["ui"]["correct"], True)
            else:
                show_feedback(lang["ui"]["incorrect"], False)
        else:
            show_feedback(lang["ui"]["timeout"], False)
        
        # Brief pause to show feedback
        time.sleep(1.5)
    
    # Show final score
    return show_final_score(score, total_questions)

def main():
    """Main function to handle game flow"""
    state = "language"  # Start with language selection
    
    while True:
        if state == "language":
            state = show_language_selection()
        elif state == "menu":
            state = show_menu()
        elif state == "start":
            state = game()
        elif state == "play_again":
            state = game()
        elif state == "quit":
            break
        else:
            # Fallback to menu for unknown states
            state = "menu"
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()