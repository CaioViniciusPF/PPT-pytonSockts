import socket
import tkinter as tk
from tkinter import messagebox, font

class JogoPPT:
    def __init__(self, master):
        self.master = master
        master.title("Pedra, Papel e Tesoura")
        master.geometry("400x500")
        master.configure(bg="#f0f0f0")
        
        # Conexão com o servidor
        self.conectar_servidor()
        
        # Interface
        self.criar_interface()
        
        # Variáveis do jogo
        self.escolha = None
        self.player_id = None
        self.aguardando = False
    
    def conectar_servidor(self):
        HOST = input("Digite o IP do servidor: ") or '127.0.0.1'
        PORT = 55555
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
            
            # Recebe o ID do jogador
            data = self.client_socket.recv(1024).decode()
            if data == "FULL":
                messagebox.showerror("Erro", "Jogo cheio (2 jogadores já conectados)")
                self.master.quit()
                return
                
            self.player_id = int(data)
            print(f"Você é o Jogador {self.player_id}")
            
            # Thread para receber mensagens do servidor
            threading.Thread(target=self.receber_mensagens, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar: {e}")
            self.master.quit()
    
    def criar_interface(self):
        # Fonte
        font_title = font.Font(size=14, weight='bold')
        font_buttons = font.Font(size=12)
        
        # Frame do título
        self.frame_titulo = tk.Frame(self.master, bg="#f0f0f0")
        self.frame_titulo.pack(pady=10)
        
        self.label_titulo = tk.Label(
            self.frame_titulo, 
            text=f"Jogador {self.player_id if hasattr(self, 'player_id') else '?'}",
            font=font_title,
            bg="#f0f0f0"
        )
        self.label_titulo.pack()
        
        self.label_status = tk.Label(
            self.frame_titulo,
            text="Conectando...",
            bg="#f0f0f0"
        )
        self.label_status.pack()
        
        # Frame do placar
        self.frame_placar = tk.Frame(self.master, bg="#f0f0f0")
        self.frame_placar.pack(pady=10)
        
        self.label_placar = tk.Label(
            self.frame_placar,
            text="Placar: 0 x 0",
            font=font_title,
            bg="#f0f0f0"
        )
        self.label_placar.pack()
        
        # Frame das opções
        self.frame_opcoes = tk.Frame(self.master, bg="#f0f0f0")
        self.frame_opcoes.pack(pady=20)
        
        tk.Button(
            self.frame_opcoes,
            text="Pedra",
            command=lambda: self.enviar_escolha("pedra"),
            font=font_buttons,
            width=10,
            bg="#dddddd"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            self.frame_opcoes,
            text="Papel",
            command=lambda: self.enviar_escolha("papel"),
            font=font_buttons,
            width=10,
            bg="#dddddd"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            self.frame_opcoes,
            text="Tesoura",
            command=lambda: self.enviar_escolha("tesoura"),
            font=font_buttons,
            width=10,
            bg="#dddddd"
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame do histórico
        self.frame_historico = tk.Frame(self.master, bg="#f0f0f0")
        self.frame_historico.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.text_historico = tk.Text(
            self.frame_historico,
            height=10,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="white"
        )
        self.text_historico.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.text_historico)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_historico.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_historico.yview)
    
    def enviar_escolha(self, escolha):
        if self.aguardando:
            messagebox.showwarning("Aguarde", "Aguarde o outro jogador fazer sua escolha")
            return
            
        self.escolha = escolha
        self.client_socket.send(f"CHOICE:{escolha}".encode())
        self.label_status.config(text=f"Você escolheu: {escolha.capitalize()}\nAguardando outro jogador...")
        self.aguardando = True
    
    def receber_mensagens(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                    
                if data.startswith("RESULT:"):
                    parts = data.split(":")
                    resultado = parts[1]
                    escolha1 = parts[2]
                    escolha2 = parts[3]
                    
                    self.master.after(0, self.atualizar_interface, resultado, escolha1, escolha2)
                    
            except ConnectionResetError:
                self.master.after(0, self.conexao_perdida)
                break
    
    def atualizar_interface(self, resultado, escolha1, escolha2):
        self.aguardando = False
        
        # Atualiza histórico
        self.text_historico.config(state=tk.NORMAL)
        self.text_historico.insert(tk.END, f"Rodada:\n")
        self.text_historico.insert(tk.END, f"Jogador 1: {escolha1.capitalize()}\n")
        self.text_historico.insert(tk.END, f"Jogador 2: {escolha2.capitalize()}\n")
        self.text_historico.insert(tk.END, f"Resultado: {resultado}\n\n")
        self.text_historico.see(tk.END)
        self.text_historico.config(state=tk.DISABLED)
        
        # Atualiza status
        self.label_status.config(text=f"Resultado: {resultado}\nFaça sua próxima escolha")
        
        # Atualiza placar (simplificado - o servidor deveria enviar)
        if "1" in resultado:
            placar = self.label_placar.cget("text").split(":")[1].strip().split(" x ")
            novo_placar = f"Placar: {int(placar[0])+1} x {placar[1]}"
            self.label_placar.config(text=novo_placar)
        elif "2" in resultado:
            placar = self.label_placar.cget("text").split(":")[1].strip().split(" x ")
            novo_placar = f"Placar: {placar[0]} x {int(placar[1])+1}"
            self.label_placar.config(text=novo_placar)
    
    def conexao_perdida(self):
        messagebox.showerror("Erro", "Conexão com o servidor perdida")
        self.master.quit()

if __name__ == "__main__":
    import threading
    
    root = tk.Tk()
    jogo = JogoPPT(root)
    root.mainloop()
    
    try:
        jogo.client_socket.close()
    except:
        pass