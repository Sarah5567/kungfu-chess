import asyncio
from pathlib import Path
import websockets
import json
from websockets.legacy.server import WebSocketServerProtocol, serve
from server.game_logic.EventBus import event_bus
from server.game_logic.Board import Board
from server.game_logic.Game import Game

PORT = 6789

connected_players = set()
player_roles: dict[WebSocketServerProtocol, str] = {}
game_started = False


def create_board():
    return Board(
        cell_H_pix=80,
        cell_W_pix=80,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=8,
        H_cells=8,
    )


board = create_board()

base_path = Path(__file__).resolve().parent.parent
pieces_root = base_path.parent / "PIECES"
placement_csv = base_path / "board.csv"

game = Game(board, pieces_root=pieces_root, placement_csv=placement_csv)


def publish_input_event(event_type, data):
    event_bus.publish(event_type, data)


# Custom JSON encoder for complex objects
def json_serializer(obj):
    """Custom serializer for objects that can't be serialized by default"""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    else:
        return str(obj)


async def handle_board_update(event_data):
    try:
        await notify_all(json.dumps({
            "type": 'BOARD_UPDATE',
            "data": event_data
        }, default=json_serializer))
    except Exception as e:
        print(f"Error in handle_board_update: {e}")


async def handle_victory(event_data):
    try:
        await notify_all(json.dumps({
            "type": 'VICTORY',
            "data": event_data
        }, default=json_serializer))
    except Exception as e:
        print(f"Error in handle_victory: {e}")


async def notify_all(message: str):
    if connected_players:
        # Send to each player individually to handle connection errors
        disconnected = set()
        for player in connected_players:
            try:
                await player.send(message)
            except websockets.ConnectionClosed:
                disconnected.add(player)
            except Exception as e:
                print(f"Error sending message to player: {e}")
                disconnected.add(player)

        # Remove disconnected players
        for player in disconnected:
            if player in connected_players:
                connected_players.remove(player)
            if player in player_roles:
                del player_roles[player]


async def send_safe(websocket, data):
    """Safely send data to websocket with error handling"""
    try:
        message = json.dumps(data, default=json_serializer)
        await websocket.send(message)
        return True
    except websockets.ConnectionClosed:
        print(f"Connection closed while sending: {data.get('type', 'unknown')}")
        return False
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


async def handle_connection(websocket: WebSocketServerProtocol):
    global game_started

    if len(connected_players) >= 2:
        await send_safe(websocket, {
            "type": "ERROR",
            "data": {"message": "Game is full"}
        })
        await websocket.close()
        return

    used_roles = set(player_roles.values())
    if "white" not in used_roles:
        role = "white"
    elif "black" not in used_roles:
        role = "black"
    else:
        await send_safe(websocket, {
            "type": "ERROR",
            "data": {"message": "Both roles are taken"}
        })
        await websocket.close()
        return

    player_roles[websocket] = role
    connected_players.add(websocket)

    print(f"Player connected as {role}")

    # Send role assignment
    role_sent = await send_safe(websocket, {
        "type": "ROLE",
        "data": {"role": role}
    })

    if not role_sent:
        # Clean up if sending failed
        if websocket in connected_players:
            connected_players.remove(websocket)
        if websocket in player_roles:
            del player_roles[websocket]
        return

    # Prepare board state - make sure it's serializable
    try:
        board_state = game.get_board_state()
        # Test serialization
        json.dumps(board_state, default=json_serializer)

        init_sent = await send_safe(websocket, {
            "type": "INIT",
            "data": {
                'board_state': board_state,
                'cell_H_pix': board.cell_H_pix,
                'cell_W_pix': board.cell_W_pix,
                'cell_H_m': board.cell_H_m,
                'cell_W_m': board.cell_W_m,
                'W_cells': board.W_cells,
                'H_cells': board.H_cells
            }
        })

        if not init_sent:
            # Clean up if sending failed
            if websocket in connected_players:
                connected_players.remove(websocket)
            if websocket in player_roles:
                del player_roles[websocket]
            return

        print(f"INIT message sent to {role}")

    except Exception as e:
        print(f"Error preparing or sending INIT message: {e}")
        if websocket in connected_players:
            connected_players.remove(websocket)
        if websocket in player_roles:
            del player_roles[websocket]
        return

    # Start the game only when two players are connected
    if len(connected_players) == 2 and not game_started:
        game_started = True
        asyncio.create_task(game.run())

    try:
        async for message in websocket:
            try:
                msg = json.loads(message)
                msg_type = msg.get("type")
                raw_params = msg.get("params", {})
                publish_input_event(msg_type, raw_params)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON received: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")

    except websockets.ConnectionClosed:
        print(f"Player {player_roles.get(websocket, 'unknown')} disconnected")
    except Exception as e:
        print(f"Connection error for {player_roles.get(websocket, 'unknown')}: {e}")
    finally:
        # Clean up
        if websocket in connected_players:
            connected_players.remove(websocket)
        if websocket in player_roles:
            del player_roles[websocket]


async def main():
    # Subscribe before anything else
    event_bus.subscribe(
        'BOARD_UPDATE',
        lambda event: asyncio.create_task(handle_board_update(event.data))
    )
    event_bus.subscribe(
        'VICTORY',
        lambda event: asyncio.create_task(handle_victory(event.data))
    )

    async with serve(handle_connection, "localhost", PORT):
        print(f"WebSocket server started on port {PORT}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Server error: {e}")