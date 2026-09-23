"""AGRO-CE - painel de dados públicos, recorte pecuária (PPM, SIDRA 3939, 2003-2024).

Roteador do dashboard, seguindo o wireframe: navegação por abas no topo e
filtros globais (município e período) na barra lateral, válidos para as telas
Pecuária e Território. Cada tela fica em app/views/.
"""

import streamlit as st

from comum import ESTADO, municipios
from data import ANO_FIM, ANO_INICIO

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
    st.caption("Os filtros aplicam-se às telas Pecuária e Território.")

paginas = [
    st.Page("views/visao_geral.py", title="1 Visão geral", default=True, url_path="visao-geral"),
    st.Page("views/pecuaria.py", title="2 Pecuária", url_path="pecuaria"),
    st.Page("views/territorio.py", title="3 Território", url_path="territorio"),
    st.Page("views/fontes.py", title="4 Fontes", url_path="fontes"),
]
st.navigation(paginas, position="top").run()
