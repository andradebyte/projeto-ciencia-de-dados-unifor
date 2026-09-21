"""Dashboard - Tema 2 (Agropecuária), recorte pecuária: efetivo dos rebanhos
por espécie nos municípios do Ceará (SIDRA/PPM, tabela 3939, 2003-2024).

Este módulo implementa a Visão geral do dashboard: título, problema, recorte,
instruções de uso e os KPIs principais - cada um com unidade, período e
contexto explícitos, para evitar números soltos.
"""

import streamlit as st

from data import ANO_FIM, ANO_INICIO, ESPECIES, kpi_por_especie, load_ppm, n_municipios

st.set_page_config(
    page_title="Pecuária no Ceará | Projeto 1",
    page_icon="🐄",
    layout="wide",
)

ppm = load_ppm()
kpis = kpi_por_especie(ppm)
municipios_cobertos = n_municipios(ppm)

# ---------------------------------------------------------------------------
# Título
# ---------------------------------------------------------------------------
st.title("Pecuária no Ceará: evolução dos rebanhos municipais (2003-2024)")

# ---------------------------------------------------------------------------
# Problema
# ---------------------------------------------------------------------------
st.markdown(
    "**Problema.** Como os efetivos de bovinos, caprinos, ovinos, suínos e "
    "galináceos se transformaram nos municípios do Ceará entre 2003 e 2024, "
    "e quais municípios concentram cada espécie? A pecuária é tratada aqui "
    "como recorte da missão *Agropecuária e transformação econômica* do "
    "Projeto 1, que também abrange produção agrícola (PAM) e estrutura "
    "econômica municipal (PIB)."
)

# ---------------------------------------------------------------------------
# Recorte e instruções de uso
# ---------------------------------------------------------------------------
col_recorte, col_instrucoes = st.columns(2)

with col_recorte:
    st.subheader("Recorte dos dados")
    st.markdown(
        f"- **Fonte:** IBGE/SIDRA, Tabela 3939 (PPM - Pesquisa da Pecuária "
        "Municipal), arquivo estático fornecido pelo professor.\n"
        f"- **Território:** Ceará e seus {municipios_cobertos} municípios "
        "(chave: código IBGE de 7 dígitos).\n"
        f"- **Período:** {ANO_INICIO}-{ANO_FIM}, série anual ({ANO_FIM - ANO_INICIO + 1} anos).\n"
        f"- **Espécies:** {', '.join(ESPECIES)} - cada uma em série "
        "independente; efetivos de espécies diferentes nunca são somados "
        "entre si (não existe \"rebanho total\").\n"
        "- **Unidade:** cabeças (efetivo do rebanho no dia 31/12 do ano de referência)."
    )

with col_instrucoes:
    st.subheader("Instruções de uso")
    st.markdown(
        "1. Os KPIs abaixo resumem, por espécie, o efetivo do Ceará em "
        f"{ANO_FIM} e a variação percentual desde {ANO_INICIO}.\n"
        "2. Compare apenas dentro de uma mesma espécie: os valores absolutos "
        "de espécies diferentes não são comparáveis (unidades animais distintas).\n"
        "3. As seções seguintes do dashboard detalham comparação territorial "
        "entre municípios e o cruzamento com outras bases da missão.\n"
        "4. Consulte \"Fontes e metodologia\" ao final da página para "
        "limitações e símbolos especiais do SIDRA."
    )

# ---------------------------------------------------------------------------
# KPIs - um por espécie, com unidade, período e contexto explícitos
# ---------------------------------------------------------------------------
st.subheader("Principais indicadores")
st.caption(
    f"Efetivo do rebanho no Ceará em {ANO_FIM} (cabeças) e variação percentual "
    f"em relação a {ANO_INICIO}. Cada cartão é uma espécie independente."
)

colunas_kpi = st.columns(len(ESPECIES))
for coluna, (_, linha) in zip(colunas_kpi, kpis.iterrows()):
    coluna.metric(
        label=f"{linha['especie']} - efetivo {ANO_FIM} (cab.)",
        value=f"{linha['efetivo_atual_cab']:,}".replace(",", "."),
        delta=f"{linha['variacao_pct']:+.1f}% vs {ANO_INICIO}",
        help=(
            f"Unidade: cabeças. Período: {ANO_FIM}, com variação percentual "
            f"desde {ANO_INICIO}. Contexto: efetivo do rebanho de {linha['especie'].lower()} "
            "no Ceará (nível estadual), fonte SIDRA/PPM 3939. Não comparável a outras espécies."
        ),
    )
