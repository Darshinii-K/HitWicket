import asyncio
import websockets
import json
from game_logic import Game

class WebSocketGameServer:
    def __init__(self):
        self.game = Game()
        self.clients = {}  # To store connected clients and their player identifier (A or B)
        self.current_player = None

    async def handler(self, websocket, path):
        # Assign player to connected client
        player = None
        if 'A' not in self.clients:
            player = 'A'
        elif 'B' not in self.clients:
            player = 'B'
        else:
            await websocket.send(json.dumps({"type": "error", "message": "Game is full!"}))
            return

        self.clients[player] = websocket
        self.current_player = player

        await websocket.send(json.dumps({"type": "assign_player", "player": player}))

        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(data, player)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection with player {player} closed.")
            del self.clients[player]
        finally:
            if player in self.clients:
                del self.clients[player]

    async def process_message(self, data, player):
        if data["type"] == "initialize":
            player_a_pieces = data["player_a_pieces"]
            player_b_pieces = data["player_b_pieces"]
            self.game.initialize_game(player_a_pieces, player_b_pieces)
            await self.broadcast_game_state()

        elif data["type"] == "move":
            character_name = data["character_name"]
            move_direction = data["move_direction"]
            success, message = self.game.make_move(player, character_name, move_direction)
            if success:
                await self.broadcast_game_state()
                is_game_over, winner = self.game.check_game_over()
                if is_game_over:
                    await self.broadcast_game_over(winner)
            else:
                await self.send_invalid_move(player, message)

    async def broadcast_game_state(self):
        game_state = self.game.get_board_state()
        for player, websocket in self.clients.items():
            await websocket.send(json.dumps({
                "type": "game_state",
                "board": game_state,
                "current_turn": self.game.current_turn
            }))

    async def send_invalid_move(self, player, message):
        websocket = self.clients[player]
        await websocket.send(json.dumps({"type": "invalid_move", "message": message}))

    async def broadcast_game_over(self, winner):
        for websocket in self.clients.values():
            await websocket.send(json.dumps({"type": "game_over", "winner": winner}))

    def start_server(self):
        loop = asyncio.get_event_loop()
        server = websockets.serve(self.handler, "localhost", 6789)
        loop.run_until_complete(server)
        loop.run_forever()

if __name__ == "__main__":
    server = WebSocketGameServer()
    print("WebSocket server is starting...")
    server.start_server()
