"""AGRO-CE - painel de dados públicos: agropecuária e transformação econômica no Ceará.

Bases SIDRA: PAM (5457), PPM (3939) e PIB municipal (5938), 2003-2024.
Roteador do dashboard, seguindo o wireframe: navegação por abas no topo e
filtros globais (município, período e produto PAM) na barra lateral. Cada tela
fica em app/views/.
"""

import streamlit as st

from comum import ESTADO, municipios
from data import ANO_FIM, ANO_INICIO, PRODUTOS

st.set_page_config(page_title="AGRO-CE | Pecuária no Ceará", page_icon="🐄", layout="wide")

with st.sidebar:
    st.markdown("**AGRO-CE** · painel de dados públicos")
    st.subheader("Filtros globais")
    st.selectbox(
        "Município",
        [ESTADO, *municipios()["municipio"]],
        key="filtro_municipio",
        help="Ceará (nível estadual) ou um dos 184 municípios.",
    )
    st.slider("Ano / intervalo", ANO_INICIO, ANO_FIM, (ANO_INICIO, ANO_FIM), key="filtro_anos")
    st.selectbox(
        "Produto (PAM)",
        PRODUTOS,
        key="filtro_produto",
        help="Produto agrícola da PAM usado nos KPIs, no resumo e no cruzamento.",
    )
    st.caption("Os filtros aplicam-se às telas Visão geral, Pecuária, Território e Cruzamento.")

paginas = [
    st.Page("views/visao_geral.py", title="1 Visão geral", default=True, url_path="visao-geral"),
    st.Page("views/pecuaria.py", title="2 Pecuária", url_path="pecuaria"),
    st.Page("views/territorio.py", title="3 Território", url_path="territorio"),
    st.Page("views/cruzamento.py", title="4 Cruzamento", url_path="cruzamento"),
    st.Page("views/fontes.py", title="5 Fontes", url_path="fontes"),
]
st.navigation(paginas, position="top").run()
