import pandas as pd
from typing import List

def remove_duplicates(df: pd.DataFrame, subset_keys: List[str]) -> pd.DataFrame:
    """
    Remove duplicatas de um DataFrame baseando-se nas chaves únicas informadas.
    Por regra de negócio, mantemos o último registro (keep='last').
    """
    tamanho_antes = len(df)
    df_clean = df.drop_duplicates(subset=subset_keys, keep='last')
    duplicatas_removidas = tamanho_antes - len(df_clean)
    
    print(f"Duplicatas removidas: {duplicatas_removidas}")
    return df_clean
