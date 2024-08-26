class Character:
    def __init__(self, name, player):
        self.name = name
        self.player = player

    def move(self, start_pos, direction, board):
        pass

    def is_valid_move(self, start_pos, end_pos, board):
        return 0 <= end_pos[0] < 5 and 0 <= end_pos[1] < 5 and board[end_pos[0]][end_pos[1]] is None


class Pawn(Character):
    def move(self, start_pos, direction, board):
        row, col = start_pos
        if direction == 'L':
            new_pos = (row, col - 1)
        elif direction == 'R':
            new_pos = (row, col + 1)
        elif direction == 'F':
            new_pos = (row - 1, col) if self.player == 'A' else (row + 1, col)
        elif direction == 'B':
            new_pos = (row + 1, col) if self.player == 'A' else (row - 1, col)
        else:
            return False

        if self.is_valid_move(start_pos, new_pos, board):
            return new_pos
        return False


class Hero1(Character):
    def move(self, start_pos, direction, board):
        row, col = start_pos
        if direction == 'L':
            new_pos = (row, col - 2)
        elif direction == 'R':
            new_pos = (row, col + 2)
        elif direction == 'F':
            new_pos = (row - 2, col) if self.player == 'A' else (row + 2, col)
        elif direction == 'B':
            new_pos = (row + 2, col) if self.player == 'A' else (row - 2, col)
        else:
            return False

        if self.is_valid_move(start_pos, new_pos, board):
            return new_pos
        return False


class Hero2(Character):
    def move(self, start_pos, direction, board):
        row, col = start_pos
        if direction == 'FL':
            new_pos = (row - 2, col - 2) if self.player == 'A' else (row + 2, col + 2)
        elif direction == 'FR':
            new_pos = (row - 2, col + 2) if self.player == 'A' else (row + 2, col - 2)
        elif direction == 'BL':
            new_pos = (row + 2, col - 2) if self.player == 'A' else (row - 2, col + 2)
        elif direction == 'BR':
            new_pos = (row + 2, col + 2) if self.player == 'A' else (row - 2, col - 2)
        else:
            return False

        if self.is_valid_move(start_pos, new_pos, board):
            return new_pos
        return False


class Game:
    def __init__(self):
        self.board = [[None for _ in range(5)] for _ in range(5)]
        self.players = {'A': [], 'B': []}
        self.current_turn = 'A'

    def initialize_game(self, player_a_pieces, player_b_pieces):
        # Position Player A's pieces
        for i, piece in enumerate(player_a_pieces):
            if piece == 'P':
                self.board[0][i] = Pawn(f'A-P{i+1}', 'A')
            elif piece == 'H1':
                self.board[0][i] = Hero1(f'A-H1-{i+1}', 'A')
            elif piece == 'H2':
                self.board[0][i] = Hero2(f'A-H2-{i+1}', 'A')

        # Position Player B's pieces
        for i, piece in enumerate(player_b_pieces):
            if piece == 'P':
                self.board[4][i] = Pawn(f'B-P{i+1}', 'B')
            elif piece == 'H1':
                self.board[4][i] = Hero1(f'B-H1-{i+1}', 'B')
            elif piece == 'H2':
                self.board[4][i] = Hero2(f'B-H2-{i+1}', 'B')

    def get_board_state(self):
        return [[cell.name if cell else None for cell in row] for row in self.board]

    def find_character(self, player, character_name):
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell and cell.name == character_name and cell.player == player:
                    return i, j
        return None

    def make_move(self, player, character_name, direction):
        if player != self.current_turn:
            return False, "Not your turn!"

        pos = self.find_character(player, character_name)
        if not pos:
            return False, "Character not found."

        character = self.board[pos[0]][pos[1]]
        new_pos = character.move(pos, direction, self.board)

        if new_pos:
            target_cell = self.board[new_pos[0]][new_pos[1]]
            if target_cell and target_cell.player != player:
                # Capture opponent's piece
                self.board[new_pos[0]][new_pos[1]] = None

            # Move character to the new position
            self.board[new_pos[0]][new_pos[1]] = character
            self.board[pos[0]][pos[1]] = None
            self.switch_turn()
            return True, "Move successful."
        else:
            return False, "Invalid move."

    def switch_turn(self):
        self.current_turn = 'A' if self.current_turn == 'B' else 'B'

    def check_game_over(self):
        a_pieces = sum([1 for row in self.board for cell in row if cell and cell.player == 'A'])
        b_pieces = sum([1 for row in self.board for cell in row if cell and cell.player == 'B'])

        if a_pieces == 0:
            return True, "Player B wins!"
        elif b_pieces == 0:
            return True, "Player A wins!"
        else:
            return False, None
