# 🂡 Jogo de Copas em Rede (Ring Topology)

Este projeto implementa uma **simulação do jogo de Copas (Hearts)** em uma **rede em anel utilizando sockets UDP (raw socket)**. Cada jogador é um processo independente que se comunica com o próximo por meio de pacotes JSON, formando uma topologia circular (token ring).

## 🎮 Sobre o jogo "Copas"

"Copas" é um jogo de cartas tradicional jogado por **4 jogadores**, em que o objetivo é **evitar acumular pontos**. As regras principais aplicadas nesta simulação incluem:

- Cada jogador começa com 13 cartas.
- A primeira rodada obrigatoriamente deve começar com a carta **2 de paus**.
- A cada rodada, os jogadores jogam uma carta em ordem.
- O jogador que jogar a carta mais alta do **naipe da primeira carta da rodada** "perde" e coleta todas as cartas jogadas naquela rodada.
- Cada **carta de copas vale 1 ponto** e a **rainha de espadas vale 13 pontos**.
- Se um jogador conseguir coletar **todas as cartas de copas e a rainha de espadas**, ele **dá um "Shoot the Moon"**: recebe **0 pontos**, e os demais recebem **26 pontos**.
- O jogo termina quando algum jogador atinge ou ultrapassa **100 pontos**. O jogador com **menor pontuação vence**.

## 🛠️ Tecnologias utilizadas

- Python 3
- Sockets UDP (com `socket` do Python)
- Comunicação via mensagens JSON

## 📦 Estrutura do projeto

- `ringNet.py`: arquivo principal com a lógica do jogo.
- Comunicação entre os jogadores é feita via `socket` UDP em topologia de anel.
- O bastão (`token`) circula entre os jogadores coordenando cada etapa do jogo.

## ▶️ Execução

Para iniciar o jogo, cada jogador deve ser executado em uma máquina diferente (ou em terminais diferentes com IPs simulados) com um ID de 0 a 3:
Além disso, os IPs das maquinas devem ser incluidas manualmente no vetor de IPS do codigo.
Após isso, execute da seguinte maneira (um comando em cada maquina)

```bash
python3 ringNet.py 0
python3 ringNet.py 1
python3 ringNet.py 2
python3 ringNet.py 3