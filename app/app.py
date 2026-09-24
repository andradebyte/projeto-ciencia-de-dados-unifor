"""AGRO-CE - painel de dados públicos: agropecuária e transformação econômica no Ceará.

Bases SIDRA: PAM (5457), PPM (3939) e PIB municipal (5938), 2003-2024.
Roteador do dashboard, seguindo o wireframe: navegação por abas no topo e
filtros globais (município, período e produto PAM) na barra lateral. Cada tela
fica em app/views/.
"""

import streamlit as st

from comum import ESTADO, municipios
from data import ANO_FIM, ANO_INICIO, PRODUTOS

st.set_page_config(
    page_title="AGRO-CE | Agropecuária e transformação econômica do Ceará", layout="wide"
)

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
        help="Produto agrícola usado na visão geral e no cruzamento. A tela Agricultura tem seleção própria de culturas.",
    )
    st.caption("Os filtros aplicam-se às telas Visão geral, Pecuária, Economia, Território e Cruzamento.")

paginas = [
    st.Page("views/visao_geral.py", title="1 Visão geral", default=True, url_path="visao-geral"),
    st.Page("views/agricultura.py", title="2 Agricultura — PAM", url_path="agricultura"),
    st.Page("views/pecuaria.py", title="3 Pecuária — PPM", url_path="pecuaria"),
    st.Page("views/economia.py", title="4 Economia municipal — PIB", url_path="economia"),
    st.Page("views/territorio.py", title="5 Território", url_path="territorio"),
    st.Page("views/cruzamento.py", title="6 Cruzamentos", url_path="cruzamento"),
    st.Page("views/sinteses.py", title="7 Sínteses", url_path="sinteses"),
    st.Page("views/fontes.py", title="8 Fontes e metodologia", url_path="fontes"),
]
st.navigation(paginas, position="top").run()
