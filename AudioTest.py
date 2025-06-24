# -*- coding: utf-8 -*-
import pygame
import random
import speech_recognition as sr
import time
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("Stroop Effect Game - Voice Controlled")
clock = pygame.time.Clock()

# Languages and UI text
LANGUAGES = {
    'english': {
        'colors': [("Red", (255, 0, 0)), ("Green", (0, 255, 0)), ("Blue", (0, 0, 255)),
                   ("Yellow", (255, 255, 0)), ("Pink", (255, 20, 147))],
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
        }
    },
    'hindi': {
        'colors': [("लाल", (255, 0, 0)), ("हरा", (0, 255, 0)), ("नीला", (0, 0, 255)),
                   ("पीला", (255, 255, 0)), ("गुलाबी", (255, 20, 147))],
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

# Fonts
def load_fonts():
    font_large = pygame.font.SysFont("arial", 48)
    font_medium = pygame.font.SysFont("arial", 32)
    font_small = pygame.font.SysFont("arial", 24)
    return {'large': font_large, 'medium': font_medium, 'small': font_small}
fonts = load_fonts()

# Helpers
def render_text(text, size, color):
    return fonts[size].render(text, True, color)

def update_language(lang):
    global current_language, colors, ui_text
    current_language = lang
    colors = LANGUAGES[lang]['colors']
    ui_text = LANGUAGES[lang]['ui']

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
            avg_time = sum(times) / len(times) if times else 0
            details = render_text(f"Score: {score}, Avg Time: {avg_time:.2f}s", 'small', (0, 0, 0))
        else:
            details = render_text("Not played yet", 'small', (128, 128, 128))
        screen.blit(details, (120, y_offset + 40))

    # Determine better language
    e, h = language_stats['english'], language_stats['hindi']
    if e['played'] and h['played']:
        avg_e = sum(e['times']) / len(e['times']) if e['times'] else float('inf')
        avg_h = sum(h['times']) / len(h['times']) if h['times'] else float('inf')
        winner = "English" if avg_e < avg_h else ("Hindi" if avg_h < avg_e else "Both same")
        result = render_text(f"Better Response Time: {winner}", 'medium', (0, 150, 0))
        screen.blit(result, (100, 570))

    prompt = render_text("Press SPACE to return", 'small', (100, 100, 100))
    screen.blit(prompt, (100, 640))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        clock.tick(60)

# Language selection screen
def select_language():
    screen.fill((255, 255, 255))
    screen.blit(render_text("Choose Language / भाषा चुनें", 'large', (0, 0, 200)), (200, 120))
    screen.blit(render_text("Press 1 for English", 'medium', (0, 0, 0)), (250, 200))
    screen.blit(render_text("Press 2 for Hindi / हिंदी के लिए 2 दबाएं", 'medium', (0, 0, 0)), (250, 250))
    screen.blit(render_text("Press 3 to Compare English & Hindi Results", 'medium', (0, 0, 0)), (100, 300))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    update_language('english')
                    return 'english'
                elif event.key == pygame.K_2:
                    update_language('hindi')
                    return 'hindi'
                elif event.key == pygame.K_3:
                    compare_language_stats()
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
    pygame.display.flip()

# Main game logic
def main_game():
    selected_lang = select_language()
    if not selected_lang:
        pygame.quit()
        return

    waiting = True
    while waiting:
        show_instructions()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: waiting = False
                elif event.key == pygame.K_l: return main_game()
                elif event.key == pygame.K_ESCAPE: pygame.quit(); return
        clock.tick(60)

    score = 0
    total_questions = 10
    question_count = 0
    language_stats[current_language]['times'] = []

    while question_count < total_questions:
        word_name = random.choice(colors)[0]
        correct_idx = random.randint(0, 4)
        correct_name, correct_color = colors[correct_idx]

        screen.fill((255, 255, 255))
        screen.blit(render_text(f"{ui_text['question']} {question_count + 1}/{total_questions}", 'medium', (0, 0, 0)), (20, 20))
        screen.blit(render_text(f"{ui_text['score']}: {score}", 'medium', (0, 0, 0)), (650, 20))
        word_surface = render_text(word_name, 'large', correct_color)
        screen.blit(word_surface, word_surface.get_rect(center=(450, 250)))
        screen.blit(render_text(ui_text['instruction'], 'small', (0, 0, 0)), (250, 350))
        pygame.display.flip()

        start_time = time.time()
        answered = False
        while not answered and time.time() - start_time < 5:
            index = get_voice_input()
            if index is not None:
                time_taken = time.time() - start_time
                language_stats[current_language]['times'].append(time_taken)
                answered = True
                correct = (index == correct_idx)
                score += 1 if correct else 0
                result = ui_text['correct'] if correct else ui_text['wrong']
                color = (0, 200, 0) if correct else (200, 0, 0)
                screen.fill((255, 255, 255))
                screen.blit(render_text(result, 'large', color), (350, 350))
                pygame.display.flip()
                time.sleep(1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
            clock.tick(60)

        if not answered:
            screen.fill((255, 255, 255))
            screen.blit(render_text(ui_text['timeout'], 'large', (255, 165, 0)), (300, 350))
            pygame.display.flip()
            time.sleep(1)
        question_count += 1

    # Save stats
    language_stats[current_language]['score'] = score
    language_stats[current_language]['played'] = True

    # Final Score
    screen.fill((255, 255, 255))
    screen.blit(render_text(f"{ui_text['final_score']}: {score}/{total_questions}", 'large', (0, 100, 0)), (200, 250))
    accuracy = (score / total_questions) * 100
    screen.blit(render_text(f"{ui_text['accuracy']}: {accuracy:.1f}%", 'medium', (0, 0, 0)), (300, 300))
    screen.blit(render_text(ui_text['restart'], 'small', (0, 0, 0)), (250, 400))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return main_game()
                elif event.key == pygame.K_ESCAPE: pygame.quit(); return
        clock.tick(60)

if __name__ == "__main__":
    main_game()
