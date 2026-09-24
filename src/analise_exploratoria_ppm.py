#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt


# In[2]:


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df = pd.read_csv('../data/processed/ppm_tratado.csv')
df.head()


# Como são os dados brutos do PPM?

# In[3]:


colunas_codigo = [c for c in df.columns if c.endswith('_codigo')]
df_nome = df.drop(columns=colunas_codigo)
df_nome.head()


# Como ficam os dados sem as colunas de código?

# **Regra importante (não somar espécies):** bovinos, caprinos, ovinos, suínos e galináceos são medidos em "Cabeças", mas não são unidades equivalentes entre si — uma cabeça de boi e uma de galinha não têm o mesmo peso econômico ou biológico. Por isso, em nenhum momento desta análise somamos `tipo_rebanho_nome` entre si (não existe "rebanho total"). Toda agregação (Brasil, Ceará, participação %, municípios) é feita **dentro de uma mesma espécie**.

# In[4]:


df_nome.groupby('tipo_rebanho_nome')['valor'].describe()


# Como se distribui o efetivo (em cabeças) de cada espécie?

# In[5]:


print("Valores nulos:", df_nome['valor'].isna().sum())
print("Valores inibidos (sigilo do IBGE):", df_nome['valor_is_inibido'].sum())
print("Linhas duplicadas:", df_nome.duplicated().sum())


# Os dados têm valores nulos, inibidos ou duplicados?

# In[6]:


territorios = df_nome['territorio_nome'].unique()
print(len(territorios))
print(territorios)


# Quantos e quais territórios temos no PPM?

# In[7]:


anos = df_nome['ano_nome'].unique()
print(len(anos))
print(anos)


# Quantos e quais anos o PPM cobre?

# In[8]:


variaveis = df_nome['variavel_nome'].unique()
print(len(variaveis))
print(variaveis)


# Quais variáveis o PPM mede?

# In[9]:


unidades = df_nome['unidade'].unique()
print(len(unidades))
print(unidades)


# Em qual unidade essa variável é medida?

# In[10]:


especies = df_nome['tipo_rebanho_nome'].unique()
print(len(especies))
print(especies)


# Quais espécies de rebanho o PPM cobre?

# ## Bovino

# Como evoluiu o efetivo de bovino no Brasil e no Ceará?

# In[11]:


projecao_bovino_brasil = df_nome[(df_nome['tipo_rebanho_nome'] == 'Bovino') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_bovino_brasil


# In[12]:


projecao_bovino_ceara = df_nome[(df_nome['tipo_rebanho_nome'] == 'Bovino') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_bovino_ceara


# In[13]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}
series_bovino = {"Brasil": projecao_bovino_brasil['Bovino'], "Ceará": projecao_bovino_ceara['Bovino']}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
for territorio, cor in cores.items():
    serie = series_bovino[territorio]
    ax1.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax2.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

ax1.set_title("Efetivo de Bovino — Brasil x Ceará")
ax1.set_xlabel("Ano")
ax1.set_ylabel("Cabeças")
ax1.grid(True, color="#e1e0d9", linewidth=0.8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.legend(frameon=False)

ax2.set_yscale("log")
ax2.set_title("Efetivo de Bovino — Brasil x Ceará (escala log)")
ax2.set_xlabel("Ano")
ax2.set_ylabel("Cabeças (escala log)")
ax2.grid(True, color="#e1e0d9", linewidth=0.8)
ax2.spines[["top", "right"]].set_visible(False)
ax2.legend(frameon=False)

plt.tight_layout()
plt.show()


# In[14]:


print(projecao_bovino_brasil)
print()
print(projecao_bovino_ceara)


# ## Caprino

# Como evoluiu o efetivo de caprino no Brasil e no Ceará?

# In[15]:


projecao_caprino_brasil = df_nome[(df_nome['tipo_rebanho_nome'] == 'Caprino') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_caprino_brasil


# In[16]:


projecao_caprino_ceara = df_nome[(df_nome['tipo_rebanho_nome'] == 'Caprino') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_caprino_ceara


# In[17]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}
series_caprino = {"Brasil": projecao_caprino_brasil['Caprino'], "Ceará": projecao_caprino_ceara['Caprino']}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
for territorio, cor in cores.items():
    serie = series_caprino[territorio]
    ax1.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax2.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

ax1.set_title("Efetivo de Caprino — Brasil x Ceará")
ax1.set_xlabel("Ano")
ax1.set_ylabel("Cabeças")
ax1.grid(True, color="#e1e0d9", linewidth=0.8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.legend(frameon=False)

ax2.set_yscale("log")
ax2.set_title("Efetivo de Caprino — Brasil x Ceará (escala log)")
ax2.set_xlabel("Ano")
ax2.set_ylabel("Cabeças (escala log)")
ax2.grid(True, color="#e1e0d9", linewidth=0.8)
ax2.spines[["top", "right"]].set_visible(False)
ax2.legend(frameon=False)

plt.tight_layout()
plt.show()


# In[18]:


print(projecao_caprino_brasil)
print()
print(projecao_caprino_ceara)


# ## Ovino

# Como evoluiu o efetivo de ovino no Brasil e no Ceará?

# In[19]:


projecao_ovino_brasil = df_nome[(df_nome['tipo_rebanho_nome'] == 'Ovino') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_ovino_brasil


# In[20]:


projecao_ovino_ceara = df_nome[(df_nome['tipo_rebanho_nome'] == 'Ovino') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_ovino_ceara


# In[21]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}
series_ovino = {"Brasil": projecao_ovino_brasil['Ovino'], "Ceará": projecao_ovino_ceara['Ovino']}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
for territorio, cor in cores.items():
    serie = series_ovino[territorio]
    ax1.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax2.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

ax1.set_title("Efetivo de Ovino — Brasil x Ceará")
ax1.set_xlabel("Ano")
ax1.set_ylabel("Cabeças")
ax1.grid(True, color="#e1e0d9", linewidth=0.8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.legend(frameon=False)

ax2.set_yscale("log")
ax2.set_title("Efetivo de Ovino — Brasil x Ceará (escala log)")
ax2.set_xlabel("Ano")
ax2.set_ylabel("Cabeças (escala log)")
ax2.grid(True, color="#e1e0d9", linewidth=0.8)
ax2.spines[["top", "right"]].set_visible(False)
ax2.legend(frameon=False)

plt.tight_layout()
plt.show()


# In[22]:


print(projecao_ovino_brasil)
print()
print(projecao_ovino_ceara)


# ## Suíno

# Como evoluiu o efetivo de suíno no Brasil e no Ceará?

# In[23]:


projecao_suino_brasil = df_nome[(df_nome['tipo_rebanho_nome'] == 'Suíno - total') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_suino_brasil


# In[24]:


projecao_suino_ceara = df_nome[(df_nome['tipo_rebanho_nome'] == 'Suíno - total') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_suino_ceara


# In[25]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}
series_suino = {"Brasil": projecao_suino_brasil['Suíno - total'], "Ceará": projecao_suino_ceara['Suíno - total']}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
for territorio, cor in cores.items():
    serie = series_suino[territorio]
    ax1.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax2.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

ax1.set_title("Efetivo de Suíno — Brasil x Ceará")
ax1.set_xlabel("Ano")
ax1.set_ylabel("Cabeças")
ax1.grid(True, color="#e1e0d9", linewidth=0.8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.legend(frameon=False)

ax2.set_yscale("log")
ax2.set_title("Efetivo de Suíno — Brasil x Ceará (escala log)")
ax2.set_xlabel("Ano")
ax2.set_ylabel("Cabeças (escala log)")
ax2.grid(True, color="#e1e0d9", linewidth=0.8)
ax2.spines[["top", "right"]].set_visible(False)
ax2.legend(frameon=False)

plt.tight_layout()
plt.show()


# In[26]:


print(projecao_suino_brasil)
print()
print(projecao_suino_ceara)


# ## Galináceos

# Como evoluiu o efetivo de galináceos no Brasil e no Ceará?

# In[27]:


projecao_galinaceos_brasil = df_nome[(df_nome['tipo_rebanho_nome'] == 'Galináceos - total') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_galinaceos_brasil


# In[28]:


projecao_galinaceos_ceara = df_nome[(df_nome['tipo_rebanho_nome'] == 'Galináceos - total') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
)
projecao_galinaceos_ceara


# In[29]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}
series_galinaceos = {"Brasil": projecao_galinaceos_brasil['Galináceos - total'], "Ceará": projecao_galinaceos_ceara['Galináceos - total']}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
for territorio, cor in cores.items():
    serie = series_galinaceos[territorio]
    ax1.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax2.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

ax1.set_title("Efetivo de Galináceos — Brasil x Ceará")
ax1.set_xlabel("Ano")
ax1.set_ylabel("Cabeças")
ax1.grid(True, color="#e1e0d9", linewidth=0.8)
ax1.spines[["top", "right"]].set_visible(False)
ax1.legend(frameon=False)

ax2.set_yscale("log")
ax2.set_title("Efetivo de Galináceos — Brasil x Ceará (escala log)")
ax2.set_xlabel("Ano")
ax2.set_ylabel("Cabeças (escala log)")
ax2.grid(True, color="#e1e0d9", linewidth=0.8)
ax2.spines[["top", "right"]].set_visible(False)
ax2.legend(frameon=False)

plt.tight_layout()
plt.show()


# In[30]:


print(projecao_galinaceos_brasil)
print()
print(projecao_galinaceos_ceara)


# ## Participação do Ceará no Brasil (%)

# In[31]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}


# ### Bovino

# Quanto o Ceará representa do efetivo de bovino do Brasil, ano a ano?

# In[32]:


percentual_bovino = (projecao_bovino_ceara['Bovino'] / projecao_bovino_brasil['Bovino']) * 100
resto_bovino = 100 - percentual_bovino

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_bovino.index, percentual_bovino, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_bovino.index, resto_bovino, left=percentual_bovino, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_bovino.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_bovino.index)
ax.invert_yaxis()
ax.set_xlabel("% do efetivo de bovino do Brasil")
ax.set_title("Participação do Ceará no efetivo de bovino do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_bovino)


# ### Caprino

# Quanto o Ceará representa do efetivo de caprino do Brasil, ano a ano?

# In[33]:


percentual_caprino = (projecao_caprino_ceara['Caprino'] / projecao_caprino_brasil['Caprino']) * 100
resto_caprino = 100 - percentual_caprino

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_caprino.index, percentual_caprino, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_caprino.index, resto_caprino, left=percentual_caprino, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_caprino.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_caprino.index)
ax.invert_yaxis()
ax.set_xlabel("% do efetivo de caprino do Brasil")
ax.set_title("Participação do Ceará no efetivo de caprino do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_caprino)


# ### Ovino

# Quanto o Ceará representa do efetivo de ovino do Brasil, ano a ano?

# In[34]:


percentual_ovino = (projecao_ovino_ceara['Ovino'] / projecao_ovino_brasil['Ovino']) * 100
resto_ovino = 100 - percentual_ovino

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_ovino.index, percentual_ovino, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_ovino.index, resto_ovino, left=percentual_ovino, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_ovino.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_ovino.index)
ax.invert_yaxis()
ax.set_xlabel("% do efetivo de ovino do Brasil")
ax.set_title("Participação do Ceará no efetivo de ovino do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_ovino)


# ### Suíno

# Quanto o Ceará representa do efetivo de suíno do Brasil, ano a ano?

# In[35]:


percentual_suino = (projecao_suino_ceara['Suíno - total'] / projecao_suino_brasil['Suíno - total']) * 100
resto_suino = 100 - percentual_suino

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_suino.index, percentual_suino, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_suino.index, resto_suino, left=percentual_suino, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_suino.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_suino.index)
ax.invert_yaxis()
ax.set_xlabel("% do efetivo de suíno do Brasil")
ax.set_title("Participação do Ceará no efetivo de suíno do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_suino)


# ### Galináceos

# Quanto o Ceará representa do efetivo de galináceos do Brasil, ano a ano?

# In[36]:


percentual_galinaceos = (projecao_galinaceos_ceara['Galináceos - total'] / projecao_galinaceos_brasil['Galináceos - total']) * 100
resto_galinaceos = 100 - percentual_galinaceos

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_galinaceos.index, percentual_galinaceos, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_galinaceos.index, resto_galinaceos, left=percentual_galinaceos, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_galinaceos.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_galinaceos.index)
ax.invert_yaxis()
ax.set_xlabel("% do efetivo de galináceos do Brasil")
ax.set_title("Participação do Ceará no efetivo de galináceos do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_galinaceos)


# ## Análise por Município

# ### Bovino

# Quais municípios têm maior e menor efetivo de bovino, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[37]:


pivot_municipios_bovino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Bovino') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_bovino


# In[38]:


total_municipios_bovino = pivot_municipios_bovino.sum(axis=0).sort_values(ascending=False)
top8_melhores_bovino = total_municipios_bovino.head(8)
top8_piores_bovino = total_municipios_bovino.tail(8).sort_values()

print("Top 8 melhores municípios - Bovino (soma 2003-2024):")
print(top8_melhores_bovino)
print()
print("Top 8 piores municípios - Bovino (soma 2003-2024):")
print(top8_piores_bovino)


# In[39]:


participacao_municipios_bovino = pivot_municipios_bovino.div(pivot_municipios_bovino.sum(axis=1), axis=0) * 100
ordem_municipios_bovino = total_municipios_bovino.index
cmap_municipios = plt.colormaps["viridis"]
n_municipios = len(ordem_municipios_bovino)
cor_por_municipio_bovino = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_bovino)}

anos_resumo = [2003, 2023]

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_bovino:
        pct = participacao_municipios_bovino.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_bovino[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% do efetivo de bovino do Ceará")
ax.set_title("Efetivo de bovino do Ceará preenchido pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Caprino

# Quais municípios têm maior e menor efetivo de caprino, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[40]:


pivot_municipios_caprino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Caprino') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_caprino


# In[41]:


total_municipios_caprino = pivot_municipios_caprino.sum(axis=0).sort_values(ascending=False)
top8_melhores_caprino = total_municipios_caprino.head(8)
top8_piores_caprino = total_municipios_caprino.tail(8).sort_values()

print("Top 8 melhores municípios - Caprino (soma 2003-2024):")
print(top8_melhores_caprino)
print()
print("Top 8 piores municípios - Caprino (soma 2003-2024):")
print(top8_piores_caprino)


# In[42]:


participacao_municipios_caprino = pivot_municipios_caprino.div(pivot_municipios_caprino.sum(axis=1), axis=0) * 100
ordem_municipios_caprino = total_municipios_caprino.index
cmap_municipios = plt.colormaps["viridis"]
n_municipios = len(ordem_municipios_caprino)
cor_por_municipio_caprino = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_caprino)}

anos_resumo = [2003, 2023]

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_caprino:
        pct = participacao_municipios_caprino.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_caprino[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% do efetivo de caprino do Ceará")
ax.set_title("Efetivo de caprino do Ceará preenchido pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Ovino

# Quais municípios têm maior e menor efetivo de ovino, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[43]:


pivot_municipios_ovino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Ovino') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_ovino


# In[44]:


total_municipios_ovino = pivot_municipios_ovino.sum(axis=0).sort_values(ascending=False)
top8_melhores_ovino = total_municipios_ovino.head(8)
top8_piores_ovino = total_municipios_ovino.tail(8).sort_values()

print("Top 8 melhores municípios - Ovino (soma 2003-2024):")
print(top8_melhores_ovino)
print()
print("Top 8 piores municípios - Ovino (soma 2003-2024):")
print(top8_piores_ovino)


# In[45]:


participacao_municipios_ovino = pivot_municipios_ovino.div(pivot_municipios_ovino.sum(axis=1), axis=0) * 100
ordem_municipios_ovino = total_municipios_ovino.index
cmap_municipios = plt.colormaps["viridis"]
n_municipios = len(ordem_municipios_ovino)
cor_por_municipio_ovino = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_ovino)}

anos_resumo = [2003, 2023]

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_ovino:
        pct = participacao_municipios_ovino.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_ovino[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% do efetivo de ovino do Ceará")
ax.set_title("Efetivo de ovino do Ceará preenchido pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Suíno

# Quais municípios têm maior e menor efetivo de suíno, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[46]:


pivot_municipios_suino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Suíno - total') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_suino


# In[47]:


total_municipios_suino = pivot_municipios_suino.sum(axis=0).sort_values(ascending=False)
top8_melhores_suino = total_municipios_suino.head(8)
top8_piores_suino = total_municipios_suino.tail(8).sort_values()

print("Top 8 melhores municípios - Suíno (soma 2003-2024):")
print(top8_melhores_suino)
print()
print("Top 8 piores municípios - Suíno (soma 2003-2024):")
print(top8_piores_suino)


# In[48]:


participacao_municipios_suino = pivot_municipios_suino.div(pivot_municipios_suino.sum(axis=1), axis=0) * 100
ordem_municipios_suino = total_municipios_suino.index
cmap_municipios = plt.colormaps["viridis"]
n_municipios = len(ordem_municipios_suino)
cor_por_municipio_suino = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_suino)}

anos_resumo = [2003, 2023]

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_suino:
        pct = participacao_municipios_suino.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_suino[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% do efetivo de suíno do Ceará")
ax.set_title("Efetivo de suíno do Ceará preenchido pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Galináceos

# Quais municípios têm maior e menor efetivo de galináceos, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[49]:


pivot_municipios_galinaceos = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Galináceos - total') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_galinaceos


# In[50]:


total_municipios_galinaceos = pivot_municipios_galinaceos.sum(axis=0).sort_values(ascending=False)
top8_melhores_galinaceos = total_municipios_galinaceos.head(8)
top8_piores_galinaceos = total_municipios_galinaceos.tail(8).sort_values()

print("Top 8 melhores municípios - Galináceos (soma 2003-2024):")
print(top8_melhores_galinaceos)
print()
print("Top 8 piores municípios - Galináceos (soma 2003-2024):")
print(top8_piores_galinaceos)


# In[51]:


participacao_municipios_galinaceos = pivot_municipios_galinaceos.div(pivot_municipios_galinaceos.sum(axis=1), axis=0) * 100
ordem_municipios_galinaceos = total_municipios_galinaceos.index
cmap_municipios = plt.colormaps["viridis"]
n_municipios = len(ordem_municipios_galinaceos)
cor_por_municipio_galinaceos = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_galinaceos)}

anos_resumo = [2003, 2023]

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_galinaceos:
        pct = participacao_municipios_galinaceos.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_galinaceos[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% do efetivo de galináceos do Ceará")
ax.set_title("Efetivo de galináceos do Ceará preenchido pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ## Crescimento (2003 → 2023)

# ### Espécies (Ceará)

# Quanto cresceu o efetivo de cada espécie no Ceará entre 2003 e 2023? (séries independentes, não somadas)

# In[52]:


print("Crescimento do efetivo por espécie (Ceará, 2003 → 2023):")
fator_bovino = projecao_bovino_ceara.loc[2023, 'Bovino'] / projecao_bovino_ceara.loc[2003, 'Bovino']
print(f"Bovino: {fator_bovino:.2f}x")
fator_caprino = projecao_caprino_ceara.loc[2023, 'Caprino'] / projecao_caprino_ceara.loc[2003, 'Caprino']
print(f"Caprino: {fator_caprino:.2f}x")
fator_ovino = projecao_ovino_ceara.loc[2023, 'Ovino'] / projecao_ovino_ceara.loc[2003, 'Ovino']
print(f"Ovino: {fator_ovino:.2f}x")
fator_suino = projecao_suino_ceara.loc[2023, 'Suíno - total'] / projecao_suino_ceara.loc[2003, 'Suíno - total']
print(f"Suíno: {fator_suino:.2f}x")
fator_galinaceos = projecao_galinaceos_ceara.loc[2023, 'Galináceos - total'] / projecao_galinaceos_ceara.loc[2003, 'Galináceos - total']
print(f"Galináceos: {fator_galinaceos:.2f}x")


# ### Municípios

# Quais municípios mais cresceram em cada espécie, entre 2003 e 2023?

# In[53]:


crescimento_municipios_bovino = (pivot_municipios_bovino.loc[2023] / pivot_municipios_bovino.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Bovino (2003 → 2023):")
for municipio, fator in crescimento_municipios_bovino.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[54]:


crescimento_municipios_caprino = (pivot_municipios_caprino.loc[2023] / pivot_municipios_caprino.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Caprino (2003 → 2023):")
for municipio, fator in crescimento_municipios_caprino.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[55]:


crescimento_municipios_ovino = (pivot_municipios_ovino.loc[2023] / pivot_municipios_ovino.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Ovino (2003 → 2023):")
for municipio, fator in crescimento_municipios_ovino.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[56]:


crescimento_municipios_suino = (pivot_municipios_suino.loc[2023] / pivot_municipios_suino.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Suíno (2003 → 2023):")
for municipio, fator in crescimento_municipios_suino.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[57]:


crescimento_municipios_galinaceos = (pivot_municipios_galinaceos.loc[2023] / pivot_municipios_galinaceos.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Galináceos (2003 → 2023):")
for municipio, fator in crescimento_municipios_galinaceos.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# ## Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia

# In[58]:


cidades_investigar = ["Fortaleza - CE", "Maracanaú - CE", "São Gonçalo do Amarante - CE", "Caucaia - CE"]
cores_investigar = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
cor_por_cidade_investigar = dict(zip(cidades_investigar, cores_investigar))


# Como se compara a evolução do efetivo dessas 4 cidades, espécie por espécie?

# In[59]:


serie_cidades_bovino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Bovino') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_bovino[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Efetivo de bovino (Cabeças, escala log)")
ax.set_title("Efetivo de bovino — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[60]:


serie_cidades_caprino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Caprino') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_caprino[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Efetivo de caprino (Cabeças, escala log)")
ax.set_title("Efetivo de caprino — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[61]:


serie_cidades_ovino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Ovino') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_ovino[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Efetivo de ovino (Cabeças, escala log)")
ax.set_title("Efetivo de ovino — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[62]:


serie_cidades_suino = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Suíno - total') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_suino[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Efetivo de suíno (Cabeças, escala log)")
ax.set_title("Efetivo de suíno — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[63]:


serie_cidades_galinaceos = df_nome[
    (df_nome['tipo_rebanho_nome'] == 'Galináceos - total') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_galinaceos[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Efetivo de galináceos (Cabeças, escala log)")
ax.set_title("Efetivo de galináceos — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# ## Boxplot do Efetivo por Espécie (Ceará)

# Como se distribui o efetivo de cada espécie entre os municípios e anos, e existem outliers?

# In[64]:


nome_exibicao = {
    "Bovino": "Bovino", "Caprino": "Caprino", "Ovino": "Ovino",
    "Suíno - total": "Suíno", "Galináceos - total": "Galináceos",
}

efetivo_ceara_municipios = df_nome[
    (df_nome['nivel_territorial_nome'] == 'Município') & (df_nome['territorio_nome'].str.endswith('- CE'))
].copy()
efetivo_ceara_municipios['especie'] = efetivo_ceara_municipios['tipo_rebanho_nome'].map(nome_exibicao)

fig, ax = plt.subplots(figsize=(10, 6))
sb.boxplot(data=efetivo_ceara_municipios, x='especie', y='valor', ax=ax)
ax.set_yscale('log')
ax.set_xlabel('Espécie')
ax.set_ylabel('Efetivo (Cabeças, escala log)')
ax.set_title('Dispersão do efetivo por espécie, entre municípios do Ceará (2003–2024)')
ax.tick_params(axis='x', rotation=15)
plt.tight_layout()
plt.show()


# In[65]:


for especie in efetivo_ceara_municipios['tipo_rebanho_nome'].unique():
    serie = efetivo_ceara_municipios[efetivo_ceara_municipios['tipo_rebanho_nome'] == especie]
    valores = serie['valor']
    q1, q3 = valores.quantile([0.25, 0.75])
    cerca_superior = q3 + 1.5 * (q3 - q1)
    n_outliers = (valores > cerca_superior).sum()
    linha_min = serie.loc[valores.idxmin()]
    linha_max = serie.loc[valores.idxmax()]

    print(f"{nome_exibicao[especie]}:")
    print(f"  mínimo: {linha_min['valor']:,.0f} cabeças ({linha_min['territorio_nome']}, {linha_min['ano_nome']})")
    print(f"  mediana: {valores.median():,.0f} cabeças")
    print(f"  máximo: {linha_max['valor']:,.0f} cabeças ({linha_max['territorio_nome']}, {linha_max['ano_nome']})")
    print(f"  cerca superior do boxplot: {cerca_superior:,.0f} cabeças")
    print(f"  outliers acima da cerca: {n_outliers} de {len(valores)} ({n_outliers / len(valores):.1%})")
    print()


# ## Correlação entre Espécies (Ceará)

# As espécies se correlacionam entre si na variação % ano a ano? (correlação sobre o crescimento, não soma — e sem o viés de tendência comum que a correlação em nível bruto teria, já que todas cresceram ao longo do período)

# In[66]:


efetivo_ceara_especies = df_nome[df_nome['territorio_nome'] == 'Ceará'].pivot_table(
    index='ano_nome', columns='tipo_rebanho_nome', values='valor'
).rename(columns=nome_exibicao)

correlacao_especies = efetivo_ceara_especies.pct_change().dropna().corr()

fig, ax = plt.subplots(figsize=(7, 6))
sb.heatmap(correlacao_especies, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
ax.set_title('Correlação entre espécies (Ceará, variação % ano a ano)')
plt.tight_layout()
plt.show()


# **Leitura da correlação:** usando variação % ano a ano (não o nível bruto, que ficava inflado pela tendência comum de crescimento das 5 espécies), o quadro é bem diferente:
# 
# - **Caprino, Ovino e Suíno (0.69–0.72):** correlacionam moderadamente entre si — quando um cresce mais num ano, os outros tendem a acompanhar. Coerente com serem criações de pequeno porte, muitas vezes no mesmo estabelecimento rural do semiárido.
# - **Galináceos × Caprino/Ovino/Suíno (-0.33 a -0.41):** correlação **negativa** — quando os pequenos ruminantes crescem mais num ano, a avicultura tende a crescer menos (ou cair). Faz sentido: avicultura no Ceará é puxada por poucos polos industriais (ex: Beberibe) com ciclo de produção próprio, desligado do calendário de seca/pasto que afeta caprino/ovino/suíno.
# - **Bovino:** correlação fraca a moderada com as demais (0.04–0.49) — dinâmica bem própria, não acompanha nem os ruminantes menores nem a avicultura de forma consistente.
# 
# Moral: a correlação em nível bruto (0.66–0.97 para tudo) escondia esse contraste — parecia que todas as espécies "andavam juntas", mas na verdade só caprino/ovino/suíno têm relação real ano a ano, e galináceos se move na direção oposta.
