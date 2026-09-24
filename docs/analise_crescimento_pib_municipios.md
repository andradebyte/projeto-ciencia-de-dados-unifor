# Análise: Crescimento do PIB dos Municípios do Ceará (2003–2023)

Este documento reúne os resultados das análises geoespacial e setorial do PIB municipal, produzidas em `notebooks/analise_exploratoria_pib_geoespacial.ipynb` e `notebooks/analise_pib_setorial.ipynb`. Aqui só os resultados e as conclusões — o código-fonte está nos respectivos notebooks.

---

## Parte 1: Mapa de crescimento e ranking (2003 → 2023)

Para cada um dos 184 municípios do Ceará, calculou-se o fator de crescimento do PIB a preços correntes entre 2003 e 2023 (`PIB_2023 / PIB_2003`), com nomes de município identificados no mapa coroplético e listados em ranking no terminal.

### Top 10 municípios que mais cresceram

| Posição | Município | Crescimento (2003→2023) |
|---|---|---|
| 1 | São Gonçalo do Amarante - CE | 70,0x |
| 2 | Itaitinga - CE | 38,4x |
| 3 | Jijoca de Jericoacoara - CE | 26,6x |
| 4 | Pereiro - CE | 21,8x |
| 5 | Aquiraz - CE | 17,8x |
| 6 | Frecheirinha - CE | 16,2x |
| 7 | Uruoca - CE | 14,0x |
| 8 | Cruz - CE | 13,9x |
| 9 | Quixeré - CE | 11,8x |
| 10 | Beberibe - CE | 11,5x |

São Gonçalo do Amarante se destaca isoladamente: quase o dobro do segundo colocado (Itaitinga).

---

## Parte 2: Por que São Gonçalo do Amarante cresceu tanto?

### Base de dados usada

O dataset original do projeto (`data/processed/pib_tratado.csv`) só tem PIB total e VAB agropecuário — não permite isolar indústria/serviços. Para investigar a causa do crescimento, foi necessário buscar uma base adicional: **VAB setorial por município** (agropecuária, indústria, serviços, administração pública), obtida diretamente da API do IBGE (agregado SIDRA 5938, mesma tabela do projeto, variáveis setoriais 513/517/6575/525).

**Limitação de dados**: o IBGE ainda não divulgou o VAB setorial de 2022 e 2023 (mesmo gap já registrado em `data/fontes.csv` para a base original). Por isso a análise setorial usa o último ano disponível: **2021**.

### Composição setorial de São Gonçalo do Amarante

| Setor | Participação 2003 | Participação 2021 | Crescimento do setor |
|---|---|---|---|
| Agropecuária | 14,0% | 0,7% | 3,8x |
| Indústria | 9,8% | **74,3%** | **592,8x** |
| Serviços | 40,5% | 20,6% | 39,8x |
| Administração pública | 35,7% | 4,4% | 9,7x |

A indústria passou de menos de 10% do PIB municipal para quase três quartos dele, com crescimento absoluto de quase 600 vezes — disparadamente o fator dominante.

### É um padrão do estado ou um caso isolado?

Calculou-se a correlação, entre os 184 municípios, entre a participação da indústria no VAB em 2003 e o crescimento total do PIB até 2021:

> **Correlação: -0,021** (praticamente nula)

Ou seja, não existe um padrão estadual em que "município mais industrializado cresce mais" — o resultado de São Gonçalo do Amarante é um **efeito concentrado e pontual**, não uma tendência geral.

### Conclusão

O crescimento de 70x do PIB de São Gonçalo do Amarante é explicado por uma transformação estrutural do município de base agropecuária/administrativa para base industrial, compatível com a instalação do **Complexo Industrial e Portuário do Pecém** (siderúrgica CSP, refinaria, porto) no período. A ausência de correlação geral entre indústria e crescimento no restante do estado reforça que não é um efeito setorial difuso, e sim um investimento específico e localizado.

### Próximo passo, se aprofundar

Para confirmar a hipótese do Complexo do Pecém com mais precisão (e não apenas por composição setorial agregada), seria necessário cruzar com bases que o projeto ainda não tem: RAIS/CAGED (abertura de vínculos formais por CNAE e ano, no município) ou histórico de investimento/instalação de empresas do complexo.
