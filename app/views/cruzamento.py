"""Tela 4 - Cruzamento entre bases (PAM x PPM x PIB), integradas pelo código IBGE.

Associações exploratórias: nenhuma leitura aqui é causal. Espécies nunca são
somadas; cada uma aparece em série própria.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from comum import (
    CINZA,
    ESTADO,
    PALETA_VERMELHOS,
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
from data import ANO_VAB_FIM, cruzamento_municipal, pam_serie, serie_por_especie
from insights import correlacao_banana_vab_por_ano, quadro_municipal, spearman, spearman_series

municipio, ini, fim, produto = filtros_globais()
nivel, codigo = territorio_do_filtro(municipio)

st.title("Cruzamento entre bases — PAM × PPM × PIB")
st.caption(
    f"Filtro herdado: {municipio} · produto {produto} · período {ini}–{fim}. "
    "Junção pelo código IBGE de 7 dígitos, nunca pelo nome."
)
with st.container(border=True):
    st.markdown(
        "**Nota fixa:** PAM e PPM vão até 2024, o cruzamento com o PIB até 2023 e o VAB "
        f"agropecuário só até {ANO_VAB_FIM}; os períodos não coincidem totalmente. "
        "Os gráficos abaixo mostram associações exploratórias, não relações causais."
    )

# ---------------------------------------------------------------------------
# Evidência 1: dispersão produção agrícola x efetivo bovino, cor/tamanho = VAB agro
# ---------------------------------------------------------------------------
ano_max = min(fim, ANO_VAB_FIM)
col_disp, col_frust = st.columns(2)

with col_disp:
    with st.container(border=True):
        if ano_max < ini:
            st.markdown("**Dispersão produção × efetivo bovino**")
            st.warning(
                f"O período escolhido ({ini}–{fim}) não inclui nenhum ano com VAB agropecuário "
                f"(até {ANO_VAB_FIM}). Ajuste o intervalo na barra lateral."
            )
        else:
            ano = ano_max if ini == ano_max else st.slider("Ano do corte", ini, ano_max, ano_max, key="ano_corte")
            base, diag = cruzamento_municipal(ppm(), pam(), pib(), produto, ano)
            pontos = base[
                (base["quantidade_t"] > 0) & (base["efetivo_bovinos"] > 0) & base["pct_vab_agro"].notna()
            ].copy()
            pontos["tamanho"] = pontos["pct_vab_agro"].clip(lower=1)
            pontos["qtd_fmt"] = pontos["quantidade_t"].map(fmt_int)
            pontos["bov_fmt"] = pontos["efetivo_bovinos"].map(fmt_int)
            pontos["vab_fmt"] = pontos["pct_vab_agro"].map(lambda v: fmt_dec(v, 1))

            st.markdown(f"**Dispersão — {produto.lower()} (PAM, log) × efetivo bovino (PPM, log) · {ano}**")
            if len(pontos) < 3:
                st.warning(f"Apenas {len(pontos)} município(s) com produção de {produto.lower()} em {ano}.")
            else:
                fig = px.scatter(
                    pontos,
                    x="quantidade_t",
                    y="efetivo_bovinos",
                    size="tamanho",
                    color="pct_vab_agro",
                    color_continuous_scale=PALETA_VERMELHOS,
                    size_max=22,
                    log_x=True,
                    log_y=True,
                    custom_data=["municipio", "codigo_ibge", "qtd_fmt", "bov_fmt", "vab_fmt"],
                    labels={
                        "quantidade_t": f"Quantidade produzida de {produto.lower()} (t, log)",
                        "efetivo_bovinos": "Efetivo bovino (cab., log)",
                        "pct_vab_agro": "VAB agro (%)",
                    },
                )
                fig.update_traces(
                    marker=dict(line=dict(width=0.5, color="white")),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b> (IBGE %{customdata[1]})<br>"
                        f"Produção de {produto.lower()}: " "%{customdata[2]} t<br>"
                        "Efetivo bovino: %{customdata[3]} cab.<br>"
                        "VAB agro / VAB total: %{customdata[4]}%<extra></extra>"
                    ),
                )
                if municipio != ESTADO and municipio in set(pontos["municipio"]):
                    sel = pontos[pontos["municipio"] == municipio]
                    fig.add_trace(
                        go.Scatter(
                            x=sel["quantidade_t"],
                            y=sel["efetivo_bovinos"],
                            mode="markers",
                            marker=dict(size=30, color="rgba(0,0,0,0)", line=dict(width=3, color=PRETO)),
                            name=municipio,
                            hoverinfo="skip",
                        )
                    )
                ticks = dict(tickvals=[10, 100, 1000, 10000, 100000], ticktext=["10", "100", "1 mil", "10 mil", "100 mil"], minor=dict(showgrid=False))
                fig.update_xaxes(**ticks)
                fig.update_yaxes(**ticks)
                fig.update_layout(**PLOT_LAYOUT, height=420, coloraxis_colorbar=dict(title="VAB agro (%)"))
                st.plotly_chart(fig)

                rho = spearman_series(pontos["quantidade_t"], pontos["efetivo_bovinos"])
                st.caption(
                    f"{len(pontos)} de {diag['n_uniao']} municípios plotados; os demais não têm produção "
                    f"positiva de {produto.lower()} ({diag['sem_producao']}) ou VAB no ano "
                    f"({diag['sem_vab']}). Tamanho e tom do ponto = participação do VAB agropecuário (%). "
                    "Contorno preto = município filtrado. "
                    f"Correlação de Spearman entre produção e efetivo bovino: ρ = {fmt_dec(rho) if rho is not None else '—'} "
                    "(associação exploratória)."
                )

# ---------------------------------------------------------------------------
# Evidência 2: frustração de safra x crescimento do rebanho (espécies separadas)
# ---------------------------------------------------------------------------
with col_frust:
    with st.container(border=True):
        st.markdown(
            f"**Frustração de safra ({produto.lower()}) × índice dos rebanhos caprino e ovino — {municipio}**"
        )
        if ini == fim:
            st.warning("Escolha um intervalo com pelo menos dois anos para ver a evolução.")
        else:
            agro = pam_serie(pam(), nivel, codigo, produto, ini, fim)
            rebanhos = serie_por_especie(ppm(), nivel, codigo, ini, fim)
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(
                go.Bar(
                    x=agro.index,
                    y=agro["frustracao"],
                    name="Frustração de safra",
                    marker_color=CINZA,
                    hovertemplate="%{x}: frustração %{y:.3f}<extra></extra>",
                ),
                secondary_y=False,
            )
            for nome, cor, traco in [("Caprinos", VERMELHO, "solid"), ("Ovinos", PRETO, "dash")]:
                base_ini = rebanhos[nome].loc[ini]
                if base_ini:
                    idx = rebanhos[nome] / base_ini * 100
                    fig2.add_trace(
                        go.Scatter(
                            x=idx.index,
                            y=idx.values,
                            name=f"{nome} (índice {ini}=100)",
                            mode="lines",
                            line=dict(color=cor, width=3, dash=traco),
                            hovertemplate=f"<b>{nome}</b><br>%{{x}}: índice %{{y:.1f}}<extra></extra>",
                        ),
                        secondary_y=True,
                    )
            fig2.update_yaxes(title_text="Frustração (0 a 1)", secondary_y=False, rangemode="tozero")
            fig2.update_yaxes(title_text=f"Índice ({ini} = 100)", secondary_y=True, showgrid=False)
            fig2.update_layout(
                **PLOT_LAYOUT,
                height=420,
                xaxis_title="Ano",
                legend=dict(orientation="h", yanchor="bottom", y=1.0),
            )
            st.plotly_chart(fig2)
            sem_dado = int(agro["frustracao"].isna().sum())
            st.caption(
                "Frustração = 1 − área colhida / área plantada, só onde há área plantada. "
                + (f"{sem_dado} ano(s) sem área plantada ficam sem barra. " if sem_dado else "")
                + "Caprinos e ovinos são séries independentes (não somadas)."
            )

# ---------------------------------------------------------------------------
# Leitura rápida
# ---------------------------------------------------------------------------
if ano_max >= ini:
    with st.container(border=True):
        st.markdown("**Leitura rápida**")
        st.markdown(
            f"- **Integração:** {diag['n_pam']} municípios na PAM, {diag['n_ppm']} na PPM e "
            f"{diag['n_pib']} no PIB; {diag['n_comum']} em comum, junção 1:1 por código IBGE "
            f"({diag['n_uniao'] - diag['n_comum']} sem correspondência).\n"
            "- **Limite:** a dispersão compara municípios em um único ano; correlação alta ou baixa "
            "não indica causa nem dependência econômica. A participação do VAB agropecuário "
            "descreve a estrutura econômica, não a vulnerabilidade do município.\n"
            "- **Valores monetários** do PIB e da PAM estão a preços correntes; este cruzamento "
            "usa apenas participações e quantidades físicas."
        )
        st.page_link("views/fontes.py", label="Ver metodologia completa →", icon=":material/menu_book:")

# ---------------------------------------------------------------------------
# Achados de correlação calculados (independem do ano do filtro)
# ---------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(f"**O que os dados mostram nos cruzamentos — {ANO_VAB_FIM}**")
    quadro = quadro_municipal(pam(), ppm(), pib(), ANO_VAB_FIM)
    rho_pam, n_pam = spearman(quadro, "valor_total", "vab_agro")
    rho_pct, n_pct = spearman(quadro, "valor_total", "pct_vab_agro")
    if rho_pam is not None:
        st.markdown(
            f"- Valor agrícola × VAB agropecuário: **ρ = {fmt_dec(rho_pam, 3)}** (n = {n_pam}) — "
            "associação forte entre municípios."
        )
    if rho_pct is not None:
        st.markdown(
            f"- Valor agrícola × participação da agropecuária: **ρ = {fmt_dec(rho_pct, 3)}** (n = {n_pct}) — "
            "produzir muito não é o mesmo que depender da agropecuária."
        )
    melhor = None
    for cultura in ("milho", "feijao"):
        for especie in ("bovino", "ovino", "caprino", "suino"):
            valor, n = spearman(quadro, f"area_{cultura}", f"efetivo_{especie}")
            if valor is not None and (melhor is None or valor > melhor[1]):
                melhor = (f"{cultura} × {especie}", valor, n)
    if melhor:
        st.markdown(
            f"- Padrão territorial: **{melhor[0]}** apresentam a maior associação área × rebanho "
            f"(ρ = {fmt_dec(melhor[1], 3)}, n = {melhor[2]}) — agricultura familiar mista."
        )
    melao = [spearman(quadro, "area_melao", f"efetivo_{e}")[0] for e in ("bovino", "ovino", "caprino", "suino", "galinaceos")]
    melao = [r for r in melao if r is not None]
    if melao:
        st.markdown(
            f"- Relação fraca: o **melão** tem correlação próxima de zero com rebanhos "
            f"(entre {min(melao):.2f} e {max(melao):.2f})."
        )
    banana = correlacao_banana_vab_por_ano(pam(), pib(), 2003, ANO_VAB_FIM).dropna(subset=["rho"])
    if not banana.empty:
        st.markdown(
            f"- Valor da banana × VAB agropecuário, ano a ano: **{banana['rho'].min():.2f} a {banana['rho'].max():.2f}**, "
            f"sem ano negativo ({len(banana)} anos)."
        )
    st.page_link("views/sinteses.py", label="Ver todas as sínteses", icon=":material/lightbulb:")
