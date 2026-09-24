import os
from pathlib import Path

# Local imports
from data_loader import load_pam_data, load_ppm_data, load_pib_data
from data_cleaner import remove_duplicates
from data_standardizer import tratar_simbolos_ausencias, padronizar_colunas_e_categorias

def run_pipeline():
    print("Iniciando pipeline de preparação de dados...")
    
    # Paths base
    base_dir = Path(__file__).resolve().parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    
    # Criar pasta de dados tratados se não existir
    os.makedirs(processed_dir, exist_ok=True)
    
    # --- 1. Leitura ---
    print("\n--- 1. Leitura dos Dados ---")
    print("Lendo bases PAM...")
    df_pam = load_pam_data(raw_dir)
    print(f"Base PAM carregada com {len(df_pam)} registros.")
    
    print("Lendo base PPM...")
    ppm_path = raw_dir / "t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv"
    df_ppm = load_ppm_data(str(ppm_path))
    print(f"Base PPM carregada com {len(df_ppm)} registros.")
    
    print("Lendo base PIB...")
    pib_path = raw_dir / "t5938_pib_agropecuaria_2003_2023_ce_br.csv"
    df_pib = load_pib_data(str(pib_path))
    print(f"Base PIB carregada com {len(df_pib)} registros.")
    
    # --- 2. Limpeza (Remoção de Duplicatas) ---
    print("\n--- 2. Limpeza de Duplicatas ---")
    chaves_pam = ['nivel_territorial_codigo', 'territorio_codigo', 'ano_codigo', 'variavel_codigo', 'produto_codigo']
    chaves_ppm = ['nivel_territorial_codigo', 'territorio_codigo', 'ano_codigo', 'variavel_codigo', 'tipo_rebanho_codigo']
    chaves_pib = ['nivel_territorial_codigo', 'territorio_codigo', 'ano_codigo', 'variavel_codigo']
    
    print("Removendo duplicatas PAM...")
    df_pam = remove_duplicates(df_pam, subset_keys=chaves_pam)
    print("Removendo duplicatas PPM...")
    df_ppm = remove_duplicates(df_ppm, subset_keys=chaves_ppm)
    print("Removendo duplicatas PIB...")
    df_pib = remove_duplicates(df_pib, subset_keys=chaves_pib)
    
    # --- 3. Padronização ---
    print("\n--- 3. Padronização (Tratamento de Símbolos, Ausências, Colunas e Categorias) ---")
    print("Padronizando PAM...")
    df_pam = tratar_simbolos_ausencias(df_pam)
    df_pam = padronizar_colunas_e_categorias(df_pam)
    
    print("Padronizando PPM...")
    df_ppm = tratar_simbolos_ausencias(df_ppm)
    df_ppm = padronizar_colunas_e_categorias(df_ppm)
    
    print("Padronizando PIB...")
    df_pib = tratar_simbolos_ausencias(df_pib)
    df_pib = padronizar_colunas_e_categorias(df_pib)
    
    # Validações Finais
    print("\n--- Validação Pós-Tratamento ---")
    print(f"PAM - Nulos (ausentes + especiais): {df_pam['valor'].isna().sum()} | Inibidos (X): {df_pam['valor_is_inibido'].sum()}")
    print(f"PPM - Nulos (ausentes + especiais): {df_ppm['valor'].isna().sum()} | Inibidos (X): {df_ppm['valor_is_inibido'].sum()}")
    print(f"PIB - Nulos (ausentes + especiais): {df_pib['valor'].isna().sum()} | Inibidos (X): {df_pib['valor_is_inibido'].sum()}")
    
    # --- 4. Salvamento ---
    print("\n--- 4. Salvamento dos Dados Tratados ---")
    pam_out = processed_dir / "pam_tratado.csv"
    ppm_out = processed_dir / "ppm_tratado.csv"
    pib_out = processed_dir / "pib_tratado.csv"
    
    print(f"Salvando {pam_out}...")
    df_pam.to_csv(pam_out, index=False)
    
    print(f"Salvando {ppm_out}...")
    df_ppm.to_csv(ppm_out, index=False)
    
    print(f"Salvando {pib_out}...")
    df_pib.to_csv(pib_out, index=False)
    
    print("\n--- 5. Cruzamento das Bases (Camada Analytical) ---")
    script_path = base_dir / "src" / "cruzamento_bases.py"
    if script_path.exists():
        import subprocess
        import sys
        print("Executando cruzamento_bases.py...")
        # Executa a partir da pasta src para respeitar os caminhos relativos do script original
        resultado = subprocess.run([sys.executable, script_path.name], cwd=str(base_dir / "src"))
        if resultado.returncode == 0:
            print("\nCruzamento e geração da camada analytical concluídos!")
        else:
            print("\nErro ao tentar cruzar as bases.")
    else:
        print("\nScript cruzamento_bases.py não encontrado, pulando etapa de integração.")
        
    print("\nPipeline executado com sucesso!")

if __name__ == "__main__":
    run_pipeline()
