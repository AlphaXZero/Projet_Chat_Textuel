import asyncio
import websockets
import json

clients = {}
rooms = ["general"]


async def handle_client(websocket):
    clients[websocket] = {"user": None, "room": "general"}
    try:
        await send_rooms(websocket)
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            if action == "login":
                already_taken = False
                username = data.get("user")
                for i in clients.values():
                    if i["user"] == username:
                        already_taken = True
                if already_taken:
                    await send_message(websocket, f"le pseduo {username} est déjà pris")
                else:
                    clients[websocket]["user"] = username
                    await send_message(
                        websocket,
                        f"Bienvenue, {clients[websocket]['user']}! Vous êtes dans le salon 'general'.",
                    )
            elif clients[websocket]["user"] is None:
                await send_message(
                    websocket, "veuillez choisir un pseudo avant de pouvoir chatter"
                )

            elif action == "join_room":
                room = data.get("room")
                clients[websocket]["room"] = room
                await send_message(websocket, f"Vous avez rejoint le salon {room}.")

            elif action == "send_message":
                room = clients[websocket]["room"]
                user = clients[websocket]["user"]
                message = data.get("message")
                await broadcast(room, clients, f"{user}: {message}")

            elif action == "create_room":
                room = data.get("room")
                if room not in rooms:
                    rooms.append(room)
                    await send_message(websocket, f"Le salon {room} a été créé.")
                else:
                    await send_message(websocket, f"Le salon {room} existe déjà.")

    except websockets.exceptions.ConnectionClosed:
        print("error")
    finally:
        if websocket in clients:
            del clients[websocket]


async def send_message(websocket, message):
    await websocket.send(json.dumps({"action": "message", "message": message}))


async def send_rooms(websocket):
    await websocket.send(json.dumps({"action": "rooms", "rooms": rooms}))


async def broadcast(room, clients, message):
    for websocket, client in clients.items():
        if client["room"] == room:
            await send_message(websocket, message)


async def main(ip, port):
    server = await websockets.serve(handle_client, ip, port)
    await server.wait_closed()


if __name__ == "__main__":
    print("serveur démaré")
    asyncio.run(main("127.0.0.2", 8001))
