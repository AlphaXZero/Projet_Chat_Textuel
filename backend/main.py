import asyncio
import websockets
import json

clients = {}
rooms = {"general": []}


async def handle_client(websocket):
    clients[websocket] = {"user": None, "room": "general"}
    try:
        await send_rooms(websocket)

        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "set_username":
                already_taken = False
                username = data.get("user")
                for i in clients.values():
                    if i["user"] == username:
                        already_taken = True
                if already_taken:
                    await send_message(websocket, f"le pseduo {username} est déjà pris")
                else:
                    clients[websocket]["user"] = username
                    rooms["general"].append(websocket)
                    await send_message(
                        websocket,
                        f"Bienvenue, {username}! Vous êtes dans le salon 'general'.",
                    )

            elif action == "join_room":
                room = data.get("room")
                clients[websocket]["room"] = room
                rooms[room].append(websocket)
                await send_message(websocket, f"Vous avez rejoint le salon {room}.")

            elif action == "send_message":
                room = clients[websocket]["room"]
                user = clients[websocket]["user"]
                message = data.get("message")
                await broadcast(room, f"{user}: {message}")

            elif action == "create_room":
                room = data.get("room")
                if room not in rooms:
                    rooms[room] = []
                    await send_message(websocket, f"Le salon {room} a été créé.")
                else:
                    await send_message(websocket, f"Le salon {room} existe déjà.")

    except websockets.exceptions.ConnectionClosed:
        print("error deco")
    finally:
        if websocket in clients:
            room = clients[websocket]["room"]
            if room in rooms:
                rooms[room].remove(websocket)
            del clients[websocket]


async def send_message(websocket, message):
    await websocket.send(json.dumps({"action": "message", "message": message}))


async def send_rooms(websocket):
    await websocket.send(json.dumps({"action": "rooms", "rooms": list(rooms.keys())}))


async def broadcast(room, message):
    for client in rooms[room]:
        await send_message(client, message)


async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    await server.wait_closed()


if __name__ == "__main__":
    print("serveur démaré")
    asyncio.run(main())
