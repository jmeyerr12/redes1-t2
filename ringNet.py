import socket
import time
import json
import sys

meu_id = int(sys.argv[1])

jogadores = [
    ("10.254.225.24", 5000),
    ("10.254.225.25", 5000),
    ("10.254.225.26", 5000),
    ("10.254.225.27", 5000),
]

MEU_IP, MEU_PORTA = jogadores[meu_id]
PROXIMO_IP, PROXIMO_PORTA = jogadores[(meu_id + 1) % 4]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((MEU_IP, MEU_PORTA))

print(f"[{meu_id}] Iniciado em {MEU_IP}:{MEU_PORTA}")

# Inicialização: ping-pong
if meu_id == 0:
    ping = {"tipo": "ping", "de": meu_id}
    time.sleep(1)
    sock.sendto(json.dumps(ping).encode(), (PROXIMO_IP, PROXIMO_PORTA))

    while True:
        data, _ = sock.recvfrom(1024)
        msg = json.loads(data.decode())

        if msg["tipo"] == "pong":
            print(f"[{meu_id}] Todos online. Enviando bastão.")
            time.sleep(1)
            token = {"tipo": "token"}
            sock.sendto(json.dumps(token).encode(), (PROXIMO_IP, PROXIMO_PORTA))
            break
        else:
            sock.sendto(data, (PROXIMO_IP, PROXIMO_PORTA))

else:
    while True:
        data, _ = sock.recvfrom(1024)
        msg = json.loads(data.decode())

        if msg["tipo"] == "ping":
            if meu_id == 3:
                pong = {"tipo": "pong"}
                sock.sendto(json.dumps(pong).encode(), (PROXIMO_IP, PROXIMO_PORTA))
            else:
                sock.sendto(data, (PROXIMO_IP, PROXIMO_PORTA))
        elif msg["tipo"] == "pong":
            sock.sendto(data, (PROXIMO_IP, PROXIMO_PORTA))
            break

# Loop principal (bastão)
while True:
    data, _ = sock.recvfrom(1024)
    msg = json.loads(data.decode())

    if msg["tipo"] == "token":
        print(f"[{meu_id}] Recebi o bastão.")
        time.sleep(2)
        sock.sendto(json.dumps(msg).encode(), (PROXIMO_IP, PROXIMO_PORTA))
