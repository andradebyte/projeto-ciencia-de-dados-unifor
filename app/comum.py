"""Elementos compartilhados entre as telas: cache dos dados, filtros globais e estilo."""

from typing import NamedTuple

import pandas as pd
import streamlit as st

from data import (
    ANO_FIM,
    ANO_INICIO,
    ESPECIES,
    PRODUTOS,
    load_malha,
    load_pam,
    load_pib,
    load_ppm,
    municipios_lista,
)

VERMELHO = "#E53935"
VERMELHO_ESCURO = "#7F0000"
PRETO = "#111111"
CINZA = "#9E9E9E"
PALETA_VERMELHOS = ["#FDE0DD", "#FBB4B9", "#EF6C6C", VERMELHO, VERMELHO_ESCURO]
ESTADO = "Ceará — estado"
PLOT_LAYOUT = dict(
    template="plotly_white",
    font=dict(color=PRETO),
    margin=dict(l=0, r=0, t=10, b=0),
)


@st.cache_data
def ppm() -> pd.DataFrame:
    return load_ppm()


@st.cache_data
def pam() -> pd.DataFrame:
    return load_pam()


@st.cache_data
def pib() -> pd.DataFrame:
    return load_pib()


@st.cache_data
def malha() -> dict:
    return load_malha()


@st.cache_data
def municipios() -> pd.DataFrame:
    return municipios_lista(ppm())


class Filtros(NamedTuple):
    municipio: str
    ini: int
    fim: int
    produto: str


def filtros_globais() -> Filtros:
    """Município, período e produto PAM escolhidos na barra lateral."""
    ini, fim = st.session_state.get("filtro_anos", (ANO_INICIO, ANO_FIM))
    return Filtros(
        st.session_state.get("filtro_municipio", ESTADO),
        ini,
        fim,
        st.session_state.get("filtro_produto", PRODUTOS[0]),
    )


def territorio_do_filtro(municipio: str) -> tuple[str, str]:
    """(nível, código) SIDRA do filtro: Ceará (N3) ou um município (N6)."""
    if municipio == ESTADO:
        return "N3", "23"
    m = municipios()
    return "N6", m.loc[m["municipio"] == municipio, "codigo_ibge"].iloc[0]


def seletor_especie(key: str) -> str:
    """Seletor de espécie cuja escolha é herdada entre as telas."""
    atual = st.session_state.get("especie", ESPECIES[0])
    escolhida = st.pills("Espécie", ESPECIES, default=atual, selection_mode="single", key=key)
    escolhida = escolhida or atual
    st.session_state["especie"] = escolhida
    return escolhida


def fmt_int(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def fmt_dec(valor: float, casas: int = 2) -> str:
    """Número com vírgula decimal (padrão brasileiro)."""
    return f"{valor:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")
