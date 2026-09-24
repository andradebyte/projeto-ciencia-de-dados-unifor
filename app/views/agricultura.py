"""Tela - Agricultura (PAM): sete culturas, cinco variáveis, séries independentes.

Produtos de culturas diferentes nunca são somados em área, quantidade ou
rendimento; cada cultura permanece em sua própria série. O valor monetário por
hectare usa exclusivamente o agregado estadual oficial do Ceará.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from comum import (
    CINZA,
    ESTADO,
    PLOT_LAYOUT,
    PRETO,
    VERMELHO,
    filtros_globais,
    fmt_dec,
    fmt_int,
    malha,
    pam,
    territorio_do_filtro,
)
from data import PRODUTOS, cultura_dominante, pam_matriz, producao_por_hectare
from insights import crescimento_cultura, frustracao_media_estado, lider_por_hectare, ranking_valor

METRICAS = {
    "valor_producao": ("Valor da produção", "Mil Reais", "valor da produção"),
    "area_plantada": ("Área plantada", "Hectares", "área plantada"),
    "area_colhida": ("Área colhida", "Hectares", "área colhida"),
    "quantidade": ("Quantidade produzida", "Toneladas", "quantidade produzida"),
    "rendimento": ("Rendimento médio", "kg/ha", "rendimento médio"),
}
CORES_PRODUTO = {
    "Milho (em grão)": "#E53935",
    "Feijão (em grão)": "#111111",
    "Mandioca": "#B71C1C",
    "Cana-de-açúcar": "#9E9E9E",
    "Banana (cacho)": "#EF6C6C",
    "Castanha de caju": "#7F0000",
    "Melão": "#FBB4B9",
}

municipio, ini, fim, _ = filtros_globais()
nivel, codigo = territorio_do_filtro(municipio)
dados = pam()

st.title("Agricultura — Produção Agrícola Municipal")
st.caption(
    f"Território: **{municipio}** · período {ini}–{fim}. Comparações sempre dentro da "
    "mesma cultura: áreas, quantidades e rendimentos de produtos distintos não são equivalentes."
)

if ini == fim:
    st.info("Escolha um intervalo com pelo menos dois anos na barra lateral para ver a evolução.")
    st.stop()

# ---------------------------------------------------------------------------
# Evolução por cultura (métrica selecionável)
# ---------------------------------------------------------------------------
metric_key = st.selectbox(
    "Variável da PAM",
    list(METRICAS),
    format_func=lambda k: METRICAS[k][0],
    key="pam_metrica",
)
rotulo, unidade, _ = METRICAS[metric_key]
matriz = pam_matriz(dados, nivel, codigo, metric_key, ini, fim).reindex(columns=PRODUTOS)
culturas = st.multiselect(
    "Culturas exibidas", PRODUTOS, default=PRODUTOS, key="pam_culturas"
)
exibidas = [c for c in PRODUTOS if c in culturas]

with st.container(border=True):
    st.markdown(f"**Evolução de {rotulo.lower()} por cultura — {municipio}**")
    if not exibidas:
        st.warning("Selecione ao menos uma cultura.")
    else:
        fig = go.Figure()
        for produto in exibidas:
            serie = matriz[produto]
            fig.add_trace(
                go.Scatter(
                    x=serie.index,
                    y=serie.values,
                    name=produto,
                    mode="lines+markers",
                    line=dict(color=CORES_PRODUTO[produto], width=2.4),
                    hovertemplate=f"<b>{produto}</b><br>%{{x}}: %{{y:,.2f}} {unidade}<extra></extra>",
                )
            )
        fig.update_layout(
            **PLOT_LAYOUT,
            height=380,
            xaxis_title="Ano",
            yaxis_title=f"{rotulo} ({unidade})",
            legend=dict(orientation="h", yanchor="bottom", y=1.0),
        )
        st.plotly_chart(fig)
        st.caption(
            "Valores nominais (Mil Reais) quando a variável é o valor da produção; sem deflação. "
            "Fonte: PAM 5457."
        )

# ---------------------------------------------------------------------------
# Síntese de achados (calculada)
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("**O que os dados mostram na agricultura**")
    cresc = crescimento_cultura(dados, "N3", "23", 2003, min(fim, 2024))
    rk = ranking_valor(dados, "N3", "23", 2003, min(fim, 2024))
    if not cresc.empty:
        topo, baixo = cresc.iloc[0], cresc.iloc[-1]
        st.markdown(
            f"- No Ceará, o valor da produção de **{topo['produto_nome']}** cresceu "
            f"**{topo['fator']:.1f}×** (2003→{min(fim, 2024)}), o maior avanço entre as culturas; "
            f"**{baixo['produto_nome']}** teve o menor ({baixo['fator']:.1f}×)."
        )
    if not rk.empty:
        subiu = rk[(rk["fim_pos"] < rk["ini_pos"])]
        if not subiu.empty:
            mudou = subiu.sort_values("fim_pos").iloc[0]
            st.markdown(
                f"- **{mudou['produto']}** foi de {int(mudou['ini_pos'])}º para "
                f"{int(mudou['fim_pos'])}º no ranking de valor da produção."
            )
    lider = lider_por_hectare(dados, min(fim, 2024))
    if lider:
        st.markdown(
            f"- Em {min(fim, 2024)}, **{lider['produto']}** lidera o valor bruto por hectare colhido "
            f"(R$ {fmt_dec(lider['valor'])}/ha), o que mede valor por área, não lucro."
        )
    frust = frustracao_media_estado(dados, 2003, min(fim, 2024))
    if frust is not None:
        st.markdown(
            f"- Frustração média de safra no estado: **{fmt_dec(frust, 3)}** "
            "(1 − área colhida / área plantada, só onde há plantio)."
        )

# ---------------------------------------------------------------------------
# Área plantada: valor absoluto x participação percentual
# ---------------------------------------------------------------------------
with st.container(border=True):
    modo = st.radio(
        "Área plantada",
        ["Valor absoluto (ha)", "Participação percentual (%)"],
        horizontal=True,
        key="pam_area_modo",
    )
    area = pam_matriz(dados, nivel, codigo, "area_plantada", ini, fim).reindex(columns=PRODUTOS)
    if modo.startswith("Participação"):
        total_ano = area.sum(axis=1, min_count=1)
        plot_data = area.div(total_ano, axis=0) * 100
        y_title = "Participação na área plantada (%)"
    else:
        plot_data = area
        y_title = "Área plantada (ha)"
    st.markdown(f"**Área plantada — {municipio}**")
    if not exibidas:
        st.warning("Selecione ao menos uma cultura acima.")
    else:
        fig_area = go.Figure()
        for produto in exibidas:
            fig_area.add_trace(
                go.Scatter(
                    x=plot_data.index,
                    y=plot_data[produto].values,
                    name=produto,
                    mode="lines+markers",
                    line=dict(color=CORES_PRODUTO[produto], width=2.4),
                    hovertemplate=f"<b>{produto}</b><br>%{{x}}: %{{y:,.2f}}<extra></extra>",
                )
            )
        fig_area.update_layout(
            **PLOT_LAYOUT, height=340, xaxis_title="Ano", yaxis_title=y_title,
            legend=dict(orientation="h", yanchor="bottom", y=1.0),
        )
        st.plotly_chart(fig_area)
        st.caption("Na participação, o denominador é a soma das sete culturas em cada ano.")

# ---------------------------------------------------------------------------
# Valor bruto da produção por hectare colhido (agregado estadual do Ceará)
# ---------------------------------------------------------------------------
st.subheader("Valor bruto da produção por hectare colhido no Ceará")
st.caption(
    "Recorte fixo: agregado estadual oficial do Ceará. "
    "Cálculo: valor da produção (mil reais) × 1.000 ÷ área colhida (hectares). "
    "Mede valor bruto por área, não lucro nem rendimento físico em kg/ha."
)
hectare = producao_por_hectare(dados)
hectare = hectare[hectare["produto_nome"].isin(exibidas)] if exibidas else hectare
with st.container(border=True):
    col_a, col_b = st.columns([1, 3])
    ano_ha = col_a.select_slider(
        "Ano (leitura)", options=sorted(hectare["ano_codigo"].unique()),
        value=max(hectare["ano_codigo"].unique()), key="pam_ano_ha",
    )
    if hectare["valor_por_ha_rs"].notna().sum() == 0:
        st.warning("Sem área colhida positiva para calcular o indicador.")
    else:
        fig_ha = go.Figure()
        for produto in exibidas:
            serie = hectare[hectare["produto_nome"] == produto].set_index("ano_codigo")
            fig_ha.add_trace(
                go.Scatter(
                    x=serie.index, y=serie["valor_por_ha_rs"], name=produto, mode="lines+markers",
                    line=dict(color=CORES_PRODUTO[produto], width=2.4),
                    customdata=serie[["area_colhida_ha", "valor_producao_rs"]].values,
                    hovertemplate=(
                        f"<b>{produto}</b><br>%{{x}}<br>Área colhida: %{{customdata[0]:,.0f}} ha"
                        "<br>Valor da produção: R$ %{customdata[1]:,.0f}"
                        "<br>Valor bruto: R$ %{y:,.0f}/ha<extra></extra>"
                    ),
                )
            )
        fig_ha.update_layout(
            **PLOT_LAYOUT, height=360, xaxis_title="Ano",
            yaxis_title="R$/ha colhido", legend=dict(orientation="h", yanchor="bottom", y=1.0),
        )
        st.plotly_chart(fig_ha)
        linha_ano = hectare[hectare["ano_codigo"] == ano_ha].dropna(subset=["valor_por_ha_rs"])
        if not linha_ano.empty:
            lider = linha_ano.sort_values("valor_por_ha_rs", ascending=False).iloc[0]
            st.caption(
                f"Em {ano_ha}, maior valor bruto por hectare entre as culturas exibidas: "
                f"**{lider['produto_nome']}** — R$ {fmt_dec(lider['valor_por_ha_rs'])}/ha."
            )
        st.caption("Valores correntes, sem correção pela inflação.")

# ---------------------------------------------------------------------------
# Área plantada x área colhida (diferença não é automaticamente "perda")
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("**Área plantada × área colhida**")
    cultura_gap = st.selectbox(
        "Cultura para comparar áreas",
        exibidas or PRODUTOS,
        index=(exibidas or PRODUTOS).index("Milho (em grão)") if "Milho (em grão)" in (exibidas or PRODUTOS) else 0,
        key="pam_cultura_gap",
    )
    plantada = pam_matriz(dados, nivel, codigo, "area_plantada", ini, fim).reindex(columns=PRODUTOS)[cultura_gap]
    colhida = pam_matriz(dados, nivel, codigo, "area_colhida", ini, fim).reindex(columns=PRODUTOS)[cultura_gap]
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Scatter(x=plantada.index, y=plantada.values, name="Área plantada",
                                 mode="lines", line=dict(color=PRETO, width=2.5)))
    fig_gap.add_trace(go.Scatter(x=colhida.index, y=colhida.values, name="Área colhida",
                                 mode="lines", line=dict(color=VERMELHO, width=2.5)))
    fig_gap.update_layout(**PLOT_LAYOUT, height=320, xaxis_title="Ano", yaxis_title="Hectares",
                          legend=dict(orientation="h", yanchor="bottom", y=1.0))
    st.plotly_chart(fig_gap)
    anos_disp = [int(a) for a in plantada.index]
    if not anos_disp:
        st.caption(f"{municipio} não registra área de {cultura_gap.lower()} no período escolhido.")
    else:
        ano_dif = st.select_slider(
            "Ano da diferença", options=anos_disp, value=max(anos_disp), key="pam_ano_dif"
        )
        p_ano, c_ano = plantada.loc[ano_dif], colhida.loc[ano_dif]
        col_dif, col_pct = st.columns(2)
        if pd.notna(p_ano) and pd.notna(c_ano):
            dif = p_ano - c_ano
            pct = (dif / p_ano * 100) if p_ano else None
            col_dif.metric(
                f"Área plantada não colhida — {ano_dif}",
                f"{fmt_int(dif)} ha",
                help="Área plantada menos área colhida no ano selecionado. Não é necessariamente perda.",
            )
            col_pct.metric("Diferença percentual", f"{fmt_dec(pct)}%" if pct is not None else "-")
        else:
            col_dif.metric(f"Área plantada não colhida — {ano_dif}", "-")
            col_pct.metric("Diferença percentual", "-")
            st.caption(f"{municipio} não registra área de {cultura_gap.lower()} em {ano_dif}.")
        periodizada = (plantada - colhida).dropna()
        if not periodizada.empty:
            pct_periodo = (periodizada.sum() / plantada.sum() * 100) if plantada.sum() else None
            st.caption(
                f"No período {ini}–{fim}: média de {fmt_int(periodizada.mean())} ha/ano não colhidos "
                + (f"({fmt_dec(pct_periodo)}% da área plantada somada no período). " if pct_periodo is not None else ". ")
                + "Em muitos anos o valor é zero porque toda a área plantada foi colhida — não é erro."
            )
    st.caption(
        "A diferença é 'área plantada que não se converteu em área colhida'. "
        "Não a chamamos de perda: a PAM não informa a causa."
    )

# ---------------------------------------------------------------------------
# Mapa: cultura dominante por município
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("**Cultura dominante por município**")
    ano_mapa = st.select_slider(
        "Ano do mapa", options=list(range(2003, 2025)), value=min(fim, 2024), key="pam_ano_mapa"
    )
    dom = cultura_dominante(dados, ano_mapa)
    sem_dado = int(dom["cultura_dominante"].isna().sum())
    mapa_geo = malha()
    fig_mapa = px.choropleth(
        dom,
        geojson=mapa_geo,
        locations="codigo_ibge",
        featureidkey="properties.codarea",
        color="cultura_dominante",
        color_discrete_map=CORES_PRODUTO,
        category_orders={"cultura_dominante": PRODUTOS},
        custom_data=["municipio", "cultura_dominante", "valor_dominante", "participacao_pct"],
    )
    fig_mapa.update_traces(
        marker_line_width=0.4, marker_line_color="white",
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>Cultura dominante: %{customdata[1]}"
            "<br>Valor da produção: R$ %{customdata[2]:,.0f} mil"
            "<br>Participação no valor analisado: %{customdata[3]:.1f}%<extra></extra>"
        ),
    )
    if municipio != ESTADO:
        cod_sel = dom.loc[dom["municipio"] == municipio, "codigo_ibge"]
        if not cod_sel.empty:
            fig_mapa.add_trace(
                go.Choropleth(
                    geojson=mapa_geo, locations=cod_sel, featureidkey="properties.codarea",
                    z=[1], colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                    showscale=False, showlegend=False,
                    marker_line_color=PRETO, marker_line_width=2.5, hoverinfo="skip",
                )
            )
    fig_mapa.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
    fig_mapa.update_layout(**PLOT_LAYOUT, height=520,
                           legend=dict(orientation="h", yanchor="top", y=0, title_text="Cultura dominante"))
    st.plotly_chart(fig_mapa)
    st.caption(
        f"Cultura de maior valor da produção em cada município, em {ano_mapa}. "
        f"{sem_dado} município(s) sem valor positivo aparecem sem cor. "
        "Malha municipal IBGE 2022, ligada por codarea."
    )

st.caption("Fonte: IBGE/SIDRA, tabela 5457 (PAM). Detalhes de tratamento na aba Fontes.")
