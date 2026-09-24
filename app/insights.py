"""Achados calculados a partir das bases tratadas.

Nenhum número estatístico é fixo: todas as funções recalculam a partir dos
DataFrames carregados por `data.py`. As leituras são associações exploratórias,
nunca causalidade.
"""

import pandas as pd

from data import (
    ANO_PIB_FIM,
    ANO_VAB_FIM,
    CEARA_TERRITORIO_CODIGO,
    producao_por_hectare,
)

PRODUTO_SLUG = {
    "Milho (em grão)": "milho",
    "Feijão (em grão)": "feijao",
    "Mandioca": "mandioca",
    "Cana-de-açúcar": "cana",
    "Banana (cacho)": "banana",
    "Castanha de caju": "castanha",
    "Melão": "melao",
}
ESPECIE_SLUG = {
    "Bovinos": "bovino",
    "Caprinos": "caprino",
    "Ovinos": "ovino",
    "Suínos": "suino",
    "Galináceos": "galinaceos",
}


def quadro_municipal(pam: pd.DataFrame, ppm: pd.DataFrame, pib: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Um município por linha (código IBGE): valor agrícola, rebanhos e economia.

    Colunas: `valor_total` (soma das 7 culturas, Mil Reais), `area_<slug>`,
    `efetivo_<slug>`, `vab_agro`, `vab_total`, `pct_vab_agro`, `pib`.
    """
    pam_ano = pam[(pam["nivel_territorial_codigo"] == "N6") & (pam["ano_codigo"] == ano)].copy()
    pam_ano["slug"] = pam_ano["produto_nome"].map(PRODUTO_SLUG)

    valor = pam_ano[pam_ano["variavel"] == "valor_producao"].pivot_table(
        index="territorio_codigo", columns="slug", values="valor"
    )
    valor.columns = [f"valor_{c}" for c in valor.columns]
    area = pam_ano[pam_ano["variavel"] == "area_plantada"].pivot_table(
        index="territorio_codigo", columns="slug", values="valor"
    )
    area.columns = [f"area_{c}" for c in area.columns]
    valor["valor_total"] = valor.sum(axis=1, min_count=1)

    quadro = valor.join(area, how="outer")
    if ppm is not None and not ppm.empty and "nivel_territorial_codigo" in ppm.columns:
        ppm_ano = ppm[(ppm["nivel_territorial_codigo"] == "N6") & (ppm["ano_codigo"] == ano)].copy()
        ppm_ano["slug"] = ppm_ano["especie"].map(ESPECIE_SLUG)
        efetivo = ppm_ano.pivot_table(index="territorio_codigo", columns="slug", values="valor")
        efetivo.columns = [f"efetivo_{c}" for c in efetivo.columns]
        quadro = quadro.join(efetivo, how="outer")
    if pib is not None and not pib.empty and "nivel_territorial_codigo" in pib.columns:
        pib_ano = pib[(pib["nivel_territorial_codigo"] == "N6") & (pib["ano_codigo"] == ano)]
        econ = pib_ano.pivot_table(index="territorio_codigo", columns="variavel", values="valor")
        quadro = quadro.join(econ, how="outer")
    return quadro.reset_index()


def spearman(quadro: pd.DataFrame, coluna_a: str, coluna_b: str) -> tuple[float | None, int]:
    """Spearman com exclusão de pares ausentes. Devolve (rho, n)."""
    if coluna_a not in quadro.columns or coluna_b not in quadro.columns:
        return None, 0
    par = quadro[[coluna_a, coluna_b]].dropna()
    if len(par) < 3:
        return None, len(par)
    if par[coluna_a].nunique() < 2 or par[coluna_b].nunique() < 2:
        return None, len(par)
    return round(par[coluna_a].corr(par[coluna_b], method="spearman"), 3), len(par)


def crescimento_cultura(pam: pd.DataFrame, nivel: str, codigo: str, ini: int, fim: int) -> pd.DataFrame:
    """Fator de crescimento do valor da produção por cultura, ordenado."""
    sub = pam[
        (pam["nivel_territorial_codigo"] == nivel)
        & (pam["territorio_codigo"] == codigo)
        & (pam["variavel"] == "valor_producao")
    ]
    piv = sub.pivot_table(index="ano_codigo", columns="produto_nome", values="valor")
    if ini not in piv.index or fim not in piv.index:
        return pd.DataFrame()
    fator = (piv.loc[fim] / piv.loc[ini]).where(piv.loc[ini] > 0)
    return fator.dropna().sort_values(ascending=False).rename("fator").reset_index()


def ranking_valor(pam: pd.DataFrame, nivel: str, codigo: str, ini: int, fim: int) -> pd.DataFrame:
    """Posição de cada cultura no ranking de valor da produção, em dois anos."""
    sub = pam[
        (pam["nivel_territorial_codigo"] == nivel)
        & (pam["territorio_codigo"] == codigo)
        & (pam["variavel"] == "valor_producao")
    ]
    piv = sub.pivot_table(index="ano_codigo", columns="produto_nome", values="valor")
    if ini not in piv.index or fim not in piv.index:
        return pd.DataFrame()
    return pd.DataFrame(
        {"ini_pos": piv.loc[ini].rank(ascending=False), "fim_pos": piv.loc[fim].rank(ascending=False)}
    ).reset_index().rename(columns={"index": "produto", "produto_nome": "produto"})


def frustracao_media_estado(pam: pd.DataFrame, ini: int, fim: int) -> float | None:
    """Frustração média de safra (1 − colhida/plantada) no Ceará, por cultura-ano."""
    estado = pam[
        (pam["nivel_territorial_codigo"] == "N3")
        & (pam["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
        & pam["ano_codigo"].between(ini, fim)
    ]
    plantada = estado[estado["variavel"] == "area_plantada"].pivot_table(
        index="ano_codigo", columns="produto_nome", values="valor"
    )
    colhida = estado[estado["variavel"] == "area_colhida"].pivot_table(
        index="ano_codigo", columns="produto_nome", values="valor"
    )
    frustracao = 1 - colhida / plantada.where(plantada > 0)
    valor = frustracao.stack().dropna().mean()
    return round(float(valor), 3) if pd.notna(valor) else None


def lider_por_hectare(pam: pd.DataFrame, ano: int) -> dict | None:
    """Cultura de maior valor bruto por hectare colhido no Ceará em um ano."""
    base = producao_por_hectare(pam)
    linha = base[base["ano_codigo"] == ano].dropna(subset=["valor_por_ha_rs"])
    if linha.empty:
        return None
    topo = linha.sort_values("valor_por_ha_rs", ascending=False).iloc[0]
    return {"produto": topo["produto_nome"], "valor": float(topo["valor_por_ha_rs"])}


def crescimento_especie(ppm: pd.DataFrame, nivel: str, codigo: str, ini: int, fim: int) -> pd.DataFrame:
    """Fator de crescimento do efetivo por espécie, ordenado."""
    sub = ppm[
        (ppm["nivel_territorial_codigo"] == nivel)
        & (ppm["territorio_codigo"] == codigo)
        & (ppm["ano_codigo"].between(ini, fim))
    ]
    piv = sub.pivot_table(index="ano_codigo", columns="especie", values="valor")
    if ini not in piv.index or fim not in piv.index:
        return pd.DataFrame()
    fator = (piv.loc[fim] / piv.loc[ini]).where(piv.loc[ini] > 0)
    return fator.dropna().sort_values(ascending=False).rename("fator").reset_index().rename(columns={"index": "especie"})


def municipios_lideres_especie(ppm: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Município de maior efetivo em cada espécie no ano dado."""
    sub = ppm[
        (ppm["nivel_territorial_codigo"] == "N6")
        & (ppm["ano_codigo"] == ano)
    ].copy()
    idx = sub.groupby("especie")["valor"].idxmax()
    topo = sub.loc[idx, ["especie", "territorio_nome", "valor"]].copy()
    topo["territorio_nome"] = topo["territorio_nome"].str.removesuffix(" - CE")
    return topo.sort_values("especie").reset_index(drop=True)


def pib_estado(pib: pd.DataFrame, ini: int, fim: int) -> dict | None:
    """Fator de crescimento do PIB do Ceará entre dois anos."""
    ce = pib[
        (pib["nivel_territorial_codigo"] == "N3")
        & (pib["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
        & (pib["variavel"] == "pib")
    ].set_index("ano_codigo")["valor"]
    if ini not in ce.index or fim not in ce.index or ce.loc[ini] == 0:
        return None
    return {"fator": round(float(ce.loc[fim] / ce.loc[ini]), 1), "ini": float(ce.loc[ini]), "fim": float(ce.loc[fim])}


def desconcentracao_fortaleza(pib: pd.DataFrame, ini: int, fim: int) -> dict | None:
    """Participação de Fortaleza no PIB do Ceará em dois anos."""
    def _share(ano: int) -> float | None:
        ce = pib[(pib["nivel_territorial_codigo"] == "N3") & (pib["territorio_codigo"] == CEARA_TERRITORIO_CODIGO) & (pib["ano_codigo"] == ano) & (pib["variavel"] == "pib")]["valor"].sum()
        fort = pib[(pib["nivel_territorial_codigo"] == "N6") & (pib["territorio_nome"] == "Fortaleza - CE") & (pib["ano_codigo"] == ano) & (pib["variavel"] == "pib")]["valor"].sum()
        return round(float(fort / ce * 100), 1) if ce else None
    a, b = _share(ini), _share(fim)
    return {"ini": a, "fim": b} if a is not None and b is not None else None


def sga_caso(pib: pd.DataFrame, ini: int, fim_pib: int, fim_vab: int) -> dict | None:
    """São Gonçalo do Amarante: crescimento do PIB e participação agropecuária."""
    def _serie(variavel: str) -> pd.Series:
        return pib[
            (pib["nivel_territorial_codigo"] == "N6")
            & (pib["territorio_nome"] == "São Gonçalo do Amarante - CE")
            & (pib["variavel"] == variavel)
        ].set_index("ano_codigo")["valor"]
    p = _serie("pib")
    pct = _serie("pct_vab_agro").dropna()
    if ini not in p.index or p.loc[ini] == 0:
        return None
    pct_ini = pct.get(ini)
    pct_fim = pct.loc[pct.index.max()] if not pct.empty else None
    return {
        "fator": round(float(p.loc[fim_pib] / p.loc[ini]), 1) if fim_pib in p.index else None,
        "pct_ini": round(float(pct_ini), 1) if pct_ini is not None and pd.notna(pct_ini) else None,
        "pct_fim": round(float(pct_fim), 1) if pct_fim is not None and pd.notna(pct_fim) else None,
    }


def correlacao_banana_vab_por_ano(pam: pd.DataFrame, pib: pd.DataFrame, ini: int, fim: int) -> pd.DataFrame:
    """Spearman entre valor da banana e VAB agropecuário, ano a ano."""
    linhas = []
    for ano in range(ini, fim + 1):
        quadro = quadro_municipal(pam, pd.DataFrame(), pib, ano)
        if "valor_banana" not in quadro or "vab_agro" not in quadro:
            continue
        rho, n = spearman(quadro, "valor_banana", "vab_agro")
        linhas.append({"ano": ano, "rho": rho, "n": n})
    return pd.DataFrame(linhas)


def correlacao_valor_vab_por_ano(pam: pd.DataFrame, pib: pd.DataFrame, ini: int, fim: int) -> pd.DataFrame:
    """Spearman entre o valor total das 7 culturas e o VAB agropecuário, ano a ano."""
    linhas = []
    for ano in range(ini, fim + 1):
        quadro = quadro_municipal(pam, pd.DataFrame(), pib, ano)
        if "valor_total" not in quadro or "vab_agro" not in quadro:
            continue
        rho, n = spearman(quadro, "valor_total", "vab_agro")
        linhas.append({"ano": ano, "rho": rho, "n": n})
    return pd.DataFrame(linhas)


def metrica_por_cultura_estado(pam: pd.DataFrame, variavel: str, ano: int) -> pd.Series:
    """Valor de uma variável por cultura no agregado estadual do Ceará, em um ano."""
    sub = pam[
        (pam["nivel_territorial_codigo"] == "N3")
        & (pam["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
        & (pam["variavel"] == variavel)
        & (pam["ano_codigo"] == ano)
    ]
    return sub.set_index("produto_nome")["valor"]


def lideres_valor_por_cultura(pam: pd.DataFrame, ano: int) -> dict:
    """Município de maior valor da produção em cada cultura, no ano dado."""
    sub = pam[
        (pam["nivel_territorial_codigo"] == "N6")
        & (pam["variavel"] == "valor_producao")
        & (pam["ano_codigo"] == ano)
    ]
    idx = sub.groupby("produto_nome")["valor"].idxmax()
    topo = sub.loc[idx, ["produto_nome", "territorio_nome"]].copy()
    topo["territorio_nome"] = topo["territorio_nome"].str.removesuffix(" - CE")
    return topo.set_index("produto_nome")["territorio_nome"].to_dict()


def maior_diferenca_plantada_colhida(pam: pd.DataFrame, produto: str) -> dict | None:
    """Ano de maior diferença entre área plantada e colhida no Ceará, por cultura."""
    ce = pam[
        (pam["nivel_territorial_codigo"] == "N3")
        & (pam["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
        & (pam["produto_nome"] == produto)
    ]
    p = ce[ce["variavel"] == "area_plantada"].set_index("ano_codigo")["valor"]
    c = ce[ce["variavel"] == "area_colhida"].set_index("ano_codigo")["valor"]
    dif = (p - c).dropna()
    if dif.empty or dif.max() <= 0:
        return None
    ano = dif.idxmax()
    return {"ano": int(ano), "dif": float(dif.loc[ano]), "pct": float(dif.loc[ano] / p.loc[ano] * 100) if p.loc[ano] else None}


def participacao_especie_estado(ppm: pd.DataFrame, ano: int, especie: str = "Galináceos") -> float | None:
    """Participação de uma espécie no total de cabeças do Ceará, em um ano."""
    sub = ppm[
        (ppm["nivel_territorial_codigo"] == "N3")
        & (ppm["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
        & (ppm["ano_codigo"] == ano)
    ]
    serie = sub.set_index("especie")["valor"]
    total = serie.sum()
    return round(float(serie.get(especie, 0) / total * 100), 1) if total else None


def crescimento_brasil(pib: pd.DataFrame, ini: int, fim: int) -> float | None:
    """Fator de crescimento do PIB do Brasil entre dois anos."""
    br = pib[(pib["nivel_territorial_codigo"] == "N1") & (pib["variavel"] == "pib")].set_index("ano_codigo")["valor"]
    if ini not in br.index or fim not in br.index or br.loc[ini] == 0:
        return None
    return round(float(br.loc[fim] / br.loc[ini]), 2)


def vab_estado_ce(pib: pd.DataFrame, ano: int) -> dict:
    """VAB total, VAB agropecuário e participação do Ceará em um ano."""
    ce = pib[
        (pib["nivel_territorial_codigo"] == "N3")
        & (pib["territorio_codigo"] == CEARA_TERRITORIO_CODIGO)
        & (pib["ano_codigo"] == ano)
    ].set_index("variavel")["valor"]
    return {"vab_total": ce.get("vab_total"), "vab_agro": ce.get("vab_agro"), "pct": ce.get("pct_vab_agro")}


def top_participacao_agro(pib: pd.DataFrame, ano: int, n: int = 5) -> pd.DataFrame:
    """Municípios com maior participação da agropecuária no VAB, em um ano."""
    sub = pib[
        (pib["nivel_territorial_codigo"] == "N6")
        & (pib["ano_codigo"] == ano)
        & (pib["variavel"] == "pct_vab_agro")
    ].copy()
    sub["municipio"] = sub["territorio_nome"].str.removesuffix(" - CE")
    return sub[["municipio", "valor"]].rename(columns={"valor": "pct"}).nlargest(n, "pct").reset_index(drop=True)


def municipio_pib_e_agro(pib: pd.DataFrame, municipio: str, ano: int) -> dict:
    """PIB, VAB agropecuário e participação de um município em um ano."""
    sub = pib[(pib["territorio_nome"] == f"{municipio} - CE") & (pib["ano_codigo"] == ano)].set_index("variavel")["valor"]
    return {"pib": sub.get("pib"), "vab_agro": sub.get("vab_agro"), "pct": sub.get("pct_vab_agro")}


def municipios_crescimento_pib(pib: pd.DataFrame, ini: int, fim: int, n: int = 10) -> list[str]:
    """Nomes dos municípios com maior fator de crescimento do PIB entre dois anos."""
    def _serie(ano: int) -> pd.DataFrame:
        sub = pib[
            (pib["nivel_territorial_codigo"] == "N6")
            & (pib["variavel"] == "pib")
            & (pib["ano_codigo"] == ano)
        ].copy()
        sub["municipio"] = sub["territorio_nome"].str.removesuffix(" - CE")
        return sub[["territorio_codigo", "municipio", "valor"]].set_index("territorio_codigo")

    a = _serie(ini).rename(columns={"valor": "ini", "municipio": "nome"})
    b = _serie(fim).rename(columns={"valor": "fim"})
    m = a.join(b, how="inner")
    m["fator"] = (m["fim"] / m["ini"]).where((m["ini"] > 0) & (m["fim"] > 0))
    return m.dropna(subset=["fator"]).sort_values("fator", ascending=False).head(n)["nome"].tolist()


def variacoes_anuais_corr(pam: pd.DataFrame, pib: pd.DataFrame, ini: int, fim: int) -> dict:
    """Correlação entre variações anuais das somas municipais (PAM × VAB agro)."""
    somas = []
    for ano in range(ini, fim + 1):
        quadro = quadro_municipal(pam, pd.DataFrame(), pib, ano)
        if "valor_total" not in quadro or "vab_agro" not in quadro:
            continue
        somas.append((float(quadro["valor_total"].sum()), float(quadro["vab_agro"].sum())))
    mudancas = [(b[0] / a[0] - 1, b[1] / a[1] - 1) for a, b in zip(somas, somas[1:]) if a[0] and a[1]]
    if len(mudancas) < 3:
        return {"pearson": None, "spearman": None, "n": len(mudancas)}
    x = pd.Series([m[0] for m in mudancas])
    y = pd.Series([m[1] for m in mudancas])
    return {"pearson": round(float(x.corr(y)), 3), "spearman": round(float(x.corr(y, method="spearman")), 3), "n": len(mudancas)}
