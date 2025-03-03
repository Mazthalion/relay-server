import asyncio
import websockets
import json
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('panstwa-miasta-server')

# Lista podłączonych graczy (maksymalnie 2)
connected_players = set()

# Przechowywane dane gry
game_data = {
    "categories": [],
    "letter": "",
    "player1_name": "",
    "player2_name": "",
    "player1_answers": [],
    "player2_answers": [],
    "player1_score": 0,
    "player2_score": 0,
    "round_owner": 1  # Pierwszy losuje host
}

async def handle_connection(websocket, path):
    global game_data
    
    # Dodaj nowego gracza do połączeń
    connected_players.add(websocket)
    logger.info(f"🔗 New player connected! Total players: {len(connected_players)}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"📥 Received data: {data}")

                # Gracz wysyła swoje imię
                if "player_name" in data:
                    if len(connected_players) == 1:
                        game_data["player1_name"] = data["player_name"]
                        await broadcast({"player1_name": game_data["player1_name"]})
                    else:
                        game_data["player2_name"] = data["player_name"]
                        await broadcast({"player2_name": game_data["player2_name"]})
                
                # Host losuje kategorie i literkę
                if "categories" in data and "letter" in data:
                    game_data["categories"] = data["categories"]
                    game_data["letter"] = data["letter"]
                    await broadcast({"categories": game_data["categories"], "letter": game_data["letter"]})

                # Gracze wysyłają swoje odpowiedzi
                if "answers_p1" in data:
                    game_data["player1_answers"] = data["answers_p1"]
                    await broadcast({"player1_answers": game_data["player1_answers"]})
                if "answers_p2" in data:
                    game_data["player2_answers"] = data["answers_p2"]
                    await broadcast({"player2_answers": game_data["player2_answers"]})

                # Otrzymano punkty
                if "scores" in data:
                    game_data["player1_score"] = data["scores"][0]
                    game_data["player2_score"] = data["scores"][1]
                    await broadcast({"scores": [game_data["player1_score"], game_data["player2_score"]]})

                # Synchronizacja sceny
                if "scene_change" in data:
                    await broadcast({"scene_change": data["scene_change"]})

                # Akcje
                if "action" in data:
                    await broadcast({"action": data["action"]})

                # Zmiana tury gracza losującego
                if "switch_round" in data:
                    game_data["round_owner"] = 2 if game_data["round_owner"] == 1 else 1
                    await broadcast({"round_owner": game_data["round_owner"]})
            
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")

    except websockets.exceptions.ConnectionClosed:
        logger.warning("❌ Player disconnected!")
    finally:
        connected_players.remove(websocket)
        logger.info(f"👋 Player left. Total players: {len(connected_players)}")

async def broadcast(message):
    """ Wysyła wiadomość do wszystkich podłączonych graczy """
    if connected_players:
        message_json = json.dumps(message)
        await asyncio.wait([player.send(message_json) for player in connected_players])

# Uruchomienie serwera
async def main():
    # Ustaw adres IP i port dla serwera
    host = "0.0.0.0"  # Nasłuchuje na wszystkich interfejsach
    port = 8765      # Port WebSocket

    server = await websockets.serve(handle_connection, host, port)
    logger.info(f"🚀 WebSocket Server Running on ws://{host}:{port}")
    
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
