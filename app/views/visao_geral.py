"""Tela 1 - Visão geral: contexto, KPIs (PPM, PAM e PIB) e atalhos para as demais telas."""

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from comum import (
    PLOT_LAYOUT,
    PRETO,
    VERMELHO,
    filtros_globais,
    fmt_dec,
    fmt_int,
    pam,
    pib,
    ppm,
    territorio_do_filtro,
)
from data import (
    ANO_PIB_FIM,
    ANO_VAB_FIM,
    ESPECIES,
    n_municipios,
    pam_serie,
    pib_serie,
    serie_por_especie,
)
from insights import (
    crescimento_especie,
    desconcentracao_fortaleza,
    lider_por_hectare,
    pib_estado,
    sga_caso,
)

dados = ppm()
municipio, ini, fim, produto = filtros_globais()
nivel, codigo = territorio_do_filtro(municipio)
serie = serie_por_especie(dados, nivel, codigo, ini, fim)
agro = pam_serie(pam(), nivel, codigo, produto, ini, fim)
vab_fim = min(fim, ANO_VAB_FIM)
economia = pib_serie(pib(), nivel, codigo, ini, vab_fim) if ini <= vab_fim else None

st.title("Agropecuária e transformação econômica no Ceará")
st.markdown(
    "**Problema.** Como a produção agrícola e os efetivos pecuários se transformaram nos "
    "municípios do Ceará entre 2003 e 2024, e como isso se relaciona com a estrutura "
    "econômica municipal nos anos em que as bases têm período comum? O painel integra "
    "PAM (5457), PPM (3939) e PIB municipal (5938) pelo código IBGE do município."
)

# ---------------------------------------------------------------------------
# KPIs do wireframe: cada um com unidade, período e território explícitos
# ---------------------------------------------------------------------------
st.caption(
    f"Território: **{municipio}** · período {ini}–{fim} · produto PAM: **{produto}**. "
    "Cada indicador informa unidade, período e fonte no ícone de ajuda."
)
k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Municípios cobertos",
    n_municipios(dados),
    help="Municípios do Ceará (N6) presentes nas três bases, chave: código IBGE de 7 dígitos.",
)

bovinos = serie["Bovinos"].dropna()
if bovinos.empty or ini == fim or bovinos.loc[ini] == 0:
    k2.metric(f"Efetivo bovino {ini}→{fim}", fmt_int(bovinos.loc[fim]), delta="sem base", delta_color="off")
else:
    k2.metric(
        f"Efetivo bovino {ini}→{fim}",
        fmt_int(bovinos.loc[fim]),
        delta=f"{(bovinos.loc[fim] / bovinos.loc[ini] - 1) * 100:+.1f}% vs {ini}",
        delta_color="off",
        help=f"Cabeças em 31/12 de {fim}, {municipio}. Variação percentual desde {ini}. Fonte: PPM 3939.",
    )

frustracao = agro["frustracao"].dropna()
k3.metric(
    "Frustração média de safra",
    fmt_dec(frustracao.mean()) if not frustracao.empty else "-",
    delta=produto if not frustracao.empty else "sem área plantada",
    delta_color="off",
    help=(
        "Frustração = 1 − área colhida / área plantada (razão de 0 a 1), calculada só onde a "
        f"área plantada é positiva. Média dos anos {ini}–{fim}, {municipio}, {produto}. Fonte: PAM 5457."
    ),
)

if economia is not None and economia["pct_vab_agro"].notna().any():
    anos_vab = economia["pct_vab_agro"].dropna().index
    k4.metric(
        "VAB agro / VAB total (méd.)",
        f"{fmt_dec(economia['pct_vab_agro'].mean(), 1)}%",
        delta=f"média {anos_vab.min()}–{anos_vab.max()}",
        delta_color="off",
        help=(
            "Participação do VAB agropecuário no VAB total (%), preços correntes. Disponível "
            f"apenas até {ANO_VAB_FIM}; a média usa só os anos do período com dado. Fonte: PIB 5938."
        ),
    )
else:
    k4.metric(
        "VAB agro / VAB total (méd.)",
        "-",
        delta=f"VAB só até {ANO_VAB_FIM}",
        delta_color="off",
        help="O período escolhido não tem anos com VAB agropecuário (disponível até 2021).",
    )

# Efetivo por espécie (séries independentes)
st.caption(
    f"Efetivo por espécie em {fim} (cabeças) e variação desde {ini}. Cada cartão é uma "
    "espécie independente, sem soma entre elas. Fonte: PPM 3939."
)
for coluna, especie in zip(st.columns(len(ESPECIES)), ESPECIES):
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
        help=f"Unidade: cabeças (31/12). Território: {municipio}. Não comparável a outras espécies.",
    )

# ---------------------------------------------------------------------------
# Síntese de achados (calculada)
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown("**O que os dados mostram**")
    achados = []
    est = pib_estado(pib(), 2003, ANO_PIB_FIM)
    if est:
        achados.append(f"A economia do Ceará cresceu **{est['fator']}×** no PIB nominal (2003→{ANO_PIB_FIM}).")
    desc = desconcentracao_fortaleza(pib(), 2003, ANO_PIB_FIM)
    if desc and desc["fim"] < desc["ini"]:
        achados.append(f"Fortaleza perdeu participação relativa no PIB estadual: **{desc['ini']}% → {desc['fim']}%**.")
    calc = sga_caso(pib(), 2003, ANO_PIB_FIM, ANO_VAB_FIM)
    if calc and calc["fator"] and calc["pct_fim"] is not None and calc["pct_ini"] is not None and calc["pct_fim"] < calc["pct_ini"]:
        achados.append(
            f"São Gonçalo do Amarante cresceu **{calc['fator']}×** enquanto sua participação agropecuária caiu "
            f"de {calc['pct_ini']}% para {calc['pct_fim']}%."
        )
    lider = lider_por_hectare(pam(), 2024)
    if lider:
        achados.append(f"Em 2024, **{lider['produto']}** teve o maior valor bruto por hectare colhido no estado.")
    cresc_esp = crescimento_especie(ppm(), "N3", "23", 2003, 2024)
    if not cresc_esp.empty:
        achados.append(f"Na pecuária, **{cresc_esp.iloc[0]['especie']}** teve o maior crescimento relativo ({cresc_esp.iloc[0]['fator']:.2f}×).")
    for linha in achados:
        st.markdown(f"- {linha}")
    st.page_link("views/sinteses.py", label="Ver todas as sínteses", icon=":material/lightbulb:")

# ---------------------------------------------------------------------------
# Resumo (PAM) + atalhos
# ---------------------------------------------------------------------------
col_resumo, col_atalhos = st.columns([3, 2])
with col_resumo:
    with st.container(border=True):
        st.markdown(f"**Resumo: produção de {produto.lower()}, {municipio}, {ini}–{fim}**")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=agro.index,
                y=agro["quantidade"],
                name="Quantidade produzida (t)",
                mode="lines",
                line=dict(color=VERMELHO, width=3),
                hovertemplate="%{x}: %{y:,.0f} t<extra>Quantidade produzida</extra>",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=agro.index,
                y=agro["area_colhida"],
                name="Área colhida (ha)",
                mode="lines",
                line=dict(color=PRETO, width=2, dash="dash"),
                hovertemplate="%{x}: %{y:,.0f} ha<extra>Área colhida</extra>",
            ),
            secondary_y=True,
        )
        fig.update_yaxes(title_text="Toneladas", secondary_y=False, rangemode="tozero")
        fig.update_yaxes(title_text="Hectares", secondary_y=True, rangemode="tozero", showgrid=False)
        fig.update_layout(
            **PLOT_LAYOUT,
            height=280,
            xaxis_title="Ano",
            legend=dict(orientation="h", yanchor="bottom", y=1.0),
        )
        st.plotly_chart(fig)
        if agro["quantidade"].fillna(0).sum() == 0:
            st.caption(f"{municipio} não registra produção de {produto.lower()} no período.")

with col_atalhos:
    with st.container(border=True):
        st.markdown("**Ver agricultura (PAM) →**")
        st.caption("Sete culturas, área plantada × colhida e valor bruto por hectare")
        st.page_link("views/agricultura.py", label="Abrir tela Agricultura", icon=":material/agriculture:")
    with st.container(border=True):
        st.markdown("**Ver economia municipal (PIB) →**")
        st.caption("PIB, VAB agropecuário, participação e maiores economias")
        st.page_link("views/economia.py", label="Abrir tela Economia", icon=":material/trending_up:")
    with st.container(border=True):
        st.markdown("**Ver evolução da pecuária →**")
        st.caption("5 espécies, índice base = primeiro ano do intervalo, séries independentes")
        st.page_link("views/pecuaria.py", label="Abrir tela Pecuária", icon=":material/show_chart:")
    with st.container(border=True):
        st.markdown("**Ver comparação entre municípios →**")
        st.caption("Mapa coroplético, ranking e distribuição por espécie")
        st.page_link("views/territorio.py", label="Abrir tela Território", icon=":material/map:")
    with st.container(border=True):
        st.markdown("**Ver cruzamento entre bases →**")
        st.caption("PAM × PPM × PIB por código IBGE do município")
        st.page_link("views/cruzamento.py", label="Abrir tela Cruzamento", icon=":material/scatter_plot:")

with st.expander("Recorte dos dados e instruções de uso"):
    st.markdown(
        "- **Fontes:** IBGE/SIDRA, tabelas 5457 (PAM), 3939 (PPM) e 5938 (PIB municipal), "
        "arquivos estáticos fornecidos pelo professor e tratados em `dados/processed`.\n"
        f"- **Território:** Ceará e {n_municipios(dados)} municípios (chave: código IBGE de 7 dígitos).\n"
        "- **Período:** 2003–2024 (PAM e PPM); PIB até 2023 e VAB agropecuário até 2021.\n"
        "- **Uso:** escolha município, período e produto na barra lateral; compare sempre "
        "dentro de uma mesma espécie ou produto, pois unidades diferentes não são equivalentes."
    )

st.caption("Fontes: SIDRA 5457 (PAM) · 3939 (PPM) · 5938 (PIB municipal) — detalhes na aba 5 Fontes.")
