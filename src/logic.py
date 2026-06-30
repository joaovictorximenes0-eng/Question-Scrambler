# logic.py
import json
import os
import re
import random

class QuizManager:
    def __init__(self):
        self.perguntas = []
        self.perguntas_incorretas = {}
        self.nome_banco_atual = ""
        self.indices_perguntas = []
        self.indice_atual = 0
        self.acertos = 0
        self.erros = 0
        
    def listar_bancos(self, pasta="banco_de_perguntas"):
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        return [f for f in os.listdir(pasta) if f.endswith('.json')]

    def carregar_banco(self, nome_arquivo, pasta="banco_de_perguntas"):
        caminho_completo = os.path.join(pasta, nome_arquivo)
        self.nome_banco_atual = os.path.splitext(nome_arquivo)[0]
        
        with open(caminho_completo, 'r', encoding='utf-8') as file:
            self.perguntas = json.load(file)
            
        self.indices_perguntas = list(range(len(self.perguntas)))
        random.shuffle(self.indices_perguntas) # Embaralha
        self.acertos = 0
        self.erros = 0
        
        # Carrega histórico de erros
        self.carregar_incorretas()

    def obter_pergunta_atual(self):
        if not self.indices_perguntas:
            return None
        indice_real = self.indices_perguntas[0] # Pega o primeiro da lista embaralhada
        return self.perguntas[indice_real]

    def avancar_pergunta(self):
        if self.indices_perguntas:
            self.indices_perguntas.pop(0)

    def registrar_resultado(self, acertou, pergunta):
        if acertou:
            self.acertos += 1
        else:
            self.erros += 1
            num = str(pergunta['numero'])
            if num in self.perguntas_incorretas:
                self.perguntas_incorretas[num]['contador'] += 1
            else:
                self.perguntas_incorretas[num] = {
                    'resposta': pergunta['resposta'], 
                    'contador': 1
                }
            # Salva imediatamente ao errar (opcional, mas seguro)
            self.salvar_incorretas()

    # --- Persistência de Erros ---
    def carregar_incorretas(self):
        arquivo = f"perguntas_incorretas_{self.nome_banco_atual}.txt"
        self.perguntas_incorretas = {}
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i in range(0, len(lines), 3):
                    try:
                        # Adaptei para string para evitar erros de chave
                        numero = lines[i].strip().split(": ")[1] 
                        resposta = lines[i+1].strip().split(": ")[1]
                        contador = int(lines[i+2].strip().split(": ")[1])
                        self.perguntas_incorretas[numero] = {'resposta': resposta, 'contador': contador}
                    except (IndexError, ValueError):
                        pass

    def salvar_incorretas(self):
        if not self.perguntas_incorretas:
            return
        arquivo = f"perguntas_incorretas_{self.nome_banco_atual}.txt"
        with open(arquivo, 'w', encoding='utf-8') as file:
            for numero, info in self.perguntas_incorretas.items():
                file.write(f"Pergunta {numero}: {info['resposta']}\n")
                file.write(f"Contador de Erros: {info['contador']}\n\n")

    # --- Helpers de Validação ---
    def validar_resposta_alternativa(self, resposta_usuario_texto, pergunta):
        """
        Retorna (True/False, Índice Correto, Índice Escolhido)
        """
        alts = pergunta.get('alternativas', [])
        idx_escolhido = -1
        
        # Tenta achar o índice da resposta do usuário
        for i, alt in enumerate(alts):
            if alt == resposta_usuario_texto:
                idx_escolhido = i
                break
        
        idx_correto = self._encontrar_indice_correto(pergunta)
        
        # Se achou índice exato
        if idx_correto is not None and idx_escolhido != -1:
            return (idx_escolhido == idx_correto), idx_correto, idx_escolhido
            
        # Fallback: Comparação de texto normalizado
        resp_norm = self._normalize(pergunta.get('resposta', ''))
        user_norm = self._normalize(resposta_usuario_texto)
        return (resp_norm == user_norm), -1, -1

    def _normalize(self, s):
        if not s: return ""
        s = re.sub(r'^[A-Za-z]\W*\s*', '', s.strip()) # Remove "A) "
        return re.sub(r'\s+', ' ', s).strip().lower()

    def _encontrar_indice_correto(self, pergunta):
        alts = pergunta.get('alternativas', [])
        resp_raw = pergunta.get('resposta', '')
        
        # 1. Letra inicial (A, B, C...)
        m = re.match(r'^\s*([A-Za-z])\b', resp_raw)
        if m:
            idx = ord(m.group(1).lower()) - 97
            if 0 <= idx < len(alts): return idx
            
        # 2. Texto exato normalizado
        resp_norm = self._normalize(resp_raw)
        for i, a in enumerate(alts):
            if self._normalize(a) == resp_norm: return i
        return None