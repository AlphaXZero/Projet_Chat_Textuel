import asyncio
import websockets
import json
import logging

clients = {}
rooms = ["general"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


async def handle_client(websocket):
    clients[websocket] = {"user": None, "room": "general"}
    logger.info("Nouvelle connexion client %s.", websocket.remote_address)

    try:
        await send_rooms(websocket)

        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "login":
                username = data.get("user")
                already_taken = any(c["user"] == username for c in clients.values())

                if already_taken:
                    logger.info("Login échoué : pseudo '%s' déjà pris.", username)
                    await send_message(
                        websocket,
                        f"le pseudo {username} est déjà pris",
                    )
                else:
                    logger.info("Login réussi : '%s' connecté avec succès.", username)
                    clients[websocket]["user"] = username
                    await send_message(
                        websocket,
                        f"Bienvenue, {username}! Vous êtes dans le salon 'general'.",
                    )

            elif clients[websocket]["user"] is None:
                await send_message(
                    websocket,
                    "veuillez choisir un pseudo avant de pouvoir chatter",
                )

            elif action == "join_room":
                room = data.get("room")
                clients[websocket]["room"] = room
                logger.info(
                    "Utilisateur '%s' a rejoint le salon '%s'.",
                    clients[websocket]["user"],
                    room,
                )
                await send_message(
                    websocket,
                    f"Vous avez rejoint le salon {room}.",
                )

            elif action == "send_message":
                room = clients[websocket]["room"]
                user = clients[websocket]["user"]
                message = data.get("message")

                logger.info(
                    "Message dans '%s' par '%s' : %s",
                    room,
                    user,
                    message,
                )

                await broadcast(room, clients, f"{user}: {message}")

            elif action == "create_room":
                room = data.get("room")
                if room not in rooms:
                    rooms.append(room)
                    logger.info(
                        "Salon '%s' créé par '%s'.",
                        room,
                        clients[websocket]["user"],
                    )
                    await send_message(
                        websocket,
                        f"Le salon {room} a été créé.",
                    )
                else:
                    await send_message(
                        websocket,
                        f"Le salon {room} existe déjà.",
                    )

    except websockets.exceptions.ConnectionClosed:
        logger.info(
            "Client déconnecté : %s",
            websocket.remote_address,
        )
    except Exception:
        logger.exception("Erreur inattendue")

    finally:
        if websocket in clients:
            del clients[websocket]
            logger.info(
                "Client supprimé : %s",
                websocket.remote_address,
            )


async def send_message(websocket, message):
    await websocket.send(json.dumps({"action": "message", "message": message}))


async def send_rooms(websocket):
    await websocket.send(json.dumps({"action": "rooms", "rooms": rooms}))


async def broadcast(room, clients, message):
    for websocket, client in clients.items():
        if client["room"] == room:
            await send_message(websocket, message)


async def main(ip, port):
    logger.info("Serveur démarré sur %s:%s", ip, port)
    server = await websockets.serve(handle_client, ip, port)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main("127.0.0.2", 8001))
