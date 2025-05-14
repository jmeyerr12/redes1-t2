import socket
import time
import json
import random
import sys

PORT = 31204
player_id = int(sys.argv[1])
naipes = ["ouros", "copas", "espadas", "paus"]
cartas = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
players = [
    ("10.254.225.25", PORT),  # Jogador 0
    ("10.254.225.26", PORT),  # Jogador 1
    ("10.254.225.27", PORT),  # Jogador 2
    ("10.254.225.28", PORT),  # Jogador 3
]

#define meu IP e IP do próximo jogador no anel
MY_IP, MY_PORT = players[player_id]
NEXT_IP, NEXT_PORT = players[(player_id + 1) % 4]

#cria socket e coloca entre os jogadores
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((MY_IP, MY_PORT))
print(f"Jogador {player_id} iniciado em {MY_IP}:{MY_PORT}. Aguardando bastão...")

#apenas o jogador 0 cria o bastão no início
if player_id == 0:
    deck = [carta + naipe for carta in cartas for naipe in naipes] #junta cada carta com um naipe
    random.shuffle(deck);
    hands = {
        0: deck[0:13],
        1: deck[13:26],
        2: deck[26:39],
        3: deck[39:52]
    }
    print(f"[{player_id}] Cartas distribuídas.")

    time.sleep(10)  #espera os outros iniciarem (pra garantir que da certo rode o 0 por ultimo)
    token = {
        "type": "token",
        "round": 1,
        "plays": [],
        "scores": [0, 0, 0, 0],
        "starter": 0,
        "hands": hands
    }
    sock.sendto(json.dumps(token).encode(), (NEXT_IP, NEXT_PORT))

#loop principal de recebimento de mensagens
while True:
    data, addr = sock.recvfrom(1024)
    message = json.loads(data.decode())

    #quando recebe o bastao
    if message["type"] == "token":
        if "hands" in message:
            my_hand = message["hands"][str(player_id)] if isinstance(message["hands"], dict) else message["hands"][player_id]
            print(f"[{player_id}] Minhas cartas: {my_hand}")

        ja_joguei = any(play["player"] == player_id for play in message["plays"])

        # Loop até o jogador digitar uma carta válida
        while True:
            print(f"[{player_id}] Sua mão: {my_hand}")
            carta_escolhida = input(f"[{player_id}] Digite a carta que deseja jogar exatamente como ela aparece (ex: 5copas): ").strip()

            if carta_escolhida in my_hand:
                my_hand.remove(carta_escolhida)
                print(f"[{player_id}] Jogando: {carta_escolhida}")
                message["plays"].append({
                    "player": player_id,
                    "card": carta_escolhida
                })
                break
            else:
                print(f"[{player_id}] Você não tem essa carta! Tente novamente.")


        # Se for o 4º a jogar, fecha a rodada
        if len(message["plays"]) == 4:
            print(f"[{player_id}] Rodada {message['round']} completa.")
            print("Jogadas:", message["plays"])

            # (Aqui futuramente entra a lógica para calcular o vencedor e pontuação)

            # Prepara próxima rodada
            message["round"] += 1
            message["plays"] = []

        time.sleep(2)  # Tempo com o bastão
        print(f"[{player_id}] Passando o bastão...")
        sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))
