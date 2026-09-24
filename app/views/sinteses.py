"""Tela - Sínteses: achados e perguntas respondidas a partir das bases.

Nenhum número é fixo: cada resposta é recalculada dos dados carregados.
Relações são associações exploratórias, nunca causalidade.
"""

import streamlit as st

from comum import fmt_dec, fmt_int, pam, pib, ppm
from data import ANO_PIB_FIM, ANO_VAB_FIM, pib_por_municipio
from insights import (
    correlacao_valor_vab_por_ano,
    crescimento_brasil,
    crescimento_especie,
    lider_por_hectare,
    lideres_valor_por_cultura,
    maior_diferenca_plantada_colhida,
    metrica_por_cultura_estado,
    municipio_pib_e_agro,
    municipios_crescimento_pib,
    municipios_lideres_especie,
    participacao_especie_estado,
    pib_estado,
    quadro_municipal,
    sga_caso,
    spearman,
    top_participacao_agro,
    vab_estado_ce,
    variacoes_anuais_corr,
)

st.title("Sínteses e perguntas")
st.caption(
    "Todas as respostas são calculadas a partir das bases tratadas a cada carregamento. "
    "Associações não são apresentadas como causalidade."
)

DADOS_PAM, DADOS_PPM, DADOS_PIB = pam(), ppm(), pib()
QUADRO = quadro_municipal(DADOS_PAM, DADOS_PPM, DADOS_PIB, ANO_VAB_FIM)


def br_num(valor: float, casas: int = 1) -> str:
    return f"{valor:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def dinheiro(mil_reais: float) -> str:
    if mil_reais is None:
        return "—"
    reais = mil_reais * 1000
    if abs(reais) >= 1e9:
        return f"R$ {br_num(reais / 1e9)} bilhões"
    if abs(reais) >= 1e6:
        return f"R$ {br_num(reais / 1e6)} milhões"
    return f"R$ {br_num(reais / 1e3, 0)} mil"


def qa(pergunta: str, resposta: str) -> None:
    st.markdown(f"**{pergunta}**")
    st.markdown(resposta)


# ===========================================================================
# Destaques (calculados)
# ===========================================================================
st.subheader("Destaques")
rho_agro, n_agro = spearman(QUADRO, "valor_total", "vab_agro")
rho_pct, n_pct = spearman(QUADRO, "valor_total", "pct_vab_agro")
caso = sga_caso(DADOS_PIB, 2003, ANO_PIB_FIM, ANO_VAB_FIM)
est = pib_estado(DADOS_PIB, 2003, ANO_PIB_FIM)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Valor agrícola × VAB agro", f"ρ = {fmt_dec(rho_agro, 3)}" if rho_agro is not None else "—",
              help=f"Spearman entre municípios, {ANO_VAB_FIM}, n = {n_agro}.")
with col2:
    st.metric("Produção × participação", f"ρ = {fmt_dec(rho_pct, 3)}" if rho_pct is not None else "—",
              help="Valor das culturas × participação da agropecuária. Dimensões diferentes.")
with col3:
    st.metric("Crescimento do PIB do Ceará", f"{est['fator']}×" if est else "—", help="2003→2023, nominal.")
with col4:
    st.metric("São Gonçalo do Amarante", f"{caso['fator']}×" if caso and caso["fator"] else "—",
              help="Crescimento do PIB, com participação agropecuária em queda.")

# ===========================================================================
# Perguntas e respostas
# ===========================================================================
st.subheader("Perguntas e respostas")

# --- PAM ---
with st.expander("PAM — Agricultura", expanded=False):
    area = metrica_por_cultura_estado(DADOS_PAM, "area_plantada", 2024)
    quant = metrica_por_cultura_estado(DADOS_PAM, "quantidade", 2024)
    rend = metrica_por_cultura_estado(DADOS_PAM, "rendimento", 2024)
    valor = metrica_por_cultura_estado(DADOS_PAM, "valor_producao", 2024)
    lideres = lideres_valor_por_cultura(DADOS_PAM, 2024)

    topo_area = area.idxmax()
    qa("Qual cultura ocupou mais área em 2024?",
       f"{topo_area}, com {fmt_int(area[topo_area])} hectares plantados.")
    topo_quant = quant.idxmax()
    qa("Qual cultura produziu mais toneladas em 2024?",
       f"{topo_quant}, com {fmt_int(quant[topo_quant])} toneladas.")
    topo_rend = rend.idxmax()
    qa("Qual cultura teve maior rendimento médio?",
       f"{topo_rend}, com {fmt_int(rend[topo_rend])} kg/ha em 2024.")
    topo_valor = valor.idxmax()
    share = valor[topo_valor] / valor.sum() * 100
    qa("Qual cultura gerou maior valor da produção?",
       f"{topo_valor}, com cerca de {dinheiro(valor[topo_valor])}, "
       f"representando {fmt_dec(share)}% do valor das sete culturas analisadas.")
    qa("Ter mais área plantada significa gerar mais valor econômico?",
       f"Não. O milho utilizou cerca de {fmt_int(area['Milho (em grão)'])} hectares e gerou "
       f"{dinheiro(valor['Milho (em grão)'])}, enquanto a banana utilizou apenas cerca de "
       f"{fmt_int(area['Banana (cacho)'])} hectares e gerou {dinheiro(valor['Banana (cacho)'])}.")
    lider_ha = lider_por_hectare(DADOS_PAM, 2024)
    qa("Qual cultura gerou mais valor bruto por hectare colhido?",
       f"{lider_ha['produto']}, com cerca de R$ {br_num(lider_ha['valor'] / 1000)} mil por hectare em 2024."
       if lider_ha else "Sem área colhida positiva para calcular.")
    dif_milho = maior_diferenca_plantada_colhida(DADOS_PAM, "Milho (em grão)")
    qa("Toda área plantada de milho virou área colhida?",
       (f"Não. Em {dif_milho['ano']} houve uma diferença de {fmt_int(dif_milho['dif'])} hectares, "
        f"equivalente a cerca de {fmt_dec(dif_milho['pct'])}% da área plantada.")
       if dif_milho else "No período disponível, a área plantada de milho foi sempre colhida.")
    if lideres:
        qa("Quais municípios lideraram cada cultura em valor da produção em 2024?",
           " · ".join(f"{c}: {m}" for c, m in sorted(lideres.items(), key=lambda x: x[0].lower())) + ".")

# --- PPM ---
with st.expander("PPM — Pecuária", expanded=False):
    rebanhos = DADOS_PPM[
        (DADOS_PPM["nivel_territorial_codigo"] == "N3")
        & (DADOS_PPM["territorio_codigo"] == "23")
        & (DADOS_PPM["ano_codigo"] == 2024)
    ].set_index("especie")["valor"]
    topo_reb = rebanhos.idxmax()
    qa("Qual é o rebanho mais numeroso do Ceará?",
       f"{topo_reb}, com cerca de {fmt_int(rebanhos[topo_reb])} cabeças em 2024.")
    cresc_esp = crescimento_especie(DADOS_PPM, "N3", "23", 2003, 2024)
    if len(cresc_esp) >= 2:
        qa("Qual espécie mais cresceu entre 2003 e 2024?",
           f"{cresc_esp.iloc[0]['especie']}, com crescimento de cerca de {br_num(cresc_esp.iloc[0]['fator'], 2)}×. "
           f"{cresc_esp.iloc[1]['especie']} ficou em segundo, com cerca de {br_num(cresc_esp.iloc[1]['fator'], 2)}×.")
    pct_gali = participacao_especie_estado(DADOS_PPM, 2024, "Galináceos")
    qa("Quanto os galináceos representam entre os cinco rebanhos analisados?",
       f"Cerca de {fmt_dec(pct_gali)}% de todas as cabeças." if pct_gali is not None else "—")
    lideres_reb = municipios_lideres_especie(DADOS_PPM, 2024)
    if not lideres_reb.empty:
        qa("Quais municípios se destacam em cada criação?",
           " · ".join(f"{r.especie}: {r.territorio_nome}" for r in lideres_reb.itertuples()) + ".")
    qa("Mais animais significa necessariamente mais dinheiro?",
       "Não. A PPM informa o número de cabeças, não faturamento, produção de carne, leite, ovos ou lucro.")

# --- Economia ---
with st.expander("Economia municipal", expanded=False):
    qa("Como o PIB do Ceará evoluiu entre 2003 e 2023?",
       f"Passou de cerca de {dinheiro(est['ini'])} para {dinheiro(est['fim'])}, um crescimento nominal "
       f"de cerca de {br_num(est['fator'])}×." if est else "—")
    qa("Esse crescimento representa crescimento real?",
       "Não necessariamente. Os valores são a preços correntes, portanto ainda contêm o efeito da inflação.")
    br_fator = crescimento_brasil(DADOS_PIB, 2003, ANO_PIB_FIM)
    if est and br_fator:
        qa("O Ceará cresceu proporcionalmente mais do que o Brasil?",
           f"No período, sim em valores nominais: Ceará cerca de {br_num(est['fator'])}× e Brasil "
           f"cerca de {br_num(br_fator)}×.")
    topo_pib = pib_por_municipio(DADOS_PIB, "pib", ANO_PIB_FIM).nlargest(1, "pib")
    if not topo_pib.empty:
        qa("Qual município possui o maior PIB do Ceará?",
           f"{topo_pib.iloc[0]['municipio']}, com cerca de {dinheiro(topo_pib.iloc[0]['pib'])} em {ANO_PIB_FIM}.")
    if caso and caso["fator"]:
        qa("Qual município mais cresceu proporcionalmente entre 2003 e 2023?",
           f"São Gonçalo do Amarante, cerca de {br_num(caso['fator'])}×.")
    cresceu = municipios_crescimento_pib(DADOS_PIB, 2003, ANO_PIB_FIM)
    if cresceu:
        qa("Quais foram os municípios que mais cresceram proporcionalmente?",
           ", ".join(cresceu) + ".")
    vab_2003 = vab_estado_ce(DADOS_PIB, 2003)
    vab_2021 = vab_estado_ce(DADOS_PIB, ANO_VAB_FIM)
    qa("Quanto de riqueza foi criada pelas atividades econômicas do Ceará?",
       f"O valor adicionado bruto total passou de cerca de {dinheiro(vab_2003['vab_total'])} em 2003 "
       f"para {dinheiro(vab_2021['vab_total'])} em 2021."
       if vab_2003["vab_total"] is not None else "—")
    qa("Quanto da riqueza criada em 2021 veio da agropecuária?",
       f"Aproximadamente {dinheiro(vab_2021['vab_agro'])}." if vab_2021["vab_agro"] is not None else "—")
    if vab_2021["pct"] is not None:
        qa("Qual porcentagem do VAB do Ceará veio da agropecuária em 2021?",
           f"Aproximadamente {fmt_dec(vab_2021['pct'])}%, enquanto as demais atividades "
           f"representaram {fmt_dec(100 - vab_2021['pct'])}%.")
    topo_pct = top_participacao_agro(DADOS_PIB, ANO_VAB_FIM)
    if not topo_pct.empty:
        qa("Quais municípios possuem maior participação da agropecuária em sua economia?",
           ", ".join(f"{r.municipio} ({fmt_dec(r.pct)}%)" for r in topo_pct.itertuples()) + " lideram.")
    if caso and caso["pct_fim"] is not None:
        qa("O crescimento de São Gonçalo do Amarante veio da agropecuária?",
           "Não. Os dados mostram uma transformação muito mais ligada à indústria; a participação "
           f"da agropecuária ficou muito pequena ({caso['pct_ini']}% → {caso['pct_fim']}%).")

# --- Cruzamentos ---
with st.expander("Perguntas e respostas dos cruzamentos", expanded=False):
    qa("Municípios com maior valor da produção agrícola também tendem a gerar mais riqueza pela agropecuária?",
       f"Sim. Em {ANO_VAB_FIM}, a correlação de Spearman foi de cerca de {fmt_dec(rho_agro, 2)}, "
       "uma associação positiva forte.")
    serie_ano = correlacao_valor_vab_por_ano(DADOS_PAM, DADOS_PIB, 2003, ANO_VAB_FIM).dropna(subset=["rho"])
    if not serie_ano.empty:
        qa("Essa relação apareceu somente em 2021?",
           f"Não. Entre 2003 e {ANO_VAB_FIM} ela permaneceu forte, com valores anuais entre "
           f"{fmt_dec(serie_ano['rho'].min(), 2)} e {fmt_dec(serie_ano['rho'].max(), 2)}.")
    variacoes = variacoes_anuais_corr(DADOS_PAM, DADOS_PIB, 2003, ANO_VAB_FIM)
    if variacoes["pearson"] is not None:
        qa("Quando olhamos o Ceará inteiro ao longo do tempo, PAM e VAB agropecuário caminham juntos?",
           f"Sim. As variações anuais apresentaram correlação próxima de {br_num(variacoes['pearson'], 2)} (Pearson).")
    qa("Municípios com mais animais também tendem a possuir maior VAB da agropecuária?",
       "Sim, mas a força varia conforme o rebanho.")
    correl_esp = {
        e: spearman(QUADRO, f"efetivo_{e}", "vab_agro")[0]
        for e in ("galinaceos", "bovino", "suino", "ovino", "caprino")
    }
    correl_esp = {k: v for k, v in correl_esp.items() if v is not None}
    if correl_esp:
        ordem = sorted(correl_esp, key=correl_esp.get, reverse=True)
        nomes = {"galinaceos": "galináceos", "bovino": "bovinos", "suino": "suínos", "ovino": "ovinos", "caprino": "caprinos"}
        qa("Quais rebanhos apresentaram maior associação em 2021?",
           "; ".join(f"{nomes[e]} {fmt_dec(correl_esp[e], 2)}" for e in ordem) + ".")
        qa("Essa relação é tão forte quanto a da agricultura?",
           "Não. O valor das culturas apresentou uma relação mais forte com o VAB agropecuário.")
    pares = {}
    for cultura in ("milho", "feijao"):
        for especie in ("bovino", "ovino", "caprino", "suino"):
            pares[f"{cultura} × {especie}"] = spearman(QUADRO, f"area_{cultura}", f"efetivo_{especie}")[0]
    pares = {k: v for k, v in pares.items() if v is not None}
    if pares:
        melhor = max(pares, key=pares.get)
        qa("Qual foi a relação mais forte encontrada entre culturas e rebanhos?",
           f"{melhor}, com correlação de cerca de {fmt_dec(pares[melhor], 2)}.")
        qa("Isso significa que plantar milho causa aumento de bovinos?",
           "Não. Significa apenas que essas atividades aparecem juntas com mais frequência nos mesmos municípios.")
    melao = [spearman(QUADRO, "area_melao", f"efetivo_{e}")[0] for e in ("bovino", "ovino", "caprino", "suino", "galinaceos")]
    melao = [r for r in melao if r is not None]
    qa("Todas as culturas apresentaram relação com a pecuária?",
       "Não. O melão apresentou correlações próximas de zero com praticamente todos os rebanhos analisados."
       if melao and max(abs(r) for r in melao) < 0.1 else "Não há padrão único entre culturas e rebanhos.")
    qa("Um município que produz muito possui grande participação agropecuária na economia?",
       f"Não. A relação entre o valor das sete culturas e a participação agropecuária foi relativamente "
       f"fraca, cerca de {fmt_dec(rho_pct, 2)}.")
    sj = municipio_pib_e_agro(DADOS_PIB, "São João do Jaguaribe", ANO_VAB_FIM)
    be = municipio_pib_e_agro(DADOS_PIB, "Beberibe", ANO_VAB_FIM)
    qa("Ter maior participação percentual significa gerar mais riqueza agropecuária em reais?",
       "Não. Participação percentual e valor absoluto são dimensões diferentes.")
    if sj and be and sj["pct"] is not None and be["pct"] is not None:
        qa("Exemplo?",
           f"São João do Jaguaribe tinha cerca de {fmt_dec(sj['pct'])}% da economia ligada à agropecuária, "
           f"mas VAB agropecuário de cerca de {dinheiro(sj['vab_agro'])}. Beberibe tinha participação menor, "
           f"{fmt_dec(be['pct'])}%, mas cerca de {dinheiro(be['vab_agro'])} de VAB agropecuário.")
    qa("PIB alto significa município agropecuário?",
       "Não. Fortaleza e São Gonçalo do Amarante são exemplos claros.")

# --- Insights gerais ---
st.subheader("Insights que encontramos")

CORES_TEMA = {
    "Agricultura": "#c92032",
    "Pecuária": "#317a70",
    "Economia": "#315c8d",
    "Relações entre bases": "#a45f23",
}


def bloco_insights(titulo: str, itens: list[str]) -> None:
    cor = CORES_TEMA[titulo]
    lista = "".join(f"<li>{item}</li>" for item in itens)
    st.markdown(
        f"<div style='border-left:4px solid {cor}; background:#fbfbfb; padding:12px 16px; "
        f"border-radius:6px; margin:10px 0;'>"
        f"<strong style='color:{cor}; font-size:0.95rem'>{titulo}</strong>"
        f"<ul style='margin:6px 0 0 18px; color:#1e2936'>{lista}</ul></div>",
        unsafe_allow_html=True,
    )

col_a, col_b = st.columns(2)
with col_a:
    bloco_insights("Agricultura", [
        "Área, quantidade, produtividade e valor econômico contam histórias diferentes.",
        "Ter mais terra não significa gerar mais valor.",
        "A banana lidera em valor econômico entre as sete culturas.",
        "O milho ocupa a maior área, mas não lidera em valor.",
        "O melão usa pouca área, mas tem o maior valor bruto por hectare colhido.",
        "Existem especializações agrícolas municipais diferentes pelo Ceará.",
    ])
    bloco_insights("Pecuária", [
        "Os galináceos dominam numericamente a pecuária, mas cabeças não representam valor econômico.",
        "Tauá se destaca simultaneamente em caprinos e ovinos.",
    ])
with col_b:
    bloco_insights("Economia", [
        "Fortaleza concentra grande parte da economia estadual, mas quase não depende da agropecuária.",
        "São Gonçalo do Amarante é um grande outlier de crescimento, não puxado pela agropecuária.",
        "Uma economia municipal pode ser muito grande e pouco agropecuária.",
    ])
    bloco_insights("Relações entre bases", [
        "A relação mais clara foi valor da produção agrícola × VAB da agropecuária.",
        "A pecuária também se relaciona à riqueza agropecuária, mas de forma menos direta.",
        "Milho e feijão aparecem em municípios com maiores rebanhos; o melão, não.",
        "Participação percentual e valor absoluto são dimensões diferentes.",
        "Correlação não significa causalidade: são associações, não causa e efeito.",
    ])

st.info(
    "**Insight geral:** agricultura, pecuária e estrutura econômica municipal estão relacionadas, mas de formas "
    "diferentes. O valor da produção agrícola tem associação forte com a riqueza agropecuária, enquanto os "
    "rebanhos têm relações mais moderadas. Produzir muito não significa, necessariamente, que a agropecuária "
    "tenha grande peso na economia municipal."
)

st.caption(
    "Cada resposta é recalculada das bases a cada carregamento. Nenhum valor é fixo. "
    "Relações fracas, negativas ou inexistentes permanecem visíveis."
)
