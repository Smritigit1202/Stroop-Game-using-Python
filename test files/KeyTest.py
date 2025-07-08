import pygame
import random
import time
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stroop Effect - English & Hindi")
clock = pygame.time.Clock()

# Fonts
english_font = pygame.font.SysFont("Arial", 36)
hindi_font = pygame.font.Font("Mangal.ttf", 36)

# Colors
COLORS = {
    "Red": (255, 0, 0),
    "Green": (0, 255, 0),
    "Yellow": (255, 255, 0),
    "Blue": (0, 0, 255),
    "Pink": (255, 105, 180)
}

color_keys = {
    "Red": pygame.K_r,
    "Green": pygame.K_g,
    "Yellow": pygame.K_y,
    "Blue": pygame.K_b,
    "Pink": pygame.K_p
}

color_words_hindi = {
    "Red": "लाल",
    "Green": "हरा",
    "Yellow": "पीला",
    "Blue": "नीला",
    "Pink": "गुलाबी"
}

results = {"English": {}, "Hindi": {}}

# Utility function
def draw_text(text, font, color, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, y))
    screen.blit(render, rect)

def run_stroop_game(language):
    score = 0
    total_questions = 10
    start_time = time.time()

    for i in range(total_questions):
        word_color = random.choice(list(COLORS.keys()))
        font_color = random.choice(list(COLORS.values()))

        waiting_for_input = True
        while waiting_for_input:
            screen.fill((255, 255, 255))
            draw_text(f"Question {i+1}/{total_questions}", english_font, (0, 0, 0), 60)

            if language == "English":
                draw_text(word_color, english_font, font_color, HEIGHT//2)
            else:
                hindi_word = color_words_hindi[word_color]
                draw_text(hindi_word, hindi_font, font_color, HEIGHT//2)

            draw_text("Press: R G Y B P", english_font, (50, 50, 50), HEIGHT - 80)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    for color, key in color_keys.items():
                        if event.key == key:
                            if COLORS[color] == font_color:
                                score += 1
                            waiting_for_input = False
                            break

    end_time = time.time()
    total_time = round(end_time - start_time, 2)
    results[language] = {"score": score, "time": total_time}

def compare_results():
    screen.fill((255, 255, 255))
    draw_text("--- Comparison ---", english_font, (0, 0, 0), 80)

    if "score" in results["English"] and "score" in results["Hindi"]:
        eng = results["English"]
        hin = results["Hindi"]
        draw_text(f"English: {eng['score']}/10 in {eng['time']}s", english_font, (0, 100, 0), 200)
        draw_text(f"Hindi: {hin['score']}/10 in {hin['time']}s", english_font, (0, 0, 150), 260)

        eff_eng = eng['score'] / eng['time'] if eng['time'] > 0 else 0
        eff_hin = hin['score'] / hin['time'] if hin['time'] > 0 else 0

        if eff_eng > eff_hin:
            winner = "English"
        elif eff_hin > eff_eng:
            winner = "Hindi"
        else:
            winner = "Tie"

        draw_text(f"More Efficient: {winner}", english_font, (150, 0, 0), 340)
    else:
        draw_text("Play both modes to compare.", english_font, (150, 0, 0), 200)

    draw_text("Press M to return to Menu", english_font, (100, 100, 100), 500)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                waiting = False

# Main Menu
running = True
while running:
    screen.fill((255, 255, 255))
    draw_text("Stroop Effect Game", english_font, (0, 0, 0), 100)
    draw_text("1. Play in English", english_font, (0, 100, 0), 200)
    draw_text("2. Play in Hindi", english_font, (0, 0, 150), 260)
    draw_text("3. Compare Results", english_font, (150, 0, 0), 320)
    draw_text("4. Exit", english_font, (100, 100, 100), 380)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                run_stroop_game("English")
            elif event.key == pygame.K_2:
                run_stroop_game("Hindi")
            elif event.key == pygame.K_3:
                compare_results()
            elif event.key == pygame.K_4:
                running = False

pygame.quit()
