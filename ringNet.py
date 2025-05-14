import socket
import time
import json
import sys

# Argumentos: meu_id de 0 a 3
meu_id = int(sys.argv[1])

# Lista de IPs e portas
jogadores = [
    ("10.254.225.24", 5000),  # Jogador 0
    ("10.254.225.25", 5000),  # Jogador 1
    ("10.254.225.26", 5000),  # Jogador 2
    ("10.254.225.27", 5000),  # Jogador 3
]

MEU_IP, MEU_PORTA = jogadores[meu_id]
PROXIMO_IP, PROXIMO_PORTA = jogadores[(meu_id + 1) % 4]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((MEU_IP, MEU_PORTA))

print(f"Jogador {meu_id} iniciado. Esperando bastão...")

# Só o jogador 0 cria o bastão
if meu_id == 0:
    time.sleep(2)
    bastao = {"tipo": "token"}
    sock.sendto(json.dumps(bastao).encode(), (PROXIMO_IP, PROXIMO_PORTA))

# Loop principal
while True:
    data, addr = sock.recvfrom(1024)
    msg = json.loads(data.decode())

    if msg["tipo"] == "token":
        print(f"[{meu_id}] Recebi o bastão! Executando ação...")

        # Aqui entra lógica do jogo Copas (a ser feita na próxima fase)

        time.sleep(2)  # Tempo com o bastão
        print(f"[{meu_id}] Passando o bastão...")
        sock.sendto(json.dumps(msg).encode(), (PROXIMO_IP, PROXIMO_PORTA))
