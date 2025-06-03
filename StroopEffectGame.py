#STROOP EFFECT GAME
#made using pygame and python 3.4.1
import highScoreModule
import pygame 
import random
pygame.init() #initialises the pygame modules
screen = pygame.display.set_mode((600, 600))
#slightly transparent background of menu screen
background = pygame.Surface(screen.get_size())
#puts the title: "stroop effect game" in the window title
pygame.display.set_caption("Stroop Effect Game")

class button():
    """Class used for the two menu buttons"""
    
    def __init__(self,screen,left,top,width,height,name):
        self.label = name
        #main menu colour scheme has red buttons
        self.buttonColour = (255,0,0)
        self.buttonRect = pygame.Rect(left,top,width,height)
        self.buttonSurface = pygame.Surface(self.buttonRect.size)

    def drawButton(self,screen):
        """Draws a button for the menu"""
        self.buttonSurface.fill(self.buttonColour)
        self.buttonSurface.convert()
        #ensures the surface is drawn in the same postion as the rect
        screen.blit(self.buttonSurface, (self.buttonRect.x,self.buttonRect.y))
        pygame.draw.rect(self.buttonSurface,self.buttonColour, self.buttonRect,1)
        self.drawText(screen)

    def drawText(self, screen):
        """Writes the buttons name on the button surface"""
        #text font is in ariel size 50
        buttonTextFont = pygame.font.SysFont("ariel", 50)
        #dark blue is used for the button font
        buttonText = buttonTextFont.render(self.label,True,(0,55,90),self.buttonColour)
        buttonText = buttonText.convert()
        screen.blit(buttonText,self.buttonRect)        

class colouredWord():
    """class used for the coloured words that get displayed on the
    screen during the gameplay"""

    def __init__(self,fontColour, word):    
        wordFont = pygame.font.SysFont("ariel",72) #font for the colour word text    
        self.theColourText = wordFont.render(word,True,fontColour)
        #position of word is determined randomly
        self.position = [random.randrange(40,420),random.randrange(40,440)]

    def drawWord(self,screen):
        screen.blit(self.theColourText, self.position)

    def moveWord(self, screen, vector, backgroundColour):    
        wordClearSurface = pygame.Surface(self.theColourText.get_size())
        wordClearSurface.fill((backgroundColour))
        screen.blit(wordClearSurface, self.position)

        if not(0 < self.position[0] < 420):
            vector[0] = -1*vector[0]    
        if not(40 < self.position[1] < 440):
            vector[1] = -1*vector[1]
                    
        self.position[0] += vector[0]
        self.position[1] += vector[1]
        screen.blit(self.theColourText, self.position)

def drawMenu(screen, background, playButton, highScoreButton):
    """draws the background and main menu buttons to the screen"""
    #makes the background green
    background.fill((153,255,153))
    background = background.convert()
    screen.blit(background, (0,0))
    #draws the menu buttons
    playButton.drawButton(screen)
    highScoreButton.drawButton(screen)

    #draws the title: stroop effect
    titleFont = pygame.font.SysFont("impact",60)
    titleText = titleFont.render("Stroop Effect game", True, (75,0,130))
    titleText.convert()
    screen.blit(titleText, (60,50))
    
    #draws the instruction text
    instructionFont = pygame.font.SysFont("verdana",32)
    instructionText = instructionFont.render("Made by Smriti Aggarwal",True, (220,20,60))
    instructionText.convert()
    screen.blit(instructionText, (100,450))
    pygame.display.update()

def playGame():
    """the main gameplay loop, draws colours to the screen in different
    font colours and detects when the player clicks the correct button,
    then increments thier score by one"""
    #background used to clear screen of existing words
    gameBackground = pygame.Surface((600,500))
    gameBackground.fill((255,255,255))
    gameBackground.convert()
    
    #the colours six colours that will be used and thier corresponding RGB values
    colours = (("Red",(255,0,0)),("Green",(0,255,0)),("Blue",(0,0,255)),
               ("Yellow",(255,255,0)),("Pink",(255,20,147)),("Purple",(128,0,128)))
    
    colourButtonRects = [] #rects to detect the user's click
    drawGameButtons(colourButtonRects, colours) #draws the buttons for the users answer 
    userScore = 0 #stores the users score
    timer = 0.0 #stores the time that the user has been playing
    timelimit = 30 #time limit the user has to score as many as possible
    FPS = 40 #Framerate in Frames per second
    
    while timer<timelimit:
        #updates the clock
        clock = pygame.time.Clock()
        milliseconds = clock.tick(FPS)
        timer += milliseconds /1000
        isMoving = False
        
        fontColourIndex = random.randrange(0,6)
        fontColour = colours[fontColourIndex][1]
        word = colours[random.randrange(0,6)][0]

        theColouredWord = colouredWord(fontColour, word)
        
        if userScore >= 5:
            #draw coloured background if the user's scores above 5
            backGroundColourIndex = random.randrange(0,6)
            
            while backGroundColourIndex == fontColourIndex:
                backGroundColourIndex = random.randrange(0,6)
            backgroundColour = colours[backGroundColourIndex][1]
            gameBackground.fill(backgroundColour)
        if userScore >= 10:
            isMoving = True
            movementVector = [random.randrange(-5,5),random.randrange(-5,5)]
    
        #screen is cleared before new word is written to screen
        screen.blit(gameBackground, (0,0))
        #displays the score to the top of the screen
        displayHeaderInfo("Score: " + str(userScore), 1, (255,255,0))
        #displays the word in its generated position
        theColouredWord.drawWord(screen)
        pygame.display.update()

        #while loop runs until the user has clicked the correct button
        userClicked = False
        while userClicked ==False and timer<timelimit:

            if isMoving == True:
                theColouredWord.moveWord(screen,movementVector, backgroundColour)

            #updates the clock
            milliseconds = clock.tick(FPS)
            timer += milliseconds /1000
            #displays updated clock at the top of the screen
            displayHeaderInfo("Timer: " + str(round(timer)), 2, (255,0,0))
            
            pygame.display.update()
                            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #program closes when player closes window
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(colourButtonRects)):
                        #when mouse button is pressed, the cursor posistion is
                        #checked to see if its over the correct button
                        if (colourButtonRects[i].collidepoint(pygame.mouse.get_pos())
                            and i == fontColourIndex):
                            userClicked = True
                            userScore +=1
                            screen.blit(gameBackground, (0,0))
    gameBackground.fill((255,255,255))
    screen.blit(gameBackground,(0,0))

    highScoreModule.updateHighScores(userScore, screen)
    #drawMenu(playButtonRect, highScoreButtonRect, screen, background)
                                      
def drawGameButtons(buttonRects, colours):
    """draws the game buttons to the bottom of the screen and creates rects
    around them, and displays colour (in words) on the button"""
    buttonColour = (250,235,215)
    buttons = list()
    #steps through and creates six buttons to the buttom of the screen
    for i in range(len(colours)):
        if i <=2:
            #puts the first three buttons on the top row
            buttonRects.append(pygame.Rect(i*200,500,200,50))
        else:
            #puts the second three buttons on the bottom row
            buttonRects.append(pygame.Rect((i-3)*200,550,200,50))
        #all buttons are the same size
        buttons.append(pygame.Surface(buttonRects[i].size))
        #all buttons are the same colour
        buttons[i].fill(buttonColour)
        buttons[i].convert
        #the surfaces are drawn in the same position the rects are in
        screen.blit(buttons[i],(buttonRects[i].x,buttonRects[i].y))
        pygame.draw.rect(buttons[i],buttonColour,buttonRects[i],30)

        buttonFont = pygame.font.SysFont("ariel", 50)
        #the relevant colour word is put in the rects
        buttonText = buttonFont.render(colours[i][0],True,(0,55,90,0))
        buttonText = buttonText.convert_alpha()
        screen.blit(buttonText,(buttonRects[i].x+50,buttonRects[i].y+5))
        
def displayHeaderInfo(text, position, colour):
    """puts the score and time remaining at the top of the screen"""
    Font = pygame.font.SysFont("ariel", 50)
    Text = Font.render(text,True,(0,0,0),(255,255,255))
    Text = Text.convert()
    screen.blit(Text,(600-(200*position),0))

playButton= button(screen,200,200,200,50,"       Play")
highScoreButton = button(screen,200,300,200,50," High Score")

drawMenu(screen, background, playButton, highScoreButton)    

menuloop = True
while menuloop:
    #event getter for the menu
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            #closes the program when the user clicks the close window button
            menuloop = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if playButton.buttonRect.collidepoint(pygame.mouse.get_pos()):
                #allows the user to play the game when the mouse 
                #button is released over the play button
                playGame()
                #re draws the menu when the user has finished playing the game
                drawMenu(screen,background, playButton, highScoreButton)
            elif highScoreButton.buttonRect.collidepoint(pygame.mouse.get_pos()):
                #displays the highscores when the mouse button 
                #is released over the high score button
                highScoreModule.displayHighScores(screen,background)
                #re draws the menu when the user has
                #finished looking at the high scores
                drawMenu(screen,background, playButton, highScoreButton)

        #changes the colour of the button when 
        #the mouse button is down and over the button
        elif playButton.buttonRect.collidepoint(pygame.mouse.get_pos()):
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                playButton.buttonColour = (255,255,0)
            else:
                playButton.buttonColour = (255,165,0)
            playButton.drawButton(screen)
            pygame.display.update()
            
        elif highScoreButton.buttonRect.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEBUTTONDOWN:
                highScoreButton.buttonColour = (255,255,0)
            else:
                highScoreButton.buttonColour = (255,165,0)
            highScoreButton.drawButton(screen)
            pygame.display.update()
        else:
            playButton.buttonColour = (255,0,0)
            playButton.drawButton(screen)
            highScoreButton.buttonColour = (255,0,0)
            highScoreButton.drawButton(screen)
            pygame.display.update()
pygame.quit()