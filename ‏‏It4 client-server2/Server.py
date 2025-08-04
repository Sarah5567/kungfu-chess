# server.py
import asyncio
import websockets
import json
connected = set()
players = {}  # websocket -> color
async def handler(websocket):
    if len(players) >= 2:
        await websocket.send(json.dumps({"type": "error", "message": "Game is full."}))
        await websocket.close()
        return

    color = "white" if "white" not in players.values() else "black"
    players[websocket] = color
    connected.add(websocket)
    await websocket.send(json.dumps({"type": "assign", "color": color}))
    print(f"[Server] Player {color} connected.")

    try:
        async for message in websocket:
            data = json.loads(message)
            data['color'] = players[websocket]

            # Broadcast the move to the opponent
            for other in connected:
                if other != websocket:  # Do not send the move back to the sender
                    await other.send(json.dumps(data))
    except websockets.ConnectionClosed:
        print(f"[Server] Player {players[websocket]} disconnected.")
    finally:
        connected.remove(websocket)
        del players[websocket]
async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server started on ws://localhost:8765")
        await asyncio.Future()  # run forever
if __name__ == "__main__":
    asyncio.run(main())
