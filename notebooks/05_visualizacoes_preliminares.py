"""
Visualizacoes preliminares (secao 5 do relatorio de acompanhamento), a partir
do cruzamento gerado por 04_cruzamento_pam_ppm_pib.py.

Visualizacao 1: taxa de frustracao de safra vs. crescimento do efetivo de
caprinos e ovinos (especies mantidas separadas, nunca somadas - ver
data/README_DADOS.md item 4-5 e notebooks/06_evolucao_pecuaria.py), 2003-2024,
Ceara + 2 municipios de exemplo.
Visualizacao 2: dispersao PAM x PPM x PIB por municipio, ano de referencia
2021 (ultimo ano com participacao do VAB agropecuario valida).
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = "data/dados_originais"
SIDRA_NA = {"...": pd.NA, "..": pd.NA, "X": pd.NA}
SIDRA_ZERO = {"-": 0.0}


def read_sidra(path, extra_dtypes=None):
    dtypes = {"territorio_codigo": "string", "ano_codigo": "Int64", "nivel_territorial_codigo": "string"}
    if extra_dtypes:
        dtypes.update(extra_dtypes)
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=dtypes, keep_default_na=False)
    df["valor"] = df["valor"].replace(SIDRA_NA).replace(SIDRA_ZERO)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    return df


pam_plant = read_sidra(f"{RAW}/t5457_pam_area_plantada_2003_2024_ce_br.csv", {"produto_codigo": "string"})
pam_colh = read_sidra(f"{RAW}/t5457_pam_area_colhida_2003_2024_ce_br.csv", {"produto_codigo": "string"})
pam_qtd = read_sidra(f"{RAW}/t5457_pam_quantidade_produzida_2003_2024_ce_br.csv", {"produto_codigo": "string"})
ppm = read_sidra(f"{RAW}/t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv", {"tipo_rebanho_codigo": "string"})
pib = read_sidra(f"{RAW}/t5938_pib_agropecuaria_2003_2023_ce_br.csv", {"variavel_codigo": "string"})

# ---------------------------------------------------------------------------
# Visualizacao 1: serie temporal estado + 2 municipios de exemplo
# ---------------------------------------------------------------------------
# Caprino e ovino tratados como series SEPARADAS (nunca somadas - ver
# data/README_DADOS.md item 4-5): cada especie e uma unidade diferente.
CAPRINO_OVINO = {"2681": "caprino", "2677": "ovino"}

def frustracao_por_territorio(cod, nivel):
    p = pam_plant[(pam_plant["territorio_codigo"] == cod) & (pam_plant["nivel_territorial_codigo"] == nivel)]
    c = pam_colh[(pam_colh["territorio_codigo"] == cod) & (pam_colh["nivel_territorial_codigo"] == nivel)]
    p_ano = p.groupby("ano_codigo")["valor"].sum()
    c_ano = c.groupby("ano_codigo")["valor"].sum()
    return (1 - c_ano / p_ano).rename("taxa_frustracao_safra")

def indice_por_especie(cod, nivel, tipo_rebanho_codigo):
    r = ppm[(ppm["territorio_codigo"] == cod) & (ppm["nivel_territorial_codigo"] == nivel)
            & (ppm["tipo_rebanho_codigo"] == tipo_rebanho_codigo)]
    r_ano = r.groupby("ano_codigo")["valor"].sum()
    base = r_ano.loc[2003]
    return (r_ano / base * 100).rename("indice_2003_100")

# municipio de exemplo: o de maior efetivo medio de caprinos 2003-2024 (dado real,
# especie escolhida isoladamente - nao e uma soma caprino+ovino)
ppm_mun = ppm[ppm["nivel_territorial_codigo"] == "N6"]
capr_mun = ppm_mun[ppm_mun["tipo_rebanho_codigo"] == "2681"]
media_mun = capr_mun.groupby(["territorio_codigo", "territorio_nome"])["valor"].mean().sort_values(ascending=False)
top1 = media_mun.head(1)
print("1 municipio de exemplo (maior efetivo medio de CAPRINOS, 2003-2024):")
print(top1)

territorios_v1 = [("23", "N3", "Ceará (estado)")] + [
    (cod, "N6", nome) for (cod, nome) in top1.index
]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharex=True)
for cod, nivel, nome in territorios_v1:
    fr = frustracao_por_territorio(cod, nivel)
    axes[0].plot(fr.index, fr.values, marker="o", markersize=3, label=nome)
    for tipo_cod, tipo_nome in CAPRINO_OVINO.items():
        idx = indice_por_especie(cod, nivel, tipo_cod)
        linestyle = "-" if tipo_nome == "caprino" else "--"
        axes[1].plot(idx.index, idx.values, marker="o", markersize=3, linestyle=linestyle,
                     label=f"{nome} — {tipo_nome}")

axes[0].set_title("Taxa de frustração de safra\n(1 − área colhida / área plantada)")
axes[0].set_ylabel("Taxa")
axes[0].axhline(0, color="grey", linewidth=0.6)
axes[1].set_title("Crescimento do efetivo — caprinos e ovinos\n(séries separadas, índice 2003 = 100)")
axes[1].set_ylabel("Índice (2003=100)")
for ax in axes:
    ax.set_xlabel("Ano")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
fig.suptitle("Visualização 1 (preliminar) — frustração de safra vs. crescimento dos efetivos\n"
             "de caprinos e ovinos (espécies separadas), 2003–2024", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.92])
fig.savefig("notebooks/fig_visualizacao1_serie_temporal.png", dpi=150)
print("Figura salva: notebooks/fig_visualizacao1_serie_temporal.png")

# valores citaveis para a interpretacao
fr_ce = frustracao_por_territorio("23", "N3")
idx_ce_caprino = indice_por_especie("23", "N3", "2681")
idx_ce_ovino = indice_por_especie("23", "N3", "2677")
print(f"\nCeará - taxa de frustração de safra: media 2003-2024 = {fr_ce.mean():.3f}, "
      f"min={fr_ce.min():.3f} (ano {fr_ce.idxmin()}), max={fr_ce.max():.3f} (ano {fr_ce.idxmax()})")
print(f"Ceará - indice caprinos em 2024 = {idx_ce_caprino.loc[2024]:.1f} (2003=100)")
print(f"Ceará - indice ovinos em 2024 = {idx_ce_ovino.loc[2024]:.1f} (2003=100)")

# ---------------------------------------------------------------------------
# Visualizacao 2: dispersao PAM x PPM x PIB, ano de referencia 2021
# ---------------------------------------------------------------------------
ANO_REF = 2021
pam_qtd_mun = pam_qtd[pam_qtd["nivel_territorial_codigo"] == "N6"]
qtd_ano = pam_qtd_mun[pam_qtd_mun["ano_codigo"] == ANO_REF].groupby(
    ["territorio_codigo", "territorio_nome"])["valor"].sum().rename("qtd_produzida_t")

# Efetivo de UMA especie apenas (bovinos - maior peso economico na pecuaria
# cearense). Bovino, caprino, ovino, suino e galinaceo nao sao unidades
# equivalentes e nunca devem ser somados entre si (ver data/README_DADOS.md
# item 4-5 e notebooks/06_evolucao_pecuaria.py, que trata as 5 especies
# separadamente).
efetivo_ano = ppm_mun[(ppm_mun["ano_codigo"] == ANO_REF) & (ppm_mun["tipo_rebanho_codigo"] == "2670")].groupby(
    ["territorio_codigo", "territorio_nome"])["valor"].sum().rename("efetivo_bovino_cab")

pib_mun = pib[pib["nivel_territorial_codigo"] == "N6"]
pib_wide_ano = pib_mun[pib_mun["ano_codigo"] == ANO_REF].pivot_table(
    index=["territorio_codigo", "territorio_nome"], columns="variavel_codigo", values="valor"
).rename(columns={"37": "pib_mil_r", "498": "vab_total_mil_r", "513": "vab_agro_mil_r",
                   "516": "participacao_vab_agro_pct"})

viz2 = qtd_ano.to_frame().join(efetivo_ano, how="inner").join(pib_wide_ano, how="inner").reset_index()
print(f"\nVisualização 2 — municípios com PAM+PPM+PIB completos em {ANO_REF}: {len(viz2)} de 184")

fig2, ax2 = plt.subplots(figsize=(7.5, 5.5))
sizes = 15 + (viz2["participacao_vab_agro_pct"].clip(lower=0)) * 6
sc = ax2.scatter(viz2["qtd_produzida_t"] + 1, viz2["efetivo_bovino_cab"] + 1, s=sizes,
                  c=viz2["participacao_vab_agro_pct"], cmap="viridis", alpha=0.75, edgecolor="white", linewidth=0.3)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel("Quantidade produzida (PAM, t/ano, escala log) — 7 produtos, soma")
ax2.set_ylabel("Efetivo de bovinos (PPM, cabeças, escala log)")
ax2.set_title(f"Visualização 2 (preliminar) — PAM x PPM x PIB por município, {ANO_REF}")
cb = fig2.colorbar(sc, ax=ax2)
cb.set_label("Participação do VAB agropecuário no VAB total (%)")
fig2.tight_layout()
fig2.savefig("notebooks/fig_visualizacao2_dispersao.png", dpi=150)
print("Figura salva: notebooks/fig_visualizacao2_dispersao.png")

corr = viz2[["qtd_produzida_t", "efetivo_bovino_cab", "participacao_vab_agro_pct"]].corr(method="spearman")
print("\nCorrelação de Spearman (2021):")
print(corr)

top5 = viz2.sort_values("participacao_vab_agro_pct", ascending=False).head(5)[
    ["territorio_nome", "qtd_produzida_t", "efetivo_bovino_cab", "participacao_vab_agro_pct"]]
print("\nTop 5 municípios por participação do VAB agropecuário (2021):")
print(top5.to_string(index=False))
