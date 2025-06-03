import pygame
#import StroopEffectGame

def updateHighScores(userScore, screen):
    """gets the users name and adds their score to the highScore text file"""
    pygame.init()
    #defines what keys are allowed for the user's name
    permittedLetters= "abcdefghijklmnopqrstuvwxyz"
    userName = ""

    #prints the user's score to the screen and asks for thier name
    endScreenFont = pygame.font.SysFont("ariel", 50)
    endScreenLine1 = endScreenFont.render("You scored: "+str(userScore),True,(0,25,0),(255,255,255))
    endScreenLine2 = endScreenFont.render("Please enter your name: ",True, (25,0,0), (255,255,255))
    endScreenLine1 = endScreenLine1.convert()
    endScreenLine2 = endScreenLine2.convert()
    screen.blit(endScreenLine1,(180,100))
    screen.blit(endScreenLine2,(93,150))
    pygame.display.update()

    userIsEnteringName = True
    while userIsEnteringName:
        #loops through until the user presses the enter key
        for event in pygame.event.get():
            
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) in permittedLetters:
                    #adds the character corresponding to the key the user pressed
                    #to userName
                    if pygame.key.get_mods() == 1:
                        #detects whether shift key is pressed for uppercase letters
                        userName += pygame.key.name(event.key).upper()
                    else:
                        userName += pygame.key.name(event.key)
                    #shows the user's input so far on the screen
                    displayUserInputOnScreen(userName, endScreenFont, screen)
                elif pygame.key.name(event.key)== "return":
                    #the enter key will only allow the user to continue if they
                    #have entered a name
                    if not(userName==""):
                        userIsEnteringName = False
                elif pygame.key.name(event.key)== "backspace":
                    #removes the last character from userName
                    userName = userName[:len(userName)-1]
                    displayUserInputOnScreen(userName, endScreenFont, screen)
            elif event.type == pygame.QUIT:
                    #program closes when player closes window
                    quit()

    addUserScoreToTextFile(userScore,userName)

def addUserScoreToTextFile(userScore, userName):
    """adds the user's most recent score to the high score text file"""
    #opens HighScores.txt (is in the directory the source file is in)
    highScoreFile = open("HighScores.txt", "a+")
    #puts the user's name at the end of the text file and new line character
    highScoreFile.write(userName+"\n")
    #puts the user's score at the end of the text file and a new line character
    highScoreFile.write(str(userScore)+"\n")
    highScoreFile.close()

def displayHighScores(screen, background):
    """displays the top 5 high scores from the text file on the screen"""
    highScoresRaw = [] #used for storing raw output from the text file
    highScores =[] #used for storing the highscores in a two dimensional list
    #seperated into name and scores
    highScoreFile = open("HighScores.txt", "r")
    for line in highScoreFile:
        #steps through the text file getting each of the lines, striping them
        #of the new line characters and adding them to highScoresRaw
        highScoresRaw.append(line.rstrip())
    for i in range(0,len(highScoresRaw),2):
        #gets every 2 items from highScoresRaw and puts them in highScores
        highScores.append((int(highScoresRaw[i+1]),highScoresRaw[i]))

    #sorts the high scores so Highest are at the top    
    highScores.sort(reverse = True)
    background.fill((153,255,153))
    background = background.convert()
    screen.blit(background,(0,0))
    highScoreFont = pygame.font.SysFont("ariel", 50)
    #puts the header "high Scores" at the top of the screen
    title = highScoreFont.render("High Scores: ", True, (0,0,255))
    screen.blit(title,(100,0))
    scoreText = []
    userNamesText = []
    nameColour = (6,114,120)

    for j in range(0, len(highScores)):
        #writes the jth name to the screen
        userNamesText.append(highScoreFont.render(highScores[j][1], True,nameColour))
        screen.blit(userNamesText[j],(100,100+j*100))
        #wrties the jth score to the screen
        scoreText.append(highScoreFont.render(str(highScores[j][0]), True, nameColour))
        screen.blit(scoreText[j], (400, 100+j*100))

    pygame.display.update()

    #Waits for the user to click the mouse
    userIsLookingAtScores = True
    while userIsLookingAtScores:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                userIsLookingAtScores = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                userIsLookingAtScores = False
    
def displayUserInputOnScreen(userName, font, screen):
    """displays the user's input so far to the screen"""
    #box creates a blank space for the user's name to go in
    resetbox = pygame.Surface((600,37))
    #box is white
    resetbox.fill((255,255,255))
    resetbox.convert()
    screen.blit(resetbox,(0,200))
    
    userInputText = font.render(userName,True,(0,0,25),(255,255,255))
    userInputText.convert()
    #ensures the displayed name is centered
    screen.blit(userInputText,(round((600-userInputText.get_width())/2),200))
    pygame.display.update()