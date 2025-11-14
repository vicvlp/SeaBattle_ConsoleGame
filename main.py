"""
Python 3.7+

Battleship

Classic console Battleship game to play against the computer.

Implementation highlights:
- 6x6 board
- Fleet: one 3-cell ship, two 2-cell ships, four 1-cell ships
- Automatic ship placement
- Visual board using Unicode symbols
- Exceptions to handle input errors

Classes:
- Dot: representation of a point on the board
- Ship: ship with certain length and orientation
- Board: game board with placement and shooting logic
- Player, User, AI: player classes
- Game: game controller

To quit the game, enter 'stop' instead of coordinates.

Author: Viktor Pichugin | hsdpa08@gmail.com | vicvlp@mail.ru
Version: 1.0
"""

import random


class BoardException(Exception):
    """Base class for board-related exceptions"""
    pass

class BoardOutException(BoardException):
    """Exception for shots outside the board"""
    def __str__(self):
        return "You are trying to shoot outside the board!"

class BoardUsedException(BoardException):
    """Exception for shooting at a previously used cell"""
    def __str__(self):
        return "You have already shot at this cell!"

class BoardWrongShipException(BoardException):
    """Exception for incorrect ship placement"""
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        """Override equality for convenient dot comparison"""
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        """String representation of a dot for debugging"""
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, length, orientation):
        """
        Initialize a ship
        :param bow: bow (front) point of the ship (Dot)
        :param length: ship length
        :param orientation: orientation (0 - horizontal, 1 - vertical)
        """
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length
    
    @property
    def dots(self):
        """Return a list of all dots occupied by the ship"""
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            
            if self.orientation == 0:
                cur_x += i
            elif self.orientation == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        """Check whether the ship is hit by the given shot"""
        return shot in self.dots

class Board:
    _EMPTY_SIGN = "\u25A1"    # Empty cell (unicode white square)
    _SHIP_SIGN = "\u25A0"     # Ship cell (unicode black square)
    _CONTOUR_SIGN = "\u00B7"  # Contour around destroyed ships (unicode middle dot)
    _HIT_SIGN = "\u2573"      # Hit mark (unicode diagonal cross)
    _LOSE_SIGN = "\u25CF"     # Miss mark (unicode black circle)

    def __init__(self, hid=False):
        # Initial board fill: 6x6 with empty signs
        self.field = [[self._EMPTY_SIGN] * 6 for _ in range(6)]
        self.ships = []
        self.hid = hid
        self.live_ships = 0
        self.busy_dots = []  # Occupied dots (ships + surrounding contour)
        self.shot_dots = []  # Dots that have already been shot at
    
    def __str__(self):
        """Graphical representation of the board"""
        res = "    | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1}   | " + " | ".join(row) + " |"
        
        if self.hid:
            # Replace ship symbols with empty cells when hiding the board
            res = res.replace(self._SHIP_SIGN, self._EMPTY_SIGN)
        
        return res
    
    def out(self, dot):
        """Check if a dot is outside the board boundaries"""
        return not ((0 <= dot.x < 6) and (0 <= dot.y < 6))  # True if outside, False if inside
    
    def contour(self, ship, verb=False):
        """Mark the contour around a ship on the board"""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for d in ship.dots:  # Iterate over all ship dots
            for dx, dy in near:  # Iterate over all relative offsets (for contour calculation)
                cur = Dot(d.x + dx, d.y + dy)  # Current contour dot being considered

                if verb:  # If the ship is destroyed
                    # Use _CONTOUR_SIGN to mark the contour when the ship is dead
                    # If coordinates are not outside the board
                    # and the place is not already a hit or a miss (to avoid overwriting)
                    if not self.out(cur) \
                        and (self.field[cur.y][cur.x] != self._HIT_SIGN) \
                        and (self.field[cur.y][cur.x] != self._LOSE_SIGN):
                        self.field[cur.y][cur.x] = self._CONTOUR_SIGN  # Mark contour around destroyed ship

                # If the dot is not out of bounds and not already in busy_dots
                if not self.out(cur) and cur not in self.busy_dots:
                    self.busy_dots.append(cur)
    
    def add_ship(self, ship):
        """Add a ship to the board"""
        for d in ship.dots:
            if self.out(d) or d in self.busy_dots:
                raise BoardWrongShipException()
        
        for d in ship.dots:
            self.field[d.y][d.x] = self._SHIP_SIGN  # Mark ship cell
            self.busy_dots.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
        self.live_ships += 1
    
    def shot(self, dot):
        """Perform a shot at the board"""
        if self.out(dot):
            raise BoardOutException()
        
        if dot in self.shot_dots:
            raise BoardUsedException()
        
        self.shot_dots.append(dot)
        
        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.y][dot.x] = self._HIT_SIGN  # Mark a hit
                
                if ship.lives == 0:  # If this ship has no lives left
                    self.live_ships -= 1  # Decrease the total number of remaining ships
                    self.contour(ship, verb=True)
                    print("Ship destroyed!")
                    return True
                else:
                    print("Ship wounded!")
                    return True
        
        self.field[dot.y][dot.x] = self._LOSE_SIGN  # Mark a miss
        print("Miss!")
        return False

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        """Abstract method for requesting a move"""
        raise NotImplementedError()
    
    def move(self):
        """Execute a player's move"""
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        """Randomly choose a dot to shoot"""
        # Note: hunt/target strategy is not implemented in this version
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Computer move: {d.x+1} {d.y+1}")
        return d

class User(Player):
    def ask(self):
        """Request shot coordinates from the user"""
        while True:
            try:
                coords = input("Your move (format: x y): ").strip()
                
                if coords.lower() == "stop":
                    print("Game terminated. Thanks for playing!")
                    exit(0)  # Immediate exit
                
                x, y = map(int, coords.split())
                if not (1 <= x <= 6 and 1 <= y <= 6):
                    print("Coordinates must be between 1 and 6!")
                    continue

                return Dot(x-1, y-1)
            except ValueError:
                print("Please enter two numbers separated by a space!")

class Game:
    def __init__(self):
        user_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hid = True
        
        self.user = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)
    
    def random_board(self):
        """Generate a random board with ships"""
        board = None
        while board is None:
            board = self.try_generate_board()
        return board
    
    def try_generate_board(self):
        """Attempt to generate a board with ships"""
        lens = [3, 2, 2, 1, 1, 1, 1]  # Ship lengths
        board = Board()
        attempts = 0
        
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None  # Too many attempts — restart generation
                
                ship = Ship(
                    Dot(random.randint(0, 5), random.randint(0, 5)),
                    length,
                    random.randint(0, 1)
                )
                try:
                    print(f"Test {ship.dots}")
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        return board
    
    def draw_boards(self):
        """Display the game boards"""
        print("-" * 20)
        print("User board:")
        print(self.user.board)
        print("-" * 20)
        print("Computer board:")
        print(self.ai.board)

    def greet(self):
        """Greeting and game instructions"""
        print("-------------------")
        print("  Welcome to the   ")
        print("     Battleship    ")
        print("       game!       ")
        print("-------------------")
        print(" Input format: x y ")
        print(" x - column number ")
        print(" y - row number    ")
    
    def loop(self):
        """Main game loop"""
        num = 0
        while True:
            self.draw_boards()
            
            if num % 2 == 0:
                print("-" * 20)
                print("User's turn!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Computer's turn!")
                input('Press "Enter" to let the computer move')  # Pause for control
                repeat = self.ai.move()
            
            if repeat:
                num -= 1  # Repeat turn on hit
            
            if self.ai.board.live_ships == 0:
                self.draw_boards()  # Final board display
                print("-" * 20)
                print("User won!")
                break
            
            if self.user.board.live_ships == 0:
                self.draw_boards()  # Final board display
                print("-" * 20)
                print("Computer won!")
                break
            
            num += 1
    
    def start(self):
        """Start the game"""
        self.greet()
        self.loop()

# Start the game
if __name__ == "__main__":
    g = Game()
    g.start()