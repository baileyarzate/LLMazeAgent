def array_to_ascii(maze, player_location):
    num_rows = len(maze)
    num_cols = len(maze[0])
    ascii_maze = []
    for i in range(num_rows):
        ascii_row = []
        for j in range(num_cols):
            if maze[i][j] == 1:
                ascii_row.append("#")
            elif maze[i][j] == 0:
                ascii_row.append(" ")
            else:
                ascii_row.append("W")
        ascii_maze.append(ascii_row)

    ascii_maze[player_location[1]][player_location[0]] = 'P'

    ascii_string_maze = ""
    for i in range(num_rows):
        for j in range(num_cols):
            ascii_string_maze += ascii_maze[i][j]
        ascii_string_maze += '\n'

    return ascii_string_maze