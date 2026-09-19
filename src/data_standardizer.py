import pandas as pd
import numpy as np

def tratar_simbolos_ausencias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata símbolos especiais e ausências na coluna 'valor'.
    - '-' e '0' são convertidos para '0.0'
    - 'X', '..', '...' são convertidos para NaN
    - Cria a flag 'valor_is_inibido' para os casos em que o valor era 'X'
    - Converte a coluna 'valor' para numérico
    """
    df_treated = df.copy()
    
    # Garantir que a coluna valor seja string para o tratamento inicial
    df_treated['valor'] = df_treated['valor'].astype(str).str.strip()
    
    # 1. Criar a flag binária para 'X' (Dado Inibido)
    df_treated['valor_is_inibido'] = np.where(df_treated['valor'] == 'X', 1, 0)
    
    # 2. Aplicar as regras de substituição
    substituicoes = {
        '-': '0.0',
        '0': '0.0',
        'X': np.nan,
        '..': np.nan,
        '...': np.nan
    }
    df_treated['valor'] = df_treated['valor'].replace(substituicoes)
    
    # 3. Converter para numérico
    df_treated['valor'] = pd.to_numeric(df_treated['valor'], errors='coerce')
    
    return df_treated
