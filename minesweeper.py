import itertools
import random
from copy import *


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def __eq__(self, other):
        self.height = deepcopy(other.height)
        self.width = deepcopy(other.width)
        self.mines = deepcopy(other.mines)
        self.board = deepcopy(other.board)

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0
        neighbors = []

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.append((i, j))
                    if self.board[i][j]:
                        count += 1

        return neighbors, count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        The only time we know cells contain mines for certain is when
        all the cells in the set are mines. 
        """
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        The only time we know cells are safe for certain is when all
        the cells in the set are safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        Since the sentence is only useful to us when the status of a
        cell is uncertain, we remove any cells whose status has been 
        confirmed. So we remove the cell, and update self.count.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        Since the sentence is only useful to us when the status of a 
        cell is uncertain, we remove any cells whose status has been
        confirmed. So we remove the cell, and self.count remains same.
        """
        if cell in self.cells:
            self.cells.remove(cell)



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()
        
        # Keep track of available moves
        self.probs = {}
        for i in range(height):
            for j in range(width):
                self.probs[(i, j)] = 0

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        self.probs.pop(cell, None)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        self.probs.pop(cell, None)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def getNeighbors(self, cell, count):
        i, j = cell;
        neighbors = set()
        for x in range(i-1, i+2):
            for y in range(j-1, j+2):
                n = (x,y)
                if x >= 0 and x < self.height and \
                   y >= 0 and y < self.width and \
                   n not in self.mines and \
                   n not in self.safes and \
                   n != cell:
                    neighbors.add(n)
                if n in self.mines:
                    # We reduce the count by one to avoid sentences
                    # conveying duplicate information.
                    count -= 1
        return neighbors, count

    def updateKnowledge(self, sentence):
        changesMade = False
        newSentence = sentence
        
        allSafes = set()
        allMines = set()
        for s in self.knowledge:
            if s == sentence:
                continue

            if sentence.cells.issubset(s.cells):
                newCells = s.cells - sentence.cells
                newCount = s.count - sentence.count
                newSentence = Sentence(newCells, newCount)

                if newSentence not in self.knowledge:
                    changesMade = True
                    self.knowledge.append(newSentence)
            
            elif s.cells.issubset(sentence.cells):
                newCells = sentence.cells - s.cells
                newCount = sentence.count - s.count
                newSentence = Sentence(newCells, newCount)

                if newSentence not in self.knowledge:
                    changesMade = True
                    self.knowledge.append(newSentence)

            allSafes |= s.known_safes()
            allMines |= s.known_mines()

        if len(allSafes) > 0:
            changesMade = True
            for safe in allSafes:
                self.mark_safe(safe)
        
        if len(allMines) > 0:
            changesMade = True
            for mine in allMines:
                self.mark_mine(mine)
            
        if changesMade:
            self.updateKnowledge(newSentence)

    def removeEmpties(self):
        empty = Sentence(set(), 0)
        self.knowledge = [x for x in self.knowledge if x != empty]

    def removeDupes(self):
        unique_knowledge = []
        for s in self.knowledge:
            if s not in unique_knowledge:
                unique_knowledge.append(s)
        self.knowledge = unique_knowledge
    
    def removeObvious(self):
        for s in self.knowledge:
            cellsCopy = deepcopy(s.cells)
            if s.count == 0 and len(s.cells) != 0:
                for cell in cellsCopy:
                    self.mark_safe(cell)
            elif s.count == len(s.cells):
                for cell in cellsCopy:
                    self.mark_mine(cell)
    
    def recalcProb(self):
        for s in self.knowledge:
            if s.cells:
                prob = s.count / len(s.cells)
                for cell in s.cells:
                    if self.probs.get(cell):
                        if self.probs[cell] > prob:
                            self.probs[cell] = prob

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark the cell as safe, and that a move has been made
        self.moves_made.add(cell)
        self.probs.pop(cell, None)
        self.mark_safe(cell)
        # Add new sentence
        neighborCells, count = self.getNeighbors(cell, count)
        newSentence = Sentence(neighborCells, count)
        self.knowledge.append(newSentence)
        self.updateKnowledge(newSentence)
        self.removeEmpties()
        self.removeDupes()
        self.removeObvious()
        self.recalcProb()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safeCells = self.safes - self.moves_made
        if safeCells:
            return safeCells.pop()
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.probs) > 0:
            return random.choice(list(self.probs.keys()))
        return None
        
    def make_calc_move(self):
        """
        Returns the best move to make on the Minesweeper
        board based on probability.
        """
        if len(self.probs) > 0 and len(list(set(list(self.probs.values())))) > 2:            
            movesList = [[x, self.probs[x]] for x in self.probs]
            movesList.sort(key=lambda x: x[1])
            bestProb = movesList[0][1]

            bestMoves = [x for x in movesList if x[1] == bestProb]
            return random.choice(bestMoves)[0]
        return None

