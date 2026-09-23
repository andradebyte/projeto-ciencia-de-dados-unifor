"""Tela 1 - Visão geral: contexto, KPIs e atalhos para as demais telas."""

import plotly.graph_objects as go
import streamlit as st

from comum import (
    PLOT_LAYOUT,
    VERMELHO,
    filtros_globais,
    fmt_int,
    ppm,
    territorio_do_filtro,
)
from data import ESPECIES, n_municipios, serie_por_especie

dados = ppm()
municipio, ini, fim = filtros_globais()
nivel, codigo = territorio_do_filtro(municipio)
serie = serie_por_especie(dados, nivel, codigo, ini, fim)

st.title("Agropecuária e transformação econômica no Ceará")
st.markdown(
    "**Problema.** Como os efetivos de bovinos, caprinos, ovinos, suínos e galináceos "
    "se transformaram nos municípios do Ceará entre 2003 e 2024, e quais municípios "
    "concentram cada espécie? A pecuária é o recorte desta versão do painel, dentro da "
    "missão *Agropecuária e transformação econômica* do Projeto 1."
)

# ---------------------------------------------------------------------------
# KPIs: um por espécie, com unidade, período e território explícitos
# ---------------------------------------------------------------------------
st.caption(
    f"Território: **{municipio}** ({n_municipios(dados)} municípios cobertos no Ceará) · efetivo em "
    f"{fim} (cabeças) e variação percentual desde {ini}. Cada cartão é uma espécie "
    "independente, sem soma entre elas."
)
colunas = st.columns(len(ESPECIES))
for coluna, especie in zip(colunas, ESPECIES):
    s = serie[especie].dropna()
    if s.empty or ini == fim or s.loc[ini] == 0:
        variacao = "sem base de comparação"
    else:
        variacao = f"{(s.loc[fim] / s.loc[ini] - 1) * 100:+.1f}% vs {ini}"
    coluna.metric(
        f"{especie} {ini}→{fim}",
        fmt_int(s.loc[fim]) if fim in s.index else "-",
        delta=variacao,
        delta_color="off",
        help=(
            f"Unidade: cabeças (31/12). Território: {municipio}. Fonte: SIDRA/PPM 3939. "
            "Não comparável a outras espécies."
        ),
    )

# ---------------------------------------------------------------------------
# Resumo + atalhos
# ---------------------------------------------------------------------------
col_resumo, col_atalhos = st.columns([3, 2])
with col_resumo:
    with st.container(border=True):
        st.markdown(f"**Resumo: efetivo de bovinos, {municipio}, {ini}–{fim}**")
        fig = go.Figure(
            go.Scatter(
                x=serie.index,
                y=serie["Bovinos"],
                mode="lines",
                line=dict(color=VERMELHO, width=3),
                hovertemplate="%{x}: %{y:,.0f} cab.<extra></extra>",
            )
        )
        fig.update_layout(**PLOT_LAYOUT, height=260, yaxis_title="Cabeças", xaxis_title="Ano")
        st.plotly_chart(fig)

with col_atalhos:
    with st.container(border=True):
        st.markdown("**Ver evolução da pecuária →**")
        st.caption("5 espécies, índice base = primeiro ano do intervalo, séries independentes")
        st.page_link("views/pecuaria.py", label="Abrir tela Pecuária", icon=":material/show_chart:")
    with st.container(border=True):
        st.markdown("**Ver comparação entre municípios →**")
        st.caption("Mapa coroplético, ranking e distribuição por espécie")
        st.page_link("views/territorio.py", label="Abrir tela Território", icon=":material/map:")

with st.expander("Recorte dos dados e instruções de uso"):
    st.markdown(
        f"- **Fonte:** IBGE/SIDRA, tabela 3939 (PPM), arquivo estático fornecido pelo professor.\n"
        f"- **Território:** Ceará e {n_municipios(dados)} municípios (chave: código IBGE de 7 dígitos).\n"
        "- **Período:** 2003-2024, série anual. **Unidade:** cabeças no dia 31/12.\n"
        "- **Uso:** escolha município e período na barra lateral; compare sempre dentro de "
        "uma mesma espécie, pois espécies diferentes não são unidades equivalentes."
    )

st.caption("Fontes: SIDRA 3939 (PPM) · detalhes na aba 4 Fontes.")
