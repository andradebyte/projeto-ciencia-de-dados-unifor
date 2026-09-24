"""Tela - Economia municipal (PIB): PIB, VAB total e agropecuário e participação.

Valores a preços correntes, sem deflação. O PIB vai até 2023; o VAB total, o VAB
agropecuário e a participação só existem até 2021. Nenhuma leitura é causal.
"""

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from comum import (
    CINZA,
    ESTADO,
    PLOT_LAYOUT,
    PRETO,
    VERMELHO,
    filtros_globais,
    fmt_dec,
    fmt_int,
    municipios,
    pib,
    territorio_do_filtro,
)
from data import ANO_PIB_FIM, ANO_VAB_FIM, pib_por_municipio, pib_serie
from insights import desconcentracao_fortaleza, pib_estado

SGA = "São Gonçalo do Amarante"

municipio, ini, fim, _ = filtros_globais()
nivel, codigo = territorio_do_filtro(municipio)
fim_pib = min(fim, ANO_PIB_FIM)
ini_pib = min(ini, fim_pib)
dados = pib()

st.title("Economia municipal — PIB e valor adicionado bruto")
st.caption(
    f"Território: **{municipio}** · período {ini}–{fim}. PIB até {ANO_PIB_FIM}; "
    f"VAB total, VAB agropecuário e participação até {ANO_VAB_FIM}. Valores correntes, sem deflação."
)

# ---------------------------------------------------------------------------
# PIB do território selecionado
# ---------------------------------------------------------------------------
serie = pib_serie(dados, nivel, codigo, ini, fim_pib)
with st.container(border=True):
    st.markdown(f"**Produto Interno Bruto — {municipio}**")
    s = serie["pib"].dropna()
    if s.empty:
        st.warning("Sem PIB no período escolhido.")
    else:
        fig = go.Figure(
            go.Scatter(
                x=s.index, y=s.values, mode="lines+markers", name="PIB",
                line=dict(color=VERMELHO, width=3),
                hovertemplate="%{x}: R$ %{y:,.0f} mil<extra>PIB</extra>",
            )
        )
        fig.update_layout(**PLOT_LAYOUT, height=320, xaxis_title="Ano", yaxis_title="PIB (Mil Reais)")
        st.plotly_chart(fig)
        if ini in s.index and s.loc[ini]:
            st.caption(
                f"Variação nominal {ini}→{fim_pib}: "
                f"**{(s.loc[fim_pib] / s.loc[ini] - 1) * 100:+.1f}%** "
                f"({s.loc[fim_pib] / s.loc[ini]:.1f}×). Valores correntes."
            )

# ---------------------------------------------------------------------------
# Ceará × Brasil: absoluto ou índice base 2003
# ---------------------------------------------------------------------------
with st.container(border=True):
    modo = st.radio("Ceará × Brasil", ["Valor absoluto", "Índice (2003 = 100)"], horizontal=True, key="pib_modo")
    ce = pib_serie(dados, "N3", "23", ini_pib, fim_pib)["pib"].dropna()
    br = pib_serie(dados, "N1", "1", ini_pib, fim_pib)["pib"].dropna()
    titulo = "Índice (primeiro ano = 100)" if modo.startswith("Índice") else "PIB (Mil Reais)"
    if ce.empty and br.empty:
        st.info(f"Não há PIB no período selecionado (disponível até {ANO_PIB_FIM}).")
    else:
        fig_cmp = go.Figure()
        for nome, s, cor in [("Ceará", ce, VERMELHO), ("Brasil", br, PRETO)]:
            if s.empty:
                continue
            if modo.startswith("Índice"):
                base = s.loc[s.index.min()]
                y = s / base * 100 if base else s
            else:
                y = s
            fig_cmp.add_trace(
                go.Scatter(x=s.index, y=y, name=nome, mode="lines+markers",
                           line=dict(color=cor, width=2.6), hovertemplate=f"{nome} %{{x}}: %{{y:,.1f}}<extra></extra>")
            )
        fig_cmp.update_layout(**PLOT_LAYOUT, height=320, xaxis_title="Ano", yaxis_title=titulo,
                              legend=dict(orientation="h", yanchor="bottom", y=1.0))
        st.plotly_chart(fig_cmp)

# ---------------------------------------------------------------------------
# Maiores economias e quem mais cresceu
# ---------------------------------------------------------------------------
col_top, col_growth = st.columns(2)

with col_top:
    with st.container(border=True):
        st.markdown("**10 maiores PIB municipais**")
        if ini_pib < fim_pib:
            ano_top = st.slider("Ano do ranking", ini_pib, fim_pib, fim_pib, key="pib_ano_top")
        else:
            ano_top = fim_pib
            st.caption(f"Ano do ranking: {ano_top} (o período escolhido tem um único ano com PIB).")
        ranking = pib_por_municipio(dados, "pib", ano_top).dropna(subset=["pib"])
        top10 = ranking.nlargest(10, "pib").sort_values("pib")
        fig_top = go.Figure(
            go.Bar(
                x=top10["pib"], y=top10["municipio"], orientation="h",
                marker_color=[PRETO if m == municipio else VERMELHO for m in top10["municipio"]],
                customdata=top10[["municipio"]].values,
                hovertemplate="<b>%{customdata[0]}</b><br>PIB: R$ %{x:,.0f} mil<extra></extra>",
            )
        )
        fig_top.update_layout(**PLOT_LAYOUT, height=360, xaxis_title="PIB (Mil Reais)", yaxis_title="")
        st.plotly_chart(fig_top)
        st.caption(f"{len(ranking)} municípios com PIB em {ano_top}. Valores correntes.")

with col_growth:
    with st.container(border=True):
        st.markdown("**Municípios que mais cresceram**")
        c1, c2 = st.columns(2)
        a0 = c1.number_input("Ano inicial", min_value=2003, max_value=ANO_PIB_FIM - 1, value=2003, key="pib_cresc_ini")
        a1 = c2.number_input("Ano final", min_value=2004, max_value=ANO_PIB_FIM, value=ANO_PIB_FIM, key="pib_cresc_fim")
        if a1 <= a0:
            st.warning("O ano final precisa ser maior que o inicial.")
        else:
            p0 = pib_por_municipio(dados, "pib", a0).set_index("codigo_ibge")["pib"]
            p1 = pib_por_municipio(dados, "pib", a1).set_index("codigo_ibge")["pib"]
            nomes = pib_por_municipio(dados, "pib", a1).set_index("codigo_ibge")["municipio"]
            crescimento = ((p1 / p0).where((p0 > 0) & (p1 > 0))).dropna().sort_values(ascending=False)
            top5 = crescimento.head(10)
            fig_g = go.Figure(
                go.Bar(
                    x=top5.values, y=[nomes.get(c, c) for c in top5.index], orientation="h",
                    marker_color=VERMELHO,
                    hovertemplate="%{y}<br>%{x:.1f}× entre os anos escolhidos<extra></extra>",
                )
            )
            fig_g.update_layout(**PLOT_LAYOUT, height=360, xaxis_title="Fator de crescimento",
                                yaxis_title="", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_g)
            st.caption("Fator = PIB final / PIB inicial (nominal). Bases iniciais pequenas inflam o fator.")

# ---------------------------------------------------------------------------
# VAB total e agropecuário, participação e composição
# ---------------------------------------------------------------------------
if ini <= ANO_VAB_FIM:
    vab = pib_serie(dados, nivel, codigo, ini, ANO_VAB_FIM)
    col_vab, col_comp = st.columns([3, 2])
    with col_vab:
        with st.container(border=True):
            st.markdown(f"**Valor adicionado bruto — {municipio}**")
            fig_vab = go.Figure()
            for coluna, nome, cor in [("vab_total", "VAB total", PRETO), ("vab_agro", "VAB agropecuário", VERMELHO)]:
                s = vab[coluna].dropna()
                fig_vab.add_trace(
                    go.Scatter(x=s.index, y=s.values, name=nome, mode="lines+markers",
                               line=dict(color=cor, width=2.6),
                               hovertemplate=f"{nome} %{{x}}: R$ %{{y:,.0f}} mil<extra></extra>")
                )
            fig_vab.update_layout(**PLOT_LAYOUT, height=320, xaxis_title="Ano", yaxis_title="Mil Reais",
                                  legend=dict(orientation="h", yanchor="bottom", y=1.0))
            st.plotly_chart(fig_vab)
    with col_comp:
        with st.container(border=True):
            st.markdown("**Composição do VAB**")
            anos_vab = [a for a in vab["pct_vab_agro"].dropna().index]
            if not anos_vab:
                st.info("Sem VAB agropecuário no período escolhido.")
            else:
                ano_vab = st.select_slider("Ano", options=anos_vab, value=max(anos_vab), key="pib_ano_vab")
                linha = vab.loc[ano_vab]
                agro, total = linha["vab_agro"], linha["vab_total"]
                pct = linha["pct_vab_agro"]
                fig_comp = go.Figure(
                    go.Bar(
                        x=[pct, 100 - pct], y=["Composição"], orientation="h",
                        marker_color=[VERMELHO, CINZA], name="VAB",
                        hovertemplate="%{x:.2f}%<extra></extra>",
                    )
                )
                fig_comp.update_layout(**PLOT_LAYOUT, barmode="stack", height=250,
                                       xaxis=dict(title="Participação (%)", range=[0, 100]),
                                       showlegend=False)
                st.plotly_chart(fig_comp)
                st.caption(
                    f"{ano_vab}: agropecuária **{fmt_dec(pct)}%** "
                    f"(R$ {fmt_int(agro)} mil de R$ {fmt_int(total)} mil); demais atividades {fmt_dec(100 - pct)}%."
                )
else:
    st.info(
        f"O período escolhido ({ini}–{fim}) não inclui ano com valor adicionado bruto "
        f"(disponível até {ANO_VAB_FIM}). Ajuste o intervalo para ver VAB e participação."
    )

# ---------------------------------------------------------------------------
# Caso: São Gonçalo do Amarante
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f"**{SGA} — transformação econômica**")
    lista = municipios()
    cod_sga = lista.loc[lista["municipio"] == SGA, "codigo_ibge"]
    if cod_sga.empty:
        st.info("Município não encontrado na base.")
    else:
        sga = pib_serie(dados, "N6", cod_sga.iloc[0], 2003, fim_pib)
        s_pib = sga["pib"].dropna()
        fator = (s_pib.loc[fim_pib] / s_pib.loc[2003]) if 2003 in s_pib.index and s_pib.loc[2003] else None
        sga_vab = pib_serie(dados, "N6", cod_sga.iloc[0], 2003, ANO_VAB_FIM)
        pct0 = sga_vab["pct_vab_agro"].loc[2003] if 2003 in sga_vab.index else None
        pct1 = sga_vab["pct_vab_agro"].dropna()
        pct1 = pct1.loc[pct1.index.max()] if not pct1.empty else None
        c1, c2, c3 = st.columns(3)
        c1.metric("Crescimento do PIB", f"{fator:.1f}×" if fator else "-", help=f"2003→{fim_pib}, nominal")
        c2.metric("Participação agropecuária", f"{fmt_dec(pct0, 1)}% → {fmt_dec(pct1, 1)}%" if pct0 and pct1 else "-",
                  help=f"2003→{ANO_VAB_FIM}")
        c3.metric("VAB agropecuário (2021)", f"R$ {fmt_int(sga_vab['vab_agro'].dropna().iloc[-1])} mil"
                  if sga_vab["vab_agro"].notna().any() else "-")
        fig_sga = make_subplots(specs=[[{"secondary_y": True}]])
        fig_sga.add_trace(
            go.Scatter(x=s_pib.index, y=s_pib.values, name="PIB", mode="lines+markers",
                       line=dict(color=VERMELHO, width=3),
                       hovertemplate="%{x}: R$ %{y:,.0f} mil<extra>PIB</extra>"),
            secondary_y=False,
        )
        pct_serie = sga_vab["pct_vab_agro"].dropna()
        fig_sga.add_trace(
            go.Scatter(x=pct_serie.index, y=pct_serie.values, name="Participação agropecuária (%)",
                       mode="lines+markers", line=dict(color=PRETO, width=2, dash="dash"),
                       hovertemplate="%{x}: %{y:.2f}%<extra>Participação agro</extra>"),
            secondary_y=True,
        )
        fig_sga.update_yaxes(title_text="PIB (Mil Reais)", secondary_y=False, rangemode="tozero")
        fig_sga.update_yaxes(title_text="Participação agropecuária (%)", secondary_y=True, showgrid=False)
        fig_sga.update_layout(**PLOT_LAYOUT, height=340, xaxis_title="Ano",
                              legend=dict(orientation="h", yanchor="bottom", y=1.0))
        st.plotly_chart(fig_sga)
        st.caption(
            "O forte crescimento econômico de São Gonçalo do Amarante não acompanha aumento da "
            "participação da agropecuária. Contexto externo: resultado compatível com transformação "
            "industrial na região do Complexo do Pecém — as três bases não demonstram causalidade e "
            "não trazem participação industrial."
        )

st.caption("Fonte: IBGE/SIDRA, tabela 5938 (PIB dos Municípios). Detalhes na aba Fontes.")

with st.container(border=True):
    st.markdown("**O que os dados mostram na economia**")
    est = pib_estado(dados, 2003, ANO_PIB_FIM)
    if est:
        st.markdown(
            f"- O PIB do Ceará passou de R$ {fmt_int(est['ini'])} mil para R$ {fmt_int(est['fim'])} mil "
            f"(**{est['fator']}×**, 2003→{ANO_PIB_FIM}), em valores correntes."
        )
    desc = desconcentracao_fortaleza(dados, 2003, ANO_PIB_FIM)
    if desc:
        tendencia = "perdeu" if desc["fim"] < desc["ini"] else "ganhou"
        st.markdown(
            f"- Fortaleza {tendencia} participação relativa no PIB estadual: "
            f"**{desc['ini']}% → {desc['fim']}%**, indicando leve desconcentração."
        )
    st.markdown(
        f"- VAB agropecuário e participação só existem até {ANO_VAB_FIM}; por isso as médias e "
        "participações desta tela param nesse ano."
    )
    st.page_link("views/sinteses.py", label="Ver todas as sínteses", icon=":material/lightbulb:")
