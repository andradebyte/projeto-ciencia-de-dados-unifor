from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
PAM_PATH = BASE_DIR / "dados" / "processed" / "pam_tratado.csv"


@st.cache_data
def load_pam(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.drop(columns=[c for c in df.columns if c.endswith("_codigo")])


st.set_page_config(page_title="PAM - Ceará", layout="wide")
st.title("Produção Agrícola Municipal (PAM) - Ceará")

df = load_pam(PAM_PATH)

col1, col2, col3 = st.columns(3)
territorio = col1.selectbox("Território", sorted(df["territorio_nome"].unique()), index=0)
variavel = col2.selectbox("Variável", sorted(df["variavel_nome"].unique()))
produtos = col3.multiselect(
    "Produtos", sorted(df["produto_nome"].unique()), default=sorted(df["produto_nome"].unique())
)

filtrado = df[
    (df["territorio_nome"] == territorio)
    & (df["variavel_nome"] == variavel)
    & (df["produto_nome"].isin(produtos))
]

unidade = filtrado["unidade"].iloc[0] if not filtrado.empty else ""

pivot = filtrado.pivot_table(
    index="ano_nome", columns="produto_nome", values="valor", aggfunc="sum"
)

st.subheader(f"{variavel} ({unidade}) - {territorio}")
st.line_chart(pivot)

with st.expander("Ver dados"):
    st.dataframe(filtrado, use_container_width=True)
