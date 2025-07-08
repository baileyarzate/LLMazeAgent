#SOURCE CODE FOR GAME: https://github.com/DBgirl/PyGames/tree/c562037ec178991bb22b514c10d0fc0dfab38c13/Timed-Maze
import pygame
import random
import time
import csv
import os
import time
from prompt_eng import useLLM
from prompt_eng import array_to_ascii

#import LLM
from google import genai
with open("api_key.txt", "r") as file:
    API_KEY = file.read().strip()
client = genai.Client(api_key=API_KEY)

chat = None #client.chats.create(model="gemma-3-27b-it") #None -- use None when using non chat (One Shot)

# Initialize Pygame
pygame.init()
pygame.font.init()

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
    
    def reset_location(self):
        self.x = 0
        self.y = 0

# Main function
def main(player_name: str, player_type: str, maze: list, chat = None) -> None:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 36)
    pygame.display.set_caption("Maze Game")

    # maze is a 2D array, this would be the input
    if maze[0][1] == 1 and maze[1][0] == 1:
        print("Maze is impossible to solve. Ending Script.")
        return 0
    if maze[-1][-2] == 1 and maze[-2][-1] == 1:
        print("Maze is impossible to solve. Ending Script.")
        return 0
    player = Player()
    init_location = player.get_location()

    running = True
    won = False

    #logging information
    start_time = time.time()
    number_of_moves = 0

    llm_response = useLLM(player, maze, client, llm=player_name, chat=chat)
    
    index = 0
    puzzle_attempts = 1
    number_of_moves = 0
    old_response = []
    list_of_moves = []
    while running:
        try:
            llm_response[index]
        except: 
            print("LLM incorrectly thought it solved the puzzle.")
            if llm_response not in old_response:
                old_response.append(llm_response)
            puzzle_attempts += 1
            index = 0
            llm_response = useLLM(player, maze, client, llm=player_name, previous = old_response, chat=chat)
        
        try:
            if llm_response[index] == 'up':
                player.move(0, -1, maze)
                number_of_moves += 1
            elif llm_response[index] == 'down':
                player.move(0, 1, maze)
                number_of_moves += 1
            elif llm_response[index] == 'left':
                player.move(-1, 0, maze)
                number_of_moves += 1
            elif llm_response[index] == 'right':
                player.move(1, 0, maze)
                number_of_moves += 1
            list_of_moves.append(llm_response[index])
        except:
            print("LLM gave undesired output. Next attempt.")
            puzzle_attempts += 1
            index = 0
            llm_response = useLLM(player, maze, client, chat=chat)

        screen.fill(WHITE)
        draw_maze(screen, maze)
        player.draw(screen)
        if maze[player.y][player.x] == 2:
            won = True
            running = False

        max_number_of_attempts = 10
        if puzzle_attempts > max_number_of_attempts:
            running = False
            reason = f'Could not solve in {max_number_of_attempts} attempts'

        pygame.display.flip()
        time.sleep(0.2) #uncomment this to display the llm doing actions
        index += 1

    screen.fill(WHITE)
    if won:
        reason = 'success'
        time_text = font.render('You won!', True, BLACK)
    else:
        reason = 'failure'
        time_text = font.render(reason, True, BLACK)
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
    file_exists = os.path.isfile('results/'+filename)
    with open('results/'+filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Name', 'Type', 'Trial', 'Win?', 'Total Time', 'Number of Moves', 'LLM Attempts', "List of Moves" "Maze Layout", "PST end of Sample", "Outcome Reason"])  # Header
        if end_time - start_time < 60 or end_time - start_time > 120:
            writer.writerow([player_name, player_type, trial_number, won, end_time - start_time, number_of_moves, puzzle_attempts, list_of_moves, array_to_ascii(maze, init_location).replace("\n", "\\n"), time.localtime(), reason])

    screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2 - time_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(1000)
    pygame.quit()
    

if __name__ == "__main__":
    #llm options: 'gemini-2.5-flash', "gemma-3-4b-it", "gemma-3-12b-it", "gemma-3-27b-it",... more availible 
    for _ in range(30):
        pygame.init()
        fixed_maze = create_maze()
        main("gemma-3-27b-it", "ZeroShot", fixed_maze) #Player types: Human, no context, saved context