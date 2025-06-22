#SOURCE CODE FOR GAME: https://github.com/DBgirl/PyGames/tree/c562037ec178991bb22b514c10d0fc0dfab38c13/Timed-Maze
import pygame
import random
import time
import csv
import os
from prompt_eng import array_to_ascii

#import LLM
from google import genai
API_KEY = "AIzaSyDT0t9FK-e0eau_itO-VNoRLmQ8V1MoA8s"
client = genai.Client(api_key=API_KEY)

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 200 #600
SCREEN_HEIGHT = 225  # 650, Increased height for timer display
CELL_SIZE = 20
MAZE_WIDTH = SCREEN_WIDTH // CELL_SIZE
MAZE_HEIGHT = (SCREEN_HEIGHT - 50) // CELL_SIZE  # Adjusted height for timer display
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (192, 192, 192)

# Create Maze
def create_maze():
    maze = [[0] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]
    # Randomly add obstacles
    for _ in range(10): #200
        x = random.randint(0, MAZE_WIDTH - 1)
        y = random.randint(0, MAZE_HEIGHT - 1) 
        maze[y][x] = 1
    # Set endpoint
    maze[MAZE_HEIGHT - 1][MAZE_WIDTH - 1] = 2
    return maze

# Draw Maze
def draw_maze(screen, maze):
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif maze[y][x] == 2:
                pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Player class
class Player:
    def __init__(self):
        self.x = 0
        self.y = 0

    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and maze[new_y][new_x] != 1:
            self.x = new_x
            self.y = new_y

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    def get_location(self):
        return self.x, self.y

# Main function
def main(player_name: str, player_type: str, useLLM: bool) -> None:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 36)
    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()

    maze = create_maze()
    # maze is a 2D array, this would be the input
    if maze[0][1] == 1 and maze[1][0] == 1:
        import sys
        print("Maze is impossible to solve. Ending Script.")
        sys.exit()
    player = Player()

    running = True
    won = False

    #logging information
    start_time = time.time()
    number_of_moves = 0

    move_successful = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                reason = "User Exitted Game"
            elif event.type == pygame.KEYDOWN:
                number_of_moves = number_of_moves + 1
                if event.key == pygame.K_UP:
                    player.move(0, -1, maze)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1, maze)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0, maze)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0, maze)

        if useLLM:  # move comes from LLM
            player_location = player.get_location()
            ascii_map = array_to_ascii(maze, player_location)
            try: last_location
            except: 
                last_location = "None, this is your first move."
                last_move = "None"
            prompt = f"""
            You are playing a maze game. Your goal is to reach the 'W' character in the maze below.
            You are at 'P'. '#' are walls. Spaces are open.

            Your previous location: {last_location}
            Your current location: {player_location}

            Maze:
            {ascii_map}
            """
            if not move_successful:
                prompt += f"\nLast move: '{last_move}' failed. You are still at {player_location}. Try another direction."
            prompt += """Rules:
            - You can move one step at a time: "up", "down", "left", or "right"
            - Do not return explanations.
            - Respond with only ONE word — your next move: "up", "down", "left", or "right"
            - Do NOT explain your reasoning.

            Your next move:
            """
            last_location = player_location
            try:
                llm_response = client.models.generate_content(
                    model="gemma-3-27b-it",
                    #model = 'gemini-2.0-flash',
                    contents=prompt
                )
                move = llm_response.text.lower().strip() 
                last_move = move
                print(f"LLM suggested move: {move}")
                if move == 'up':
                    if player_location[1] - 1 < 0 or maze[player_location[1] - 1][player_location[0]] == 1:
                        move_successful = False
                    else:
                        move_successful = True
                        player.move(0, -1, maze)
                        number_of_moves += 1

                elif move == 'down':
                    if player_location[1] + 1 >= MAZE_HEIGHT or maze[player_location[1] + 1][player_location[0]] == 1:
                        move_successful = False
                    else:
                        move_successful = True
                        player.move(0, 1, maze)
                        number_of_moves += 1

                elif move == 'left':
                    if player_location[0] - 1 < 0 or maze[player_location[1]][player_location[0] - 1] == 1:
                        move_successful = False
                    else:
                        move_successful = True
                        player.move(-1, 0, maze)
                        number_of_moves += 1

                elif move == 'right':
                    if player_location[0] + 1 >= MAZE_WIDTH or maze[player_location[1]][player_location[0] + 1] == 1:
                        move_successful = False
                    else:
                        move_successful = True
                        player.move(1, 0, maze)
                        number_of_moves += 1

                print("New location:",player.get_location())
                

            except Exception as e:
                print(f"Error calling LLM: {e}")

        screen.fill(WHITE)
        draw_maze(screen, maze)
        player.draw(screen)
        if maze[player.y][player.x] == 2:
            won = True
            running = False

        #if timer.is_time_up():
        max_number_of_moves = 30
        if number_of_moves > max_number_of_moves:
            running = False
            reason = f'Maximum Number of Moves Exceeded ({max_number_of_moves})'

        pygame.display.flip()

    screen.fill(WHITE)
    if won:
        time_text = font.render('You won!', True, BLACK)
    else:
        time_text = font.render(reason, True, BLACK)
    try:
        print(ascii_map)
    except UnboundLocalError as E:
        print("ASCII Map not shown for human solver. ")
    end_time = time.time()

    
    #LOGGING
    filename = f'{player_name}_{player_type}_log.csv'

    # Step 1: Determine trial number
    trial_number = 1
    if os.path.exists(filename):
        with open(filename, 'r', newline='') as f:
            reader = list(csv.reader(f))
            if len(reader) > 1: 
                try:
                    last_row = reader[-1]
                    trial_number = int(last_row[2]) + 1  
                except (IndexError, ValueError):
                    trial_number = 1

    # Step 2: Write row
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Name', 'Type', 'Trial', 'Win?', 'Time', 'Number of Moves'])  # Header
        writer.writerow([player_name, player_type, trial_number, won, end_time - start_time, number_of_moves])

    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2 - time_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    

if __name__ == "__main__":
    main("Jesse", "Human", useLLM=False) #Player types: Human, no context, saved context