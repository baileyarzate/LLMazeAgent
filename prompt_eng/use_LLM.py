import ast
from prompt_eng import array_to_ascii
import random

def useLLM(player, maze, client, previous = None):
    player_location = player.get_location()
    ascii_map = array_to_ascii(maze, player_location)

    prompt = f"""
    You are solving a maze game.

    Legend:
    - '#' = wall
    - 'P' = your current position
    - 'W' = the goal
    - ' ' = empty space you can move through

    You can move in four directions: "up", "down", "left", or "right", one step at a time.

    """
    prompt += f"Previous Failure(s): {previous}"
    prompt += f"""

    Maze:
    {ascii_map}

    Your task:
    - Find a path from 'P' to 'W'
    - Return a Python list of directions like this: ["right", "down", "down", "left", ...]

    Rules:
    - Do NOT return any explanation.
    - Do NOT include ```python or triple backticks.
    - ONLY return the list of moves. 

    Your answer:
    """

    raw_response = client.models.generate_content(
        model="gemma-3-27b-it",
        #model = 'gemini-2.5-flash',
        contents=prompt
    ).text.strip()

    # Remove triple backticks and language hints if present
    if raw_response.startswith("```"):
        raw_response = raw_response.split("```")[1].strip()  # remove the first code block
    if raw_response.startswith("python"):
        raw_response = raw_response[len("python"):].strip()

    try:
        moves = ast.literal_eval(raw_response)
        if isinstance(moves, list) and all(m in {"up", "down", "left", "right"} for m in moves):
            return moves
        else:
            raise ValueError("Not a valid move list.")
    except Exception as e:
        print("LLM response parsing failed:", e)
        print("Raw LLM output:", raw_response)
        return []
