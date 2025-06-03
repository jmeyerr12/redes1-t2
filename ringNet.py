import socket
import time
import json
import random
import sys

# < --DEFINICOES-- > #
PORT = 31204
player_id = int(sys.argv[1])

naipes = ["ouros", "copas", "espadas", "paus"]
valores = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

players = [
    "10.254.225.12",
    "10.254.225.10",
    "10.254.225.6",
    "10.254.225.14",
]

MY_IP = players[player_id]
NEXT_IP = players[(player_id + 1) % 4]

ordem_cartas = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
    "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}
# < --- > #

# devolve o valor e naipe da carta distintos
def extrair_valor_naipe(carta):
    for valor in ordem_cartas:
        if carta.startswith(valor):
            naipe = carta[len(valor):]
            return valor, naipe
    return None, None


# embaralha as cartas em 4 conjuntos
def distribuir_cartas():
    baralho = [valor + naipe for valor in valores for naipe in naipes]
    random.shuffle(baralho)
    return {
        0: baralho[0:13],
        1: baralho[13:26],
        2: baralho[26:39],
        3: baralho[39:52]
    }

# funcao de processar a jogada de cada pessoa
def jogar_carta_interativamente(mao, naipe_da_mesa, copas_no_jogo, is_primeiro):
    while True:
        print(f"[{player_id}] Sua mão: {mao}")
        carta = input(f"[{player_id}] Digite a carta que deseja jogar (ex: 5paus): ").strip()
        vetor_de_naipes = []
        for card in mao:
            _,naipe = extrair_valor_naipe(card)
            vetor_de_naipes.append(naipe)

        # se so tiver copas, pode iniciar com copas mesmo sem o copas ter sido quebrado
        so_tem_copas = all(n == "copas" for n in vetor_de_naipes)

        if carta in mao:
            _,naipe_da_carta = extrair_valor_naipe(carta)
            # pessoa que comeca so pode comecar com o 2 de paus
            if "2paus" in mao and carta != "2paus":
                print(f"[{player_id}] Só é possivel iniciar uma partida com a carta 2paus.")
                continue
        
            # pessoa que comeca a rodada so pode comecar com o copas se o copas tiver sido jogado OU for a unica opcao de inicio
            elif is_primeiro and naipe_da_carta == "copas" and not copas_no_jogo and not so_tem_copas:
                print(f"[{player_id}] O copas ainda não foi quebrado e você ainda tem cartas que não sejam de copas. Não é possivel iniciar com copas")
                continue
            
            # pessoa eh obrigada a jogar carta do naipe da mesa SE tiver uma carta desse naipe
            elif not is_primeiro and naipe_da_carta != naipe_da_mesa and any(n == naipe_da_mesa for n in vetor_de_naipes):
                print(f"[{player_id}] Você ainda tem cartas com o naipe da mesa.")
                print(f"[{player_id}] Naipe da mesa é [{naipe_da_mesa}]")
                continue
            
            mao.remove(carta)
            is_copas_jogado = (naipe_da_carta == "copas")
            return carta, is_copas_jogado # eh importante ver se a carta jogada eh de copas para que seja registrado que o copas foi quebrado

        # carta selecionada nao existe na mao, volta o loop
        print(f"[{player_id}] Você não tem essa carta. Tente novamente.")


# define o perdedor de uma rodada (o que tiver jogado a maior entre 4 cartas)
def calcular_perdedor(plays):
    valor_base, naipe_base = extrair_valor_naipe(plays[0]["card"])
    melhor_jogada = None
    maior_valor = -1

    for jogada in plays:
        valor, naipe = extrair_valor_naipe(jogada["card"])
        if naipe == naipe_base:
            if ordem_cartas[valor] > maior_valor:
                maior_valor = ordem_cartas[valor]
                melhor_jogada = jogada

    perdedor = melhor_jogada["player"]

    return perdedor

# extrai todas as cartas jogadas em uma rodada
def extrair_cartas_jogadas(plays):
    return [play["card"] for play in plays]

# 1. no fim de um "set" de 13 rodadas, os pontos sao contabilizados com base nas cartas obtidas;
# 2. cada carta de copas vale um ponto, e a rainha de espadas vale 13 pontos;
# 3. existe uma regra extra chamada "Shoot the Moon", que dita que se uma pessoa tiver coletada todas
# as cartas de copas e a rainha de espadas, ela recebe 0 pontos e todos os outros jogadores recebem 26 pontos;
# 4. lembrando que quanto mais pontos pior.
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
sock.bind((MY_IP, PORT))

print(f"Jogador {player_id} iniciado em {MY_IP}:{PORT}. Aguardando bastão...")

# inicialmente, o player 0 cria o bastao inicial e embaralha as cartas
# posteriormente, esse processo eh feito por qualquer pessoa que estiver terminando a rodada
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
        "copas_ja_jogado": False,
        "gameover": False
    }
    sock.sendto(json.dumps(token).encode(), (NEXT_IP, PORT))

my_hand = None
naipe_da_mesa = None
# loop principal
while True:
    data, _ = sock.recvfrom(2048)
    message = json.loads(data.decode())

    if message["type"] == "token":
        # ve se o jogo eh um jogo finalizado
        if message["gameover"] == True:
            print(f"[{player_id}] Jogo encerrado - um dos jogadores chegou a 100 pontos ou mais. Placar final: {message['scores']}")
            time.sleep(2)
            sock.sendto(json.dumps(message).encode(), (NEXT_IP, PORT))
            break

        # obtem as cartas
        if (my_hand is None or len(my_hand) == 0) and "hands" in message:
            my_hand = message["hands"][str(player_id)]

        # define primeiro jogador no estado inicial do jogo
        if message["round"] == 0 and "2paus" in my_hand:
            message["starter"] = player_id
            message["round"] += 1
            print(f"[{player_id}] Primeiro jogador encontrado: Jogador {player_id}...")

        # se a partida ta comecando agora e voce nao eh o primeiro a jogar, ou mesmo o primeiro jogador ainda nao foi encontrado, pula sua vez
        if (message["starter"] != player_id and len(message["plays"]) == 0) or message["round"] == 0:
            time.sleep(2)
            print(f"[{player_id}] Procurando primeiro jogador...")
            sock.sendto(json.dumps(message).encode(), (NEXT_IP, PORT))
            continue

        ja_joguei = any(play["player"] == player_id for play in message["plays"])

        if not ja_joguei:
            if message["plays"]:
                _, naipe_da_mesa = extrair_valor_naipe(message["plays"][0]["card"])

            carta, copas_jogado = jogar_carta_interativamente(my_hand, naipe_da_mesa, message["copas_ja_jogado"], (message["starter"] == player_id))
            if (player_id == message["starter"]):
                _,naipe_carta = extrair_valor_naipe(carta)
                naipe_da_mesa = naipe_carta # se a pessoa for o starter, a carta que ela jogou eh o naipe da mesa
            if copas_jogado:
                message["copas_ja_jogado"] = True
            print(f"[{player_id}] Jogando: {carta}")
            message["plays"].append({"player": player_id, "card": carta})

        # fim da rodada
        if len(message["plays"]) == 4:
            print(f"[{player_id}] Rodada {message['round']} completa.")
            print("Jogadas:", message["plays"])

            perdedor = calcular_perdedor(message["plays"])
            message["collected"][perdedor] += extrair_cartas_jogadas(message["plays"])
        
            print(f"[{player_id}] Jogador {perdedor} perdeu a rodada e coletou as cartas jogadas")

            message["round"] += 1
            message["plays"] = []
            message["starter"] = perdedor # quem perde uma rodada, inicia a proxima
            message["copas_ja_jogado"] = False

        # round 14 quer dizer que todos ja jogaram todas as suas cartas, ou seja, precisamos resetar os dados atuais
        if message["round"] == 14:
            # contabiliza os pontos, incluindo a possibilidade de um "shoot the moon"
            pontos_finais = contar_pontos_todos(message["collected"])
            for i in range(4):
                message["scores"][i] += pontos_finais[i]
            print(f"[{player_id}] Placar: {message['scores']}")

            # se alguem chego a 100 pontos, jogo acabou, e todos os jogadores vao cair no aviso no inicio da proxima rodada
            if any(p >= 100 for p in message["scores"]):
                message["gameover"] = True

            # reseta as maos para a proxima partida de cartas
            novasMaos = distribuir_cartas()
            message["hands"] = novasMaos
            message["round"] = 0
            message["collected"] = [[], [], [], []]

        time.sleep(2)
        print(f"[{player_id}] Passando o bastão...")
        sock.sendto(json.dumps(message).encode(), (NEXT_IP, PORT))
