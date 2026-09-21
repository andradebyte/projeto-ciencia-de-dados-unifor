"""Carregamento e indicadores da PPM (efetivo dos rebanhos, tabela SIDRA 3939).

Regra obrigatoria (data/README_DADOS.md item 4-5): bovinos, caprinos, ovinos,
suinos e galinaceos NAO sao unidades equivalentes e NUNCA devem ser somados
entre si. Cada especie e tratada em serie propria, do carregamento aos KPIs.
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "dados_originais"
PPM_FILE = RAW_DIR / "t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv"

SIDRA_NA = {"...": pd.NA, "..": pd.NA, "X": pd.NA}
SIDRA_ZERO = {"-": 0.0}

REBANHO_COD_NOME = {
    "2670": "Bovinos",
    "2681": "Caprinos",
    "2677": "Ovinos",
    "32794": "Suínos",
    "32796": "Galináceos",
}
ESPECIES = list(REBANHO_COD_NOME.values())

ANO_INICIO = 2003
ANO_FIM = 2024
CEARA_TERRITORIO_CODIGO = "23"


def _read_sidra(path: Path, extra_dtypes: dict | None = None) -> pd.DataFrame:
    dtypes = {
        "territorio_codigo": "string",
        "ano_codigo": "Int64",
        "nivel_territorial_codigo": "string",
    }
    if extra_dtypes:
        dtypes.update(extra_dtypes)
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=dtypes, keep_default_na=False)
    df["valor"] = df["valor"].replace(SIDRA_NA).replace(SIDRA_ZERO)
    df["valor"] = pd.to_numeric(df["valor"], errors="raise")
    return df


def load_ppm() -> pd.DataFrame:
    df = _read_sidra(PPM_FILE, {"tipo_rebanho_codigo": "string"})
    df["especie"] = df["tipo_rebanho_codigo"].map(REBANHO_COD_NOME)
    return df


def kpi_por_especie(ppm: pd.DataFrame) -> pd.DataFrame:
    """Efetivo do Ceará em ANO_FIM e variação % desde ANO_INICIO, uma linha por espécie.

    Cada espécie é calculada em série independente; os valores nunca são
    somados entre espécies (efetivo de rebanhos distintos não é equivalente).
    """
    ce = ppm[
        (ppm["nivel_territorial_codigo"] == "N3")
        & (ppm["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
    ]
    linhas = []
    for especie in ESPECIES:
        serie = ce.loc[ce["especie"] == especie].set_index("ano_codigo")["valor"].sort_index()
        efetivo_fim = serie.loc[ANO_FIM]
        efetivo_inicio = serie.loc[ANO_INICIO]
        variacao_pct = (efetivo_fim / efetivo_inicio - 1) * 100
        linhas.append(
            {
                "especie": especie,
                "efetivo_atual_cab": int(efetivo_fim),
                "variacao_pct": round(float(variacao_pct), 1),
            }
        )
    return pd.DataFrame(linhas)


def n_municipios(ppm: pd.DataFrame) -> int:
    return ppm.loc[ppm["nivel_territorial_codigo"] == "N6", "territorio_codigo"].nunique()
