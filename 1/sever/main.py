import asyncio
import websockets
import json

from handlers.MoveHandler import MoveHandler
from handlers.CollisionHandler import CollisionHandler
from game_state import GameState

PORT = 6789
game_state = GameState()

handlers = {
    "move": MoveHandler(game_state),
    "collision": CollisionHandler(game_state)
}


async def handle_connection(websocket):
    async for message in websocket:
        try:
            msg = json.loads(message)
            msg_type = msg.get("type")
            data = msg.get("data", {})

            handler = handlers.get(msg_type)
            if not handler:
                await websocket.send(json.dumps({
                    "type": "ERROR",
                    "data": {"message": f"Unknown message type: {msg_type}"}
                }))
                continue

            response = handler.handle(data)
            if response:
                await websocket.send(json.dumps(response))

        except Exception as e:
            await websocket.send(json.dumps({
                "type": "ERROR",
                "data": {"message": str(e)}
            }))


async def main():
    async with websockets.serve(handle_connection, "localhost", PORT):
        print(f"WebSocket server started on port {PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
