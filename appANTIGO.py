# app.py (versão corrigida)
import json
import os
import random
import platform
import re

chance_inverter = 0.0

# Função para limpar o console
def limpar_console():
    sistema = platform.system()
    if sistema == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Função para carregar perguntas de um arquivo JSON
def carregar_perguntas(arquivo_json):
    with open(arquivo_json, 'r', encoding='utf-8') as file:
        perguntas = json.load(file)
    return perguntas

# Função para carregar perguntas incorretas de um arquivo TXT
def carregar_incorretas(nome_arquivo):
    perguntas_incorretas = {}
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(0, len(lines), 3):
                try:
                    numero = int(lines[i].strip().split(": ")[1])
                    resposta_info = lines[i+1].strip().split(": ")[1]
                    contador = int(lines[i+2].strip().split(": ")[1])
                    perguntas_incorretas[numero] = {'resposta': resposta_info, 'contador': contador}
                except (IndexError, ValueError):
                    pass
    return perguntas_incorretas

# Função para salvar perguntas incorretas em um arquivo TXT
def salvar_incorretas(perguntas_incorretas, nome_arquivo):
    with open(nome_arquivo, 'w', encoding='utf-8') as file:
        for numero, info in perguntas_incorretas.items():
            file.write(f"Pergunta {numero}: {info['resposta']}\n")
            file.write(f"Contador de Erros: {info['contador']}\n\n")

# --- helpers de normalização e detecção de resposta correta ---
def _normalize_option_text(s: str) -> str:
    """Remove prefix de letra/extras e normaliza espaços e minusculas."""
    if s is None:
        return ""
    s = s.strip()
    # remove prefixos do tipo "A)", "A.", "A -", "A ", "A –"
    s = re.sub(r'^[A-Za-z]\W*\s*', '', s)
    # collapse spaces
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()

def encontrar_indice_correto(pergunta) -> int:
    """
    Retorna o índice (0-based) da alternativa correta ou None se não identificado.
    Estratégia:
     1) se pergunta['resposta'] começar com letra (A..Z), usar isso;
     2) senão, normalizar e comparar textos das alternativas;
     3) senão, comparar igualdade limpa.
    """
    alts = pergunta.get('alternativas', [])
    resp_raw = pergunta.get('resposta', '')
    if not alts:
        return None

    # 1) tentativa por letra inicial na resposta: "B texto..." -> 'b' -> índice
    m = re.match(r'^\s*([A-Za-z])\b', resp_raw)
    if m:
        letra = m.group(1).lower()
        idx = ord(letra) - 97
        if 0 <= idx < len(alts):
            return idx

    # 2) normalização textual: remove prefixos e compara
    resp_norm = _normalize_option_text(resp_raw)
    if resp_norm:
        for i, a in enumerate(alts):
            if _normalize_option_text(a) == resp_norm:
                return i

    # 3) fallback: compara stripped completas
    resp_strip = resp_raw.strip().lower()
    for i, a in enumerate(alts):
        if a.strip().lower() == resp_strip:
            return i

    # não conseguiu identificar
    return None

# --- fim helpers ---

def quiz(perguntas, nome_banco):
    perguntas_incorretas = carregar_incorretas(f"perguntas_incorretas_{nome_banco}.txt")
    acertos = 0
    erros = 0
    indices_perguntas = list(range(len(perguntas)))

    # Perguntar só uma vez se o usuário quer usar alternativas
    usar_alternativas = False
    if any("alternativas" in p for p in perguntas):
        escolha = input("Detectei questões com alternativas. Deseja usá-las? (s/n): ").strip().lower()
        usar_alternativas = (escolha == 's')

    while indices_perguntas:
        limpar_console()
        print(f"\nAcertos: {acertos} | Erros: {erros}")
        indice = random.choice(indices_perguntas)
        pergunta = perguntas[indice]

        print(f"\nPergunta {pergunta['numero']}:")

        if usar_alternativas and "alternativas" in pergunta:
            # Mostra a pergunta + alternativas
            print(pergunta['pergunta'])
            alts = pergunta['alternativas']
            for i, alt in enumerate(alts, 1):
                letra = chr(96 + i)  # 1 -> a, 2 -> b, ...
                print(f"{i}) {alt}   [{letra}]")

            resposta_usuario = input("\nDigite o número ou a letra da alternativa correta (ou 'q' para sair): ").strip().lower()
            if resposta_usuario == 'q':
                break

            try:
                # Aceita tanto número quanto letra (dinamicamente até len(alts))
                if resposta_usuario.isdigit():
                    indice_resp = int(resposta_usuario) - 1
                elif re.match(r'^[a-z]$', resposta_usuario):
                    indice_resp = ord(resposta_usuario) - 97
                else:
                    raise ValueError("Entrada inválida")

                # valida índice
                if indice_resp < 0 or indice_resp >= len(alts):
                    raise IndexError("Alternativa fora do intervalo")

                alternativa_escolhida = alts[indice_resp]

                # determina índice correto (mais robusto que comparar strings diretamente)
                indice_correto = encontrar_indice_correto(pergunta)

                acertou = False
                if indice_correto is not None:
                    acertou = (indice_resp == indice_correto)
                else:
                    # fallback: compara strings normalizadas (quando não foi possível detectar índice)
                    if _normalize_option_text(alternativa_escolhida) == _normalize_option_text(pergunta.get('resposta', '')):
                        acertou = True

                if acertou:
                    print("✅ Correto!")
                    acertos += 1
                else:
                    print(f"❌ Errado. Resposta certa: {pergunta['resposta']}")
                    erros += 1
                    if pergunta['numero'] in perguntas_incorretas:
                        perguntas_incorretas[pergunta['numero']]['contador'] += 1
                    else:
                        perguntas_incorretas[pergunta['numero']] = {'resposta': pergunta['resposta'], 'contador': 1}
            except (ValueError, IndexError):
                print("Entrada inválida ou alternativa fora do intervalo.")
        else:
            # Fluxo normal que você já tinha
            print(pergunta['pergunta'])
            input("\nPressione Enter para ver a resposta...")
            print(f"Resposta: {pergunta['resposta']}")

            resposta_usuario = input("\nVocê acertou a resposta? (1 para Sim, 0 para Não, q para sair): ").strip().lower()
            if resposta_usuario == '1':
                acertos += 1
            elif resposta_usuario == '0':
                erros += 1
                if pergunta['numero'] in perguntas_incorretas:
                    perguntas_incorretas[pergunta['numero']]['contador'] += 1
                else:
                    perguntas_incorretas[pergunta['numero']] = {'resposta': pergunta['resposta'], 'contador': 1}
            elif resposta_usuario == 'q':
                break

        indices_perguntas.remove(indice)

    if perguntas_incorretas:
        nome_arquivo = f"perguntas_incorretas_{nome_banco}.txt"
        salvar_incorretas(perguntas_incorretas, nome_arquivo)

    print(f"\nAcertos finais: {acertos}")
    print(f"Erros finais: {erros}")

# Menu para seleção do banco de perguntas
def menu():
    pasta = "banco_de_perguntas"  # Nome da pasta onde estão os arquivos JSON
    arquivos_json = [f for f in os.listdir(pasta) if f.endswith('.json')]

    if not arquivos_json:
        print("Nenhum arquivo JSON encontrado na pasta.")
        return

    print("Escolha o banco de perguntas:")
    for i, arquivo in enumerate(arquivos_json, 1):
        nome_materia = os.path.splitext(arquivo)[0]  # Nome do arquivo sem extensão
        print(f"{i} - {nome_materia} ({arquivo})")

    escolha = input("Digite o número correspondente à sua escolha: ")

    try:
        indice = int(escolha) - 1
        arquivo_json = arquivos_json[indice]
        nome_banco = os.path.splitext(arquivo_json)[0]
    except (IndexError, ValueError):
        print("Escolha inválida.")
        return

    perguntas = carregar_perguntas(os.path.join(pasta, arquivo_json))
    quiz(perguntas, nome_banco)

if __name__ == "__main__":
    menu()
