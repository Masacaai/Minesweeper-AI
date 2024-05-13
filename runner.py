import pygame
import sys
import time
import os

from minesweeper import Minesweeper, MinesweeperAI

SIZE = 16
MINES = (5 * SIZE * SIZE) // 32

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
BLUE = (125, 125, 255)
GREEN = (125, 255, 125)
RED = (255, 125, 125)
PURPLE = (60, 60, 125)
MAROON = (125, 60, 60)
TURQUOISE = (60, 125, 125)

# Create game
pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)

# Compute relative path
filepath = os.path.dirname(os.path.realpath(__file__))

# Fonts
BITFONT = filepath + "/assets/fonts/8-bit.ttf"
smallFont = pygame.font.Font(BITFONT, 20)
mediumFont = pygame.font.Font(BITFONT, 28)
largeFont = pygame.font.Font(BITFONT, 40)
hugeFont = pygame.font.Font(BITFONT, 80)

# Number-color mappings
numColor = { 1 : BLUE,
             2 : GREEN,
             3 : RED,
             4 : PURPLE,
             5 : MAROON,
             6 : TURQUOISE,
             7 : BLACK,
             8 : GRAY }

# Class to handle drop-down menus
class DropDown():
    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / SIZE, board_height / SIZE))
board_origin = (BOARD_PADDING, BOARD_PADDING)


# Add images
flag = pygame.image.load(filepath + "/assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load(filepath + "/assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))
logo = pygame.image.load(filepath + "/assets/images/logo.png")
logo = pygame.transform.scale(logo, ((width / 4), (width / 4)))
cat = pygame.image.load(filepath + "/assets/images/cat.png")
cat = pygame.transform.scale(cat, ((width / 5), (width / 4)))
pizza = pygame.image.load(filepath + "/assets/images/pizza.png")
pizza = pygame.transform.scale(pizza, ((width / 5), (width / 4)))
cry = pygame.image.load(filepath + "/assets/images/cry.png")
cry = pygame.transform.scale(cry, ((width / 4), (width / 3)))

# Create game and AI agent
game = Minesweeper(height=SIZE, width=SIZE, mines=MINES)
ai = MinesweeperAI(height=SIZE, width=SIZE)

# Drop-down menu
COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

gridList = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    (2 / 3) * width, (3 / 4) * height - 20, 200, 50, 
    pygame.font.Font(BITFONT, 28), 
    "Select Grid", ["8 x 8", 
                    "12 x 12",
                    "16 x 16" ])

gridMap = { "8 x 8" : 8,
            "12 x 12" : 12,
            "16 x 16" : 16}

def recursive_add(move, game, revealed, ai, checked):
    checked.append(move)
    neighbors, nearby = game.nearby_mines(move) 
    revealed.add(move)
    ai.add_knowledge(move, nearby)
    if nearby == 0:
        for n in neighbors:
            if n not in checked:
                revealed, ai, checked = recursive_add(n, game, revealed, ai, checked) 
    
    return revealed, ai, checked

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
lost = False

# Open a logfile
if os.path.exists(filepath + "/log.txt"):
    os.remove(filepath + "/log.txt")
log = open("log.txt", "a")

# Set count for number of games played
countGames = 1

# Set count for number of moves made
countMoves = 0

# Set selectedOption value
selected_option = -1

# Set newGame status
newGame = True

# Set move status
move = False

# Set buttonClicked status
buttonClicked = False

# Set automate status
automate = False

# Show instructions initially
instructions = True

# Hide game initially
mainGame = False

# Set time elasped
timeElasped = 0

while True:

    if newGame:
        log.write("Game " + str(countGames) + ":\n")
        og_stdout = sys.stdout
        sys.stdout = log
        game.print()
        sys.stdout = og_stdout
        log.write("Current knowledge:\n")
        for i in ai.knowledge:
            log.write(str(i)+ "\n")
        log.write("\n")
        log.flush()
        newGame = False

    screen.fill(BLACK)
    
    # Show game instructions
    if instructions:

        # Title
        title = hugeFont.render("Minesweeper", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2) + 120, (height / 3) + 70)
        screen.blit(title, titleRect)

        logoRect = pygame.Rect((width / 10), (height / 4), width / 2, height / 2)
        screen.blit(logo, logoRect)

        # Play game button
        playButton = pygame.Rect((width / 6), (3 / 4) * height - 20, (width / 2) - 10, 50)
        playButtonText = mediumFont.render("Play Game", True, BLACK)
        playButtonRect = playButtonText.get_rect()
        playButtonRect.center = playButton.center

        mouse = pygame.mouse.get_pos()
        
        gridList.menu_active = gridList.rect.collidepoint(mouse)
        gridList.active_option = -1

        for i in range(len(gridList.options)):
            rect = gridList.rect.copy()
            rect.y += (i+1) * gridList.rect.height
            if rect.collidepoint(mouse):
                gridList.active_option = i
                break
                
        if not gridList.menu_active and gridList.active_option == -1:
            gridList.draw_menu = False

        gridList.draw(screen)
        
        if playButtonRect.collidepoint(mouse):
            pygame.draw.rect(screen, GRAY, playButton)
        else:
            pygame.draw.rect(screen, WHITE, playButton)
        screen.blit(playButtonText, playButtonRect)
 
    if mainGame:
        # Draw board
        cells = []
        for i in range(SIZE):
            row = []
            for j in range(SIZE):

                # Draw rectangle for cell
                rect = pygame.Rect(
                    board_origin[0] + j * cell_size,
                    board_origin[1] + i * cell_size,
                    cell_size, cell_size
                )
            
                if (i, j) in revealed:
                    pygame.draw.rect(screen, BLACK, rect)
                else:
                    pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, WHITE, rect, 3)
            
                # Add a mine, flag, or number if needed
                if game.is_mine((i, j)) and lost:
                    screen.blit(mine, rect)
                elif (i, j) in ai.mines:
                    screen.blit(flag, rect)
                elif (i, j) in revealed:
                    cellCount = game.nearby_mines((i, j))[1]
                    if cellCount != 0:
                        neighbors = mediumFont.render(
                            str(cellCount),
                            True, 
                            numColor[cellCount]
                        )
                        neighborsTextRect = neighbors.get_rect()
                        neighborsTextRect.center = rect.center
                        screen.blit(neighbors, neighborsTextRect)

                row.append(rect)
            cells.append(row)

        catRect = pygame.Rect((7 / 10) * width + 20, (height / 15), width / 2, height / 2)
        pizzaRect = pygame.Rect((7 / 10) * width + 20, (height / 15), width / 2, height / 2)
        cryRect = pygame.Rect((7 / 10) * width - 20, (height / 15) - 40, width / 2, height / 2)
        
        if game.mines == ai.mines:
            screen.blit(pizza, pizzaRect)
        elif lost:
            screen.blit(cry, cryRect)
        else:
            screen.blit(cat, catRect)

        # AI Move button
        aiButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (2 / 3) * height - 30,
            (width / 3) - BOARD_PADDING * 3.5, 50
        )
        aiButtonText = mediumFont.render("AI Move", True, BLACK)
        aiButtonRect = aiButtonText.get_rect()
        aiButtonRect.center = aiButton.center
        
        # Reset button
        resetButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (2 / 3) * height + 40,
            (width / 3) - BOARD_PADDING * 3.5, 50
        )
        resetButtonText = mediumFont.render("Reset", True, BLACK)
        resetButtonRect = resetButtonText.get_rect()
        resetButtonRect.center = resetButton.center
        pygame.draw.rect(screen, WHITE, resetButton)
        screen.blit(resetButtonText, resetButtonRect)
    
        # Automate button
        autoButton = pygame.Rect(
            (2 / 3) * width + BOARD_PADDING, (2 / 3) * height + 110,
            (width / 3) - BOARD_PADDING * 3.5, 50
        )
        autoButtonText = mediumFont.render("Automate", True, BLACK)
        autoButtonRect = autoButtonText.get_rect()
        autoButtonRect.center = autoButton.center
        pygame.draw.rect(screen, WHITE, autoButton)
        screen.blit(autoButtonText, autoButtonRect)
        
        mouse = pygame.mouse.get_pos()
        
        if aiButtonRect.collidepoint(mouse):
            pygame.draw.rect(screen, GRAY, aiButton)
        else:
            pygame.draw.rect(screen, WHITE, aiButton)
        screen.blit(aiButtonText, aiButtonRect)
        
        if resetButtonRect.collidepoint(mouse):
            pygame.draw.rect(screen, GRAY, resetButton)
        else:
            pygame.draw.rect(screen, WHITE, resetButton)
        screen.blit(resetButtonText, resetButtonRect)
        
        if autoButtonRect.collidepoint(mouse):
            pygame.draw.rect(screen, GRAY, autoButton)
        else:
            pygame.draw.rect(screen, WHITE, autoButton)
        screen.blit(autoButtonText, autoButtonRect)

        # Display text
        text = "Lost!" if lost else "Won!" if game.mines == ai.mines else ""
        text = mediumFont.render(text, True, WHITE)
        textRect = text.get_rect()
        textRect.center = ((3 / 4) * width - 40, (1 / 2) * height + 10)
        screen.blit(text, textRect)
        
        if lost or game.mines == ai.mines:
            timeText = "Time elasped: " + str(timeElasped) + "s"
            timeText = mediumFont.render(timeText, True, WHITE)
            timeTextRect = timeText.get_rect()
            timeTextRect.center = ((3 / 4) * width + 70, (1 / 2) * height + 50)
            screen.blit(timeText, timeTextRect)

        move = None

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            log.close()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if instructions:
                if gridList.menu_active:
                    gridList.draw_menu = not gridList.draw_menu
                elif gridList.draw_menu and gridList.active_option >= 0:
                    gridList.draw_menu = False
                    selected_option = gridList.active_option
                if selected_option >= 0:
                    gridList.main = gridList.options[selected_option]
                    SIZE = gridMap[gridList.main]
                    MINES = (5 * SIZE * SIZE) // 32
                    cell_size = int(min(board_width / SIZE, board_height / SIZE))
                    flag = pygame.transform.scale(flag, (cell_size, cell_size))
                    mine = pygame.transform.scale(mine, (cell_size, cell_size))

                if playButton.collidepoint(event.pos):
                    instructions = False
                    mainGame = True
            elif mainGame:
                # If AI button clicked, make an AI move
                if  aiButton.collidepoint(event.pos) and not lost:
                    buttonClicked = True      

                # Reset game state
                elif resetButton.collidepoint(event.pos):
                    game = Minesweeper(height=SIZE, width=SIZE, mines=MINES)
                    ai = MinesweeperAI(height=SIZE, width=SIZE)
                    revealed = set()
                    lost = False
                    startTime = 0
                    automate = False
                    selected_option = -1
                    move = False
                    buttonClicked = False
                    newGame = True
                    countMoves = 0
                    countGames += 1
                    continue
        
                # Automate game
                elif autoButton.collidepoint(event.pos) and game.mines != ai.mines and not lost:
                    automate = True
                    startTime = time.time()

                # User-made move
                elif not lost:
                    for i in range(SIZE):
                        for j in range(SIZE):
                            if cells[i][j].collidepoint(event.pos) and (i, j) not in revealed:
                                move = (i, j)
    
    # Perform AI move if needed
    if automate or buttonClicked:
        move = ai.make_safe_move()
        if move is None:
            move = ai.make_calc_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    log.write("No moves left to make.\n\n")
                    automate = False
                    endTime = time.time()
                    timeElasped = round(endTime - startTime, 2)
                else:
                    countMoves += 1
                    log.write("Move " + str(countMoves) + ": No safe or calculated moves, AI making random move.\nClicked on " + str(move) + "\n")
            else:
                countMoves += 1
                log.write("Move " + str(countMoves) + ": No known safe moves, AI making calculated move.\nClicked on " + str(move) + "\n")
        else:
            countMoves += 1
            log.write("Move " + str(countMoves) + ": AI making safe move.\nClicked on " + str(move) + "\n")
        buttonClicked = False

    # Make move and update AI knowledge
    if move:
        if game.is_mine(move):
            lost = True
            log.write("Game lost!\n\n")
            automate = False
            endTime = time.time()
            timeElasped = round(endTime - startTime, 2)

        else:
            checked = []
            revealed, ai, checked = recursive_add(move, game, revealed, ai, checked) 

            log.write("Current knowledge:\n")
            for i in ai.knowledge:
                log.write(str(i) + "\n")
            log.write("Current known safes:\n")
            for i in ai.safes:
                log.write(str(i) + " ")
            log.write("\nCurrent known mines:\n")
            for i in ai.mines:
                log.write(str(i) + " ")
            log.write("\nCurrent known probabilities:\n")
            for i in ai.probs:
                if ai.probs[i] != 0:
                    log.write(str(i) + ": " + str(ai.probs[i]) + " ")
            log.write("\n\n")
            log.flush()
    
    pygame.display.flip()
