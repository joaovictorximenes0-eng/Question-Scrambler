# gui.py
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

class QuizApp:
    def __init__(self, root, manager):
        self.root = root
        self.manager = manager
        self.root.title("Quiz Simulator Pro")
        self.root.geometry("800x600")
        
        # Estilos e Fontes
        self.font_pergunta = ("Arial", 14, "bold")
        self.font_texto = ("Arial", 12)
        
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.mostrar_menu_inicial()

    def limpar_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- TELA 1: MENU ---
    def mostrar_menu_inicial(self):
        self.limpar_container()
        
        tk.Label(self.container, text="Selecione o Banco de Questões", font=("Arial", 18)).pack(pady=20)
        
        arquivos = self.manager.listar_bancos()
        if not arquivos:
            tk.Label(self.container, text="Nenhum arquivo .json encontrado na pasta 'banco_de_perguntas'.").pack()
            return

        self.combo_arquivos = ttk.Combobox(self.container, values=arquivos, state="readonly", width=40)
        self.combo_arquivos.pack(pady=10)
        self.combo_arquivos.current(0)
        
        btn_iniciar = tk.Button(self.container, text="Iniciar Quiz", command=self.iniciar_quiz, bg="#4CAF50", fg="white", font=self.font_texto)
        btn_iniciar.pack(pady=20)

    def iniciar_quiz(self):
        selecao = self.combo_arquivos.get()
        if not selecao: return
        
        self.manager.carregar_banco(selecao)
        self.mostrar_pergunta()

    # --- TELA 2: PERGUNTA ---
    def mostrar_pergunta(self):
        self.limpar_container()
        
        pergunta = self.manager.obter_pergunta_atual()
        
        if not pergunta:
            self.mostrar_resultado_final()
            return

        # Cabeçalho (Score)
        tk.Label(self.container, text=f"Acertos: {self.manager.acertos} | Erros: {self.manager.erros}", fg="gray").pack(anchor="e")
        tk.Label(self.container, text=f"Questão {pergunta['numero']}", font=("Arial", 10, "bold")).pack(anchor="w")

        # --- LÓGICA DE IMAGEM ---
        if "imagem" in pergunta and pergunta["imagem"]:
            self.carregar_imagem(pergunta["imagem"])

        # Texto da Pergunta (com quebra de linha automática)
        lbl_pergunta = tk.Label(self.container, text=pergunta['pergunta'], font=self.font_pergunta, wraplength=750, justify="left")
        lbl_pergunta.pack(pady=20)

        # Verifica se tem alternativas
        if "alternativas" in pergunta and pergunta["alternativas"]:
            self.criar_botoes_alternativas(pergunta)
        else:
            self.criar_flashcard(pergunta)

    def carregar_imagem(self, nome_imagem):
        caminho = os.path.join("imagens", nome_imagem)
        if os.path.exists(caminho):
            try:
                pil_img = Image.open(caminho)
                # Redimensionar se for muito grande, mantendo proporção
                pil_img.thumbnail((400, 300)) 
                img_tk = ImageTk.PhotoImage(pil_img)
                
                lbl_img = tk.Label(self.container, image=img_tk)
                lbl_img.image = img_tk # Referência necessária para o Garbage Collector não apagar
                lbl_img.pack(pady=10)
            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")

    def criar_botoes_alternativas(self, pergunta):
        frame_alts = tk.Frame(self.container)
        frame_alts.pack(fill="x", pady=10)
        
        for alt in pergunta['alternativas']:
            btn = tk.Button(frame_alts, text=alt, font=self.font_texto, wraplength=700, anchor="w", justify="left",
                            command=lambda a=alt: self.verificar_alternativa(a, pergunta))
            btn.pack(fill="x", pady=5, padx=10)

    def criar_flashcard(self, pergunta):
        btn_ver = tk.Button(self.container, text="Ver Resposta", command=lambda: self.mostrar_resposta_flashcard(pergunta))
        btn_ver.pack(pady=20)

    # --- TELA 3: FEEDBACK ---
    def verificar_alternativa(self, resposta_usuario, pergunta):
        acertou, idx_correto, idx_escolhido = self.manager.validar_resposta_alternativa(resposta_usuario, pergunta)
        
        msg = "✅ Correto!" if acertou else f"❌ Errado!\nA resposta correta é: {pergunta['resposta']}"
        cor = "green" if acertou else "red"
        
        self.manager.registrar_resultado(acertou, pergunta)
        messagebox.showinfo("Resultado", msg) # Pode substituir por um Label na tela se preferir
        
        self.manager.avancar_pergunta()
        self.mostrar_pergunta()

    def mostrar_resposta_flashcard(self, pergunta):
        # Remove botão "Ver Resposta"
        self.container.pack_forget() 
        
        lbl_resp = tk.Label(self.container, text=f"Resposta: {pergunta['resposta']}", font=("Arial", 12, "bold"), fg="blue", wraplength=750)
        lbl_resp.pack(pady=20)
        
        frame_botoes = tk.Frame(self.container)
        frame_botoes.pack(pady=10)
        
        tk.Button(frame_botoes, text="Eu Acertei", bg="#8BC34A", command=lambda: self.processar_flashcard(True, pergunta)).pack(side="left", padx=20)
        tk.Button(frame_botoes, text="Eu Errei", bg="#FF5722", command=lambda: self.processar_flashcard(False, pergunta)).pack(side="right", padx=20)

    def processar_flashcard(self, acertou, pergunta):
        self.manager.registrar_resultado(acertou, pergunta)
        self.manager.avancar_pergunta()
        self.mostrar_pergunta()

    # --- TELA 4: FINAL ---
    def mostrar_resultado_final(self):
        self.limpar_container()
        tk.Label(self.container, text="Quiz Finalizado!", font=("Arial", 20, "bold")).pack(pady=30)
        
        texto_resumo = f"Acertos: {self.manager.acertos}\nErros: {self.manager.erros}"
        tk.Label(self.container, text=texto_resumo, font=("Arial", 16)).pack(pady=20)
        
        tk.Button(self.container, text="Voltar ao Menu", command=self.mostrar_menu_inicial).pack(pady=20)