"""
Primeiro cruzamento reproduzivel: PAM (5457) x PPM (3939) x PIB municipal (5938).

Chave de pareamento: territorio_codigo (codigo IBGE de 7 digitos), nivel N6
(municipio), nunca o nome do municipio. Trata os simbolos especiais do SIDRA
antes de qualquer conta, conforme data/README_DADOS.md:
  "-"   -> zero exato, nao resultante de arredondamento -> convertido para 0.0
  "0"   -> ja numerico (zero resultante de arredondamento) -> mantido
  "..." -> dado nao disponivel -> convertido para NaN (nunca para zero)
Nao ha ocorrencias de ".." ou "X" nestes arquivos (conferido linha a linha).
"""

import pandas as pd

pd.set_option("display.width", 120)

RAW = "data/dados_originais"

SIDRA_NA = {"...": pd.NA, "..": pd.NA, "X": pd.NA}  # nao disponivel / nao se aplica / sigiloso
SIDRA_ZERO = {"-": 0.0}  # zero exato, nao resultante de arredondamento


def read_sidra(path, extra_dtypes=None):
    dtypes = {"territorio_codigo": "string", "ano_codigo": "Int64", "nivel_territorial_codigo": "string"}
    if extra_dtypes:
        dtypes.update(extra_dtypes)
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=dtypes, keep_default_na=False)
    n_dash = (df["valor"] == "-").sum()
    n_dots = (df["valor"] == "...").sum()
    df["valor"] = df["valor"].replace(SIDRA_NA).replace(SIDRA_ZERO)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    return df, n_dash, n_dots


# ---------------------------------------------------------------------------
# 1. Carga das tres tabelas, apenas nivel N6 (municipios do Ceara)
# ---------------------------------------------------------------------------
pam_qtd, pam_qtd_dash, pam_qtd_dots = read_sidra(
    f"{RAW}/t5457_pam_quantidade_produzida_2003_2024_ce_br.csv", {"produto_codigo": "string"}
)
pam_plant, pam_plant_dash, _ = read_sidra(
    f"{RAW}/t5457_pam_area_plantada_2003_2024_ce_br.csv", {"produto_codigo": "string"}
)
pam_colh, pam_colh_dash, _ = read_sidra(
    f"{RAW}/t5457_pam_area_colhida_2003_2024_ce_br.csv", {"produto_codigo": "string"}
)
ppm, ppm_dash, ppm_dots = read_sidra(
    f"{RAW}/t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv", {"tipo_rebanho_codigo": "string"}
)
pib, pib_dash, pib_dots = read_sidra(
    f"{RAW}/t5938_pib_agropecuaria_2003_2023_ce_br.csv", {"variavel_codigo": "string"}
)

print("Simbolos tratados (contagem de celulas 'valor'):")
print(f"  PAM quantidade produzida : '-' -> 0  = {pam_qtd_dash}")
print(f"  PAM area plantada        : '-' -> 0  = {pam_plant_dash}")
print(f"  PAM area colhida         : '-' -> 0  = {pam_colh_dash}")
print(f"  PPM efetivo rebanhos     : '-' -> 0  = {ppm_dash}")
print(f"  PIB (37/498/513/516)     : '...' -> NaN = {pib_dots}")

pam_qtd_mun = pam_qtd[pam_qtd["nivel_territorial_codigo"] == "N6"].copy()
pam_plant_mun = pam_plant[pam_plant["nivel_territorial_codigo"] == "N6"].copy()
pam_colh_mun = pam_colh[pam_colh["nivel_territorial_codigo"] == "N6"].copy()
ppm_mun = ppm[ppm["nivel_territorial_codigo"] == "N6"].copy()
pib_mun = pib[pib["nivel_territorial_codigo"] == "N6"].copy()

# ---------------------------------------------------------------------------
# 2. Cardinalidade bruta: PAM/PPM sao "long" (varios produtos/rebanhos por
#    municipio-ano), PIB ja e uma linha por municipio-ano-variavel.
# ---------------------------------------------------------------------------
n_prod = pam_qtd_mun["produto_codigo"].nunique()
n_reb = ppm_mun["tipo_rebanho_codigo"].nunique()
n_var_pib = pib_mun["variavel_codigo"].nunique()
print(f"\nGranularidade bruta: PAM = {n_prod} produtos/municipio-ano; "
      f"PPM = {n_reb} rebanhos/municipio-ano; PIB = {n_var_pib} variaveis/municipio-ano")

pib_wide = pib_mun.pivot_table(
    index=["territorio_codigo", "territorio_nome", "ano_codigo"],
    columns="variavel_codigo", values="valor", aggfunc="first"
).rename(columns={"37": "pib_correntes_mil_r", "498": "vab_total_mil_r",
                   "513": "vab_agro_mil_r", "516": "participacao_vab_agro_pct"}).reset_index()

# checagem de cardinalidade raw PAM(long) -> PIB(wide) por municipio-ano
raw_check = pam_qtd_mun.merge(
    pib_wide[["territorio_codigo", "ano_codigo"]], on=["territorio_codigo", "ano_codigo"],
    how="inner", indicator=True
)
razao = raw_check.groupby(["territorio_codigo", "ano_codigo"]).size()
print(f"\nCardinalidade observada PAM(long) -> PIB(1 linha/municipio-ano): "
      f"min={razao.min()}, max={razao.max()}, moda={razao.mode().iloc[0]}  "
      f"(esperado N:1, N={n_prod})")

raw_check_ppm = ppm_mun.merge(
    pib_wide[["territorio_codigo", "ano_codigo"]], on=["territorio_codigo", "ano_codigo"],
    how="inner", indicator=True
)
razao_ppm = raw_check_ppm.groupby(["territorio_codigo", "ano_codigo"]).size()
print(f"Cardinalidade observada PPM(long) -> PIB(1 linha/municipio-ano): "
      f"min={razao_ppm.min()}, max={razao_ppm.max()}, moda={razao_ppm.mode().iloc[0]}  "
      f"(esperado N:1, N={n_reb})")

# ---------------------------------------------------------------------------
# 3. Agregacao a nivel municipio-ano (uma linha por municipio-ano em cada base)
# ---------------------------------------------------------------------------
pam_agg = pam_qtd_mun.groupby(["territorio_codigo", "territorio_nome", "ano_codigo"], as_index=False)[
    "valor"].sum().rename(columns={"valor": "qtd_produzida_total_t"})
plant_agg = pam_plant_mun.groupby(["territorio_codigo", "ano_codigo"], as_index=False)[
    "valor"].sum().rename(columns={"valor": "area_plantada_total_ha"})
colh_agg = pam_colh_mun.groupby(["territorio_codigo", "ano_codigo"], as_index=False)[
    "valor"].sum().rename(columns={"valor": "area_colhida_total_ha"})
pam_agg = pam_agg.merge(plant_agg, on=["territorio_codigo", "ano_codigo"], how="left")
pam_agg = pam_agg.merge(colh_agg, on=["territorio_codigo", "ano_codigo"], how="left")
pam_agg["taxa_frustracao_safra"] = 1 - (pam_agg["area_colhida_total_ha"] / pam_agg["area_plantada_total_ha"])

ppm_agg = ppm_mun.groupby(["territorio_codigo", "territorio_nome", "ano_codigo"], as_index=False)[
    "valor"].sum().rename(columns={"valor": "efetivo_total_cab"})
ppm_capr_ovi = ppm_mun[ppm_mun["tipo_rebanho_codigo"].isin(["2681", "2677"])].groupby(
    ["territorio_codigo", "ano_codigo"], as_index=False)["valor"].sum().rename(
    columns={"valor": "efetivo_caprino_ovino_cab"})
ppm_agg = ppm_agg.merge(ppm_capr_ovi, on=["territorio_codigo", "ano_codigo"], how="left")

# ---------------------------------------------------------------------------
# 4. Cruzamento final PAM_agg x PPM_agg x PIB_wide por codigo IBGE + ano
# ---------------------------------------------------------------------------
m1 = pam_agg.merge(ppm_agg[["territorio_codigo", "ano_codigo", "efetivo_total_cab",
                             "efetivo_caprino_ovino_cab"]],
                    on=["territorio_codigo", "ano_codigo"], how="outer", indicator="_m_pam_ppm")
final = m1.merge(pib_wide, on=["territorio_codigo", "ano_codigo"], how="outer", indicator="_m_com_pib")

print("\n--- Resultado do merge PAM_agg x PPM_agg (outer, por codigo+ano) ---")
print(m1["_m_pam_ppm"].value_counts())

print("\n--- Resultado do merge (PAM+PPM) x PIB (outer, por codigo+ano) ---")
print(final["_m_com_pib"].value_counts())

# municipios (nao pares codigo-ano) presentes em cada base
cod_pam = set(pam_agg["territorio_codigo"])
cod_ppm = set(ppm_agg["territorio_codigo"])
cod_pib = set(pib_wide["territorio_codigo"])
print(f"\nMunicipios distintos -> PAM={len(cod_pam)}  PPM={len(cod_ppm)}  PIB={len(cod_pib)}")
print(f"Interseccao PAM&PPM&PIB = {len(cod_pam & cod_ppm & cod_pib)}")
print(f"Em PAM mas nao em PIB = {sorted(cod_pam - cod_pib)}")
print(f"Em PIB mas nao em PAM = {sorted(cod_pib - cod_pam)}")

anos_pam = sorted(pam_agg["ano_codigo"].unique())
anos_pib = sorted(pib_wide["ano_codigo"].unique())
anos_vab_validos = sorted(pib_wide.loc[pib_wide["vab_agro_mil_r"].notna(), "ano_codigo"].unique())
print(f"\nAnos PAM/PPM: {anos_pam[0]}-{anos_pam[-1]} ({len(anos_pam)} anos)")
print(f"Anos PIB (var 37): {anos_pib[0]}-{anos_pib[-1]} ({len(anos_pib)} anos)")
print(f"Anos com VAB agropecuario/participacao validos (nao '...'): "
      f"{anos_vab_validos[0]}-{anos_vab_validos[-1]} ({len(anos_vab_validos)} anos)")

inter_full = final[(final["ano_codigo"] >= 2003) & (final["ano_codigo"] <= 2023) &
                    (final["_m_com_pib"] == "both")]
print(f"\nLinhas municipio-ano com PAM+PPM+PIB simultaneamente disponiveis (2003-2023): "
      f"{len(inter_full)} de {184*21} possiveis ({184*21 - len(inter_full)} faltantes)")
inter_vab = inter_full[inter_full["vab_agro_mil_r"].notna()]
print(f"Das quais com VAB agropecuario valido (2003-2021): {len(inter_vab)} linhas")

final.to_csv("data/cruzamento_pam_ppm_pib_municipio_ano.csv", sep=";", index=False, encoding="utf-8-sig")
print("\nArquivo de cruzamento salvo em data/cruzamento_pam_ppm_pib_municipio_ano.csv")
