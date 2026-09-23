"""Comparação territorial - Tema 2 (Agropecuária), recorte pecuária: efetivo dos
rebanhos por município do Ceará (SIDRA/PPM, tabela 3939, 2003-2024).

Integra a malha municipal do IBGE (GeoJSON, dado geográfico auxiliar - não
conta como uma das três tabelas SIDRA exigidas) à PPM pelo código IBGE de 7
dígitos (`codarea` na malha, `territorio_codigo` na PPM), e disponibiliza
ranking, distribuição e mapa para comparar os 184 municípios cearenses numa
espécie e ano selecionados.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from data import (
    ANO_FIM,
    ANO_INICIO,
    ESPECIES,
    load_malha,
    load_ppm,
    ppm_por_municipio,
    validar_codarea,
)

st.set_page_config(
    page_title="Comparação territorial | Pecuária no Ceará",
    page_icon="🗺️",
    layout="wide",
)


VERMELHO = "#E53935"
PALETA_VERMELHOS = ["#FDE0DD", "#FBB4B9", "#EF6C6C", "#E53935", "#7F0000"]
PLOT_LAYOUT = dict(template="plotly_white", font=dict(color="#111111"))


@st.cache_data
def _load_ppm() -> pd.DataFrame:
    return load_ppm()


@st.cache_data(hash_funcs={dict: id})
def _load_malha() -> dict:
    return load_malha()


ppm = _load_ppm()
malha = _load_malha()

# ---------------------------------------------------------------------------
# Título e mecanismo de comparação
# ---------------------------------------------------------------------------
st.title("Comparação territorial: efetivo pecuário por município")
st.markdown(
    "Ranking, distribuição e mapa comparam o efetivo do rebanho entre os "
    "**184 municípios do Ceará**, para uma espécie e um ano por vez "
    "(espécies distintas nunca são somadas - ver Visão geral). A malha "
    "municipal do IBGE é integrada à PPM pelo **código IBGE de 7 dígitos** "
    "(`codarea` na malha, `territorio_codigo` na PPM); o GeoJSON é um dado "
    "geográfico auxiliar e não substitui as tabelas SIDRA."
)

col_especie, col_ano = st.columns([1, 2])
with col_especie:
    especie = st.selectbox("Espécie", ESPECIES, index=0)
with col_ano:
    ano = st.slider("Ano", min_value=ANO_INICIO, max_value=ANO_FIM, value=ANO_FIM, step=1)

df = ppm_por_municipio(ppm, especie, ano)

# ---------------------------------------------------------------------------
# Validação da integração por código IBGE
# ---------------------------------------------------------------------------
with st.expander("Validação da integração geográfica (codarea ↔ território IBGE)", expanded=False):
    val = validar_codarea(malha, ppm)
    c1, c2, c3 = st.columns(3)
    c1.metric("Municípios na malha (GeoJSON)", val["n_malha"])
    c2.metric("Municípios na PPM (nível N6)", val["n_ppm"])
    c3.metric("Códigos correspondentes", val["correspondentes"])
    if val["somente_malha"] or val["somente_ppm"]:
        st.warning(
            f"Códigos presentes só na malha: {val['somente_malha']}. "
            f"Códigos presentes só na PPM: {val['somente_ppm']}."
        )
    else:
        st.success(
            "Todos os 184 códigos IBGE de 7 dígitos correspondem entre a malha e a "
            "PPM: junção 1:1, sem município perdido no mapa nem no cruzamento."
        )

if df.empty:
    st.info(f"Sem dados de {especie.lower()} para {ano}.")
    st.stop()

# ---------------------------------------------------------------------------
# Escala: classes por quantil (o efetivo é fortemente assimétrico entre
# municípios - poucos concentram valores muito altos - então uma escala
# linear deixaria quase todos os municípios na mesma cor). O rank(method=
# "first") evita erro do qcut quando há muitos municípios empatados (ex.:
# valor zero).
# ---------------------------------------------------------------------------
N_CLASSES = 5
ranks = df["efetivo_cab"].rank(method="first")
df["classe_idx"] = pd.qcut(ranks, q=N_CLASSES, labels=False) + 1
bordas = df.groupby("classe_idx")["efetivo_cab"].agg(["min", "max"])
rotulos_classe = {
    i: f"{i}: {int(row['min']):,} a {int(row['max']):,} cab.".replace(",", ".")
    for i, row in bordas.iterrows()
}
df["classe"] = df["classe_idx"].map(rotulos_classe)
ordem_classes = [rotulos_classe[i] for i in sorted(rotulos_classe)]

df["efetivo_fmt"] = df["efetivo_cab"].map(lambda v: f"{v:,}".replace(",", "."))

# ---------------------------------------------------------------------------
# Mapa coroplético
# ---------------------------------------------------------------------------
st.subheader(f"Mapa: {especie.lower()} por município, {ano}")
st.caption(
    "Escala por quantil (5 classes de igual número de municípios), não linear, "
    "porque poucos municípios concentram efetivos muito acima da maioria."
)

fig_map = px.choropleth(
    df,
    geojson=malha,
    locations="codigo_ibge",
    featureidkey="properties.codarea",
    color="classe",
    category_orders={"classe": ordem_classes},
    color_discrete_sequence=PALETA_VERMELHOS,
    custom_data=["municipio", "codigo_ibge", "efetivo_fmt", "ranking", "participacao_pct"],
)
fig_map.update_traces(
    marker_line_width=0.4,
    marker_line_color="white",
    hovertemplate=(
        "<b>%{customdata[0]}</b> (IBGE %{customdata[1]})<br>"
        f"Efetivo de {especie.lower()} em {ano}: " "%{customdata[2]} cab.<br>"
        "Posição no ranking estadual: %{customdata[3]}º de 184<br>"
        "Participação no total municipal do Ceará: %{customdata[4]}%"
        "<extra></extra>"
    ),
)
fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(**PLOT_LAYOUT, 
    margin=dict(l=0, r=0, t=10, b=0),
    legend_title_text="Efetivo (cab.) - classes por quantil",
)
st.plotly_chart(fig_map)

# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------
st.subheader("Ranking dos municípios")
top_n = st.slider("Municípios exibidos no ranking", min_value=5, max_value=50, value=15, step=5)
df_rank = df.head(top_n).sort_values("efetivo_cab")

fig_rank = px.bar(
    df_rank,
    x="efetivo_cab",
    y="municipio",
    orientation="h",
    custom_data=["codigo_ibge", "ranking", "participacao_pct"],
    labels={"efetivo_cab": f"Efetivo de {especie.lower()} (cab.)", "municipio": "Município"},
)
fig_rank.update_traces(
    marker_color=VERMELHO,
    hovertemplate=(
        "<b>%{y}</b> (IBGE %{customdata[0]})<br>"
        "Ranking: %{customdata[1]}º de 184<br>"
        "Efetivo: %{x:,} cab.<br>"
        "Participação no total municipal do Ceará: %{customdata[2]}%"
        "<extra></extra>"
    ),
)
fig_rank.update_layout(**PLOT_LAYOUT, margin=dict(l=0, r=0, t=10, b=0), height=max(320, top_n * 24))
st.plotly_chart(fig_rank)

with st.expander(f"Tabela completa - {len(df)} municípios, ordenada por efetivo"):
    st.dataframe(
        df[["ranking", "municipio", "codigo_ibge", "efetivo_cab", "participacao_pct"]],
        hide_index=True,
        column_config={
            "ranking": "Posição",
            "municipio": "Município",
            "codigo_ibge": "Código IBGE",
            "efetivo_cab": st.column_config.NumberColumn("Efetivo (cab.)", format="%d"),
            "participacao_pct": st.column_config.NumberColumn("Participação (%)", format="%.2f%%"),
        },
    )

# ---------------------------------------------------------------------------
# Distribuição
# ---------------------------------------------------------------------------
st.subheader("Distribuição entre os municípios")
escala_log = st.checkbox(
    "Escala logarítmica no eixo do efetivo (recomendado - a distribuição é assimétrica)",
    value=True,
)

fig_dist = px.histogram(
    df,
    x="efetivo_cab",
    nbins=30,
    labels={"efetivo_cab": f"Efetivo de {especie.lower()} (cab.)"},
)
fig_dist.update_traces(marker_color=VERMELHO)
if escala_log:
    fig_dist.update_xaxes(type="log")
mediana = df["efetivo_cab"].median()
fig_dist.add_vline(
    x=mediana,
    line_dash="dash",
    line_color="#111111",
    annotation_text=f"Mediana: {mediana:,.0f} cab.".replace(",", "."),
)
fig_dist.update_layout(**PLOT_LAYOUT, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Nº de municípios")
st.plotly_chart(fig_dist)

resumo = df["efetivo_cab"].describe(percentiles=[0.25, 0.5, 0.75, 0.9])
st.caption(
    f"184 municípios. Mínimo: {resumo['min']:,.0f} cab. · "
    f"P25: {resumo['25%']:,.0f} cab. · Mediana: {resumo['50%']:,.0f} cab. · "
    f"P75: {resumo['75%']:,.0f} cab. · P90: {resumo['90%']:,.0f} cab. · "
    f"Máximo: {resumo['max']:,.0f} cab.".replace(",", ".")
)

st.divider()
st.caption(
    "Fonte: IBGE/SIDRA, tabela 3939 (PPM). Malha municipal: IBGE, API de Malhas "
    "Geográficas v3, Ceará 2022 (dados/raw/malha_municipal_ce_2022.geojson) - "
    "dado geográfico auxiliar, não contabilizado entre as tabelas SIDRA integradas. "
    "Comparação limitada ao efetivo absoluto (cabeças); não normalizada por área ou "
    "população municipal, que estão fora do recorte de dados desta missão pessoal "
    "(PPM)."
)
