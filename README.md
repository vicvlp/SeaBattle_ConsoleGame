Battleship (Console version)
Classic "Battleship" game to play against the computer in the console.

Version: 1.0
Author: Viktor Pichugin
Contact: hsdpa08@gmail.com | vicvlp@mail.ru

Description
The game is implemented in Python and runs in a terminal.

Features:
Board size: 6×6.
Fleet: one 3-cell ship, two 2-cell ships, four 1-cell ships.
Automatic ship placement.
Board displayed using Unicode characters.
Input validation and error handling implemented via custom exceptions.

Requirements
Python 3.7+
Terminal that supports Unicode for correct symbol rendering.

Installation and running

Clone the repository:

git clone https://github.com/vicvlp/SeaBattle_ConsoleGame/

Change into project folder:

cd SeaBattle_ConsoleGame

Run the game:
python main.py

If you have multiple Python versions, use:
python3 main.py

Game rules and controls
Input format for coordinates: x y
where x is the column number (1..6), y is the row number (1..6).
Enter stop to quit the game.
Turns alternate between user and computer. If a player hits, they move again.

Board symbols:
▢ — empty cell
■ — ship piece (hidden on opponent's board)
× — hit
● — miss
· — contour around a sunk ship

Example session


<img width="262" height="563" alt="Screenshot_93" src="https://github.com/user-attachments/assets/39b4447f-3661-4a23-8eb5-9059147b6f0f" />
<img width="261" height="479" alt="Screenshot_94" src="https://github.com/user-attachments/assets/07b8e37a-89dd-4282-b723-804ba5f8fd4e" />



Project structure
main.py — main game file (contains all classes and logic)
Dot — point/coordinate class
Ship — ship class (length, orientation, coordinates)
Board — game board (placement, shots handling)
Player, User, AI — player classes
Game — game controller and main loop
Key components overview

Exceptions:
BoardException — base exception class.
BoardOutException — shot out of board bounds.
BoardUsedException — shot into an already used cell.
BoardWrongShipException — invalid ship placement.

Dot class:
Stores x, y coordinates.
Implements __eq__ and __repr__.

Ship class:
Constructor: Ship(bow: Dot, length: int, orientation: int) (0 — horizontal, 1 — vertical).
Property dots returns list of ship coordinates.
Method shooten(shot: Dot) checks if a shot hit the ship.

Board class:
Board size 6×6.
Methods: add_ship, out, shot, contour.
String representation via __str__. If hid=True, ship symbols are hidden.

Player classes:
Player — base class with move method.
AI — randomly selects a cell.
User — reads coordinates from input.

Game class:
Generates random boards (random_board, try_generate_board).
Manages the game loop (loop), greeting (greet), and drawing boards (draw_boards).

Improvement suggestions
Improve AI (implement hunt/target strategy after a hit).

MIT License
