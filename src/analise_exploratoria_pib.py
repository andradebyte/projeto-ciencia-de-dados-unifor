#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib as plt


# In[2]:


df_pib = pd.read_csv("../dados/processed/pib_tratado.csv")

print(f"Total de linhas: {df_pib.shape[0]}")
print(f"Total de colunas: {df_pib.shape[1]}")
print(f"Valores preenchidos (não nulos) em 'valor': {df_pib['valor'].notna().sum()}")
print(f"Valores nulos em 'valor': {df_pib['valor'].isna().sum()}")

df_pib.head()


# In[3]:


cols_codigo = [c for c in df_pib.columns if c.endswith("_codigo")]
df_pib_sem_codigo = df_pib.drop(columns=cols_codigo)

df_pib_sem_codigo.head()


# In[4]:


print(f"Territórios únicos: {df_pib_sem_codigo['territorio_nome'].nunique()}")

df_pib_sem_codigo['territorio_nome'].value_counts()


# In[5]:


df_pib_sem_codigo.groupby('variavel_nome')['valor'].describe()


# In[6]:


print("Valores nulos:", df_pib_sem_codigo['valor'].isna().sum())
print("Valores inibidos (sigilo do IBGE):", df_pib_sem_codigo['valor_is_inibido'].sum())
print("Linhas duplicadas:", df_pib_sem_codigo.duplicated().sum())
print()
print("Nulos por variável:")
print(df_pib_sem_codigo[df_pib_sem_codigo['valor'].isna()].groupby('variavel_nome').size())
print("Anos com nulos:", sorted(df_pib_sem_codigo[df_pib_sem_codigo['valor'].isna()]['ano_nome'].unique()))


# In[7]:


print(f"Menor ano: {df_pib_sem_codigo['ano_nome'].min()}")
print(f"Maior ano: {df_pib_sem_codigo['ano_nome'].max()}")


# In[8]:


anos_disponiveis = sorted(int(a) for a in df_pib_sem_codigo['ano_nome'].unique())
print(f"Total de anos: {len(anos_disponiveis)}")
print(anos_disponiveis)


# ## PIB — Brasil x Ceará

# Como o PIB do Brasil e do Ceará evoluíram entre 2003 e 2023?

# In[9]:


import matplotlib.pyplot as plt

pib_bc = df_pib_sem_codigo[
    (df_pib_sem_codigo["territorio_nome"].isin(["Brasil", "Ceará"]))
    & (df_pib_sem_codigo["variavel_nome"] == "Produto Interno Bruto a preços correntes")
].copy()
pib_bc["ano_nome"] = pib_bc["ano_nome"].astype(int)
pib_bc = pib_bc.sort_values("ano_nome")

cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}


def formata_reais(valor_mil_reais):
    reais = valor_mil_reais * 1_000
    if reais >= 1e12:
        return f"R$ {reais / 1e12:.2f} tri"
    return f"R$ {reais / 1e9:.1f} bi"


fig, ax = plt.subplots(figsize=(10, 5))
for territorio, cor in cores.items():
    serie = pib_bc[pib_bc["territorio_nome"] == territorio]
    ax.plot(serie["ano_nome"], serie["valor"], color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

    primeiro = serie.iloc[0]
    ultimo = serie.iloc[-1]
    ax.annotate(
        formata_reais(primeiro["valor"]),
        (primeiro["ano_nome"], primeiro["valor"]),
        textcoords="offset points", xytext=(0, 10), ha="left", fontsize=9, color=cor,
    )
    ax.annotate(
        formata_reais(ultimo["valor"]),
        (ultimo["ano_nome"], ultimo["valor"]),
        textcoords="offset points", xytext=(0, 10), ha="right", fontsize=9, color=cor,
    )

ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais)")
ax.set_title("PIB — Brasil x Ceará (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)

plt.show()


# In[10]:


pib_pivot = pib_bc.pivot(index="ano_nome", columns="territorio_nome", values="valor")


# In[11]:


razao_valor = pib_pivot["Brasil"] / pib_pivot["Ceará"]

for ano, razao in razao_valor.items():
    print(f"{ano}: PIB do Brasil é {razao:.2f}x o PIB do Ceará")


# In[12]:


crescimento = {}
for territorio in ["Brasil", "Ceará"]:
    serie = pib_bc[pib_bc["territorio_nome"] == territorio]
    valor_2003 = serie[serie["ano_nome"] == 2003]["valor"].iloc[0]
    valor_2023 = serie[serie["ano_nome"] == 2023]["valor"].iloc[0]
    crescimento[territorio] = valor_2023 / valor_2003

print(f"Brasil cresceu {crescimento['Brasil']:.2f}x (2003 -> 2023)")
print(f"Ceará cresceu {crescimento['Ceará']:.2f}x (2003 -> 2023)")
print(f"Brasil cresceu {crescimento['Brasil'] / crescimento['Ceará']:.2f}x mais que o Ceará")


# In[13]:


valores = {}
for territorio in ["Brasil", "Ceará"]:
    serie = pib_bc[pib_bc["territorio_nome"] == territorio]
    valores[territorio] = {
        2003: serie[serie["ano_nome"] == 2003]["valor"].iloc[0],
        2023: serie[serie["ano_nome"] == 2023]["valor"].iloc[0],
    }

dif_2003 = valores["Brasil"][2003] - valores["Ceará"][2003]
dif_2023 = valores["Brasil"][2023] - valores["Ceará"][2023]
vezes_2003 = valores["Brasil"][2003] / valores["Ceará"][2003]
vezes_2023 = valores["Brasil"][2023] / valores["Ceará"][2023]

print(f"2003 — Brasil: {formata_reais(valores['Brasil'][2003])} | Ceará: {formata_reais(valores['Ceará'][2003])}")
print(f"Diferença 2003: {formata_reais(dif_2003)} ({vezes_2003:.2f}x)")
print()
print(f"2023 — Brasil: {formata_reais(valores['Brasil'][2023])} | Ceará: {formata_reais(valores['Ceará'][2023])}")
print(f"Diferença 2023: {formata_reais(dif_2023)} ({vezes_2023:.2f}x)")


# Quantas vezes o PIB de cada um cresceu, ano a ano, em relação a 2003?

# In[14]:


import numpy as np

cresc_por_ano = pib_pivot[["Brasil", "Ceará"]].div(pib_pivot.loc[2003, ["Brasil", "Ceará"]])
anos = cresc_por_ano.index.to_numpy()
x = np.arange(len(anos))
largura = 0.35

fig, ax = plt.subplots(figsize=(14, 6))
barras_brasil = ax.bar(x - largura / 2, cresc_por_ano["Brasil"], width=largura, color=cores["Brasil"], label="Brasil")
barras_ceara = ax.bar(x + largura / 2, cresc_por_ano["Ceará"], width=largura, color=cores["Ceará"], label="Ceará")

for barras in (barras_brasil, barras_ceara):
    ax.bar_label(barras, fmt="%.2fx", fontsize=7, rotation=90, padding=3)

ax.set_xticks(x)
ax.set_xticklabels(anos, rotation=45, ha="right")
ax.set_ylabel("Fator de crescimento em relação a 2003 (x vezes)")
ax.set_title("PIB — crescimento por ano em relação a 2003 (Brasil x Ceará)")
ax.set_ylim(0, cresc_por_ano.to_numpy().max() * 1.2)
ax.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)

plt.show()


# In[15]:


razao_crescimento = cresc_por_ano["Brasil"] / cresc_por_ano["Ceará"]

for ano in cresc_por_ano.index:
    cresc_brasil = cresc_por_ano.loc[ano, "Brasil"]
    cresc_ceara = cresc_por_ano.loc[ano, "Ceará"]
    razao = razao_crescimento.loc[ano]
    print(f"{ano}: Brasil cresceu {cresc_brasil:.2f}x, Ceará cresceu {cresc_ceara:.2f}x, então o Brasil cresceu {razao:.2f}x em relação ao Ceará")


# Quantas vezes o PIB do Brasil é maior que o do Ceará, em cada ano?

# In[16]:


fig, ax = plt.subplots(figsize=(12, 5))
barras = ax.bar(razao_valor.index, razao_valor.values, color="#2a78d6", width=0.6)
ax.bar_label(barras, fmt="%.1fx", fontsize=8, rotation=90, padding=3)

ax.set_xlabel("Ano")
ax.set_ylabel("PIB Brasil / PIB Ceará (x vezes)")
ax.set_title("Quantas vezes o PIB do Brasil é maior que o do Ceará (2003–2023)")
ax.set_xticks(razao_valor.index)
ax.set_xticklabels(razao_valor.index, rotation=45, ha="right")
ax.set_ylim(0, razao_valor.max() * 1.2)
ax.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# In[17]:


ano_maior = razao_valor.idxmax()
ano_menor = razao_valor.idxmin()

print(f"Maior razão: {ano_maior} — Brasil {razao_valor.loc[ano_maior]:.2f}x o Ceará")
print(f"Menor razão: {ano_menor} — Brasil {razao_valor.loc[ano_menor]:.2f}x o Ceará")


# In[18]:


participacao_ceara = (pib_pivot["Ceará"] / pib_pivot["Brasil"]) * 100

for ano, pct in participacao_ceara.items():
    print(f"{ano}: Ceará representa {pct:.2f}% do PIB do Brasil")


# Qual a participação do Ceará no PIB do Brasil, ano a ano?

# In[19]:


anos_pct = participacao_ceara.index
resto_brasil = 100 - participacao_ceara

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(anos_pct, participacao_ceara, color=cores["Ceará"], label="Ceará")
ax.barh(anos_pct, resto_brasil, left=participacao_ceara, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in participacao_ceara.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(anos_pct)
ax.invert_yaxis()
ax.set_xlabel("% do PIB do Brasil")
ax.set_title("Participação do Ceará no PIB do Brasil (2003–2023)")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()


# Como essa participação do Ceará mudou entre 2003 e 2023?

# In[20]:


anos_resumo = [2003, 2023]
participacao_resumo = participacao_ceara.loc[anos_resumo]
resto_resumo = 100 - participacao_resumo
y_pos = [0, 1]

fig, ax = plt.subplots(figsize=(6, 2))
ax.barh(y_pos, participacao_resumo, height=0.9, color=cores["Ceará"])
ax.barh(y_pos, resto_resumo, left=participacao_resumo, height=0.9, color=cores["Brasil"])

for y, pct in zip(y_pos, participacao_resumo):
    ax.annotate(
        f"{pct:.2f}%",
        (100, y),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.annotate(
    "Ceará", (0, -0.7), xytext=(0, -0.7), ha="left", va="center", fontsize=9, color=cores["Ceará"], fontweight="bold",
)
ax.annotate(
    "Resto do Brasil", (55, -0.7), xytext=(55, -0.7), ha="left", va="center", fontsize=9, color=cores["Brasil"], fontweight="bold",
)

ax.set_yticks(y_pos)
ax.set_yticklabels(anos_resumo)
ax.invert_yaxis()
ax.set_ylim(1.6, -1.1)
ax.set_xlabel("% do PIB do Brasil")
ax.set_title("Participação do Ceará no PIB do Brasil — 2003 x 2023")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# ## PIB — Municípios do Ceará

# In[21]:


df_municipios = df_pib_sem_codigo[df_pib_sem_codigo["nivel_territorial_nome"] == "Município"].copy()

print(f"Total de linhas: {df_municipios.shape[0]}")
print(f"Municípios únicos: {df_municipios['territorio_nome'].nunique()}")

df_municipios.head()


# In[22]:


qtd_2003 = (df_municipios["ano_nome"] == 2003).sum()
qtd_2023 = (df_municipios["ano_nome"] == 2023).sum()

print(f"Registros em 2003: {qtd_2003}")
print(f"Registros em 2023: {qtd_2023}")
print(f"Maior valor: {df_municipios['valor'].max()}")
print(f"Menor valor: {df_municipios['valor'].min()}")


# In[23]:


df_municipios["unidade"].value_counts()


# In[24]:


df_municipios_pct = df_municipios[df_municipios["unidade"] == "%"].copy()

print(f"Total de linhas: {df_municipios_pct.shape[0]}")
df_municipios_pct.head(10)


# In[25]:


territorios_pct = set(df_municipios[df_municipios["unidade"] == "%"]["territorio_nome"])
territorios_reais = set(df_municipios[df_municipios["unidade"] == "Mil Reais"]["territorio_nome"])
territorios_ambos = territorios_pct & territorios_reais

print(f"Territórios com %: {len(territorios_pct)}")
print(f"Territórios com Mil Reais: {len(territorios_reais)}")
print(f"Territórios com os dois: {len(territorios_ambos)}")


# In[26]:


df_municipios_reais = df_municipios[df_municipios["unidade"] == "Mil Reais"].copy()

print(f"Total de linhas: {df_municipios_reais.shape[0]}")
df_municipios_reais.head()


# In[27]:


territorios_municipios = sorted(df_municipios_reais["territorio_nome"].unique())
print(f"Total de territórios: {len(territorios_municipios)}")
print(territorios_municipios)


# In[28]:


pib_municipios = df_municipios_reais[
    df_municipios_reais["variavel_nome"] == "Produto Interno Bruto a preços correntes"
].copy()
pib_municipios_pivot = pib_municipios.pivot(index="ano_nome", columns="territorio_nome", values="valor")


# Como foi o PIB de cada um dos 184 municípios do Ceará?

# In[29]:


municipios_ordenados = pib_municipios_pivot.columns.tolist()
n_municipios = len(municipios_ordenados)
ncols = 8
nrows = -(-n_municipios // ncols)

valor_max = pib_municipios_pivot.max().max()
municipio_max = pib_municipios_pivot.max().idxmax()
ano_max = pib_municipios_pivot[municipio_max].idxmax()

valor_min = pib_municipios_pivot.min().min()
municipio_min = pib_municipios_pivot.min().idxmin()
ano_min = pib_municipios_pivot[municipio_min].idxmin()

fig, axes = plt.subplots(nrows, ncols, figsize=(24, nrows * 1.8), sharex=True)

for ax, municipio in zip(axes.flat, municipios_ordenados):
    serie = pib_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color="#2a78d6", linewidth=1)
    ax.set_title(municipio, fontsize=7)
    ax.tick_params(labelsize=5)
    ax.spines[["top", "right"]].set_visible(False)

for ax in axes.flat[n_municipios:]:
    ax.axis("off")

fig.suptitle(
    f"PIB dos {n_municipios} municípios do Ceará (2003–2023)\n"
    f"Maior: {municipio_max} — {formata_reais(valor_max)} em {ano_max} | "
    f"Menor: {municipio_min} — {formata_reais(valor_min)} em {ano_min}",
    fontsize=12,
)
fig.tight_layout(rect=[0, 0, 1, 0.97])

plt.show()


# Quais os 10 municípios com maior PIB e como eles evoluíram?

# In[30]:


top10_municipios = pib_municipios_pivot.loc[2023].sort_values(ascending=False).head(10).index.tolist()
cores_top10 = plt.colormaps["tab10"].colors

fig, ax = plt.subplots(figsize=(10, 6))
for cor, municipio in zip(cores_top10, top10_municipios):
    serie = pib_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais)")
ax.set_title("Top 10 municípios do Ceará por PIB (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=   0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# ### Lista de municípios

# In[31]:


for posicao, municipio in enumerate(territorios_municipios, start=1):
    print(f"{posicao:3d}. {municipio}")


# In[32]:


ranking_pib_2023 = pib_municipios_pivot.loc[2023].sort_values(ascending=False)

print("Ranking de PIB dos municípios — 2023")
for posicao, (municipio, valor) in enumerate(ranking_pib_2023.items(), start=1):
    print(f"{posicao:3d}. {municipio}: {formata_reais(valor)}")


# In[33]:


ranking_pib_2003 = pib_municipios_pivot.loc[2003].sort_values(ascending=False)

print("Ranking de PIB dos municípios — 2003")
for posicao, (municipio, valor) in enumerate(ranking_pib_2003.items(), start=1):
    print(f"{posicao:3d}. {municipio}: {formata_reais(valor)}")


# In[34]:


ranking_por_ano = pib_municipios_pivot.rank(axis=1, ascending=False, method="min").astype(int)
posicoes_baturite = ranking_por_ano["Baturité - CE"]

for ano, posicao in posicoes_baturite.items():
    valor = pib_municipios_pivot.loc[ano, "Baturité - CE"]
    print(f"{ano}: posição {posicao} de {pib_municipios_pivot.shape[1]} — {formata_reais(valor)}")


# In[35]:


crescimento_municipios = (pib_municipios_pivot.loc[2023] / pib_municipios_pivot.loc[2003]).sort_values(ascending=False)

top10_mais_cresceram = crescimento_municipios.head(10)

print("Municípios que mais cresceram (2003 -> 2023)")
for posicao, (municipio, fator) in enumerate(top10_mais_cresceram.items(), start=1):
    print(f"{posicao:2d}. {municipio}: {fator:.2f}x")


# Quais municípios mais cresceram em PIB entre 2003 e 2023?

# In[36]:


cores_top10 = plt.colormaps["tab10"].colors

fig, ax = plt.subplots(figsize=(10, 6))
for cor, municipio in zip(cores_top10, top10_mais_cresceram.index):
    serie = pib_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais, escala log)")
ax.set_title("Municípios que mais cresceram — PIB por ano (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[37]:


top10_menos_cresceram = crescimento_municipios.tail(10).sort_values()

print("Municípios que menos cresceram (2003 -> 2023)")
for posicao, (municipio, fator) in enumerate(top10_menos_cresceram.items(), start=1):
    print(f"{posicao:2d}. {municipio}: {fator:.2f}x")


# Quais municípios menos cresceram em PIB entre 2003 e 2023?

# In[38]:


fig, ax = plt.subplots(figsize=(10, 6))
for cor, municipio in zip(cores_top10, top10_menos_cresceram.index):
    serie = pib_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais, escala log)")
ax.set_title("Municípios que menos cresceram — PIB por ano (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# Qual foi o de Baturité nesse período?

# In[39]:


serie_baturite = pib_municipios_pivot["Baturité - CE"]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(serie_baturite.index, serie_baturite.values, color="#e34948", linewidth=2, marker="o", markersize=4, label="Baturité - CE")

primeiro_ano, ultimo_ano = serie_baturite.index.min(), serie_baturite.index.max()
ax.annotate(
    formata_reais(serie_baturite.loc[primeiro_ano]),
    (primeiro_ano, serie_baturite.loc[primeiro_ano]),
    textcoords="offset points", xytext=(0, 10), ha="left", fontsize=9, color="#e34948",
)
ax.annotate(
    formata_reais(serie_baturite.loc[ultimo_ano]),
    (ultimo_ano, serie_baturite.loc[ultimo_ano]),
    textcoords="offset points", xytext=(0, 10), ha="right", fontsize=9, color="#e34948",
)

ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais)")
ax.set_title("PIB — Baturité (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)

plt.show()


# ### Outliers no PIB dos municípios

# Existem outliers no PIB dos municípios? Como é a distribuição por ano?

# In[40]:


dados_boxplot = [pib_municipios_pivot.loc[ano].dropna().values for ano in pib_municipios_pivot.index]

fig, ax = plt.subplots(figsize=(14, 6))
bp = ax.boxplot(
    dados_boxplot,
    positions=pib_municipios_pivot.index,
    widths=0.6,
    patch_artist=True,
    flierprops={"markerfacecolor": "#eb6834", "markeredgecolor": "#eb6834", "markersize": 3, "alpha": 0.6},
    boxprops={"facecolor": "#2a78d6", "alpha": 0.3, "edgecolor": "#2a78d6"},
    medianprops={"color": "#2a78d6"},
    whiskerprops={"color": "#2a78d6"},
    capprops={"color": "#2a78d6"},
)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais, escala log)")
ax.set_title("Distribuição do PIB dos municípios por ano (boxplot) — pontos laranja = outliers")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# In[41]:


for ano in pib_municipios_pivot.index:
    valores_ano = pib_municipios_pivot.loc[ano].dropna()
    q1_ano = valores_ano.quantile(0.25)
    q3_ano = valores_ano.quantile(0.75)
    limite_ano = q3_ano + 1.5 * (q3_ano - q1_ano)
    outliers_ano = valores_ano[valores_ano > limite_ano].sort_values(ascending=False)

    nomes = ", ".join(f"{municipio} ({formata_reais(valor)})" for municipio, valor in outliers_ano.items())
    print(f"{ano}: {nomes}")


# In[42]:


print("Média do PIB por ano — com e sem outliers")
for ano in pib_municipios_pivot.index:
    valores_ano = pib_municipios_pivot.loc[ano].dropna()
    q1_ano = valores_ano.quantile(0.25)
    q3_ano = valores_ano.quantile(0.75)
    limite_ano = q3_ano + 1.5 * (q3_ano - q1_ano)

    sem_outliers = valores_ano[valores_ano <= limite_ano]

    media_com = valores_ano.mean()
    media_sem = sem_outliers.mean()

    print(f"{ano}: com outliers = {formata_reais(media_com)} | sem outliers = {formata_reais(media_sem)}")


# Como fica a distribuição do PIB de todos os municípios, ano a ano, em pontos?

# In[43]:


fig, ax = plt.subplots(figsize=(14, 6))
for ano in pib_municipios_pivot.index:
    valores_ano = pib_municipios_pivot.loc[ano].dropna()
    ax.scatter([ano] * len(valores_ano), valores_ano.values, color="#2a78d6", alpha=0.3, s=15)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais, escala log)")
ax.set_title("PIB de todos os municípios por ano (scatter)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# In[44]:


valores_2023 = pib_municipios_pivot.loc[2023].dropna()

q1 = valores_2023.quantile(0.25)
q3 = valores_2023.quantile(0.75)
iqr = q3 - q1
limite_superior = q3 + 1.5 * iqr

outliers_2023 = valores_2023[valores_2023 > limite_superior].sort_values(ascending=False)

print(f"Limite superior (Q3 + 1.5*IQR): {formata_reais(limite_superior)}")
print(f"Outliers em 2023: {len(outliers_2023)}\n")
for municipio, valor in outliers_2023.items():
    print(f"{municipio}: {formata_reais(valor)}")


# In[45]:


df_municipios_reais.describe()


# Como foi o PIB de Fortaleza, Maracanaú, Eusébio, Pacajus, Cascavel, Baturité, Guaramiranga, Quixadá e Aiuaba?

# In[46]:


cidades_escolhidas = [
    "Fortaleza - CE",
    "Maracanaú - CE",
    "Eusébio - CE",
    "Pacajus - CE",
    "Cascavel - CE",
    "Baturité - CE",
    "Guaramiranga - CE",
    "Quixadá - CE",
    "Aiuaba - CE",
]
cidades_disponiveis = [c for c in cidades_escolhidas if c in pib_municipios_pivot.columns]

cores_escolhidas = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948", "#898781"]
cor_por_cidade = dict(zip(cidades_disponiveis, cores_escolhidas))

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_disponiveis:
    serie = pib_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais, escala log)")
ax.set_title("PIB — cidades escolhidas (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[47]:


crescimento_escolhidas = (pib_municipios_pivot.loc[2023, cidades_disponiveis] / pib_municipios_pivot.loc[2003, cidades_disponiveis]).sort_values(ascending=False)

print("Crescimento do PIB (2003 -> 2023) — cidades escolhidas")
for municipio, fator in crescimento_escolhidas.items():
    print(f"{municipio}: {fator:.2f}x")


# Quanto cada município representa do PIB do Ceará em 2023?

# In[48]:


participacao_municipios_2023 = (pib_municipios_pivot.loc[2023] / pib_pivot.loc[2023, "Ceará"]) * 100
participacao_municipios_2023 = participacao_municipios_2023.sort_values(ascending=False)

top15_participacao = participacao_municipios_2023.head(15)
outros_participacao = participacao_municipios_2023.iloc[15:].sum()

categorias = list(top15_participacao.index) + ["Outros municípios"]
valores_participacao = list(top15_participacao.values) + [outros_participacao]
cores_participacao = ["#2a78d6"] * 15 + ["#898781"]

fig, ax = plt.subplots(figsize=(12, 6))
barras = ax.bar(categorias, valores_participacao, color=cores_participacao)
ax.bar_label(barras, fmt="%.2f%%", fontsize=8, padding=3)

ax.set_xlabel("Município")
ax.set_ylabel("% do PIB do Ceará")
ax.set_title("Participação de cada município no PIB do Ceará (2023)")
ax.tick_params(axis="x", rotation=60)
ax.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# Quanto cada município representava do PIB do Ceará em 2003?

# In[49]:


participacao_municipios_2003 = (pib_municipios_pivot.loc[2003] / pib_pivot.loc[2003, "Ceará"]) * 100
participacao_municipios_2003 = participacao_municipios_2003.sort_values(ascending=False)

top15_participacao_2003 = participacao_municipios_2003.head(15)
outros_participacao_2003 = participacao_municipios_2003.iloc[15:].sum()

categorias_2003 = list(top15_participacao_2003.index) + ["Outros municípios"]
valores_participacao_2003 = list(top15_participacao_2003.values) + [outros_participacao_2003]
cores_participacao_2003 = ["#2a78d6"] * 15 + ["#898781"]

fig, ax = plt.subplots(figsize=(12, 6))
barras = ax.bar(categorias_2003, valores_participacao_2003, color=cores_participacao_2003)
ax.bar_label(barras, fmt="%.2f%%", fontsize=8, padding=3)

ax.set_xlabel("Município")
ax.set_ylabel("% do PIB do Ceará")
ax.set_title("Participação de cada município no PIB do Ceará (2003)")
ax.tick_params(axis="x", rotation=60)
ax.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# In[50]:


print("Participação de cada município no PIB do Ceará — 2023")
for municipio, pct in participacao_municipios_2023.items():
    print(f"{municipio}: {pct:.2f}%")


# Como o PIB do Ceará se reparte entre os 184 municípios, visualmente?

# In[51]:


cmap_municipios = plt.colormaps["viridis"]
n = len(participacao_municipios_2023)

fig, ax = plt.subplots(figsize=(14, 3))
esquerda = 0
for posicao, (municipio, pct) in enumerate(participacao_municipios_2023.items()):
    cor = cmap_municipios(posicao / n)
    ax.barh("Ceará", pct, left=esquerda, color=cor, edgecolor="#fcfcfb", linewidth=0.3)
    if pct > 1.5:
        ax.text(esquerda + pct / 2, 0, f"{municipio.replace(' - CE', '')} ({pct:.1f}%)", ha="center", va="center", fontsize=7, color="white", rotation=90)
    esquerda += pct

ax.set_xlabel("% do PIB do Ceará")
ax.set_title("PIB do Ceará preenchido pelos 184 municípios (2023)")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# Como se compara o PIB de Fortaleza, Maracanaú, Caucaia e São Gonçalo do Amarante?

# In[52]:


cidades_investigar = ["Fortaleza - CE", "Maracanaú - CE", "Caucaia - CE", "São Gonçalo do Amarante - CE"]
cores_investigar = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
cor_por_cidade_investigar = dict(zip(cidades_investigar, cores_investigar))

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = pib_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("PIB a preços correntes (Mil Reais, escala log)")
ax.set_title("PIB — Fortaleza, Maracanaú, Caucaia e São Gonçalo do Amarante (2003–2023)")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[53]:


crescimento_todos = pd.concat([
    pd.Series(crescimento),
    crescimento_municipios,
]).sort_values(ascending=False)

territorio_maior_crescimento = crescimento_todos.index[0]
fator_maior_crescimento = crescimento_todos.iloc[0]

print(f"Maior crescimento de PIB (2003 -> 2023) entre Brasil, Ceará e os {len(crescimento_municipios)} municípios:")
print(f"{territorio_maior_crescimento}: {fator_maior_crescimento:.2f}x")


# In[54]:


print("CAGR — taxa de crescimento anual composta (2003 -> 2023)")
n_anos = 2023 - 2003
for municipio in cidades_investigar:
    valor_2003 = pib_municipios_pivot.loc[2003, municipio]
    valor_2023 = pib_municipios_pivot.loc[2023, municipio]
    cagr = (valor_2023 / valor_2003) ** (1 / n_anos) - 1
    print(f"{municipio}: {cagr * 100:.2f}% ao ano")


# In[55]:


print("Ano do maior salto (maior crescimento % de um ano pro outro)")
for municipio in cidades_investigar:
    serie = pib_municipios_pivot[municipio]
    variacao_anual = serie.pct_change().dropna() * 100
    ano_maior_salto = variacao_anual.idxmax()
    salto = variacao_anual.loc[ano_maior_salto]
    valor_antes = serie.loc[ano_maior_salto - 1]
    valor_depois = serie.loc[ano_maior_salto]
    print(f"{municipio}: {ano_maior_salto} ({salto:.1f}% em relação ao ano anterior) — de {formata_reais(valor_antes)} ({ano_maior_salto - 1}) para {formata_reais(valor_depois)} ({ano_maior_salto})")


# Qual a variação percentual anual do PIB dessas 4 cidades?

# In[56]:


fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = pib_municipios_pivot[municipio]
    variacao_anual = serie.pct_change().dropna() * 100
    ax.plot(variacao_anual.index, variacao_anual.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.axhline(0, color="#898781", linewidth=1)
ax.set_xlabel("Ano")
ax.set_ylabel("Variação do PIB em relação ao ano anterior (%)")
ax.set_title("Variação anual do PIB — cidades escolhidas")
ax.set_xticks(range(2004, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[57]:


correlacao = pib_municipios_pivot[cidades_investigar].pct_change().dropna().corr()
print("Correlação entre a variação anual do PIB das cidades escolhidas")
correlacao


# Como mudou a posição no ranking de PIB dessas 4 cidades ao longo do tempo?

# In[58]:


fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    posicoes = ranking_por_ano[municipio]
    ax.plot(posicoes.index, posicoes.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.invert_yaxis()
ax.set_xlabel("Ano")
ax.set_ylabel(f"Posição no ranking de PIB (de {pib_municipios_pivot.shape[1]})")
ax.set_title("Posição no ranking de PIB ao longo do tempo — cidades escolhidas")
ax.set_xticks(range(2003, 2024, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper right")

plt.show()


# ## VAB Total — Brasil x Ceará

# Como evoluiu o VAB total do Brasil e do Ceará?

# In[59]:


vab_bc = df_pib_sem_codigo[
    (df_pib_sem_codigo["territorio_nome"].isin(["Brasil", "Ceará"]))
    & (df_pib_sem_codigo["variavel_nome"] == "Valor adicionado bruto a preços correntes total")
].copy()
vab_bc["ano_nome"] = vab_bc["ano_nome"].astype(int)
vab_pivot = vab_bc.pivot(index="ano_nome", columns="territorio_nome", values="valor").dropna()

fig, ax = plt.subplots(figsize=(10, 5))
for territorio, cor in cores.items():
    serie = vab_pivot[territorio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax.annotate(formata_reais(serie.iloc[0]), (serie.index[0], serie.iloc[0]), textcoords="offset points", xytext=(0, 10), ha="left", fontsize=9, color=cor)
    ax.annotate(formata_reais(serie.iloc[-1]), (serie.index[-1], serie.iloc[-1]), textcoords="offset points", xytext=(0, 10), ha="right", fontsize=9, color=cor)

ax.set_xlabel("Ano")
ax.set_ylabel("VAB total a preços correntes (Mil Reais)")
ax.set_title(f"VAB Total — Brasil x Ceará ({vab_pivot.index.min()}–{vab_pivot.index.max()})")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)

plt.show()


# In[60]:


ano_final_vab = vab_pivot.index.max()
crescimento_vab = vab_pivot.loc[ano_final_vab] / vab_pivot.loc[2003]

print(f"Crescimento do VAB total (2003 -> {ano_final_vab})")
for territorio, fator in crescimento_vab.items():
    print(f"{territorio}: {fator:.2f}x")
print(f"Brasil cresceu {crescimento_vab['Brasil'] / crescimento_vab['Ceará']:.2f}x em relação ao Ceará")


# ## VAB Total — Municípios

# Quais os 10 municípios com maior VAB total?

# In[61]:


vab_municipios = df_municipios_reais[
    df_municipios_reais["variavel_nome"] == "Valor adicionado bruto a preços correntes total"
].copy()
vab_municipios_pivot = vab_municipios.pivot(index="ano_nome", columns="territorio_nome", values="valor").dropna(how="all")

ano_vab_mun = vab_municipios_pivot.index.max()
top10_vab_municipios = vab_municipios_pivot.loc[ano_vab_mun].sort_values(ascending=False).head(10).index.tolist()

fig, ax = plt.subplots(figsize=(10, 6))
for cor, municipio in zip(cores_top10, top10_vab_municipios):
    serie = vab_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_xlabel("Ano")
ax.set_ylabel("VAB total a preços correntes (Mil Reais)")
ax.set_title(f"Top 10 municípios do Ceará por VAB total ({ano_vab_mun})")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# Quanto cada município representa do VAB total do Ceará?

# In[62]:


participacao_vab_municipios = (vab_municipios_pivot.loc[ano_vab_mun] / vab_pivot.loc[ano_vab_mun, "Ceará"]) * 100
participacao_vab_municipios = participacao_vab_municipios.sort_values(ascending=False)

top15_vab = participacao_vab_municipios.head(15)
outros_vab = participacao_vab_municipios.iloc[15:].sum()

categorias_vab = list(top15_vab.index) + ["Outros municípios"]
valores_vab = list(top15_vab.values) + [outros_vab]
cores_vab = ["#2a78d6"] * 15 + ["#898781"]

fig, ax = plt.subplots(figsize=(12, 6))
barras = ax.bar(categorias_vab, valores_vab, color=cores_vab)
ax.bar_label(barras, fmt="%.2f%%", fontsize=8, padding=3)

ax.set_xlabel("Município")
ax.set_ylabel("% do VAB total do Ceará")
ax.set_title(f"Participação de cada município no VAB total do Ceará ({ano_vab_mun})")
ax.tick_params(axis="x", rotation=60)
ax.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# ## VAB Agropecuário — Brasil x Ceará

# Como evoluiu o VAB agropecuário do Brasil e do Ceará?

# In[63]:


vab_agro_bc = df_pib_sem_codigo[
    (df_pib_sem_codigo["territorio_nome"].isin(["Brasil", "Ceará"]))
    & (df_pib_sem_codigo["variavel_nome"] == "Valor adicionado bruto a preços correntes da agropecuária")
].copy()
vab_agro_bc["ano_nome"] = vab_agro_bc["ano_nome"].astype(int)
vab_agro_pivot = vab_agro_bc.pivot(index="ano_nome", columns="territorio_nome", values="valor").dropna()

fig, ax = plt.subplots(figsize=(10, 5))
for territorio, cor in cores.items():
    serie = vab_agro_pivot[territorio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)
    ax.annotate(formata_reais(serie.iloc[0]), (serie.index[0], serie.iloc[0]), textcoords="offset points", xytext=(0, 10), ha="left", fontsize=9, color=cor)
    ax.annotate(formata_reais(serie.iloc[-1]), (serie.index[-1], serie.iloc[-1]), textcoords="offset points", xytext=(0, 10), ha="right", fontsize=9, color=cor)

ax.set_xlabel("Ano")
ax.set_ylabel("VAB agropecuário a preços correntes (Mil Reais)")
ax.set_title(f"VAB Agropecuário — Brasil x Ceará ({vab_agro_pivot.index.min()}–{vab_agro_pivot.index.max()})")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)

plt.show()


# In[64]:


ano_final_vab_agro = vab_agro_pivot.index.max()
crescimento_vab_agro = vab_agro_pivot.loc[ano_final_vab_agro] / vab_agro_pivot.loc[2003]

print(f"Crescimento do VAB agropecuário (2003 -> {ano_final_vab_agro})")
for territorio, fator in crescimento_vab_agro.items():
    print(f"{territorio}: {fator:.2f}x")
print(f"Brasil cresceu {crescimento_vab_agro['Brasil'] / crescimento_vab_agro['Ceará']:.2f}x em relação ao Ceará")


# ## VAB Agropecuário — Municípios

# Quais os 10 municípios com maior VAB agropecuário?

# In[65]:


vab_agro_municipios = df_municipios_reais[
    df_municipios_reais["variavel_nome"] == "Valor adicionado bruto a preços correntes da agropecuária"
].copy()
vab_agro_municipios_pivot = vab_agro_municipios.pivot(index="ano_nome", columns="territorio_nome", values="valor").dropna(how="all")

ano_vab_agro_mun = vab_agro_municipios_pivot.index.max()
top10_vab_agro_municipios = vab_agro_municipios_pivot.loc[ano_vab_agro_mun].sort_values(ascending=False).head(10).index.tolist()

fig, ax = plt.subplots(figsize=(10, 6))
for cor, municipio in zip(cores_top10, top10_vab_agro_municipios):
    serie = vab_agro_municipios_pivot[municipio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_xlabel("Ano")
ax.set_ylabel("VAB agropecuário a preços correntes (Mil Reais)")
ax.set_title(f"Top 10 municípios do Ceará por VAB agropecuário ({ano_vab_agro_mun})")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# Quanto cada município representa do VAB agropecuário do Ceará?

# In[66]:


participacao_vab_agro_municipios = (vab_agro_municipios_pivot.loc[ano_vab_agro_mun] / vab_agro_pivot.loc[ano_vab_agro_mun, "Ceará"]) * 100
participacao_vab_agro_municipios = participacao_vab_agro_municipios.sort_values(ascending=False)

top15_vab_agro = participacao_vab_agro_municipios.head(15)
outros_vab_agro = participacao_vab_agro_municipios.iloc[15:].sum()

categorias_vab_agro = list(top15_vab_agro.index) + ["Outros municípios"]
valores_vab_agro = list(top15_vab_agro.values) + [outros_vab_agro]
cores_vab_agro = ["#2a78d6"] * 15 + ["#898781"]

fig, ax = plt.subplots(figsize=(12, 6))
barras = ax.bar(categorias_vab_agro, valores_vab_agro, color=cores_vab_agro)
ax.bar_label(barras, fmt="%.2f%%", fontsize=8, padding=3)

ax.set_xlabel("Município")
ax.set_ylabel("% do VAB agropecuário do Ceará")
ax.set_title(f"Participação de cada município no VAB agropecuário do Ceará ({ano_vab_agro_mun})")
ax.tick_params(axis="x", rotation=60)
ax.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# ## Participação da Agropecuária no VAB — Brasil x Ceará

# Como mudou o peso da agropecuária no VAB do Brasil e do Ceará?

# In[67]:


pct_agro_bc = df_pib_sem_codigo[
    (df_pib_sem_codigo["territorio_nome"].isin(["Brasil", "Ceará"]))
    & (df_pib_sem_codigo["variavel_nome"] == "Participação do valor adicionado bruto a preços correntes da agropecuária no valor adicionado bruto a preços correntes total")
].copy()
pct_agro_bc["ano_nome"] = pct_agro_bc["ano_nome"].astype(int)
pct_agro_pivot = pct_agro_bc.pivot(index="ano_nome", columns="territorio_nome", values="valor").dropna()

fig, ax = plt.subplots(figsize=(10, 5))
for territorio, cor in cores.items():
    serie = pct_agro_pivot[territorio]
    ax.plot(serie.index, serie.values, color=cor, linewidth=2, marker="o", markersize=4, label=territorio)

ax.set_xlabel("Ano")
ax.set_ylabel("Participação da agropecuária no VAB (%)")
ax.set_title(f"Participação da agropecuária no VAB — Brasil x Ceará ({pct_agro_pivot.index.min()}–{pct_agro_pivot.index.max()})")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)

plt.show()


# ## Participação da Agropecuária no VAB — Municípios

# In[68]:


pct_agro_municipios_pivot = df_municipios_pct.copy()
pct_agro_municipios_pivot["ano_nome"] = pct_agro_municipios_pivot["ano_nome"].astype(int)
pct_agro_municipios_pivot = pct_agro_municipios_pivot.pivot(index="ano_nome", columns="territorio_nome", values="valor").dropna(how="all")

ano_pct_mun = pct_agro_municipios_pivot.index.max()
ranking_pct_agro = pct_agro_municipios_pivot.loc[ano_pct_mun].sort_values(ascending=False)

top10_mais_dependentes = ranking_pct_agro.head(10)
top10_menos_dependentes = ranking_pct_agro.tail(10).sort_values()

print(f"Municípios mais dependentes da agropecuária ({ano_pct_mun})")
for municipio, pct in top10_mais_dependentes.items():
    print(f"{municipio}: {pct:.2f}%")

print(f"\nMunicípios menos dependentes da agropecuária ({ano_pct_mun})")
for municipio, pct in top10_menos_dependentes.items():
    print(f"{municipio}: {pct:.2f}%")


# Quais municípios são mais dependentes da agropecuária?

# In[69]:


fig, ax = plt.subplots(figsize=(10, 5))
barras = ax.barh(top10_mais_dependentes.index[::-1], top10_mais_dependentes.values[::-1], color="#1baf7a")
ax.bar_label(barras, fmt="%.1f%%", fontsize=8, padding=3)

ax.set_xlabel("Participação da agropecuária no VAB (%)")
ax.set_title(f"Top 10 municípios mais dependentes da agropecuária ({ano_pct_mun})")
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)

plt.show()


# ## Correlação entre Métricas (Municípios do Ceará)

# In[70]:


metricas_municipios_ceara = df_municipios.pivot_table(
    index=['ano_nome', 'territorio_nome'], columns='variavel_nome', values='valor'
)

nomes_curtos = {
    'Produto Interno Bruto a preços correntes': 'PIB',
    'Valor adicionado bruto a preços correntes total': 'VAB Total',
    'Valor adicionado bruto a preços correntes da agropecuária': 'VAB Agro',
    'Participação do valor adicionado bruto a preços correntes da agropecuária no valor adicionado bruto a preços correntes total': '% Agro no VAB',
}

correlacao_metricas_pib = metricas_municipios_ceara.corr().rename(index=nomes_curtos, columns=nomes_curtos)

fig, ax = plt.subplots(figsize=(8, 6))
sb.heatmap(correlacao_metricas_pib, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
ax.set_title('Correlação entre métricas do PIB (municípios do Ceará, por ano)')
plt.tight_layout()
plt.show()


# **Leitura da correlação:**
# 
# - **PIB × VAB Total (1.00):** correlação perfeita — PIB municipal é basicamente o VAB total mais impostos, então andam juntos por construção.
# - **VAB Agro × PIB/VAB Total (0.10–0.11):** correlação fraca — o tamanho da economia agropecuária em Mil Reais não acompanha o tamanho geral da economia do município (municípios pequenos podem ter agropecuária relevante, municípios grandes podem ser pouco agrícolas).
# - **% Agro no VAB × PIB/VAB Total (-0.18):** fraca negativa — municípios com economia maior tendem a depender um pouco menos, proporcionalmente, da agropecuária (mais diversificados/urbanos).
# - **% Agro no VAB × VAB Agro (0.21):** fraca positiva — mais valor agropecuário em termos absolutos tende a vir acompanhado de uma participação um pouco maior no VAB total, mas a relação não é forte.
# 
# Importante: VAB total, VAB agropecuário e % agropecuária não têm dado para 2022 e 2023 (372 valores nulos = 186 territórios × 2 anos) — o PIB é divulgado mais rápido que o VAB pelo IBGE, então essa correlação usa só os anos com os quatro indicadores disponíveis.
