"""Tela 4 - Fontes e metodologia."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comum import CINZA, PLOT_LAYOUT, VERMELHO

st.title("Fontes e metodologia")

col_tabelas, col_cobertura = st.columns([3, 2])

with col_tabelas:
    with st.container(border=True):
        st.markdown("**Tabelas SIDRA utilizadas**")
        st.table(
            pd.DataFrame(
                [
                    {
                        "Código": "3939",
                        "Nome": "PPM — efetivo de bovinos, caprinos, ovinos, suínos e galináceos",
                        "Período": "2003–2024",
                        "Nível": "município",
                    },
                ]
            ).set_index("Código")
        )
        st.caption(
            "PAM (5457) e PIB municipal (5938) fazem parte da missão, mas estão fora do "
            "recorte desta versão do painel, dedicada à pecuária."
        )

    with st.container(border=True):
        st.markdown("**Tratamento e limitações**")
        st.markdown(
            "- **Símbolos especiais do SIDRA** (`-`, `0`, `X`, `..`, `...`): `-` é lido como "
            "zero absoluto; `X`, `..` e `...` seriam mantidos como não disponíveis, sem "
            "imputação. Na PPM 3939 só aparece `-` (5 registros).\n"
            "- **Chave de integração:** código IBGE do município (7 dígitos); nunca o nome.\n"
            "- **Malha municipal:** GeoJSON do IBGE (Ceará, 2022, `codarea`), dado geográfico "
            "auxiliar que não conta como tabela SIDRA. Os anéis dos polígonos são reorientados "
            "em memória para o Plotly; o arquivo em `dados/raw/` não é alterado.\n"
            "- **Espécies nunca são somadas entre si:** bovinos, caprinos, ovinos, suínos e "
            "galináceos não são unidades equivalentes; suínos e galináceos usam as categorias total.\n"
            "- **Efetivo é estoque** (cabeças em 31/12), não fluxo anual.\n"
            "- **Comparação territorial em valores absolutos**, sem normalização por área ou população.\n"
            "- Todos os dados são arquivos estáticos do repositório: o painel não consulta o SIDRA."
        )

with col_cobertura:
    with st.container(border=True):
        st.markdown("**Cobertura temporal das bases**")
        bases = [("PAM", 2003, 2024, CINZA), ("PPM", 2003, 2024, VERMELHO), ("PIB", 2003, 2023, CINZA)]
        fig = go.Figure()
        for nome, a, b, cor in bases:
            fig.add_trace(
                go.Bar(
                    y=[nome], x=[b - a + 1], base=[a], orientation="h", marker_color=cor,
                    hovertemplate=f"<b>{nome}</b>: {a}–{b}<extra></extra>", showlegend=False,
                )
            )
        fig.update_xaxes(range=[2002, 2025], dtick=5)
        fig.update_layout(**PLOT_LAYOUT, height=200)
        st.plotly_chart(fig)
        st.caption("PPM em vermelho (usada neste painel). VAB do PIB só até 2021.")

    with st.container(border=True):
        st.markdown("**Créditos / autoria**")
        st.markdown(
            "Equipe 02 — Tema 2, Agropecuária e transformação econômica · disciplina de "
            "Ciência de Dados, Unifor, 2026."
        )
