import cv2
import pygame
import time
import random
import os

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Stroop QR Game")
font = pygame.font.SysFont("Arial", 36)

# Colors and labels
colors = [("Red", (255, 0, 0)), ("Green", (0, 255, 0)), ("Blue", (0, 0, 255))]

# Load QR codes (images already generated with "Red", "Green", "Blue" encoded inside)
qr_codes = {}
qr_dir = "qrs"
detector = cv2.QRCodeDetector()

for label, _ in colors:
    path = os.path.join(qr_dir, f"qr_{label.lower()}.jpg")
    img = cv2.imread(path)
    if img is None:
        print(f"Failed to load: {path}")
        continue
    val, _, _ = detector.detectAndDecode(img)
    if val.strip().lower() == label.lower():
        qr_codes[val.lower()] = label
    else:
        print(f"QR for {label} not recognized or mismatched!")

print("Loaded QR codes:", qr_codes)

def show_text(text, color=(0, 0, 0), y=300):
    screen.fill((255, 255, 255))
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(400, y))
    screen.blit(rendered, rect)
    pygame.display.flip()

def get_qr_from_camera(timeout=10):
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()
    start = time.time()
    result = None

    while time.time() - start < timeout:
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
    score = 0
    total_questions = 5

    for q in range(total_questions):
        word, word_color = random.choice(colors)
        display_color_name, display_color_rgb = random.choice(colors)
        while word == display_color_name:
            display_color_name, display_color_rgb = random.choice(colors)

        # Display word in a different color
        show_text(word, color=display_color_rgb)

        start_time = time.time()
        detected = get_qr_from_camera(timeout=7)
        correct = display_color_name.lower()

        if detected == correct:
            show_text("✔ Correct!", (0, 200, 0))
            print("✔ Correct!")
            score += 1
        else:
            show_text("✘ Incorrect or Timeout", (200, 0, 0))
            print("✘ Incorrect or Timeout")

        time.sleep(2)

    show_text(f"Final Score: {score}/{total_questions}", (0, 0, 200), y=250)
    time.sleep(4)
    pygame.quit()

if __name__ == "__main__":
    game()
