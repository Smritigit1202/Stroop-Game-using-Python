# STROOP EFFECT GAME - Bilingual Edition
# Made using pygame and Python 3.x

import pygame
import random

pygame.init()
screen = pygame.display.set_mode((600, 600))
background = pygame.Surface(screen.get_size())
pygame.display.set_caption("Stroop Effect Game")

# Language definitions
languages = {
    "English": [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("Yellow", (255, 255, 0)),
        ("Pink", (255, 20, 147)),
        ("Purple", (128, 0, 128))
    ],
    "Hindi": [
        ("लाल", (255, 0, 0)),
        ("हरा", (0, 255, 0)),
        ("नीला", (0, 0, 255)),
        ("पीला", (255, 255, 0)),
        ("गुलाबी", (255, 20, 147)),
        ("बैंगनी", (128, 0, 128))
    ]
}

user_results = {}

def convert_to_hindi_numerals(number):
    hindi_digits = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }
    return ''.join(hindi_digits[digit] for digit in str(number))

def get_font(language=None, size=50):
    if language == "Hindi":
        return pygame.font.Font("Mangal.ttf", size)
    return pygame.font.SysFont("arial", size)

class Button:
    def __init__(self, screen, left, top, width, height, name):
        self.label = name
        self.buttonColour = (255, 0, 0)
        self.buttonRect = pygame.Rect(left, top, width, height)
        self.buttonSurface = pygame.Surface(self.buttonRect.size)

    def drawButton(self, screen):
        self.buttonSurface.fill(self.buttonColour)
        self.buttonSurface.convert()
        screen.blit(self.buttonSurface, (self.buttonRect.x, self.buttonRect.y))
        pygame.draw.rect(self.buttonSurface, self.buttonColour, self.buttonRect, 1)
        self.drawText(screen)

    def drawText(self, screen):
        buttonTextFont = get_font("English", 50)  # fixed: defaulting to English
        buttonText = buttonTextFont.render(self.label, True, (0, 55, 90), self.buttonColour)
        buttonText = buttonText.convert()
        screen.blit(buttonText, self.buttonRect)

class ColouredWord:
    def __init__(self, fontColour, word, language):
        wordFont = get_font(language, 72)
        self.theColourText = wordFont.render(word, True, fontColour)
        self.position = [random.randrange(40, 420), random.randrange(40, 440)]

    def drawWord(self, screen):
        screen.blit(self.theColourText, self.position)

    def moveWord(self, screen, vector, backgroundColour):
     wordClearSurface = pygame.Surface(self.theColourText.get_size(), pygame.SRCALPHA)
     wordClearSurface.fill(backgroundColour)
     screen.blit(wordClearSurface, self.position)

     word_width, word_height = self.theColourText.get_size()

    # Screen boundaries
     min_x = 0
     max_x = 600 - word_width
     min_y = 0
     max_y = 500 - word_height  # Limit to 500px to stay above buttons

    # Bounce off walls
     if self.position[0] <= min_x or self.position[0] >= max_x:
        vector[0] *= -1
     if self.position[1] <= min_y or self.position[1] >= max_y:
        vector[1] *= -1

    # Update position
     self.position[0] = max(min_x, min(max_x, self.position[0] + vector[0]))
     self.position[1] = max(min_y, min(max_y, self.position[1] + vector[1]))

     screen.blit(self.theColourText, self.position)

def drawMenu(screen, background, playEnglishBtn, playHindiBtn, resultsBtn):
    background.fill((153, 255, 153))
    background = background.convert()
    screen.blit(background, (0, 0))
    playEnglishBtn.drawButton(screen)
    playHindiBtn.drawButton(screen)
    resultsBtn.drawButton(screen)
    titleFont = get_font("English", 60)
    titleText = titleFont.render("Stroop Effect Game", True, (75, 0, 130))
    screen.blit(titleText, (60, 50))
    instructionFont = get_font("English", 32)
    instructionText = instructionFont.render("Let's play", True, (220, 20, 60))
    screen.blit(instructionText, (100, 450))
    pygame.display.update()

def drawGameButtons(buttonRects, colours, language):
    buttonColour = (250, 235, 215)
    buttons = []
    for i in range(len(colours)):
        if i <= 2:
            buttonRects.append(pygame.Rect(i * 200, 500, 200, 50))
        else:
            buttonRects.append(pygame.Rect((i - 3) * 200, 550, 200, 50))
        buttons.append(pygame.Surface(buttonRects[i].size))
        buttons[i].fill(buttonColour)
        buttons[i].convert()
        screen.blit(buttons[i], (buttonRects[i].x, buttonRects[i].y))
        pygame.draw.rect(buttons[i], buttonColour, buttonRects[i], 30)
        buttonFont = get_font(language, 36)
        buttonText = buttonFont.render(colours[i][0], True, (0, 55, 90, 0))
        buttonText = buttonText.convert_alpha()
        screen.blit(buttonText, (buttonRects[i].x + 20, buttonRects[i].y + 5))

def displayHeaderInfo(text, position, colour, language):
    Font = get_font(language, 50)

    if language == "Hindi":
        if "Score" in text:
            value = ''.join(filter(str.isdigit, text))
            text = "स्कोर: " + convert_to_hindi_numerals(value)
        elif "Timer" in text:
            value = ''.join(filter(str.isdigit, text))
            text = "समय: " + convert_to_hindi_numerals(value)

    Text = Font.render(text, True, (0, 0, 0), (255, 255, 255))
    screen.blit(Text, (600 - (200 * position), 0))


    
def playGame(language):
    gameBackground = pygame.Surface((600, 500))
    gameBackground.fill((255, 255, 255))
    gameBackground.convert()

    colours = languages[language]
    colourButtonRects = []
    drawGameButtons(colourButtonRects, colours, language)

    userScore = 0
    timer = 0.0
    timelimit = 30
    FPS = 40
    clock = pygame.time.Clock()

    while timer < timelimit:
        milliseconds = clock.tick(FPS)
        timer += milliseconds / 1000
        isMoving = False
        fontColourIndex = random.randrange(0, 6)
        fontColour = colours[fontColourIndex][1]
        word = colours[random.randrange(0, 6)][0]
        theColouredWord = ColouredWord(fontColour, word, language)

        if userScore >= 5:
            backGroundColourIndex = random.randrange(0, 6)
            while backGroundColourIndex == fontColourIndex:
                backGroundColourIndex = random.randrange(0, 6)
            backgroundColour = colours[backGroundColourIndex][1]
            gameBackground.fill(backgroundColour)

        if userScore >= 10:
            isMoving = True
            movementVector = [random.randrange(-5, 5), random.randrange(-5, 5)]

        screen.blit(gameBackground, (0, 0))
        displayHeaderInfo("Score: " + str(userScore), 1, (255, 255, 0), language)
        theColouredWord.drawWord(screen)
        pygame.display.update()

        userClicked = False
        while not userClicked and timer < timelimit:
            if isMoving:
                theColouredWord.moveWord(screen, movementVector, backgroundColour)
            milliseconds = clock.tick(FPS)
            timer += milliseconds / 1000
            displayHeaderInfo("Timer: " + str(round(timer)), 2, (255, 0, 0), language)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(colourButtonRects)):
                        if colourButtonRects[i].collidepoint(pygame.mouse.get_pos()) and i == fontColourIndex:
                            userClicked = True
                            userScore += 1
                            screen.blit(gameBackground, (0, 0))

    screen.blit(gameBackground, (0, 0))
    pygame.display.update()
    user_results[language] = userScore

def displayResults():
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    font = get_font("English", 40)

    y = 100
    for lang in user_results:
        resultText = font.render(f"{lang} Score: {user_results[lang]}", True, (0, 0, 0))
        screen.blit(resultText, (100, y))
        y += 60

    if "English" in user_results and "Hindi" in user_results:
        diff = user_results["English"] - user_results["Hindi"]
        feedback = "You performed better in English" if diff > 0 else "You performed better in Hindi" if diff < 0 else "Equal performance"
        analysisText = font.render(feedback, True, (255, 0, 0))
        screen.blit(analysisText, (100, y))

    pygame.display.update()
    pygame.time.wait(5000)

# Setup buttons
playEnglishBtn = Button(screen, 200, 180, 200, 50, "Play English")
playHindiBtn = Button(screen, 200, 260, 200, 50, "Play Hindi")
resultsBtn = Button(screen, 200, 340, 200, 50, "Compare Results")

drawMenu(screen, background, playEnglishBtn, playHindiBtn, resultsBtn)

# Main loop
menuloop = True
while menuloop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menuloop = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if playEnglishBtn.buttonRect.collidepoint(pygame.mouse.get_pos()):
                playGame("English")
                drawMenu(screen, background, playEnglishBtn, playHindiBtn, resultsBtn)
            elif playHindiBtn.buttonRect.collidepoint(pygame.mouse.get_pos()):
                playGame("Hindi")
                drawMenu(screen, background, playEnglishBtn, playHindiBtn, resultsBtn)
            elif resultsBtn.buttonRect.collidepoint(pygame.mouse.get_pos()):
                displayResults()
                drawMenu(screen, background, playEnglishBtn, playHindiBtn, resultsBtn)

pygame.quit()
