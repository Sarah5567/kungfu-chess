import asyncio
import websockets
import json
from websockets.legacy.server import WebSocketServerProtocol, serve
from handlers.MoveHandler import MoveHandler
from handlers.BoardUpdateHandler import BoardUpdateHandler

PORT = 6789

connected_players = set()
player_roles: dict[WebSocketServerProtocol, str] = {}
handlers = {
    "move": MoveHandler(),
    "board_update": BoardUpdateHandler()
}

async def notify_all(message: str):
    if connected_players:
        await asyncio.gather(*(player.send(message) for player in connected_players))

async def handle_connection(websocket: WebSocketServerProtocol):
    if len(connected_players) >= 2:
        await websocket.send(json.dumps({
            "type": "ERROR",
            "data": {"message": "Game is full"}
        }))
        await websocket.close()
        return

    used_roles = set(player_roles.values())
    if "white" not in used_roles:
        role = "white"
    elif "black" not in used_roles:
        role = "black"
    else:
        await websocket.send(json.dumps({
            "type": "ERROR",
            "data": {"message": "Both roles are taken"}
        }))
        await websocket.close()
        return

    player_roles[websocket] = role
    connected_players.add(websocket)

    print(f"Player connected as {role}")
    await websocket.send(json.dumps({
        "type": "ROLE",
        "data": {"role": role}
    }))

    try:
        async for message in websocket:
            msg = json.loads(message)
            msg_type = msg.get("type")
            raw_params = msg.get("params", {})

            handler = handlers.get(msg_type)
            if not handler:
                await websocket.send(json.dumps({
                    "type": "ERROR",
                    "data": {"message": f"Unknown message type: {msg_type}"}
                }))
                continue

            # העברת role לפרמטרים (אם נחוץ בצד ה-handler)
            raw_params["role"] = player_roles[websocket]
            response = handler.handle(raw_params)

            if response:
                await notify_all(json.dumps(response, default=str))

    except websockets.ConnectionClosed:
        print(f"Player {player_roles[websocket]} disconnected")
    finally:
        connected_players.remove(websocket)
        del player_roles[websocket]

async def main():
    async with serve(handle_connection, "localhost", PORT):
        print(f"WebSocket server started on port {PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
