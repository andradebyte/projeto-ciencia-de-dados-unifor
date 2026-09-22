"""Carregamento e indicadores da PPM (efetivo dos rebanhos, tabela SIDRA 3939).

Regra obrigatoria (data/README_DADOS.md item 4-5): bovinos, caprinos, ovinos,
suinos e galinaceos NAO sao unidades equivalentes e NUNCA devem ser somados
entre si. Cada especie e tratada em serie propria, do carregamento aos KPIs.
"""

import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "dados_originais"
PPM_FILE = RAW_DIR / "t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv"
MALHA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "dados_comuns"
    / "malha_municipal_ce_2022.geojson"
)

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


def load_malha() -> dict:
    """Malha municipal do Ceará (GeoJSON, IBGE, 2022).

    Dado geográfico auxiliar (data/dados_comuns/README_DADOS_COMUNS.md): não
    conta como uma das três tabelas SIDRA exigidas para integração. A chave
    de junção é a propriedade `codarea` (código IBGE de 7 dígitos).
    """
    with open(MALHA_FILE, encoding="utf-8") as f:
        return json.load(f)


def validar_codarea(malha: dict, ppm: pd.DataFrame) -> dict:
    """Correspondência entre `codarea` (malha) e `territorio_codigo` (PPM, N6).

    Retorna contagens e os códigos sem par de cada lado, para demonstrar que a
    integração geográfica por código IBGE é efetiva e não apenas nominal.
    """
    codigos_malha = {feat["properties"]["codarea"] for feat in malha["features"]}
    codigos_ppm = set(ppm.loc[ppm["nivel_territorial_codigo"] == "N6", "territorio_codigo"])
    return {
        "n_malha": len(codigos_malha),
        "n_ppm": len(codigos_ppm),
        "correspondentes": len(codigos_malha & codigos_ppm),
        "somente_malha": sorted(codigos_malha - codigos_ppm),
        "somente_ppm": sorted(codigos_ppm - codigos_malha),
    }


def ppm_por_municipio(ppm: pd.DataFrame, especie: str, ano: int) -> pd.DataFrame:
    """Efetivo por município (N6) de uma espécie em um ano, ranqueado.

    Uma única espécie por chamada: rebanhos de espécies distintas não são
    unidades equivalentes e nunca são somados (data/README_DADOS.md item 5).
    """
    sub = ppm.loc[
        (ppm["nivel_territorial_codigo"] == "N6")
        & (ppm["especie"] == especie)
        & (ppm["ano_codigo"] == ano),
        ["territorio_codigo", "territorio_nome", "valor"],
    ].rename(
        columns={
            "territorio_codigo": "codigo_ibge",
            "territorio_nome": "municipio",
            "valor": "efetivo_cab",
        }
    )
    sub = sub.astype({"efetivo_cab": "int64"}).sort_values(
        "efetivo_cab", ascending=False
    ).reset_index(drop=True)
    sub.insert(0, "ranking", range(1, len(sub) + 1))
    total = sub["efetivo_cab"].sum()
    sub["participacao_pct"] = (sub["efetivo_cab"] / total * 100).round(2) if total > 0 else 0.0
    return sub
