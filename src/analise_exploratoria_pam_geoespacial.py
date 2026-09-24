#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


# Como é a malha municipal do Ceará que vamos usar pros mapas?

# In[2]:


gdf_municipios = gpd.read_file("../data/raw/malha_municipal_ce_2022.geojson")

print(f"Total de municípios: {gdf_municipios.shape[0]}")
print(f"Geometrias inválidas antes: {(~gdf_municipios.geometry.is_valid).sum()}")

gdf_municipios["geometry"] = gdf_municipios["geometry"].make_valid()

print(f"Geometrias inválidas depois: {(~gdf_municipios.geometry.is_valid).sum()}")

gdf_municipios.plot(figsize=(6, 6), color="#2a78d6", edgecolor="#fcfcfb", linewidth=0.3)
plt.title("Malha municipal do Ceará (184 municípios)")
plt.axis("off")
plt.show()


# Qual foi o valor da produção agrícola de cada município do Ceará, e como junto isso com a malha?

# In[3]:


df_pam_raw = pd.read_csv("../data/processed/pam_tratado.csv")

valor_municipios_geo = df_pam_raw[
    (df_pam_raw["nivel_territorial_nome"] == "Município")
    & (df_pam_raw["unidade"] == "Mil Reais")
].copy()
valor_municipios_geo["territorio_codigo"] = valor_municipios_geo["territorio_codigo"].astype(str)

valor_municipios_geo_pivot = valor_municipios_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

print(f"Municípios com valor da produção: {valor_municipios_geo_pivot.shape[1]}")
valor_municipios_geo_pivot.head()


# In[4]:


gdf_valor = gdf_municipios.merge(
    valor_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios = (
    valor_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_valor.insert(1, "nome", gdf_valor["codarea"].map(nomes_municipios))

nao_casaram = gdf_valor[gdf_valor[2023].isna()]
print(f"Municípios sem valor casado: {len(nao_casaram)}")
gdf_valor.head()


# Qual o valor da produção agrícola de cada município do Ceará, no mapa, em 2023?

# In[5]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_valor.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_valor[2023].min(), vmax=gdf_valor[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Valor da produção (Mil Reais, escala log)", "shrink": 0.6},
    ax=ax,
)

quixere = gdf_valor[gdf_valor["nome"] == "Quixeré - CE"]
quixere.plot(ax=ax, facecolor="none", edgecolor="#e34948", linewidth=1.5)

ax.set_title("Valor da produção agrícola dos municípios do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[6]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_valor.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_valor[2003].min(), vmax=gdf_valor[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Valor da produção (Mil Reais, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Valor da produção agrícola dos municípios do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em valor de produção (2003 -> 2023), no mapa?

# In[7]:


gdf_valor["crescimento"] = gdf_valor[2023] / gdf_valor[2003]

ranking = gdf_valor[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking.index += 1

print("Ranking de crescimento do valor da produção por município (2003 -> 2023):")
for pos, row in ranking.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")


# In[8]:


top10 = gdf_valor.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_valor.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do valor da produção (2003 -> 2023, x vezes)", "shrink": 0.6},
    ax=ax,
)

for _, row in top10.iterrows():
    centroide = row.geometry.centroid
    ax.annotate(
        row["nome"],
        xy=(centroide.x, centroide.y),
        fontsize=6,
        ha="center",
        color="#1a1a1a",
        weight="bold",
    )

ax.set_title("Crescimento do valor da produção por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()


# Existe diferença de perda de safra (área plantada x área colhida) entre os municípios do Ceará, no mapa?

# In[9]:


colhida_geo = df_pam_raw[
    (df_pam_raw["nivel_territorial_nome"] == "Município") & (df_pam_raw["variavel_nome"] == "Área colhida")
].copy()
colhida_geo["territorio_codigo"] = colhida_geo["territorio_codigo"].astype(str)
colhida_pivot = colhida_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

plantada_geo = df_pam_raw[
    (df_pam_raw["nivel_territorial_nome"] == "Município") & (df_pam_raw["variavel_nome"] == "Área plantada ou destinada à colheita")
].copy()
plantada_geo["territorio_codigo"] = plantada_geo["territorio_codigo"].astype(str)
plantada_pivot = plantada_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

ano_perda_geo = 2023
perda_safra_geo = (colhida_pivot.loc[ano_perda_geo] / plantada_pivot.loc[ano_perda_geo] * 100).rename("pct_colhida")

gdf_perda_safra = gdf_municipios.merge(perda_safra_geo, left_on="codarea", right_index=True, how="left")

fig, ax = plt.subplots(figsize=(8, 8))
gdf_perda_safra.plot(
    column="pct_colhida",
    cmap="RdYlGn",
    vmin=0,
    vmax=100,
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "% da área plantada efetivamente colhida", "shrink": 0.6},
    ax=ax,
)

ax.set_title(f"Perda de safra por município ({ano_perda_geo})")
ax.axis("off")
plt.show()

