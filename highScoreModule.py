import pygame
import os


def updateHighScores(userScore, screen):
    """Gets the user's name and adds their score to the highScore text file"""
    pygame.init()
    permittedLetters = "abcdefghijklmnopqrstuvwxyz"
    userName = ""

    endScreenFont = pygame.font.SysFont("arial", 50)
    endScreenLine1 = endScreenFont.render("You scored: " + str(userScore), True, (0, 25, 0), (255, 255, 255))
    endScreenLine2 = endScreenFont.render("Please enter your name: ", True, (25, 0, 0), (255, 255, 255))
    screen.blit(endScreenLine1, (180, 100))
    screen.blit(endScreenLine2, (93, 150))
    pygame.display.update()

    userIsEnteringName = True
    while userIsEnteringName:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) in permittedLetters:
                    if pygame.key.get_mods() == 1:
                        userName += pygame.key.name(event.key).upper()
                    else:
                        userName += pygame.key.name(event.key)
                    displayUserInputOnScreen(userName, endScreenFont, screen)
                elif pygame.key.name(event.key) == "return":
                    if userName != "":
                        userIsEnteringName = False
                elif pygame.key.name(event.key) == "backspace":
                    userName = userName[:-1]
                    displayUserInputOnScreen(userName, endScreenFont, screen)
            elif event.type == pygame.QUIT:
                quit()

    addUserScoreToTextFile(userScore, userName)


def addUserScoreToTextFile(userScore, userName):
    """Adds the user's most recent score to the high score text file"""
    file_path = os.path.join(os.path.dirname(__file__), "HighScores.txt")
    with open(file_path, "a+") as highScoreFile:
        highScoreFile.write(userName + "\n")
        highScoreFile.write(str(userScore) + "\n")


def displayHighScores(screen, background):
    """Displays the top 5 high scores from the text file on the screen"""
    file_path = os.path.join(os.path.dirname(__file__), "HighScores.txt")
    highScoresRaw = []
    highScores = []

    with open(file_path, "r") as highScoreFile:
        for line in highScoreFile:
            highScoresRaw.append(line.rstrip())

    for i in range(0, len(highScoresRaw), 2):
        try:
            highScores.append((int(highScoresRaw[i + 1]), highScoresRaw[i]))
        except (IndexError, ValueError):
            continue

    highScores.sort(reverse=True)
    background.fill((153, 255, 153))
    screen.blit(background, (0, 0))

    highScoreFont = pygame.font.SysFont("arial", 50)
    title = highScoreFont.render("High Scores:", True, (0, 0, 255))
    screen.blit(title, (100, 0))

    nameColour = (6, 114, 120)
    for j in range(min(5, len(highScores))):
        name_text = highScoreFont.render(highScores[j][1], True, nameColour)
        score_text = highScoreFont.render(str(highScores[j][0]), True, nameColour)
        screen.blit(name_text, (100, 100 + j * 100))
        screen.blit(score_text, (400, 100 + j * 100))

    pygame.display.update()

    userIsLookingAtScores = True
    while userIsLookingAtScores:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                userIsLookingAtScores = False


def displayUserInputOnScreen(userName, font, screen):
    """Displays the user's input so far to the screen"""
    resetbox = pygame.Surface((600, 37))
    resetbox.fill((255, 255, 255))
    screen.blit(resetbox, (0, 200))

    userInputText = font.render(userName, True, (0, 0, 25), (255, 255, 255))
    screen.blit(userInputText, ((600 - userInputText.get_width()) // 2, 200))
    pygame.display.update()
