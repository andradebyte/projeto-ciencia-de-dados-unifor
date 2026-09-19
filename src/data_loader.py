import pandas as pd
import os
from pathlib import Path

def load_pam_data(directory: str) -> pd.DataFrame:
    """
    Carrega e concatena todos os arquivos CSV do PAM do diretório especificado.
    """
    arquivos_pam = [
        "t5457_pam_area_colhida_2003_2024_ce_br.csv",
        "t5457_pam_area_plantada_2003_2024_ce_br.csv",
        "t5457_pam_quantidade_produzida_2003_2024_ce_br.csv",
        "t5457_pam_rendimento_medio_2003_2024_ce_br.csv",
        "t5457_pam_valor_producao_2003_2024_ce_br.csv"
    ]
    
    dfs_pam = []
    for arquivo in arquivos_pam:
        path = Path(directory) / arquivo
        df = pd.read_csv(
            path, 
            sep=";", 
            dtype={"territorio_codigo": "string", "variavel_codigo": "string", "produto_codigo": "string"}
        )
        dfs_pam.append(df)
        
    df_pam = pd.concat(dfs_pam, ignore_index=True)
    return df_pam

def load_ppm_data(filepath: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV do PPM.
    """
    df_ppm = pd.read_csv(
        filepath, 
        sep=";", 
        dtype={"territorio_codigo": "string", "variavel_codigo": "string", "tipo_rebanho_codigo": "string"}
    )
    return df_ppm

def load_pib_data(filepath: str) -> pd.DataFrame:
    """
    Carrega o arquivo CSV do PIB.
    """
    df_pib = pd.read_csv(
        filepath, 
        sep=";", 
        dtype={"territorio_codigo": "string", "variavel_codigo": "string"}
    )
    return df_pib
