"""Carregamento e indicadores da PPM (efetivo dos rebanhos, tabela SIDRA 3939).

Regra obrigatoria (dados/README_DADOS.md item 4-5): bovinos, caprinos, ovinos,
suinos e galinaceos NAO sao unidades equivalentes e NUNCA devem ser somados
entre si. Cada especie e tratada em serie propria, do carregamento aos KPIs.
"""

import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "dados" / "raw"
PPM_FILE = RAW_DIR / "t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv"
MALHA_FILE = RAW_DIR / "malha_municipal_ce_2022.geojson"

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


def municipios_lista(ppm: pd.DataFrame) -> pd.DataFrame:
    """Municípios (N6) com código IBGE de 7 dígitos e nome sem o sufixo " - CE"."""
    m = ppm.loc[
        ppm["nivel_territorial_codigo"] == "N6", ["territorio_codigo", "territorio_nome"]
    ].drop_duplicates()
    m = m.rename(columns={"territorio_codigo": "codigo_ibge", "territorio_nome": "municipio"})
    m["municipio"] = m["municipio"].str.removesuffix(" - CE")
    return m.sort_values("municipio").reset_index(drop=True)


def serie_por_especie(
    ppm: pd.DataFrame, nivel: str, codigo: str, ano_ini: int, ano_fim: int
) -> pd.DataFrame:
    """Efetivo anual de um território (linhas = ano, colunas = espécie).

    Cada coluna é uma série independente: espécies nunca são somadas.
    """
    sub = ppm[
        (ppm["nivel_territorial_codigo"] == nivel)
        & (ppm["territorio_codigo"] == codigo)
        & ppm["ano_codigo"].between(ano_ini, ano_fim)
    ]
    piv = sub.pivot_table(index="ano_codigo", columns="especie", values="valor")
    return piv.reindex(columns=ESPECIES).sort_index()


def n_municipios(ppm: pd.DataFrame) -> int:
    return ppm.loc[ppm["nivel_territorial_codigo"] == "N6", "territorio_codigo"].nunique()


def load_malha() -> dict:
    """Malha municipal do Ceará (GeoJSON, IBGE, 2022).

    Dado geográfico auxiliar (dados/raw/README_DADOS_COMUNS.md): não
    conta como uma das três tabelas SIDRA exigidas para integração. A chave
    de junção é a propriedade `codarea` (código IBGE de 7 dígitos).
    """
    with open(MALHA_FILE, encoding="utf-8") as f:
        malha = json.load(f)
    for feat in malha["features"]:
        _orientar_aneis_horario(feat["geometry"]["coordinates"])
    return malha


def _orientar_aneis_horario(aneis: list) -> None:
    """Anel externo horário e furos anti-horários, como o Plotly (d3-geo) exige.

    A malha do IBGE vem com anéis anti-horários, o que faz cada município
    preencher o mapa inteiro. Correção só em memória: o arquivo raw não muda.
    """
    for i, anel in enumerate(aneis):
        area2 = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(anel, anel[1:] + anel[:1]))
        horario = area2 < 0
        if horario != (i == 0):
            anel.reverse()


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


def ppm_por_municipio(ppm: pd.DataFrame, especie: str, ano_ini: int, ano_fim: int) -> pd.DataFrame:
    """Efetivo médio no período e crescimento por município (N6), ranqueado.

    Uma única espécie por chamada: rebanhos de espécies distintas não são
    unidades equivalentes e nunca são somados (dados/README_DADOS.md item 5).
    `cresc_pct` fica vazio quando o efetivo inicial é zero.
    """
    sub = ppm[
        (ppm["nivel_territorial_codigo"] == "N6")
        & (ppm["especie"] == especie)
        & ppm["ano_codigo"].between(ano_ini, ano_fim)
    ]
    piv = sub.pivot_table(
        index=["territorio_codigo", "territorio_nome"], columns="ano_codigo", values="valor"
    )
    out = pd.DataFrame(
        {
            "efetivo_medio": piv.mean(axis=1).round(0).astype("int64"),
            "efetivo_ini": piv[ano_ini],
            "efetivo_fim": piv[ano_fim],
        }
    ).reset_index()
    out = out.rename(columns={"territorio_codigo": "codigo_ibge", "territorio_nome": "municipio"})
    out["municipio"] = out["municipio"].str.removesuffix(" - CE")
    out["cresc_pct"] = ((out["efetivo_fim"] / out["efetivo_ini"] - 1) * 100).where(
        (out["efetivo_ini"] > 0) & (ano_fim > ano_ini)
    ).round(1)
    out = out.sort_values("efetivo_medio", ascending=False).reset_index(drop=True)
    out.insert(0, "ranking", range(1, len(out) + 1))
    total = out["efetivo_medio"].sum()
    out["participacao_pct"] = (out["efetivo_medio"] / total * 100).round(2) if total > 0 else 0.0
    return out
