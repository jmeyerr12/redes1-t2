import socket
import time
import json
import sys

# Porta única usada por todos os jogadores
PORT = 5000

# Obtém o ID do jogador (0 a 3) passado por argumento
player_id = int(sys.argv[1])

# Lista de IPs dos jogadores na ordem do anel
players = [
    ("10.254.225.24", PORT),  # Jogador 0
    ("10.254.225.25", PORT),  # Jogador 1
    ("10.254.225.26", PORT),  # Jogador 2
    ("10.254.225.27", PORT),  # Jogador 3
]

# Define meu IP e IP do próximo jogador no anel
MY_IP, MY_PORT = players[player_id]
NEXT_IP, NEXT_PORT = players[(player_id + 1) % 4]

# Cria socket UDP e associa à porta
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((MY_IP, MY_PORT))

print(f"Jogador {player_id} iniciado em {MY_IP}:{MY_PORT}. Aguardando bastão...")

# Apenas o jogador 0 cria o bastão no início
if player_id == 0:
    time.sleep(10)  # Espera os outros iniciarem
    token = {"type": "token"}
    sock.sendto(json.dumps(token).encode(), (NEXT_IP, NEXT_PORT))

# Loop principal de recebimento de mensagens
while True:
    data, addr = sock.recvfrom(1024)
    message = json.loads(data.decode())

    # Quando receber o bastão
    if message["type"] == "token":
        print(f"[{player_id}] Recebi o bastão! Executando ação...")

        # Aqui entrará a lógica do jogo Copas

        time.sleep(2)  # Tempo com o bastão
        print(f"[{player_id}] Passando o bastão...")
        sock.sendto(json.dumps(message).encode(), (NEXT_IP, NEXT_PORT))
