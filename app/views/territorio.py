"""Tela 3 - Comparação territorial: mapa, ranking e distribuição dos 184 municípios.

Integra a malha municipal do IBGE (GeoJSON, dado geográfico auxiliar - não conta
como uma das três tabelas SIDRA) à PPM pelo código IBGE de 7 dígitos (`codarea`
na malha, `territorio_codigo` na PPM). A métrica é o efetivo médio no período
escolhido nos filtros globais, de uma espécie por vez.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from comum import (
    ESTADO,
    PALETA_VERMELHOS,
    PLOT_LAYOUT,
    PRETO,
    VERMELHO,
    filtros_globais,
    fmt_int,
    malha,
    ppm,
    seletor_especie,
)
from data import ppm_por_municipio, validar_codarea

N_CLASSES = 5

municipio, ini, fim, _ = filtros_globais()
mapa_geo = malha()

st.title("Comparação territorial — 184 municípios")
especie = seletor_especie("pills_especie_territorio")
st.caption(
    f"Filtro herdado: {especie.lower()} · {ini}–{fim}. Métrica: efetivo médio no período (cabeças)."
)

df = ppm_por_municipio(ppm(), especie, ini, fim)

# Escala por quantil: o efetivo é fortemente assimétrico (poucos municípios com
# valores muito altos), então uma escala linear deixaria quase todos na mesma
# cor. rank(method="first") evita erro do qcut quando há muitos empates (zero).
ranks = df["efetivo_medio"].rank(method="first")
df["classe_idx"] = pd.qcut(ranks, q=N_CLASSES, labels=False) + 1
bordas = df.groupby("classe_idx")["efetivo_medio"].agg(["min", "max"])
rotulos = {
    i: f"{i}: {fmt_int(r['min'])} a {fmt_int(r['max'])} cab." for i, r in bordas.iterrows()
}
df["classe"] = df["classe_idx"].map(rotulos)
ordem_classes = [rotulos[i] for i in sorted(rotulos)]
df["medio_fmt"] = df["efetivo_medio"].map(fmt_int)
df["cresc_fmt"] = df["cresc_pct"].map(lambda v: "-" if pd.isna(v) else f"{v:+.1f}%")

if municipio != ESTADO:
    linha = df[df["municipio"] == municipio].iloc[0]
    st.info(
        f"Município selecionado: **{municipio}** — {linha['ranking']}º de {len(df)} em "
        f"{especie.lower()} (efetivo médio de {fmt_int(linha['efetivo_medio'])} cab.)."
    )

CUSTOM = ["municipio", "codigo_ibge", "medio_fmt", "ranking", "participacao_pct", "cresc_fmt"]
TOOLTIP = (
    "<b>%{customdata[0]}</b> (IBGE %{customdata[1]})<br>"
    f"Efetivo médio de {especie.lower()}, {ini}–{fim}: " "%{customdata[2]} cab.<br>"
    "Ranking: %{customdata[3]}º de 184<br>"
    "Participação no total municipal: %{customdata[4]}%<br>"
    f"Crescimento {ini}→{fim}: " "%{customdata[5]}<extra></extra>"
)

col_esq, col_dir = st.columns([3, 2])

# ---------------------------------------------------------------------------
# Painel esquerdo: Mapa | Ranking | Distribuição
# ---------------------------------------------------------------------------
with col_esq:
    visao = st.segmented_control(
        "Visualização", ["Mapa", "Ranking (barras)", "Distribuição"], default="Mapa", key="visao_territorio"
    ) or "Mapa"

    with st.container(border=True):
        if visao == "Mapa":
            st.markdown(f"**Mapa coroplético — efetivo médio de {especie.lower()}**")
            fig = px.choropleth(
                df,
                geojson=mapa_geo,
                locations="codigo_ibge",
                featureidkey="properties.codarea",
                color="classe",
                category_orders={"classe": ordem_classes},
                color_discrete_sequence=PALETA_VERMELHOS,
                custom_data=CUSTOM,
            )
            fig.update_traces(marker_line_width=0.4, marker_line_color="white", hovertemplate=TOOLTIP)
            if municipio != ESTADO:
                codigo_sel = linha["codigo_ibge"]
                fig.add_trace(
                    go.Choropleth(
                        geojson=mapa_geo,
                        locations=[codigo_sel],
                        featureidkey="properties.codarea",
                        z=[1],
                        colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                        showscale=False,
                        showlegend=False,
                        marker_line_color=PRETO,
                        marker_line_width=2.5,
                        hoverinfo="skip",
                    )
                )
            fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
            fig.update_layout(
                **PLOT_LAYOUT,
                height=560,
                legend=dict(orientation="h", yanchor="top", y=0, title_text="Efetivo médio (quantis)"),
            )
            st.plotly_chart(fig)
            st.caption(
                "Escala por quantil (5 classes com o mesmo número de municípios), não linear: "
                "poucos municípios concentram efetivos muito acima da maioria."
            )

        elif visao == "Ranking (barras)":
            top_n = st.slider("Municípios exibidos", 5, 50, 20, step=5)
            d = df.head(top_n).sort_values("efetivo_medio")
            fig = px.bar(
                d, x="efetivo_medio", y="municipio", orientation="h", custom_data=CUSTOM,
                labels={"efetivo_medio": f"Efetivo médio de {especie.lower()} (cab.)", "municipio": ""},
            )
            fig.update_traces(
                marker_color=[PRETO if m == municipio else VERMELHO for m in d["municipio"]],
                hovertemplate=TOOLTIP,
            )
            fig.update_layout(**PLOT_LAYOUT, height=max(360, top_n * 24))
            st.plotly_chart(fig)

        else:
            st.markdown(f"**Distribuição do efetivo médio de {especie.lower()} entre os municípios**")
            log = st.checkbox("Escala logarítmica (recomendada: distribuição assimétrica)", value=True)
            fig = px.histogram(
                df, x="efetivo_medio", nbins=30,
                labels={"efetivo_medio": f"Efetivo médio de {especie.lower()} (cab.)"},
            )
            fig.update_traces(marker_color=VERMELHO)
            if log:
                fig.update_xaxes(type="log")
            mediana = df["efetivo_medio"].median()
            fig.add_vline(
                x=mediana, line_dash="dash", line_color=PRETO,
                annotation_text=f"Mediana: {fmt_int(mediana)} cab.",
            )
            fig.update_layout(**PLOT_LAYOUT, height=420, yaxis_title="Nº de municípios")
            st.plotly_chart(fig)
            r = df["efetivo_medio"].describe(percentiles=[0.25, 0.5, 0.75, 0.9])
            st.caption(
                f"184 municípios · mínimo {fmt_int(r['min'])} · P25 {fmt_int(r['25%'])} · "
                f"mediana {fmt_int(r['50%'])} · P75 {fmt_int(r['75%'])} · P90 {fmt_int(r['90%'])} · "
                f"máximo {fmt_int(r['max'])} (cab.)"
            )

# ---------------------------------------------------------------------------
# Painel direito: municípios de destaque (linhas clicáveis) + top 10
# ---------------------------------------------------------------------------
destaque = df.head(5)


def _selecionar_municipio() -> None:
    linhas = st.session_state["tabela_destaques"].selection.rows
    if linhas:
        st.session_state["filtro_municipio"] = destaque.iloc[linhas[0]]["municipio"]


with col_dir:
    with st.container(border=True):
        st.markdown("**Municípios de destaque** · clique numa linha para filtrar")
        st.dataframe(
            destaque[["ranking", "municipio", "efetivo_medio", "cresc_pct"]],
            hide_index=True,
            key="tabela_destaques",
            on_select=_selecionar_municipio,
            selection_mode="single-row",
            column_config={
                "ranking": st.column_config.NumberColumn("#", width=40),
                "municipio": st.column_config.TextColumn("Município", width="small"),
                "efetivo_medio": st.column_config.NumberColumn("Média", format="localized", width="small"),
                "cresc_pct": st.column_config.NumberColumn("Cresc.", format="%+.1f%%", width="small", help=f"Crescimento do efetivo {ini}→{fim}"),
            },
        )
    with st.container(border=True):
        st.markdown("**Ranking top 10 — barras**")
        d10 = df.head(10).sort_values("efetivo_medio")
        fig10 = px.bar(d10, x="efetivo_medio", y="municipio", orientation="h", custom_data=CUSTOM,
                       labels={"efetivo_medio": "Efetivo médio (cab.)", "municipio": ""})
        fig10.update_traces(
            marker_color=[PRETO if m == municipio else VERMELHO for m in d10["municipio"]],
            hovertemplate=TOOLTIP,
        )
        fig10.update_layout(**PLOT_LAYOUT, height=340)
        st.plotly_chart(fig10)

# ---------------------------------------------------------------------------
# Validação da integração e tabela completa
# ---------------------------------------------------------------------------
with st.expander("Validação da integração geográfica (codarea ↔ território IBGE)"):
    val = validar_codarea(mapa_geo, ppm())
    c1, c2, c3 = st.columns(3)
    c1.metric("Municípios na malha (GeoJSON)", val["n_malha"])
    c2.metric("Municípios na PPM (N6)", val["n_ppm"])
    c3.metric("Códigos correspondentes", val["correspondentes"])
    if val["somente_malha"] or val["somente_ppm"]:
        st.warning(
            f"Só na malha: {val['somente_malha']}. Só na PPM: {val['somente_ppm']}."
        )
    else:
        st.success(
            "Todos os 184 códigos IBGE de 7 dígitos correspondem entre a malha e a PPM: "
            "junção 1:1, sem município perdido no mapa."
        )

with st.expander("Tabela completa dos 184 municípios"):
    st.dataframe(
        df[["ranking", "municipio", "codigo_ibge", "efetivo_medio", "cresc_pct", "participacao_pct"]],
        hide_index=True,
        column_config={
            "ranking": "Posição",
            "municipio": "Município",
            "codigo_ibge": "Código IBGE",
            "efetivo_medio": st.column_config.NumberColumn("Efetivo médio (cab.)", format="localized"),
            "cresc_pct": st.column_config.NumberColumn(f"Cresc. {ini}→{fim}", format="%+.1f%%"),
            "participacao_pct": st.column_config.NumberColumn("Participação (%)", format="%.2f%%"),
        },
    )

st.caption(
    "Fonte: IBGE/SIDRA, tabela 3939 (PPM). Malha: IBGE, API de Malhas v3, Ceará 2022 "
    "(data/raw/malha_municipal_ce_2022.geojson), dado auxiliar fora das três tabelas SIDRA. "
    "Comparação em efetivo absoluto, sem normalização por área ou população."
)
