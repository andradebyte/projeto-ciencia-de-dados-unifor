#!/usr/bin/env python
# coding: utf-8

# # Análise Geoespacial do PIB — Municípios do Ceará

# In[ ]:


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


# ## Carregamento e validação da malha municipal

# In[ ]:


gdf_municipios = gpd.read_file("../data/raw/malha_municipal_ce_2022.geojson")

print(f"Total de municípios: {gdf_municipios.shape[0]}")
print(f"Geometrias inválidas antes: {(~gdf_municipios.geometry.is_valid).sum()}")

gdf_municipios["geometry"] = gdf_municipios["geometry"].make_valid()

print(f"Geometrias inválidas depois: {(~gdf_municipios.geometry.is_valid).sum()}")

gdf_municipios.plot(figsize=(6, 6), color="#2a78d6", edgecolor="#fcfcfb", linewidth=0.3)
plt.title("Malha municipal do Ceará (184 municípios)")
plt.axis("off")
plt.show()


# ## Carregamento do PIB por município

# In[ ]:


df_pib_raw = pd.read_csv("../data/processed/pib_tratado.csv")

pib_municipios_geo = df_pib_raw[
    (df_pib_raw["nivel_territorial_nome"] == "Município")
    & (df_pib_raw["variavel_nome"] == "Produto Interno Bruto a preços correntes")
].copy()
pib_municipios_geo["territorio_codigo"] = pib_municipios_geo["territorio_codigo"].astype(str)

pib_municipios_geo_pivot = pib_municipios_geo.pivot(index="ano_nome", columns="territorio_codigo", values="valor")

print(f"Municípios com PIB: {pib_municipios_geo_pivot.shape[1]}")
pib_municipios_geo_pivot.head()


# ## Junção geometria + PIB

# In[ ]:


gdf_pib = gdf_municipios.merge(
    pib_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios = (
    pib_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_pib.insert(1, "nome", gdf_pib["codarea"].map(nomes_municipios))

nao_casaram = gdf_pib[gdf_pib[2023].isna()]
print(f"Municípios sem PIB casado: {len(nao_casaram)}")
gdf_pib.head()


# Qual o PIB de cada município do Ceará, no mapa, em 2023?

# In[ ]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_pib.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_pib[2023].min(), vmax=gdf_pib[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "PIB a preços correntes (Mil Reais, escala log)", "shrink": 0.6},
    ax=ax,
)

fortaleza = gdf_pib[gdf_pib["codarea"] == "2304400"]
fortaleza.plot(ax=ax, facecolor="none", edgecolor="#e34948", linewidth=1.5)

ax.set_title("PIB dos municípios do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[ ]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_pib.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_pib[2003].min(), vmax=gdf_pib[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "PIB a preços correntes (Mil Reais, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("PIB dos municípios do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em PIB (2003 -> 2023), no mapa?

# In[ ]:


gdf_pib["crescimento"] = gdf_pib[2023] / gdf_pib[2003]

ranking = gdf_pib[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking.index += 1

print("Ranking de crescimento do PIB por município (2003 -> 2023):")
for pos, row in ranking.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")

top10 = gdf_pib.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_pib.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do PIB (2003 -> 2023, x vezes)", "shrink": 0.6},
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

ax.set_title("Crescimento do PIB por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()


# Quais municípios são mais dependentes da agropecuária, no mapa?

# In[ ]:


pct_agro_geo = df_pib_raw[
    (df_pib_raw["nivel_territorial_nome"] == "Município")
    & (df_pib_raw["variavel_nome"] == "Participação do valor adicionado bruto a preços correntes da agropecuária no valor adicionado bruto a preços correntes total")
].copy()
pct_agro_geo["territorio_codigo"] = pct_agro_geo["territorio_codigo"].astype(str)
pct_agro_geo_pivot = pct_agro_geo.pivot(index="ano_nome", columns="territorio_codigo", values="valor")

ano_pct_geo = pct_agro_geo_pivot.dropna(how="all").index.max()

gdf_pct_agro = gdf_municipios.merge(
    pct_agro_geo_pivot.loc[ano_pct_geo].rename("participacao_agro"),
    left_on="codarea",
    right_index=True,
    how="left",
)

fig, ax = plt.subplots(figsize=(8, 8))
gdf_pct_agro.plot(
    column="participacao_agro",
    cmap="Greens",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Participação da agropecuária no VAB (%)", "shrink": 0.6},
    ax=ax,
)

ax.set_title(f"Dependência da agropecuária por município ({ano_pct_geo})")
ax.axis("off")
plt.show()

