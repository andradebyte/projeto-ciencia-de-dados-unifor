#!/usr/bin/env python
# coding: utf-8

# # Cruzamento das bases (PAM x PPM x PIB)
# 
# Integra as três tabelas obrigatórias do Tema 2 (Agropecuária e transformação econômica) pela chave **código IBGE do município** (`territorio_codigo`) + **ano**, no nível `nivel_territorial_nome == 'Município'`. Não usa nome do município como chave, conforme exigido.

# In[1]:


import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


# **Regras de agregação respeitadas neste cruzamento:**
# - PAM: quantidades de produtos diferentes (unidades distintas) não são somadas — cada produto vira uma coluna própria.
# - PPM: efetivo de espécies diferentes não é somado — cada espécie vira uma coluna própria.
# - PIB: valores monetários da PAM e do PIB estão a preços correntes — nenhuma comparação de série temporal é feita sem deixar isso explícito; aqui só integramos os valores, sem deflacionar.
# - Períodos diferentes por base (PAM/PPM até 2024, PIB até 2023, VAB agropecuário até 2021) não são forçados a bater — o cruzamento produz linhas com `NaN` fora do período de cada base, e o percentual de correspondência por período é medido explicitamente abaixo.

# ## Carregamento e recorte ao nível Município

# In[2]:


df_pam = pd.read_csv('../data/processed/pam_tratado.csv')
df_ppm = pd.read_csv('../data/processed/ppm_tratado.csv')
df_pib = pd.read_csv('../data/processed/pib_tratado.csv')

pam_mun = df_pam[df_pam['nivel_territorial_nome'] == 'Município'].copy()
ppm_mun = df_ppm[df_ppm['nivel_territorial_nome'] == 'Município'].copy()
pib_mun = df_pib[df_pib['nivel_territorial_nome'] == 'Município'].copy()

for nome, df in [('PAM', pam_mun), ('PPM', ppm_mun), ('PIB', pib_mun)]:
    print(f"{nome}: {df['territorio_codigo'].nunique()} municípios, anos {df['ano_nome'].min()}-{df['ano_nome'].max()}")


# ## Cópias limpas (sem colunas `*_codigo`)
# 
# As colunas `*_codigo` (exceto `territorio_codigo`, que é a chave de pareamento) já cumpriram seu papel na etapa de tratamento — daqui pra frente só usamos os nomes. Salva uma cópia "limpa" de cada base em `data/analytical/`, sem essas colunas, para consulta e uso nos demais notebooks/dashboard.

# In[3]:


import os

os.makedirs('../data/analytical', exist_ok=True)

for nome, df in [('pam', df_pam), ('ppm', df_ppm), ('pib', df_pib)]:
    colunas_codigo = [c for c in df.columns if c.endswith('_codigo') and c != 'territorio_codigo']
    df_limpo = df.drop(columns=colunas_codigo)
    caminho = f'../data/analytical/{nome}_limpo.csv'
    df_limpo.to_csv(caminho, index=False)
    print(f"Salvo: {caminho} ({len(df_limpo)} linhas, {len(df_limpo.columns)} colunas; removidas: {colunas_codigo})")


# ## PAM em formato largo (variável × produto)
# Chave: `territorio_codigo` + `ano_nome`. Cardinalidade esperada: **1 linha por município-ano** (cada combinação de variável × produto vira uma coluna, nunca somada).

# In[4]:


produto_slug = {
    'Milho (em grão)': 'milho',
    'Feijão (em grão)': 'feijao',
    'Mandioca': 'mandioca',
    'Cana-de-açúcar': 'cana',
    'Banana (cacho)': 'banana',
    'Castanha de caju': 'castanha_caju',
    'Melão': 'melao',
}
variavel_slug_pam = {
    'Valor da produção': 'valor',
    'Área plantada ou destinada à colheita': 'area_plantada',
    'Área colhida': 'area_colhida',
    'Quantidade produzida': 'quantidade',
    'Rendimento médio da produção': 'rendimento',
}

pam_mun['coluna'] = (
    'pam_' + pam_mun['variavel_nome'].map(variavel_slug_pam) + '_' + pam_mun['produto_nome'].map(produto_slug)
)

pam_wide = pam_mun.pivot_table(
    index=['territorio_codigo', 'territorio_nome', 'ano_nome'], columns='coluna', values='valor'
).reset_index()

cardinalidade_pam = pam_mun.groupby(['territorio_codigo', 'ano_nome', 'coluna']).size().max()
print(f"Cardinalidade observada (território+ano+coluna -> linhas): máximo {cardinalidade_pam} (esperado 1)")
print(f"Linhas em pam_wide: {len(pam_wide)} (esperado: {pam_mun['territorio_codigo'].nunique()} municípios × {pam_mun['ano_nome'].nunique()} anos = {pam_mun['territorio_codigo'].nunique() * pam_mun['ano_nome'].nunique()})")
pam_wide.head()


# ## PPM em formato largo (espécie)
# Mesma chave. Cardinalidade esperada: **1 linha por município-ano** (cada espécie vira uma coluna, nunca somada).

# In[5]:


especie_slug = {
    'Bovino': 'bovino',
    'Caprino': 'caprino',
    'Ovino': 'ovino',
    'Suíno - total': 'suino',
    'Galináceos - total': 'galinaceos',
}

ppm_mun['coluna'] = 'ppm_efetivo_' + ppm_mun['tipo_rebanho_nome'].map(especie_slug)

ppm_wide = ppm_mun.pivot_table(
    index=['territorio_codigo', 'territorio_nome', 'ano_nome'], columns='coluna', values='valor'
).reset_index()

cardinalidade_ppm = ppm_mun.groupby(['territorio_codigo', 'ano_nome', 'coluna']).size().max()
print(f"Cardinalidade observada: máximo {cardinalidade_ppm} (esperado 1)")
print(f"Linhas em ppm_wide: {len(ppm_wide)}")
ppm_wide.head()


# ## PIB em formato largo (variável)
# Mesma chave. Cardinalidade esperada: **1 linha por município-ano**.

# In[6]:


variavel_slug_pib = {
    'Produto Interno Bruto a preços correntes': 'pib',
    'Valor adicionado bruto a preços correntes total': 'vab_total',
    'Valor adicionado bruto a preços correntes da agropecuária': 'vab_agropecuario',
    'Participação do valor adicionado bruto a preços correntes da agropecuária no valor adicionado bruto a preços correntes total': 'pct_agropecuario_vab',
}

pib_mun['coluna'] = 'pib_' + pib_mun['variavel_nome'].map(variavel_slug_pib)

pib_wide = pib_mun.pivot_table(
    index=['territorio_codigo', 'territorio_nome', 'ano_nome'], columns='coluna', values='valor'
).reset_index()

cardinalidade_pib = pib_mun.groupby(['territorio_codigo', 'ano_nome', 'coluna']).size().max()
print(f"Cardinalidade observada: máximo {cardinalidade_pib} (esperado 1)")
print(f"Linhas em pib_wide: {len(pib_wide)}")
pib_wide.head()


# ## Junção pela chave (território + ano)
# `outer join` para preservar todas as combinações e deixar explícito, via `NaN`, onde não há correspondência entre as bases (ex.: PIB não tem 2024; VAB agropecuário não tem 2022-2023).

# In[7]:


cruzamento = pam_wide.merge(
    ppm_wide, on=['territorio_codigo', 'territorio_nome', 'ano_nome'], how='outer', suffixes=('', '_ppm')
).merge(
    pib_wide, on=['territorio_codigo', 'territorio_nome', 'ano_nome'], how='outer', suffixes=('', '_pib')
)

cruzamento = cruzamento.sort_values(['territorio_codigo', 'ano_nome']).reset_index(drop=True)
print(f"Linhas no cruzamento final: {len(cruzamento)}")
print(f"Municípios: {cruzamento['territorio_codigo'].nunique()}")
print(f"Anos: {cruzamento['ano_nome'].min()}-{cruzamento['ano_nome'].max()}")
cruzamento.head()


# ## Medindo correspondências e não correspondências
# Quanto cada base 'bate' com as outras, por município e por ano.

# In[8]:


municipios_pam = set(pam_mun['territorio_codigo'])
municipios_ppm = set(ppm_mun['territorio_codigo'])
municipios_pib = set(pib_mun['territorio_codigo'])

print("--- Correspondência de municípios ---")
print(f"PAM ∩ PPM ∩ PIB: {len(municipios_pam & municipios_ppm & municipios_pib)} de {len(municipios_pam | municipios_ppm | municipios_pib)} municípios totais")
print(f"Em PAM mas não em PPM: {len(municipios_pam - municipios_ppm)}")
print(f"Em PAM mas não em PIB: {len(municipios_pam - municipios_pib)}")
print(f"Em PPM mas não em PIB: {len(municipios_ppm - municipios_pib)}")


# In[9]:


anos_pam = set(pam_mun['ano_nome'])
anos_ppm = set(ppm_mun['ano_nome'])
anos_pib = set(pib_mun['ano_nome'])
anos_vab = set(pib_mun.loc[pib_mun['variavel_nome'].str.contains('adicionado'), 'ano_nome'])

print("--- Correspondência de anos ---")
print(f"PAM: {sorted(anos_pam)}")
print(f"PPM: {sorted(anos_ppm)}")
print(f"PIB (todas as variáveis): {sorted(anos_pib)}")
print(f"PIB - VAB (total/agropecuário/participação): {sorted(anos_vab)}")
print()
print(f"PAM ∩ PIB: {len(anos_pam & anos_pib)} de {len(anos_pam)} anos do PAM ({len(anos_pam & anos_pib) / len(anos_pam):.1%})")
print(f"PAM ∩ VAB agropecuário: {len(anos_pam & anos_vab)} de {len(anos_pam)} anos do PAM ({len(anos_pam & anos_vab) / len(anos_pam):.1%})")


# In[10]:


print("--- % de linhas com valor ausente por coluna (no cruzamento final) ---")
colunas_valor = [c for c in cruzamento.columns if c not in ('territorio_codigo', 'territorio_nome', 'ano_nome')]
ausencia = (cruzamento[colunas_valor].isna().mean() * 100).sort_values(ascending=False)
print(ausencia.round(1))


# ## Salvando o cruzamento em `data/analytical/`

# In[11]:


import os

os.makedirs('../data/analytical', exist_ok=True)
cruzamento.to_csv('../data/analytical/cruzamento_pam_ppm_pib.csv', index=False)
print(f"Salvo: data/analytical/cruzamento_pam_ppm_pib.csv ({len(cruzamento)} linhas, {len(cruzamento.columns)} colunas)")

