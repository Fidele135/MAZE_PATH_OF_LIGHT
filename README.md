# MAZE_PATH_OF_LIGHT

# Description

Maze Path of Light is a maze puzzle game where the player guides a beam of light through different maze levels. The player chooses a direction, and the light continues moving until it reaches a wall or a crossroad. The goal is to reach the exit of each maze and move to the next level. Each level changes color to make the game more interesting.

This game is based on the structure provided in the assignment starter code, but I modified the behavior and design to match the Maze Path of Light style.

# Controls
Arrow Keys or WASD — Choose movement direction
Restart Game button — Restart the game from Level 1
# How to Run the Game

Open the project folder in the terminal and run:

python main.py

The game window will open and you can start playing.

# File Structure

main.py — Starts the game
game.py — Contains the main game logic
models.py — Defines the player and entity classes
level.py — Handles the maze layout and rules
loader.py — Loads level files from the folder
scoreboard.py — Saves the best score
config.py — Stores game settings and colors
util.py — Helper functions for movement
levels/ — Contains the maze level text files

# Features
Automatic movement system
Multiple maze levels
Level progression when reaching the exit
Color changes between levels
Crystal collection system
Trap system that reduces lives
Restart button
Score tracking and best score saving
Object-Oriented Programming structure
Modular code organization

# Reflection
1. What changes did you make to the original game?

I changed the original Pac-Man style starter code into a maze puzzle game called Maze Path of Light. Instead of the player moving step by step like Pac-Man, the player moves through the maze like a beam of light. The goal is to pass the maze and reach the exit to go to the next level. I also added multiple levels and different colors for each level to make the game more interesting.

2. How did you modularize the code?

I modularized the code by splitting the program into multiple files instead of keeping everything in one file. Each file has its own responsibility. For example, the main file starts the game, the game file controls the gameplay, the level file handles the maze, and the config file stores settings. This made the code easier to manage and understand.

3. What classes did you create or modify?

I used the same class structure that was provided in the assignment template. I worked with classes like PathOfLightGame, LightBeam, MazeLevel, ScoreBoard, and Entity. I did not create completely new classes, but I modified the existing ones to fit my Maze Path of Light game.

4. Where did you apply encapsulation?

I applied encapsulation by keeping related data and behavior inside the correct classes. For example, the LightBeam class stores the player's position, score, and lives. The MazeLevel class stores the maze layout and checks movement rules. This keeps the code organized and easier to maintain.

5. Did you use inheritance? Why or why not?

Yes, I used inheritance. The LightBeam class inherits from the Entity class. This allows the player to reuse common properties like position and color without repeating code. It also makes the design cleaner.

6. What part was most challenging?

The most challenging part was fixing errors and making sure all the files worked together correctly. I also had to understand how the different classes connect and how to make the movement system work properly in the maze.

7. What would you improve next?

If I continue working on this project, I would add more levels, improve the maze design, and make the game look more polished. I might also add sound effects or animations to make the game more engaging.