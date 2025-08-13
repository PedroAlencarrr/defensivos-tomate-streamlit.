import json
import pandas as pd
import re
import os
import sqlite3

# --- Configuração do Banco de Dados ---
# O caminho do DB precisa ser absoluto para o Streamlit Cloud
# Como o database.db estará na pasta src, ajustamos o caminho
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'src', 'database.db')

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    return re.sub(r'[^a-z0-9]', '', s.lower())

def populate_db():
    # Caminhos relativos ao local do script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    JSON_FILE_PATH = os.path.join(dir_path, 'src', 'agrofit_produtos_tomate_final_rebuilt.json')
    
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar a tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_comercial TEXT NOT NULL,
            ingrediente_ativo TEXT NOT NULL,
            dosagem TEXT,
            alvo TEXT,
            grupo_quimico TEXT,
            empresa TEXT,
            classe_toxicologica TEXT,
            mosca_branca INTEGER
        )
    """)
    conn.commit()

    # Limpar dados existentes
    cursor.execute("DELETE FROM produtos")
    conn.commit()
    print("Banco de dados limpo.")

    print(f"Carregando dados de: {JSON_FILE_PATH}")
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    print(f"Total de {len(df)} produtos carregados do JSON.")

    # Inserir dados na tabela
    for index, row in df.iterrows():
        cursor.execute("""
            INSERT INTO produtos (
                nome_comercial, ingrediente_ativo, dosagem, alvo, grupo_quimico, 
                empresa, classe_toxicologica, mosca_branca
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get("Nome Comercial"),
            row.get("Ingrediente Ativo"),
            row.get("dosagem_oficial_para_tomate_envarado") or row.get("dosagem"),
            row.get("Alvo"),
            row.get("Grupo Químico"),
            row.get("Empresa"),
            row.get("Classe Toxicológica"),
            int(bool(row.get("Mosca Branca"))) # SQLite armazena booleanos como 0 ou 1
        ))
    conn.commit()
    print(f"Banco de dados populado com {cursor.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]} produtos.")

    conn.close()

if __name__ == '__main__':
    populate_db()