import socket
import threading
import random

def handle_client(conn, player_id):
    global choices, scores, current_round
    
    conn.send(str(player_id).encode())
    
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
                
            if data.startswith("CHOICE:"):
                choice = data.split(":")[1]
                choices[player_id] = choice
                
                # Verifica se ambos jogadores escolheram
                if all(choices.values()):
                    result = determine_winner()
                    for p in players:
                        players[p].send(f"RESULT:{result}:{choices[1]}:{choices[2]}".encode())
                    
                    # Prepara para próxima rodada
                    choices = {1: None, 2: None}
                    current_round += 1
                    
        except ConnectionResetError:
            break
    
    # Remove jogador desconectado
    del players[player_id]
    conn.close()
    print(f"Jogador {player_id} desconectado.")

def determine_winner():
    choice1 = choices[1]
    choice2 = choices[2]
    
    if choice1 == choice2:
        return "Empate"
    
    win_conditions = {
        'pedra': 'tesoura',
        'papel': 'pedra',
        'tesoura': 'papel'
    }
    
    if win_conditions[choice1] == choice2:
        scores[1] += 1
        return "Jogador 1 venceu"
    else:
        scores[2] += 1
        return "Jogador 2 venceu"

def start_server():
    server.listen()
    print("Servidor aguardando conexões...")
    
    player_id = 1
    while True:
        conn, addr = server.accept()
        print(f"Conexão estabelecida com {addr}")
        
        if player_id > 2:
            conn.send("FULL".encode())
            conn.close()
            continue
            
        players[player_id] = conn
        thread = threading.Thread(target=handle_client, args=(conn, player_id))
        thread.start()
        
        player_id += 1

# Configurações do servidor
HOST = '0.0.0.0'
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

# Variáveis do jogo
players = {}
choices = {1: None, 2: None}
scores = {1: 0, 2: 0}
current_round = 1

print("Iniciando servidor de Pedra, Papel e Tesoura...")
start_server()