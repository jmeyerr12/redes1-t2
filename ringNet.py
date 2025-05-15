import socket
import time
import json
import random
import sys

PORT = 31204
player_id = int(sys.argv[1])

naipes = ["ouros", "copas", "espadas", "paus"]
valores = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

players = [
    ("10.254.225.25", PORT),
    ("10.254.225.26", PORT),
    ("10.254.225.27", PORT),
    ("10.254.225.28", PORT),
]

MY_IP, MY_PORT = players[player_id]
NEXT_IP, NEXT_PORT = players[(player_id + 1) % 4]

ordem_cartas = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}


def extrair_valor_naipe(carta):
    for valor in ordem_cartas:
        if carta.startswith(valor):
            naipe = carta[len(valor):]
            return valor, naipe
    return None, None


def distribuir_cartas():
    baralho = [valor + naipe for valor in valores for naipe in naipes]
    random.shuffle(baralho)
    return {
        0: baralho[0:13],
        1: baralho[13:26],
        2: baralho[26:39],
        3: baralho[39:52]
    }


def jogar_carta_interativamente(mao):
    while True:
        print(f"[{player_id}] Sua mão: {mao}")
        carta = input(f"[{player_id}] Digite a carta que deseja jogar (ex: 5copas): ").strip()
        if carta in mao:
            mao.remove(carta)
            return carta
        print(f"[{player_id}] Você não tem essa carta. Tente novamente.")


def calcular_vencedor(plays):
    valor_base, naipe_base = extrair_valor_naipe(plays[0]["card"])
    melhor_jogada = None
    maior_valor = -1

    for jogada in plays:
        valor, naipe = extrair_valor_naipe(jogada["card"])
        if naipe == naipe_base:
            if ordem_cartas[valor] > maior_valor:
                maior_valor = ordem_cartas[valor]
                melhor_jogada = jogada

    vencedor = melhor_jogada["player"]

    return vencedor

def extrair_cartas_jogadas(plays):
    return [play["card"] for play in plays]

def contar_pontos_todos(coletadas_por_jogador):
    pontos = [0, 0, 0, 0]
    for i in range(4):
        cartas = coletadas_por_jogador[i]
        num_copas = sum(1 for c in cartas if c.endswith("copas"))
        tem_q_espadas = "Qespadas" in cartas

        if num_copas == 13 and tem_q_espadas:
            # Shoot the Moon
            print(f"Jogador [{i}] SHOOT THE MOON!")
            for j in range(4):
                if j != i:
                    pontos[j] += 26
            # jogador que deu shoot the moon recebe 0
        else:
            # soma normal
            pontos[i] = num_copas + (13 if tem_q_espadas else 0)
    
    return pontos

# -- MAIN --
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((MY_IP, MY_PORT))

print(f"Jogador {player_id} iniciado em {MY_IP}:{MY_PORT}. Aguardando bastão...")

if player_id == 0:
    hands = distribuir_cartas()
    print(f"[{player_id}] Cartas distribuídas.")

    time.sleep(10)
    token = {
        "type": "token",
        "round": 0,
        "plays": [],
        "scores": [0, 0, 0, 0],
        "collected": [[], [], [], []],
        "starter": 0,
        "hands": hands,
        "gameover": False
    }
    sock.sendto(json.dumps(token).encode(), (NEXT_IP, NEXT_PORT))

my_hand = None

# loop principal
while True:
    data, _ = sock.recvfrom(1024)
    message = json.loads(data.decode())

    if message["type"] == "token":
        # ve se o jogo eh um jogo finalizado
        if message["gameover"] == True:
            print(f"[{player_id}] Jogo encerrado - um dos jogadores chegou a 100 pontos ou mais. Placar final: {message['scores']}")
            time.sleep(2)
            sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))
            break

        # obtem as cartas
        if my_hand is None and "hands" in message:
            my_hand = message["hands"][str(player_id)]

        # define primeiro jogador no estado inicial do jogo
        if message["round"] == 0 and "2paus" in my_hand:
            message["starter"] = player_id
            message["round"] += 1

        # se a partida ta comecando agora e voce nao eh o primeiro a jogar, ou mesmo o primeiro jogador ainda nao foi encontrado, pula sua vez
        if (message["starter"] != player_id and len(message["plays"]) == 0) or message["round"] == 0:
            time.sleep(2)
            print(f"[{player_id}] Passando o bastão...")
            sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))

        ja_joguei = any(play["player"] == player_id for play in message["plays"])

        if not ja_joguei:
            carta = jogar_carta_interativamente(my_hand)
            print(f"[{player_id}] Jogando: {carta}")
            message["plays"].append({"player": player_id, "card": carta})

        if len(message["plays"]) == 4:
            print(f"[{player_id}] Rodada {message['round']} completa.")
            print("Jogadas:", message["plays"])

            vencedor = calcular_vencedor(message["plays"])
            message["collected"][vencedor] += extrair_cartas_jogadas(message["plays"])
        
            print(f"[{player_id}] Jogador {vencedor} venceu a rodada e coletou as cartas jogadas")

            message["round"] += 1
            message["plays"] = []
            message["starter"] = vencedor

        # round 14 quer dizer que todos ja jogaram todas as suas cartas, ou seja, precisamos resetar os dados atuais
        if message["round"] == 14:
            # contabiliza os pontos, incluindo a possibilidade de um "shoot the moon"
            pontos_finais = contar_pontos_todos(message["collected"])
            for i in range(4):
                message["scores"][i] += pontos_finais[i]
            print(f"[{player_id}] Placar: {message['scores']}")

            # se alguem chego a 100 pontos, jogo acabo
            if any(p >= 100 for p in message["scores"]):
                message["gameover"] = True

            # reseta as maos para a proxima partida de cartas
            novasMaos = distribuir_cartas()
            message["hands"] = novasMaos
            message["round"] = 0
            message["collected"] = [[], [], [], []]

        time.sleep(2)
        print(f"[{player_id}] Passando o bastão...")
        sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))
