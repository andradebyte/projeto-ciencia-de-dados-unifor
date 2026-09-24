"""Carregamento e indicadores das bases SIDRA do painel: PPM (3939), PAM (5457) e PIB (5938).

O painel lê a camada `data/processed` (tabelas já tipadas e higienizadas pelo
pipeline em src/) e a malha municipal em `data/raw`. Nunca consulta o SIDRA.

Regra obrigatória (data/README_DADOS.md item 4-5): bovinos, caprinos, ovinos,
suínos e galináceos NÃO são unidades equivalentes e NUNCA são somados entre si.
Cada espécie é tratada em série própria, do carregamento aos indicadores.
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "dados" / "raw"
PROCESSED_DIR = ROOT / "dados" / "processed"
PPM_FILE = PROCESSED_DIR / "ppm_tratado.csv"
PAM_FILE = PROCESSED_DIR / "pam_tratado.csv"
PIB_FILE = PROCESSED_DIR / "pib_tratado.csv"
MALHA_FILE = RAW_DIR / "malha_municipal_ce_2022.geojson"

REBANHO_COD_NOME = {
    "2670": "Bovinos",
    "2681": "Caprinos",
    "2677": "Ovinos",
    "32794": "Suínos",
    "32796": "Galináceos",
}
ESPECIES = list(REBANHO_COD_NOME.values())

PRODUTOS = [
    "Milho (em grão)",
    "Feijão (em grão)",
    "Mandioca",
    "Cana-de-açúcar",
    "Banana (cacho)",
    "Castanha de caju",
    "Melão",
]
PAM_VARIAVEIS = {
    "8331": "area_plantada",
    "216": "area_colhida",
    "214": "quantidade",
    "112": "rendimento",
    "215": "valor_producao",
}
PIB_VARIAVEIS = {
    "37": "pib",
    "498": "vab_total",
    "513": "vab_agro",
    "516": "pct_vab_agro",
}

ANO_INICIO = 2003
ANO_FIM = 2024
ANO_PIB_FIM = 2023
ANO_VAB_FIM = 2021
CEARA_TERRITORIO_CODIGO = "23"


def _read_processed(path: Path, extra_dtypes: dict | None = None) -> pd.DataFrame:
    dtypes = {
        "territorio_codigo": "string",
        "nivel_territorial_codigo": "string",
        "variavel_codigo": "string",
    }
    if extra_dtypes:
        dtypes.update(extra_dtypes)
    df = pd.read_csv(path, dtype=dtypes)
    df["ano_codigo"] = df["ano_codigo"].astype("int64")
    return df


def load_ppm() -> pd.DataFrame:
    df = _read_processed(PPM_FILE, {"tipo_rebanho_codigo": "string"})
    df["especie"] = df["tipo_rebanho_codigo"].map(REBANHO_COD_NOME)
    return df


def load_pam() -> pd.DataFrame:
    df = _read_processed(PAM_FILE, {"produto_codigo": "string"})
    df["variavel"] = df["variavel_codigo"].map(PAM_VARIAVEIS)
    return df


def load_pib() -> pd.DataFrame:
    df = _read_processed(PIB_FILE)
    df["variavel"] = df["variavel_codigo"].map(PIB_VARIAVEIS)
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


def _serie_territorio(df, nivel, codigo, ano_ini, ano_fim, filtro_extra=None):
    mask = (
        (df["nivel_territorial_codigo"] == nivel)
        & (df["territorio_codigo"] == codigo)
        & df["ano_codigo"].between(ano_ini, ano_fim)
    )
    if filtro_extra is not None:
        mask &= filtro_extra
    return df[mask]


def pam_serie(
    pam: pd.DataFrame, nivel: str, codigo: str, produto: str, ano_ini: int, ano_fim: int
) -> pd.DataFrame:
    """Série anual da PAM de um produto e território (linhas = ano).

    `frustracao` = 1 - área colhida / área plantada, só onde a área plantada é
    positiva (denominador nulo ou zero deixa o valor vazio, sem imputação).
    """
    sub = _serie_territorio(pam, nivel, codigo, ano_ini, ano_fim, pam["produto_nome"] == produto)
    piv = sub.pivot_table(index="ano_codigo", columns="variavel", values="valor")
    piv = piv.reindex(columns=list(PAM_VARIAVEIS.values())).sort_index()
    piv["frustracao"] = (1 - piv["area_colhida"] / piv["area_plantada"]).where(
        piv["area_plantada"] > 0
    )
    return piv


def pib_serie(
    pib: pd.DataFrame, nivel: str, codigo: str, ano_ini: int, ano_fim: int
) -> pd.DataFrame:
    """PIB, VAB total, VAB agropecuário e participação (%) de um território, por ano.

    VAB e participação só existem até 2021; depois disso vêm vazios (`...`).
    """
    sub = _serie_territorio(pib, nivel, codigo, ano_ini, ano_fim)
    piv = sub.pivot_table(index="ano_codigo", columns="variavel", values="valor", dropna=False)
    return piv.reindex(columns=list(PIB_VARIAVEIS.values())).sort_index()


def cruzamento_municipal(
    ppm: pd.DataFrame, pam: pd.DataFrame, pib: pd.DataFrame, produto: str, ano: int
) -> tuple[pd.DataFrame, dict]:
    """Junção PAM x PPM x PIB por código IBGE de 7 dígitos, um município por linha.

    Chave: `codigo_ibge` (string). Cardinalidade esperada 1:1 em cada base para
    um produto e um ano; `validate="one_to_one"` falha se houver duplicatas.
    Retorna a tabela combinada e o diagnóstico de correspondências.
    """
    def _base(df, filtro, coluna):
        sub = df[(df["nivel_territorial_codigo"] == "N6") & (df["ano_codigo"] == ano) & filtro]
        return sub[["territorio_codigo", "territorio_nome", "valor"]].rename(
            columns={"territorio_codigo": "codigo_ibge", "territorio_nome": "municipio", "valor": coluna}
        )

    q = _base(pam, (pam["produto_nome"] == produto) & (pam["variavel"] == "quantidade"), "quantidade_t")
    b = _base(ppm, ppm["especie"] == "Bovinos", "efetivo_bovinos")
    v = _base(pib, pib["variavel"] == "pct_vab_agro", "pct_vab_agro")

    m = q.merge(b.drop(columns="municipio"), on="codigo_ibge", how="outer", validate="one_to_one")
    m = m.merge(v.drop(columns="municipio"), on="codigo_ibge", how="outer", validate="one_to_one")
    m["municipio"] = m["municipio"].str.removesuffix(" - CE")
    codigos = [set(x["codigo_ibge"]) for x in (q, b, v)]
    diag = {
        "n_pam": len(codigos[0]),
        "n_ppm": len(codigos[1]),
        "n_pib": len(codigos[2]),
        "n_comum": len(codigos[0] & codigos[1] & codigos[2]),
        "n_uniao": len(m),
        "sem_vab": int(m["pct_vab_agro"].isna().sum()),
        "sem_producao": int((m["quantidade_t"].fillna(0) <= 0).sum()),
    }
    return m, diag


def load_malha() -> dict:
    """Malha municipal do Ceará (GeoJSON, IBGE, 2022).

    Dado geográfico auxiliar (data/raw/README_DADOS_COMUNS.md): não
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
    unidades equivalentes e nunca são somados (data/README_DADOS.md item 5).
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
