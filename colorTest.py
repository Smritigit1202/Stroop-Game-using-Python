import cv2
import pygame
import random
import time
import os
import numpy as np

# Initialize pygame and camera
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Stroop Effect - Color Card Game")
clock = pygame.time.Clock()

# Fonts
english_font = pygame.font.SysFont("Arial", 48)
hindi_font = pygame.font.Font("mangal.ttf", 48)

# Game data
color_names_en = ["Red", "Green", "Blue"]
color_names_hi = ["लाल", "हरा", "नीला"]
rgb_values = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

# Camera setup
cap = cv2.VideoCapture(0)

def generate_question():
    return random.randint(0, 2), random.randint(0, 2)

def detect_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    height, width, _ = frame.shape

    center_h = height // 2
    center_w = width // 2
    center = hsv[height//2 - center_h//4 : height//2 + center_h//4,
                 width//2 - center_w//4 : width//2 + center_w//4]

    total_pixels = center.size / 3

    red_mask = cv2.inRange(center, np.array([0, 100, 100]), np.array([10, 255, 255])) + \
               cv2.inRange(center, np.array([160, 100, 100]), np.array([179, 255, 255]))
    green_mask = cv2.inRange(center, np.array([36, 50, 70]), np.array([89, 255, 255]))
    blue_mask = cv2.inRange(center, np.array([90, 50, 70]), np.array([128, 255, 255]))

    red_ratio = np.sum(red_mask > 0) / total_pixels
    green_ratio = np.sum(green_mask > 0) / total_pixels
    blue_ratio = np.sum(blue_mask > 0) / total_pixels

    result = -1
    label = "None"
    color = (100, 100, 100)
    threshold = 0.08  # More forgiving

    if max(red_ratio, green_ratio, blue_ratio) >= threshold:
        if red_ratio >= green_ratio and red_ratio >= blue_ratio:
            result, label, color = 0, "Red", (0, 0, 255)
        elif green_ratio >= red_ratio and green_ratio >= blue_ratio:
            result, label, color = 1, "Green", (0, 255, 0)
        else:
            result, label, color = 2, "Blue", (255, 0, 0)

    overlay = frame.copy()
    cv2.rectangle(overlay,
                  (width//2 - center_w//4, height//2 - center_h//4),
                  (width//2 + center_w//4, height//2 + center_h//4),
                  (255, 255, 255), 2)
    cv2.putText(overlay, f"Detecting: {label}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow("Camera - Show Color", overlay)

    return result

def play_game(language='en'):
    questions = 10
    score = 0
    total_time = 0

    for _ in range(questions):
        text_idx, color_idx = generate_question()
        question_text = color_names_en[text_idx] if language == 'en' else color_names_hi[text_idx]
        color_value = rgb_values[color_idx]
        font = english_font if language == 'en' else hindi_font

        screen.fill((255, 255, 255))
        text_surface = font.render(question_text, True, color_value)
        screen.blit(text_surface, (400 - text_surface.get_width() // 2, 200))
        pygame.display.flip()

        start_time = time.time()
        timeout = 5
        answered = False

        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            detected_color = detect_color(frame)

            # 🎯 If the detected color matches the expected color, count it as answered
            if detected_color == color_idx:
                answered = True
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

            remaining = timeout - (time.time() - start_time)
            countdown = english_font.render(f"Time Left: {int(remaining)}s", True, (0, 0, 0))
            screen.fill((255, 255, 255))
            screen.blit(text_surface, (400 - text_surface.get_width() // 2, 200))
            screen.blit(countdown, (300, 400))
            pygame.display.flip()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        end_time = time.time()
        total_time += (end_time - start_time)

        print(f"Expected: {color_idx}, Detected: {detected_color}")  # Debug

        if answered:
            score += 1
            feedback = "Correct!"
            color = (0, 200, 0)
        else:
            feedback = "Wrong or Time's Up"
            color = (200, 0, 0)

        screen.fill((255, 255, 255))
        screen.blit(text_surface, (400 - text_surface.get_width() // 2, 200))
        feedback_surface = english_font.render(feedback, True, color)
        screen.blit(feedback_surface, (300, 400))
        pygame.display.flip()
        time.sleep(1)
        cv2.destroyAllWindows()

    return score, total_time


def show_result(score_en, time_en, score_hi, time_hi):
    screen.fill((255, 255, 255))
    font = english_font
    eff_en = score_en / time_en if time_en else 0
    eff_hi = score_hi / time_hi if time_hi else 0
    winner = "English" if eff_en > eff_hi else "Hindi"

    lines = [
        f"English - Score: {score_en}, Time: {time_en:.2f}s, Efficiency: {eff_en:.2f}",
        f"Hindi   - Score: {score_hi}, Time: {time_hi:.2f}s, Efficiency: {eff_hi:.2f}",
        f"Better Performance: {winner}"
    ]

    for i, line in enumerate(lines):
        text = font.render(line, True, (0, 0, 0))
        screen.blit(text, (50, 150 + i * 70))

    pygame.display.flip()
    time.sleep(10)

def language_menu():
    while True:
        screen.fill((255, 255, 255))
        title = english_font.render("Choose Language", True, (0, 0, 0))
        en = english_font.render("1. English", True, (0, 0, 0))
        hi = english_font.render("2. Hindi", True, (0, 0, 0))
        compare = english_font.render("3. Compare Results", True, (0, 0, 0))

        screen.blit(title, (250, 100))
        screen.blit(en, (250, 200))
        screen.blit(hi, (250, 300))
        screen.blit(compare, (250, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'en'
                elif event.key == pygame.K_2:
                    return 'hi'
                elif event.key == pygame.K_3:
                    return 'compare'
            elif event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                exit()

# Main loop
score_data = {}
while True:
    mode = language_menu()
    if mode == 'en':
        score, total_time = play_game('en')
        score_data['en'] = (score, total_time)
    elif mode == 'hi':
        score, total_time = play_game('hi')
        score_data['hi'] = (score, total_time)
    elif mode == 'compare':
        if 'en' in score_data and 'hi' in score_data:
            show_result(score_data['en'][0], score_data['en'][1],
                        score_data['hi'][0], score_data['hi'][1])
        else:
            screen.fill((255, 255, 255))
            msg = english_font.render("Play both languages first!", True, (255, 0, 0))
            screen.blit(msg, (200, 250))
            pygame.display.flip()
            time.sleep(3)
