"""Tela 2 - Evolução da pecuária: cinco séries independentes, nunca somadas."""

import plotly.graph_objects as go
import streamlit as st

from comum import (
    CINZA,
    PLOT_LAYOUT,
    PRETO,
    VERMELHO,
    filtros_globais,
    fmt_int,
    ppm,
    seletor_especie,
    territorio_do_filtro,
)
from data import ESPECIES, serie_por_especie

TRACOS = {"Bovinos": "solid", "Caprinos": "dash", "Ovinos": "dot", "Suínos": "dashdot", "Galináceos": "longdash"}

municipio, ini, fim, _ = filtros_globais()
nivel, codigo = territorio_do_filtro(municipio)
serie = serie_por_especie(ppm(), nivel, codigo, ini, fim)

st.title(f"Evolução da pecuária — {municipio}, {ini}–{fim}")
especie = seletor_especie("pills_especie_pecuaria")

if ini == fim:
    st.info("Escolha um intervalo com pelo menos dois anos na barra lateral para ver a evolução.")
    st.stop()

# ---------------------------------------------------------------------------
# Índice base = primeiro ano do intervalo
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f"**Índice do efetivo por espécie — {ini} = 100** · 5 séries independentes")
    fig_idx = go.Figure()
    for nome in ESPECIES:
        base = serie[nome].loc[ini]
        if not base:
            continue
        idx = serie[nome] / base * 100
        destaque = nome == especie
        fig_idx.add_trace(
            go.Scatter(
                x=idx.index,
                y=idx.values,
                name=nome,
                mode="lines",
                line=dict(
                    color=VERMELHO if destaque else PRETO,
                    width=4 if destaque else 1.5,
                    dash=TRACOS[nome],
                ),
                opacity=1 if destaque else 0.55,
                hovertemplate=f"<b>{nome}</b><br>%{{x}}: índice %{{y:.1f}}<extra></extra>",
            )
        )
    fig_idx.add_hline(y=100, line_color=CINZA, line_width=0.8)
    fig_idx.update_layout(**PLOT_LAYOUT, height=340, yaxis_title=f"Índice ({ini} = 100)", xaxis_title="Ano")
    st.plotly_chart(fig_idx)
    st.caption("As espécies NÃO são somadas — cada uma é uma série independente.")

col_log, col_leitura = st.columns([2, 1])

with col_log:
    with st.container(border=True):
        st.markdown("**Efetivo absoluto em escala log (mil cabeças)**")
        fig_log = go.Figure()
        for nome in ESPECIES:
            destaque = nome == especie
            fig_log.add_trace(
                go.Scatter(
                    x=serie.index,
                    y=serie[nome] / 1000,
                    name=nome,
                    mode="lines",
                    line=dict(
                        color=VERMELHO if destaque else PRETO,
                        width=3 if destaque else 1.2,
                        dash=TRACOS[nome],
                    ),
                    opacity=1 if destaque else 0.55,
                    hovertemplate=f"<b>{nome}</b><br>%{{x}}: %{{y:,.1f}} mil cab.<extra></extra>",
                )
            )
        fig_log.update_yaxes(
            type="log",
            title="Mil cabeças (log)",
            tickvals=[100, 300, 1000, 3000, 10000, 30000],
            ticktext=["100", "300", "1 mil", "3 mil", "10 mil", "30 mil"],
            minor=dict(showgrid=False),
        )
        fig_log.update_layout(**PLOT_LAYOUT, height=300, xaxis_title="Ano")
        st.plotly_chart(fig_log)
        st.caption("A escala log permite comparar ordens de grandeza sem somar espécies.")

with col_leitura:
    with st.container(border=True):
        st.markdown(f"**Leitura rápida — {especie.lower()}**")
        s = serie[especie].dropna()
        anos = fim - ini
        if s.empty or s.loc[ini] == 0:
            st.write(f"O efetivo de {especie.lower()} em {ini} é zero: não há base para variação.")
        else:
            var = (s.loc[fim] / s.loc[ini] - 1) * 100
            cagr = ((s.loc[fim] / s.loc[ini]) ** (1 / anos) - 1) * 100
            st.markdown(
                f"- {ini}: **{fmt_int(s.loc[ini])}** cab. → {fim}: **{fmt_int(s.loc[fim])}** cab.\n"
                f"- Variação no período: **{var:+.1f}%** (média de {cagr:+.1f}% ao ano)\n"
                f"- Maior efetivo: **{s.idxmax()}** ({fmt_int(s.max())} cab.)\n"
                f"- Menor efetivo: **{s.idxmin()}** ({fmt_int(s.min())} cab.)"
            )
        st.page_link("views/territorio.py", label="Comparar municípios →", icon=":material/map:")
