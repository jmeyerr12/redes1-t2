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

print(f"[{meu_id}] Pronto em {MEU_IP}:{MEU_PORTA}")

estado = "inicial"

if meu_id == 0:
    time.sleep(2)
    msg = {"tipo": "ping", "origem": 0}
    sock.sendto(json.dumps(msg).encode(), (PROXIMO_IP, PROXIMO_PORTA))
    estado = "aguardando_pong"

while True:
    data, _ = sock.recvfrom(1024)
    msg = json.loads(data.decode())

    if msg["tipo"] == "ping":
        if meu_id == 3:
            resposta = {"tipo": "pong", "origem": 3}
            sock.sendto(json.dumps(resposta).encode(), (PROXIMO_IP, PROXIMO_PORTA))
        else:
            sock.sendto(data, (PROXIMO_IP, PROXIMO_PORTA))

    elif msg["tipo"] == "pong":
        sock.sendto(data, (PROXIMO_IP, PROXIMO_PORTA))
        if meu_id == 0 and estado == "aguardando_pong":
            print(f"[{meu_id}] Todos online. Criando bastão.")
            time.sleep(1)
            token = {"tipo": "token"}
            sock.sendto(json.dumps(token).encode(), (PROXIMO_IP, PROXIMO_PORTA))
            estado = "ativo"

    elif msg["tipo"] == "token":
        print(f"[{meu_id}] Recebi o bastão.")
        time.sleep(2)
        sock.sendto(json.dumps(msg).encode(), (PROXIMO_IP, PROXIMO_PORTA))
