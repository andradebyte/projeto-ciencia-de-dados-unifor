"""Tela 5 - Fontes e metodologia."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from comum import CINZA, PLOT_LAYOUT, VERMELHO, pam, pib, ppm
from data import ANO_VAB_FIM, cruzamento_municipal

st.title("Fontes e metodologia")

col_tabelas, col_cobertura = st.columns([3, 2])

with col_tabelas:
    with st.container(border=True):
        st.markdown("**Tabelas SIDRA utilizadas**")
        st.table(
            pd.DataFrame(
                [
                    ("5457", "PAM — área plantada, colhida, quantidade, rendimento e valor (7 produtos)", "2003–2024", "município"),
                    ("3939", "PPM — efetivo de bovinos, caprinos, ovinos, suínos e galináceos", "2003–2024", "município"),
                    ("5938", "PIB, VAB total, VAB agropecuário e participação (%)", "PIB até 2023; VAB até 2021", "município"),
                ],
                columns=["Código", "Nome", "Período", "Nível"],
            ).set_index("Código")
        )
        st.caption(
            "Produtos da PAM: milho, feijão, mandioca, cana-de-açúcar, banana, castanha de caju e melão. "
            "Todas as bases incluem Brasil (N1), Ceará (N3) e os 184 municípios (N6)."
        )

    with st.container(border=True):
        st.markdown("**Tratamento e limitações**")
        st.markdown(
            "- **Símbolos especiais do SIDRA** (`-`, `0`, `X`, `..`, `...`): `-` e `0` viram zero "
            "observado; `..` e `...` viram vazio (NaN); `X` viraria vazio com marcação de inibido. "
            "Nenhum símbolo é convertido em zero em silêncio. Resultado: 1.116 valores vazios, "
            "todos no PIB (VAB e participação de 2022 e 2023); PAM e PPM sem vazios; 0 casos de `X`.\n"
            "- **Chave de integração:** código IBGE do município (7 dígitos, lido como texto); "
            "nunca o nome.\n"
            "- **Defasagem temporal:** PAM e PPM até 2024, PIB até 2023, VAB agropecuário até 2021; "
            "cruzamentos usam só os anos comuns.\n"
            "- **Valores monetários a preços correntes**, sem deflação; por isso o painel usa "
            "participações e quantidades físicas para comparar anos.\n"
            "- **Espécies nunca são somadas entre si:** bovinos, caprinos, ovinos, suínos e "
            "galináceos não são unidades equivalentes; suínos e galináceos usam as categorias total.\n"
            "- **Efetivo é estoque** (cabeças em 31/12); produção agrícola é fluxo anual.\n"
            "- **Valor da produção (PAM) não é o VAB agropecuário**; a participação do VAB "
            "descreve a estrutura econômica, não comprova dependência ou vulnerabilidade.\n"
            "- **Frustração de safra** = 1 − área colhida / área plantada, calculada só quando a "
            "área plantada é positiva.\n"
            "- **Malha municipal:** GeoJSON do IBGE (Ceará, 2022, `codarea`), dado geográfico "
            "auxiliar que não conta como tabela SIDRA. Os anéis dos polígonos são reorientados "
            "em memória para o Plotly; o arquivo em `dados/raw/` não é alterado.\n"
            "- **Comparação territorial em valores absolutos**, sem normalização por área ou população.\n"
            "- Todos os dados são arquivos estáticos do repositório: o painel não consulta o SIDRA."
        )

    with st.container(border=True):
        st.markdown("**Diagnóstico da junção PAM × PPM × PIB**")
        _, diag = cruzamento_municipal(ppm(), pam(), pib(), "Milho (em grão)", ANO_VAB_FIM)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Municípios na PAM", diag["n_pam"])
        c2.metric("Municípios na PPM", diag["n_ppm"])
        c3.metric("Municípios no PIB", diag["n_pib"])
        c4.metric("Em comum (1:1)", diag["n_comum"])
        st.caption(
            f"Chave: código IBGE (7 dígitos). Cardinalidade esperada 1:1 por município, ano "
            f"e produto (verificada com validate='one_to_one'). Exemplo calculado para milho em "
            f"{ANO_VAB_FIM}: {diag['n_uniao'] - diag['n_comum']} municípios sem correspondência."
        )

with col_cobertura:
    with st.container(border=True):
        st.markdown("**Cobertura temporal das bases**")
        bases = [("PAM", 2003, 2024, VERMELHO), ("PPM", 2003, 2024, VERMELHO), ("PIB", 2003, 2023, VERMELHO), ("VAB agro", 2003, 2021, CINZA)]
        fig = go.Figure()
        for nome, a, b, cor in bases:
            fig.add_trace(
                go.Bar(
                    y=[nome], x=[b - a + 1], base=[a], orientation="h", marker_color=cor,
                    hovertemplate=f"<b>{nome}</b>: {a}–{b}<extra></extra>", showlegend=False,
                )
            )
        fig.update_xaxes(range=[2002, 2025], dtick=5)
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(**PLOT_LAYOUT, height=230)
        st.plotly_chart(fig)
        st.caption("VAB total e agropecuário só existem até 2021; 2022 e 2023 trazem apenas o PIB.")

    with st.container(border=True):
        st.markdown("**Créditos / autoria**")
        st.markdown(
            "Equipe 02 — Tema 2, Agropecuária e transformação econômica · disciplina de "
            "Ciência de Dados, Unifor, 2026."
        )
