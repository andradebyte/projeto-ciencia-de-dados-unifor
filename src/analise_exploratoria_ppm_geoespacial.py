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


# In[3]:


df_ppm_raw = pd.read_csv("../data/processed/ppm_tratado.csv")


# **Regra importante (não somar espécies):** assim como no notebook principal do PPM, cada espécie (bovino, caprino, ovino, suíno, galináceos) é medida em "Cabeças" mas não são unidades equivalentes entre si. Cada mapa abaixo é de uma única espécie — nenhuma soma entre espécies é feita.

# ## Bovino

# Qual foi o efetivo de bovino de cada município do Ceará, e como junto isso com a malha?

# In[4]:


bovino_municipios_geo = df_ppm_raw[
    (df_ppm_raw["nivel_territorial_nome"] == "Município")
    & (df_ppm_raw["tipo_rebanho_nome"] == "Bovino")
].copy()
bovino_municipios_geo["territorio_codigo"] = bovino_municipios_geo["territorio_codigo"].astype(str)

bovino_municipios_geo_pivot = bovino_municipios_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

print(f"Municípios com efetivo de bovino: {bovino_municipios_geo_pivot.shape[1]}")
bovino_municipios_geo_pivot.head()


# In[5]:


gdf_bovino = gdf_municipios.merge(
    bovino_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios_bovino = (
    bovino_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_bovino.insert(1, "nome", gdf_bovino["codarea"].map(nomes_municipios_bovino))

nao_casaram = gdf_bovino[gdf_bovino[2023].isna()]
print(f"Municípios sem valor casado: {len(nao_casaram)}")
gdf_bovino.head()


# Como o efetivo de bovino se distribui no mapa, em 2023?

# In[6]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_bovino.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_bovino[2023][gdf_bovino[2023] > 0].min(), vmax=gdf_bovino[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de bovino (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de bovino por município do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[7]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_bovino.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_bovino[2003][gdf_bovino[2003] > 0].min(), vmax=gdf_bovino[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de bovino (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de bovino por município do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em efetivo de bovino (2003 -> 2023), no mapa?

# In[8]:


gdf_bovino["crescimento"] = gdf_bovino[2023] / gdf_bovino[2003]

ranking_bovino = gdf_bovino[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking_bovino.index += 1

print("Ranking de crescimento do efetivo de bovino por município (2003 -> 2023):")
for pos, row in ranking_bovino.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")


# In[9]:


top10_bovino = gdf_bovino.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_bovino.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do efetivo de bovino (2003 -> 2023, x vezes)", "shrink": 0.6},
    ax=ax,
)

for _, row in top10_bovino.iterrows():
    centroide = row.geometry.centroid
    ax.annotate(
        row["nome"],
        xy=(centroide.x, centroide.y),
        fontsize=6,
        ha="center",
        color="#1a1a1a",
        weight="bold",
    )

ax.set_title("Crescimento do efetivo de bovino por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()


# ## Caprino

# Qual foi o efetivo de caprino de cada município do Ceará, e como junto isso com a malha?

# In[10]:


caprino_municipios_geo = df_ppm_raw[
    (df_ppm_raw["nivel_territorial_nome"] == "Município")
    & (df_ppm_raw["tipo_rebanho_nome"] == "Caprino")
].copy()
caprino_municipios_geo["territorio_codigo"] = caprino_municipios_geo["territorio_codigo"].astype(str)

caprino_municipios_geo_pivot = caprino_municipios_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

print(f"Municípios com efetivo de caprino: {caprino_municipios_geo_pivot.shape[1]}")
caprino_municipios_geo_pivot.head()


# In[11]:


gdf_caprino = gdf_municipios.merge(
    caprino_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios_caprino = (
    caprino_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_caprino.insert(1, "nome", gdf_caprino["codarea"].map(nomes_municipios_caprino))

nao_casaram = gdf_caprino[gdf_caprino[2023].isna()]
print(f"Municípios sem valor casado: {len(nao_casaram)}")
gdf_caprino.head()


# Como o efetivo de caprino se distribui no mapa, em 2023?

# In[12]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_caprino.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_caprino[2023][gdf_caprino[2023] > 0].min(), vmax=gdf_caprino[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de caprino (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de caprino por município do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[13]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_caprino.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_caprino[2003][gdf_caprino[2003] > 0].min(), vmax=gdf_caprino[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de caprino (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de caprino por município do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em efetivo de caprino (2003 -> 2023), no mapa?

# In[14]:


gdf_caprino["crescimento"] = gdf_caprino[2023] / gdf_caprino[2003]

ranking_caprino = gdf_caprino[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking_caprino.index += 1

print("Ranking de crescimento do efetivo de caprino por município (2003 -> 2023):")
for pos, row in ranking_caprino.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")


# In[15]:


top10_caprino = gdf_caprino.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_caprino.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do efetivo de caprino (2003 -> 2023, x vezes)", "shrink": 0.6},
    ax=ax,
)

for _, row in top10_caprino.iterrows():
    centroide = row.geometry.centroid
    ax.annotate(
        row["nome"],
        xy=(centroide.x, centroide.y),
        fontsize=6,
        ha="center",
        color="#1a1a1a",
        weight="bold",
    )

ax.set_title("Crescimento do efetivo de caprino por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()


# ## Ovino

# Qual foi o efetivo de ovino de cada município do Ceará, e como junto isso com a malha?

# In[16]:


ovino_municipios_geo = df_ppm_raw[
    (df_ppm_raw["nivel_territorial_nome"] == "Município")
    & (df_ppm_raw["tipo_rebanho_nome"] == "Ovino")
].copy()
ovino_municipios_geo["territorio_codigo"] = ovino_municipios_geo["territorio_codigo"].astype(str)

ovino_municipios_geo_pivot = ovino_municipios_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

print(f"Municípios com efetivo de ovino: {ovino_municipios_geo_pivot.shape[1]}")
ovino_municipios_geo_pivot.head()


# In[17]:


gdf_ovino = gdf_municipios.merge(
    ovino_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios_ovino = (
    ovino_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_ovino.insert(1, "nome", gdf_ovino["codarea"].map(nomes_municipios_ovino))

nao_casaram = gdf_ovino[gdf_ovino[2023].isna()]
print(f"Municípios sem valor casado: {len(nao_casaram)}")
gdf_ovino.head()


# Como o efetivo de ovino se distribui no mapa, em 2023?

# In[18]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_ovino.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_ovino[2023][gdf_ovino[2023] > 0].min(), vmax=gdf_ovino[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de ovino (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de ovino por município do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[19]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_ovino.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_ovino[2003][gdf_ovino[2003] > 0].min(), vmax=gdf_ovino[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de ovino (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de ovino por município do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em efetivo de ovino (2003 -> 2023), no mapa?

# In[20]:


gdf_ovino["crescimento"] = gdf_ovino[2023] / gdf_ovino[2003]

ranking_ovino = gdf_ovino[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking_ovino.index += 1

print("Ranking de crescimento do efetivo de ovino por município (2003 -> 2023):")
for pos, row in ranking_ovino.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")


# In[21]:


top10_ovino = gdf_ovino.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_ovino.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do efetivo de ovino (2003 -> 2023, x vezes)", "shrink": 0.6},
    ax=ax,
)

for _, row in top10_ovino.iterrows():
    centroide = row.geometry.centroid
    ax.annotate(
        row["nome"],
        xy=(centroide.x, centroide.y),
        fontsize=6,
        ha="center",
        color="#1a1a1a",
        weight="bold",
    )

ax.set_title("Crescimento do efetivo de ovino por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()


# ## Suíno

# Qual foi o efetivo de suíno de cada município do Ceará, e como junto isso com a malha?

# In[22]:


suino_municipios_geo = df_ppm_raw[
    (df_ppm_raw["nivel_territorial_nome"] == "Município")
    & (df_ppm_raw["tipo_rebanho_nome"] == "Suíno - total")
].copy()
suino_municipios_geo["territorio_codigo"] = suino_municipios_geo["territorio_codigo"].astype(str)

suino_municipios_geo_pivot = suino_municipios_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

print(f"Municípios com efetivo de suíno: {suino_municipios_geo_pivot.shape[1]}")
suino_municipios_geo_pivot.head()


# In[23]:


gdf_suino = gdf_municipios.merge(
    suino_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios_suino = (
    suino_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_suino.insert(1, "nome", gdf_suino["codarea"].map(nomes_municipios_suino))

nao_casaram = gdf_suino[gdf_suino[2023].isna()]
print(f"Municípios sem valor casado: {len(nao_casaram)}")
gdf_suino.head()


# Como o efetivo de suíno se distribui no mapa, em 2023?

# In[24]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_suino.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_suino[2023][gdf_suino[2023] > 0].min(), vmax=gdf_suino[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de suíno (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de suíno por município do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[25]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_suino.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_suino[2003][gdf_suino[2003] > 0].min(), vmax=gdf_suino[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de suíno (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de suíno por município do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em efetivo de suíno (2003 -> 2023), no mapa?

# In[26]:


gdf_suino["crescimento"] = gdf_suino[2023] / gdf_suino[2003]

ranking_suino = gdf_suino[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking_suino.index += 1

print("Ranking de crescimento do efetivo de suíno por município (2003 -> 2023):")
for pos, row in ranking_suino.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")


# In[27]:


top10_suino = gdf_suino.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_suino.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do efetivo de suíno (2003 -> 2023, x vezes)", "shrink": 0.6},
    ax=ax,
)

for _, row in top10_suino.iterrows():
    centroide = row.geometry.centroid
    ax.annotate(
        row["nome"],
        xy=(centroide.x, centroide.y),
        fontsize=6,
        ha="center",
        color="#1a1a1a",
        weight="bold",
    )

ax.set_title("Crescimento do efetivo de suíno por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()


# ## Galináceos

# Qual foi o efetivo de galináceos de cada município do Ceará, e como junto isso com a malha?

# In[28]:


galinaceos_municipios_geo = df_ppm_raw[
    (df_ppm_raw["nivel_territorial_nome"] == "Município")
    & (df_ppm_raw["tipo_rebanho_nome"] == "Galináceos - total")
].copy()
galinaceos_municipios_geo["territorio_codigo"] = galinaceos_municipios_geo["territorio_codigo"].astype(str)

galinaceos_municipios_geo_pivot = galinaceos_municipios_geo.groupby(["ano_nome", "territorio_codigo"])["valor"].sum().unstack("territorio_codigo")

print(f"Municípios com efetivo de galináceos: {galinaceos_municipios_geo_pivot.shape[1]}")
galinaceos_municipios_geo_pivot.head()


# In[29]:


gdf_galinaceos = gdf_municipios.merge(
    galinaceos_municipios_geo_pivot.T,
    left_on="codarea",
    right_index=True,
    how="left",
)

nomes_municipios_galinaceos = (
    galinaceos_municipios_geo.drop_duplicates("territorio_codigo")
    .set_index("territorio_codigo")["territorio_nome"]
)
gdf_galinaceos.insert(1, "nome", gdf_galinaceos["codarea"].map(nomes_municipios_galinaceos))

nao_casaram = gdf_galinaceos[gdf_galinaceos[2023].isna()]
print(f"Municípios sem valor casado: {len(nao_casaram)}")
gdf_galinaceos.head()


# Como o efetivo de galináceos se distribui no mapa, em 2023?

# In[30]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_galinaceos.plot(
    column=2023,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_galinaceos[2023][gdf_galinaceos[2023] > 0].min(), vmax=gdf_galinaceos[2023].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de galináceos (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de galináceos por município do Ceará (2023)")
ax.axis("off")
plt.show()


# E como era esse mapa em 2003?

# In[31]:


fig, ax = plt.subplots(figsize=(8, 8))
gdf_galinaceos.plot(
    column=2003,
    cmap="Blues",
    norm=LogNorm(vmin=gdf_galinaceos[2003][gdf_galinaceos[2003] > 0].min(), vmax=gdf_galinaceos[2003].max()),
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Efetivo de galináceos (Cabeças, escala log)", "shrink": 0.6},
    ax=ax,
)

ax.set_title("Efetivo de galináceos por município do Ceará (2003)")
ax.axis("off")
plt.show()


# Quais municípios mais cresceram em efetivo de galináceos (2003 -> 2023), no mapa?

# In[32]:


gdf_galinaceos["crescimento"] = gdf_galinaceos[2023] / gdf_galinaceos[2003]

ranking_galinaceos = gdf_galinaceos[["nome", "crescimento"]].sort_values("crescimento", ascending=False).reset_index(drop=True)
ranking_galinaceos.index += 1

print("Ranking de crescimento do efetivo de galináceos por município (2003 -> 2023):")
for pos, row in ranking_galinaceos.iterrows():
    print(f"{pos:>3}. {row['nome']:<30} {row['crescimento']:>6.1f}x")


# In[33]:


top10_galinaceos = gdf_galinaceos.nlargest(10, "crescimento")

fig, ax = plt.subplots(figsize=(9, 9))
gdf_galinaceos.plot(
    column="crescimento",
    cmap="Oranges",
    edgecolor="#fcfcfb",
    linewidth=0.3,
    legend=True,
    legend_kwds={"label": "Fator de crescimento do efetivo de galináceos (2003 -> 2023, x vezes)", "shrink": 0.6},
    ax=ax,
)

for _, row in top10_galinaceos.iterrows():
    centroide = row.geometry.centroid
    ax.annotate(
        row["nome"],
        xy=(centroide.x, centroide.y),
        fontsize=6,
        ha="center",
        color="#1a1a1a",
        weight="bold",
    )

ax.set_title("Crescimento do efetivo de galináceos por município (2003–2023)\ntop 10 municípios nomeados")
ax.axis("off")
plt.show()

