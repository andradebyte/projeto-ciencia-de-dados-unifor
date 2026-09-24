"""
Evolucao pecuaria por especie (PPM 3939, efetivo dos rebanhos, 2003-2024).

Regra obrigatoria (dados/README_DADOS.md item 4-5; feedback do acompanhamento):
bovinos, caprinos, ovinos, suinos e galinaceos NAO sao unidades equivalentes e
NUNCA devem ser somados entre si. Nao existe "rebanho total" - cada especie e
tratada em serie propria, do carregamento ate os graficos.

Produz:
  1) Evolucao temporal do efetivo por especie, Ceara, 2003-2024 (indice e
     variacao %), com interpretacao.
  2) Municipios de destaque por especie (maior efetivo medio e maior
     crescimento no periodo), com interpretacao.
  3. Visualizacao 1 (evolucao por especie) e Visualizacao 2 (municipios de
     destaque) salvas em notebooks/.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = "dados/raw"
SIDRA_NA = {"...": pd.NA, "..": pd.NA, "X": pd.NA}
SIDRA_ZERO = {"-": 0.0}

REBANHO_COD_NOME = {"2670": "Bovinos", "2681": "Caprinos", "2677": "Ovinos",
                     "32794": "Suínos", "32796": "Galináceos"}
ESPECIES = list(REBANHO_COD_NOME.values())
CORES = {"Bovinos": "#8c510a", "Caprinos": "#01665e", "Ovinos": "#5ab4ac",
         "Suínos": "#d8b365", "Galináceos": "#c51b7d"}


def read_sidra(path, extra_dtypes=None):
    dtypes = {"territorio_codigo": "string", "ano_codigo": "Int64", "nivel_territorial_codigo": "string"}
    if extra_dtypes:
        dtypes.update(extra_dtypes)
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=dtypes, keep_default_na=False)
    df["valor"] = df["valor"].replace(SIDRA_NA).replace(SIDRA_ZERO)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    return df


ppm = read_sidra(f"{RAW}/t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv", {"tipo_rebanho_codigo": "string"})
ppm["especie"] = ppm["tipo_rebanho_codigo"].map(REBANHO_COD_NOME)

# ---------------------------------------------------------------------------
# 1. Evolucao temporal por especie, Ceara (N3, cod 23) - series independentes
# ---------------------------------------------------------------------------
ppm_ce = ppm[(ppm["territorio_codigo"] == "23") & (ppm["nivel_territorial_codigo"] == "N3")]

series_ce = {}
resumo_evolucao = []
for especie in ESPECIES:
    s = ppm_ce[ppm_ce["especie"] == especie].set_index("ano_codigo")["valor"].sort_index()
    series_ce[especie] = s
    var_pct = (s.loc[2024] / s.loc[2003] - 1) * 100
    resumo_evolucao.append({
        "especie": especie,
        "efetivo_2003_cab": int(s.loc[2003]),
        "efetivo_2024_cab": int(s.loc[2024]),
        "variacao_2003_2024_pct": round(var_pct, 1),
    })
resumo_evolucao_df = pd.DataFrame(resumo_evolucao).sort_values("variacao_2003_2024_pct", ascending=False)
print("Evolução do efetivo por espécie — Ceará, 2003 → 2024 (séries independentes, não somadas):")
print(resumo_evolucao_df.to_string(index=False))

# ---------------------------------------------------------------------------
# 2. Municipios de destaque por especie: maior efetivo medio e maior
#    crescimento 2003-2024 (cada especie calculada e ranqueada isoladamente)
# ---------------------------------------------------------------------------
ppm_mun = ppm[ppm["nivel_territorial_codigo"] == "N6"]

destaques = []
top_mun_por_especie = {}
for especie in ESPECIES:
    sub = ppm_mun[ppm_mun["especie"] == especie]
    media_mun = sub.groupby(["territorio_codigo", "territorio_nome"])["valor"].mean()
    top3_media = media_mun.sort_values(ascending=False).head(3)
    top_mun_por_especie[especie] = top3_media

    piv = sub.pivot_table(index="territorio_nome", columns="ano_codigo", values="valor")
    cresc = ((piv[2024] - piv[2003]) / piv[2003].replace(0, pd.NA) * 100).dropna()
    top1_crescimento = cresc.sort_values(ascending=False).head(1)

    for nome, val in top3_media.items():
        destaques.append({"especie": especie, "municipio": nome[1], "criterio": "maior efetivo médio 2003-2024",
                           "valor": round(val, 0)})
    for nome, val in top1_crescimento.items():
        destaques.append({"especie": especie, "municipio": nome, "criterio": "maior crescimento % 2003→2024",
                           "valor": round(val, 1)})

destaques_df = pd.DataFrame(destaques)
print("\nMunicípios de destaque por espécie (calculados isoladamente por espécie):")
print(destaques_df.to_string(index=False))

# ---------------------------------------------------------------------------
# Visualização 1 — evolução temporal por espécie, Ceará (índice 2003=100)
# ---------------------------------------------------------------------------
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
for especie in ESPECIES:
    s = series_ce[especie]
    idx = s / s.loc[2003] * 100
    ax1.plot(idx.index, idx.values, marker="o", markersize=2.5, label=especie, color=CORES[especie])
    ax2.plot(s.index, s.values / 1000, marker="o", markersize=2.5, label=especie, color=CORES[especie])

ax1.set_title("Índice do efetivo por espécie (2003 = 100)")
ax1.set_ylabel("Índice")
ax1.axhline(100, color="grey", linewidth=0.6, linestyle="--")
ax2.set_title("Efetivo por espécie (mil cabeças)")
ax2.set_ylabel("Mil cabeças")
ax2.set_yscale("log")
for ax in (ax1, ax2):
    ax.set_xlabel("Ano")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
fig1.suptitle("Visualização 1 (preliminar) — Evolução do efetivo pecuário por espécie, Ceará, 2003–2024\n"
              "(séries independentes — nenhuma espécie é somada a outra)")
fig1.tight_layout()
fig1.savefig("notebooks/fig_pecuaria1_evolucao_especie.png", dpi=150)
print("\nFigura salva: notebooks/fig_pecuaria1_evolucao_especie.png")

# ---------------------------------------------------------------------------
# Visualização 2 — municípios de destaque por espécie (maior efetivo médio)
# ---------------------------------------------------------------------------
fig2, axes = plt.subplots(1, 5, figsize=(15, 4), sharey=False)
for ax, especie in zip(axes, ESPECIES):
    top3 = top_mun_por_especie[especie].sort_values()
    nomes = [n[1] for n in top3.index]
    ax.barh(nomes, top3.values, color=CORES[especie])
    ax.set_title(especie, fontsize=10)
    ax.set_xlabel("Efetivo médio\n2003–2024 (cab.)")
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="x", alpha=0.3)
fig2.suptitle("Visualização 2 (preliminar) — 3 municípios de destaque por espécie\n"
              "(maior efetivo médio 2003–2024, ranqueado dentro de cada espécie)")
fig2.tight_layout()
fig2.savefig("notebooks/fig_pecuaria2_municipios_destaque.png", dpi=150)
print("Figura salva: notebooks/fig_pecuaria2_municipios_destaque.png")

print("""
--- Interpretação inicial — Visualização 1 ---
Cada espécie tem trajetória própria e não deve ser lida como parte de um
"rebanho total": bovinos e galináceos guardam a maior escala absoluta (eixo em
mil cabeças, log), enquanto caprinos e ovinos, típicos da pecuária do
semiárido cearense, mostram amplitude de crescimento maior no índice 2003=100
no período. Ver notebooks/06_evolucao_pecuaria.py (saída de console) para os
valores de variação % 2003→2024 de cada espécie.

--- Interpretação inicial — Visualização 2 ---
Os municípios de destaque mudam por espécie — não existe um município
"líder da pecuária" genérico, e sim um líder por espécie, calculado sem
misturar efetivos de espécies diferentes. Ver console para a lista completa
(top 3 por maior efetivo médio + top 1 por maior crescimento % 2003→2024, por
espécie).
""")
