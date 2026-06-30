import pdfplumber
import re
import json
import os

def extrair_e_salvar_json(caminho_pdf, numero_lista, nome_arquivo_saida):
    questoes = []
    
    # Expressão regular para detectar "Número." no início da linha (ex: 1. ou 1))
    padrao_inicio = re.compile(r'^(\d+)[.\)]\s+(.*)')
    
    print(f"Lendo o arquivo: {caminho_pdf}...")

    with pdfplumber.open(caminho_pdf) as pdf:
        texto_completo = ""
        for page in pdf.pages:
            # Extrai o texto da página
            texto_extraido = page.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"

    linhas = texto_completo.split('\n')
    questao_atual = None
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        
        # Ignora cabeçalhos do professor/instituição para não poluir o JSON
        if any(x in linha.upper() for x in ["UEZO", "PROFESSOR", "DISCIPLINA", "LISTA"]):
            continue

        match = padrao_inicio.match(linha)
        
        if match:
            # Se já havia uma questão sendo processada, salva ela na lista
            if questao_atual:
                questoes.append(questao_atual)
            
            numero = int(match.group(1))
            primeira_frase = match.group(2)
            
            # Cria a estrutura que você solicitou
            questao_atual = {
                "id": f"L{numero_lista}_Q{numero:02d}",
                "lista": numero_lista,
                "numero": numero,
                "pergunta": [primeira_frase],
                "resposta": "", # Fica vazio para você preencher
                "dica": "",     # Fica vazio para você preencher
                "imagem": f"FISICAII_L{numero_lista}_Q{numero}.png"
            }
        elif questao_atual:
            # Se a linha não começa com número, é continuação da pergunta anterior
            questao_atual["pergunta"].append(linha)
            
    # Adiciona a última questão processada
    if questao_atual:
        questoes.append(questao_atual)

    # --- PARTE QUE SALVA O ARQUIVO ---
    try:
        with open(nome_arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(questoes, f, indent=2, ensure_ascii=False)
        print(f"Sucesso! {len(questoes)} questões salvas em: {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

# --- CONFIGURAÇÃO DE USO ---
# 1. Coloque o nome do arquivo PDF que você baixou
# 2. Defina o número da lista
# 3. Defina o nome do arquivo JSON que será criado
extrair_e_salvar_json(
    caminho_pdf="Física II - Lista 6.pdf", 
    numero_lista=6, 
    nome_arquivo_saida="banco_de_perguntas/lista6_extraida.json"
)