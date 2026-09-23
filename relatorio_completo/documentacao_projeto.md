# Documentação Completa do Projeto

> **Projeto de Ciência de Dados — Tema 2: Agropecuária e Transformação Econômica**
> Equipe: Grupo C · Repositório: [github.com/andradebyte/projeto-ciencia-de-dados-unifor](https://github.com/andradebyte/projeto-ciencia-de-dados-unifor)

Este documento reúne **tudo** que você precisa saber sobre o projeto: o que é, de onde vieram os dados, o que cada base contém, o que foi feito com elas, o que descobrimos, os cuidados metodológicos e como reproduzir qualquer etapa. É a referência única para entender, apresentar ou dar continuidade ao trabalho.

---

## Sumário

1. [O que é o projeto](#1-o-que-é-o-projeto)
2. [Contexto, problema e pergunta central](#2-contexto-problema-e-pergunta-central)
3. [Equipe e papéis](#3-equipe-e-papéis)
4. [Os datasets (fontes de dados)](#4-os-datasets-fontes-de-dados)
5. [Estrutura do repositório](#5-estrutura-do-repositório)
6. [Pipeline de preparação dos dados](#6-pipeline-de-preparação-dos-dados)
7. [Diagnóstico de qualidade (o que encontramos de "sujo")](#7-diagnóstico-de-qualidade)
8. [Análise exploratória — PIB](#8-análise-exploratória--pib)
9. [Análise exploratória — PAM](#9-análise-exploratória--pam)
10. [Análise exploratória — PPM](#10-análise-exploratória--ppm)
11. [Cruzamento das bases (PAM × PPM × PIB)](#11-cruzamento-das-bases)
12. [Estudos de caso](#12-estudos-de-caso)
13. [Visualizações geoespaciais (mapas)](#13-visualizações-geoespaciais-mapas)
14. [Dashboard (protótipo Streamlit)](#14-dashboard-protótipo-streamlit)
15. [Limitações e cuidados metodológicos](#15-limitações-e-cuidados-metodológicos)
16. [Números-chave (resumo rápido)](#16-números-chave-resumo-rápido)
17. [Como rodar / reproduzir](#17-como-rodar--reproduzir)
18. [Próximos passos](#18-próximos-passos)

---

## 1. O que é o projeto

É um projeto de **análise exploratória de dados** sobre a agropecuária dos municípios do Ceará e a sua relação com a economia local, usando **dados oficiais do IBGE** (SIDRA). O objetivo não é prever nem modelar causalidade, mas **descrever e entender** como o perfil agropecuário cearense mudou ao longo de duas décadas (2003–2024) e como isso se conecta com a transformação econômica dos municípios.

O trabalho cobre o ciclo completo de um projeto de dados:

1. **Coleta** — download programático via API do IBGE/SIDRA;
2. **Compreensão e inventário** — inspeção das bases, mapeamento de anomalias;
3. **Higienização e preparação** — pipeline automatizado de limpeza e padronização;
4. **Análise exploratória** — por base (PIB, PAM, PPM) e cruzada;
5. **Visualização** — gráficos, mapas coropléticos e um protótipo de dashboard;
6. **Comunicação** — relatórios, pitch e documentação.

O recorte territorial é o estado do **Ceará** (184 municípios), sempre com **Brasil** e **Ceará** como referências de comparação.

---

## 2. Contexto, problema e pergunta central

### Tema escolhido
**Agropecuária e transformação econômica.**

### O problema
Os municípios cearenses apresentam **trajetórias distintas de transformação agropecuária** ao longo das últimas duas décadas — tanto na composição produtiva (o que produzem) quanto na importância da agropecuária para a economia local. Muitos desses municípios estão no semiárido e são expostos a **instabilidades climáticas severas** (secas), o que pressiona suas matrizes produtivas.

### Pergunta central
> **Como o perfil agropecuário dos municípios cearenses se transformou entre 2003 e 2024, e como essas mudanças se relacionam com a sua estrutura econômica?**

### Hipótese de trabalho (linha de investigação)
A equipe investiga a associação entre:

- **perdas agrícolas** em lavouras vulneráveis (a "frustração de safra", evidenciada pela diferença entre área plantada e área colhida na base **PAM**);
- e a possível **adoção de estratégias de resiliência**, como o crescimento de rebanhos de **pequeno porte** (caprinos e ovinos, mapeados na base **PPM**);

e cruza essa transição "física" com a evolução da **participação do VAB agropecuário** no PIB municipal (base **PIB**), para dimensionar se essas mudanças reconfiguraram a **dependência econômica local**.

### Postura metodológica (importante)
A análise é **estritamente observacional e exploratória**. Isso significa:

- respeitamos a **defasagem temporal** das bases financeiras (o VAB só vai até 2021);
- **não formulamos conclusões causais** — correlação nunca é apresentada como causa.

---

## 3. Equipe e papéis

| Pessoa | Papel |
|---|---|
| Raquel Albuquerque Quirino | Problema, escopo e análise agrícola (PAM) |
| Amanda Lira Andrade Botelho | Qualidade e preparação dos dados |
| João Igor Vidal de Andrade | Integração e análise econômica (PIB) |
| Sofya Emily Oliveira | Análise pecuária (PPM) e wireframe do dashboard |

---

## 4. Os datasets (fontes de dados)

Todas as bases vêm do **SIDRA/IBGE**, baixadas pela API oficial (agregados v3), e foram armazenadas como CSV em `dados/raw/`. Os metadados completos (URLs, filtros, hashes SHA-256, horários de download) estão em `dados/fontes.csv`.

### 4.1 Visão geral das três tabelas

| Tabela SIDRA | Nome | Conteúdo | Período | Registros tratados |
|---|---|---|---|---|
| **5457** | PAM | Produção Agrícola Municipal | 2003–2024 | 143.220 |
| **3939** | PPM | Pesquisa Pecuária Municipal (efetivo dos rebanhos) | 2003–2024 | 20.460 |
| **5938** | PIB dos Municípios | PIB, VAB total, VAB agropecuário e participação | 2003–2023 | 15.624 |

Todos os arquivos contêm **Brasil** (`N1`), **Ceará** (`N3`) e os **184 municípios** cearenses (`N6`).

### 4.2 PAM — Produção Agrícola Municipal (tabela 5457)

A PAM foi baixada em **5 arquivos, um por variável** (para respeitar o limite da API). Cada arquivo tem **28.644 linhas**.

**Variáveis:**
- `8331` — Área plantada ou destinada à colheita (hectares)
- `216` — Área colhida (hectares)
- `214` — Quantidade produzida (toneladas)
- `112` — Rendimento médio da produção (kg/hectare)
- `215` — Valor da produção (Mil Reais)

**Produtos (classificação 782):**

| Código | Produto |
|---|---|
| 40122 | Milho (em grão) |
| 40112 | Feijão (em grão) |
| 40119 | Mandioca |
| 40106 | Cana-de-açúcar |
| 40136 | Banana (cacho) |
| 40143 | Castanha de caju |
| 40121 | Melão |

**Chave única:** `territorio_codigo + ano_codigo + produto_codigo + variavel_codigo`.

### 4.3 PPM — Pesquisa Pecuária Municipal (tabela 3939)

Um único arquivo com **20.460 linhas**.

**Variável:** `105` — Efetivo dos rebanhos (em **cabeças**).

**Espécies (classificação 79):**

| Código | Espécie |
|---|---|
| 2670 | Bovino |
| 2681 | Caprino |
| 2677 | Ovino |
| 32794 | Suíno (total) |
| 32796 | Galináceos (total) |

**Chave única:** `territorio_codigo + ano_codigo + tipo_rebanho_codigo`.

> **Atenção:** efetivo é **estoque** de animais; produção agrícola é **fluxo** anual. As medidas não são equivalentes e nunca devem ser somadas entre espécies.

### 4.4 PIB dos Municípios (tabela 5938)

Um único arquivo com **15.624 linhas**.

**Variáveis:**

| Código | Variável | Unidade |
|---|---|---|
| 37 | PIB a preços correntes | Mil Reais |
| 498 | VAB total a preços correntes | Mil Reais |
| 513 | VAB agropecuário a preços correntes | Mil Reais |
| 516 | Participação do VAB agropecuário no VAB total | % |

**Chave única:** `territorio_codigo + ano_codigo + variavel_codigo`.

> **Disponibilidade (crítico):** a variável `37` (PIB) está preenchida até **2023**. As variáveis `498`, `513` e `516` (VAB) estão preenchidas **só até 2021** — em 2022 e 2023 retornam `...` (não disponível) para todos os territórios. Isso define o "teto" de qualquer análise que dependa do VAB: **2021**.

### 4.5 Malha municipal (GeoJSON)

- `dados/raw/malha_municipal_ce_2022.geojson` — malha simplificada dos 184 municípios do Ceará (IBGE 2022), usada nos mapas coropléticos.
- Cada feição tem a propriedade `codarea` (código IBGE de 7 dígitos), que é a chave de junção com as tabelas.
- 184 feições, 184 `codarea` únicos, todos começando por `23`.
- Fonte: API de Malhas Geográficas do IBGE (v3).

### 4.6 Estrutura comum dos CSVs

Os arquivos são em **formato longo**, separados por `;`, codificados em **UTF-8 com BOM**. Colunas comuns:

- territoriais: `nivel_territorial_codigo`, `nivel_territorial_nome`, `territorio_codigo`, `territorio_nome`
- temporais: `ano_codigo`, `ano_nome`
- de métrica: `variavel_codigo`, `variavel_nome`, `unidade`, `valor`
- **PAM** acrescenta: `produto_codigo`, `produto_nome`
- **PPM** acrescenta: `tipo_rebanho_codigo`, `tipo_rebanho_nome`

---

## 5. Estrutura do repositório

```
projeto-ciencia-de-dados/
├── app/                      # Protótipo de dashboard (Streamlit)
│   └── main.py
├── dados/
│   ├── analytical/           # Bases cruzadas e limpas p/ análise
│   │   └── cruzamento_pam_ppm_pib.csv
│   ├── processed/            # Bases tratadas (saída do pipeline)
│   │   ├── pam_tratado.csv
│   │   ├── ppm_tratado.csv
│   │   └── pib_tratado.csv
│   ├── raw/                  # Bases brutas + malha municipal
│   │   ├── t5457_pam_*.csv   (5 arquivos)
│   │   ├── t3939_ppm_*.csv
│   │   ├── t5938_pib_*.csv
│   │   └── malha_municipal_ce_2022.geojson
│   ├── fontes.csv            # Metadados de download (URLs, hashes)
│   └── README_DADOS.md       # Documentação das bases
├── docs/                     # Relatórios e documentação
│   ├── acompanhamento.pdf
│   ├── analise_crescimento_pib_municipios.md
│   ├── relatorio_preparacao_dados.md
│   └── roteiro_pitch.md
├── notebooks/                # Análises interativas (origem dos .py)
├── src/                      # Código-fonte (pipeline + análises)
│   ├── data_loader.py
│   ├── data_cleaner.py
│   ├── data_standardizer.py
│   ├── pipeline.py
│   ├── analise_exploratoria_{pib,pam,ppm}.py
│   ├── analise_exploratoria_{pib,pam,ppm}_geoespacial.py
│   └── cruzamento_bases.py
├── requirements.txt
└── README.md
```

---

## 6. Pipeline de preparação dos dados

O pipeline (`src/pipeline.py`) orquestra **4 etapas** e transforma as bases brutas (`raw`) em bases tratadas (`processed`):

### Etapa 1 — Leitura (`src/data_loader.py`)
- Lê os 5 CSVs do PAM e os concatena; lê PPM e PIB individualmente.
- **Força tipagem como `string`** para `territorio_codigo`, `variavel_codigo`, `produto_codigo` e `tipo_rebanho_codigo`, preservando zeros à esquerda.

### Etapa 2 — Limpeza de duplicatas (`src/data_cleaner.py`)
- Remove duplicatas pela **chave primária oficial** de cada base, mantendo o último registro (`keep='last'`).
- Chaves:
  - PAM: `nivel_territorial_codigo + territorio_codigo + ano_codigo + variavel_codigo + produto_codigo`
  - PPM: `... + tipo_rebanho_codigo`
  - PIB: `... + variavel_codigo`

### Etapa 3 — Padronização (`src/data_standardizer.py`)
- `padronizar_colunas_e_categorias`: colunas para `snake_case` e `.strip()` nas categorias textuais.
- `tratar_simbolos_ausencias`: converte os símbolos especiais do IBGE na coluna `valor`:
  - `-` e `0` → `0.0`
  - `X`, `..`, `...` → `NaN`
  - cria a flag `valor_is_inibido` (1 quando o valor era `X`)
  - converte `valor` para numérico (`float`)

### Etapa 4 — Salvamento
- Grava `pam_tratado.csv`, `ppm_tratado.csv`, `pib_tratado.csv` em `dados/processed/`.

**Execução:**
```bash
python src/pipeline.py
```

---

## 7. Diagnóstico de qualidade

Durante a exploração, encontramos e quantificamos as seguintes anomalias:

### 7.1 Símbolos textuais em colunas numéricas
A coluna `valor` vinha com caracteres especiais no lugar de números (`-`, `0`, `X`, `..`, `...`).

### 7.2 Ausências reais (quantificação empírica)
- **1.116 registros ausentes** mascarados por `..`/`...` — **100% concentrados no PIB** (são exatamente o VAB 2022–2023 indisponível).
- PAM e PPM: **0** ocorrências desse tipo.

### 7.3 Sigilo estatístico (`X`)
- `X` = omissão intencional do IBGE para preservar o sigilo da fonte.
- No nosso recorte: **0 incidências** nas 3 bases.

### 7.4 Símbolo `-` (ausência de plantio/colheita)
- PAM: **314.670 ocorrências** de `-` (municípios que não plantam/colhem determinada cultura).
- PPM: apenas **5 ocorrências** (ampla cobertura dos rebanhos).

### 7.5 Inconsistências hierárquicas
- Na validação agregada, a soma dos municípios **não bateu** com o total oficial do estado em **298 recortes no PAM** e **66 no PIB**. (Ajustes de arredondamento/consolidação do IBGE.)

### 7.6 Integridade das chaves
- Necessidade de **preservar zeros à esquerda** nos códigos municipais (daí a tipagem forçada como string).

### 7.7 Volumetria final (pós-tratamento)
| Base | Registros |
|---|---|
| PAM | 143.220 |
| PPM | 20.460 |
| PIB | 15.624 |

---

## 8. Análise exploratória — PIB

Fonte do código: `src/analise_exploratoria_pib.py` e `..._pib_geoespacial.py`.

### Perguntas e respostas principais

**1. Como o PIB do Brasil e do Ceará evoluíram (2003–2023)?**
O PIB do Ceará saiu de **R$ 32,7 bi para R$ 232,2 bi** — um crescimento de **7,1×** em valores correntes.

**2. Quais municípios têm o maior PIB (2023)?**

| Posição | Município | PIB (Mil Reais) |
|---|---|---|
| 1 | Fortaleza | 86.939.832 |
| 2 | Maracanaú | 13.540.094 |
| 3 | Caucaia | 9.873.557 |
| 4 | São Gonçalo do Amarante | 6.908.373 |
| 5 | Sobral | 6.588.929 |
| 6 | Juazeiro do Norte | 6.457.543 |
| 7 | Eusébio | 4.940.352 |
| 8 | Aquiraz | 4.851.008 |
| 9 | Horizonte | 2.964.814 |
| 10 | Itapipoca | 2.550.371 |

**3. Quais municípios mais cresceram (2003 → 2023)?**

| Posição | Município | Fator |
|---|---|---|
| 1 | **São Gonçalo do Amarante** | **70,0×** |
| 2 | Itaitinga | 38,4× |
| 3 | Jijoca de Jericoacoara | 26,6× |
| 4 | Pereiro | 21,8× |
| 5 | Aquiraz | 17,8× |
| 6 | Frecheirinha | 16,2× |
| 7 | Uruoca | 14,0× |
| 8 | Cruz | 13,9× |
| 9 | Quixeré | 11,8× |
| 10 | Beberibe | 11,5× |

**4. Quanto cada município representa do PIB do Ceará?**
Fortaleza é dominante, mas perdeu espaço relativo: caiu de **46,6% (2003) para 37,4% (2023)**. A economia do estado ficou um pouco **menos concentrada** na capital.

**5. Quais municípios são mais dependentes da agropecuária (2021)?**

| Município | Participação do VAB agro |
|---|---|
| São João do Jaguaribe | 44,8% |
| Milhã | 42,9% |
| Varjota | 42,8% |
| Missão Velha | 40,0% |
| Guaraciaba do Norte | 40,0% |

E os **menos** dependentes: Fortaleza (0,2%), Maracanaú (0,2%), São Gonçalo do Amarante (0,7%), Juazeiro do Norte (0,7%), Itaitinga (0,7%).

**6. Top 10 VAB agropecuário (2021):** Beberibe (370.244), Tianguá, Limoeiro do Norte, Guaraciaba do Norte, Iguatu, Morada Nova, Missão Velha, Ubajara, São Benedito e Varjota (em Mil Reais).

### O caso São Gonçalo do Amarante (detalhado no estudo de caso, §12)

---

## 9. Análise exploratória — PAM

Fonte: `src/analise_exploratoria_pam.py` e `..._pam_geoespacial.py`.

### Perguntas e respostas principais

**1. Como evoluiu o valor da produção por produto no Ceará (2003–2024)?**
Todos os 7 produtos cresceram, mas em ritmos muito diferentes — **houve uma inversão de liderança**:

| Produto | 2003 (Mil R$) | 2024 (Mil R$) | Fator | Posição 2003 → 2024 |
|---|---|---|---|---|
| Banana | 104 | 905 | **8,7×** | 5ª → **1ª** |
| Milho | 282 | 457 | 1,6× | **1ª → 4ª** |
| Castanha de caju | 107 | 472 | 4,4× | — |
| Mandioca | 116 | 507 | 4,4× | — |
| Feijão | 221 | 403 | 1,8× | — |
| Melão | 50 | 91 | 1,8× | — |
| Cana-de-açúcar | 65 | 116 | 1,8× | — |

> A matriz produtiva do estado **migrou de grãos para fruticultura** (banana assumindo a liderança).

**2. A castanha de caju é um caso especial?**
Sim. Teve trajetória **não linear**: queda acentuada entre 2003 e 2010 (de R$ 107 mil para R$ 54 mil), depois recuperação até 4,4× em 2024. Sugere **choque específico do produto** (clima, praga ou preço) — registrado como algo a investigar, sem forçar conclusão.

**3. Quanto o Ceará representa da produção nacional?**
Calculado por métrica (valor, área plantada/colhida, quantidade), ano a ano — o peso relativo do Ceará varia por produto e métrica.

**4. Quais municípios concentram a produção (2023)?**
Top valor da produção (soma dos 7 produtos): Limoeiro do Norte (104.787), Salitre (97.219), Quixeré (85.979), Araripe (65.809), Guaraciaba do Norte (60.391) — em Mil Reais.

**5. Quais municípios mais cresceram (2003 → 2023)?**

| Município | Fator |
|---|---|
| Varjota | 19,4× |
| Apuiarés | 16,2× |
| Umirim | 10,6× |
| Palhano | 9,7× |
| Uruburetama | 9,6× |

**6. Existe frustração de safra (área plantada × colhida)?**
Sim — há um **hiato sistemático** entre área plantada e área colhida no Ceará ao longo dos anos. Essa é a peça central da hipótese de resiliência (municípios que perdem safra migrariam para atividades mais resistentes à seca).

**7. As métricas da PAM se correlacionam entre si?**
Sim — área plantada, colhida, quantidade e valor da produção são fortemente correlacionadas (esperado: são todas funções do tamanho da lavoura).

---

## 10. Análise exploratória — PPM

Fonte: `src/analise_exploratoria_ppm.py` e `..._ppm_geoespacial.py`.

### Perguntas e respostas principais

**1. Como evoluiu o efetivo de cada espécie no Ceará (2003–2023)?**

| Espécie | 2003 (cabeças) | 2023 (cabeças) | Fator |
|---|---|---|---|
| Bovino | 2.254.262 | 2.772.173 | 1,2× |
| Caprino | 869.045 | 1.156.632 | 1,3× |
| Ovino | 1.781.951 | 2.543.214 | **1,4×** |
| Suíno (total) | 1.067.314 | 1.278.548 | 1,2× |
| Galináceos (total) | 21.662.462 | 37.303.834 | **1,7×** |

> Nada "explodiu" como no PIB — aqui é **evolução gradual**. Galináceos (avicultura) e ovinos foram os que mais cresceram relativamente.

**2. Quais municípios lideram cada rebanho (2023)?**

| Espécie | Top 1 | Top 2 | Top 3 |
|---|---|---|---|
| Bovino | Morada Nova (101.048) | Quixeramobim (93.876) | Iguatu (74.273) |
| Caprino | Tauá (89.935) | Independência (57.893) | Aiuaba (53.852) |
| Ovino | Tauá (178.630) | Independência (125.415) | Morada Nova (80.260) |
| Suíno | Viçosa do Ceará (50.080) | Granja (47.025) | Massapê (42.120) |
| Galináceos | Beberibe (4.513.278) | Quixadá (3.923.415) | Horizonte (3.017.237) |

**3. As espécies se correlacionam?**
Sim — na variação % ano a ano (calculada assim de propósito para evitar o viés de tendência comum, já que todas cresceram). A correlação indica municípios de **agricultura familiar mista** (pequenos rebanhos criados juntos).

---

## 11. Cruzamento das bases

Fonte: `src/cruzamento_bases.py` e `notebooks/insights_cruzamento.ipynb`.

### Como foi feito
As três bases foram integradas pela **chave `territorio_codigo` (código IBGE) + `ano`**, usando `outer join`. Regras respeitadas:

- produtos da PAM e espécies da PPM **nunca são somados entre si** (cada um vira uma coluna própria);
- valores monetários são **correntes** (não deflacionados);
- períodos diferentes (PAM/PPM até 2024, PIB até 2023, VAB até 2021) geram `NaN` fora do período de cada base.

### Resultado do cruzamento
- **4.048 linhas** (184 municípios × 22 anos).
- **3.864 (95,5%)** têm as 3 bases presentes simultaneamente (limitado pelos 21 anos do PIB).
- **184 linhas (4,5%)** são só de 2024 (PAM e PPM sem PIB) — defasagem temporal esperada, não erro de chave.

### Insights de correlação

**1. Existe correlação entre as bases?**
Sim, e as mais fortes *entre bases diferentes* são:
- **valor da banana × VAB agropecuário: +0,64** — municípios que produzem mais banana tendem a ter VAB agropecuário maior (banana puxa a base econômica agrícola local).
- área plantada/colhida de **milho e feijão × efetivo de bovino/ovino/caprino: ~0,5** — indício de que são os **mesmos municípios de agricultura familiar mista**, não que uma coisa cause a outra.

**2. A correlação banana × VAB agro é estável?**
Sim. Fica **sempre entre +0,52 e +0,78** ao longo dos 19 anos com dado — relação estável, não artefato de juntar tudo.

**3. Índice exploratório valor agrícola / VAB agropecuário**
Em alguns municípios pequenos, o valor bruto da produção agrícola (PAM) **supera o VAB agropecuário declarado** no PIB (índice > 100%). É um índice exploratório, não oficial, e não substitui o VAB.

---

## 12. Estudos de caso

### 12.1 São Gonçalo do Amarante — por que cresceu 70×?

**O fenômeno:** PIB cresceu **~70×** entre 2003 e 2023, disparadamente o maior do estado (quase o dobro do segundo, Itaitinga com 38×).

**O que o dado mostra (composição setorial):**

| Setor | 2003 | 2021 | Crescimento |
|---|---|---|---|
| Agropecuária | 14,0% | 0,7% | 3,8× |
| **Indústria** | 9,8% | **74,3%** | **592,8×** |
| Serviços | 40,5% | 20,6% | 39,8× |
| Administração pública | 35,7% | 4,4% | 9,7× |

A **indústria** passou de <10% para ~3/4 do PIB municipal. É uma transformação estrutural de base agropecuária/administrativa para **base industrial**.

**É um padrão do estado ou caso isolado?**
Correlação (entre os 184 municípios) entre "participação da indústria em 2003" × "crescimento do PIB": **-0,021** (praticamente nula). Não há tendência estadual de "município industrializado cresce mais" — é um **efeito concentrado e pontual**.

**O cruzamento confirma:** as colunas de PAM e PPM **não acompanham** o salto do PIB. Bovino, caprino e ovino **caíram** (0,6×–0,7×); só suíno (2,8×) e galináceos (1,6×) cresceram. Ou seja, o crescimento **não é agropecuário**.

**Conclusão (como hipótese, não como dado):** compatível com a instalação do **Complexo Industrial e Portuário do Pecém** (siderúrgica CSP, refinaria, porto) no município. Para confirmar com rigor, seria preciso cruzar com RAIS/CAGED ou histórico de investimentos.

### 12.2 Várzea Alegre — o "311,8×" que engana

O maior crescimento do cruzamento inteiro é **311,8×** no valor da produção de mandioca em Várzea Alegre. Investigamos se era real:

- Em **2003**, o município produzia mandioca em apenas **2 hectares**, gerando **R$ 4 mil** (base quase zero).
- Em 2023, saltou para **R$ 1.247 mil**.

O dado é real, mas o fator é **enganoso**: o denominador de 2003 era minúsculo.

**Lição metodológica:** *fator de crescimento em município pequeno deve sempre vir acompanhado do valor absoluto* — senão qualquer salto de "quase nada" para "pouco" parece recorde.

---

## 13. Visualizações geoespaciais (mapas)

Fonte: `src/analise_exploratoria_{pib,pam,ppm}_geoespacial.py`, usando a malha municipal (`codarea`).

**PIB:**
- Mapa do PIB por município em 2023 (e 2003).
- Mapa de **crescimento do PIB (2003 → 2023)** — destaca São Gonçalo do Amarante.
- Mapa de **dependência da agropecuária** (participação do VAB agro no VAB total).

**PAM:**
- Mapa do valor da produção agrícola por município (2023 e 2003).
- Mapa de **crescimento do valor de produção**.
- Mapa de **perda de safra** (diferença área plantada × colhida) entre municípios.

**PPM:**
- Mapas de efetivo por espécie (bovino, caprino, ovino, suíno, galináceos), 2023 e 2003, e mapas de crescimento de cada uma.

> A malha vem simplificada do IBGE e tem pequenas auto-interseções em 5 municípios (Acaraú, Barbalha, Crateús, Limoeiro do Norte, Mauriti), que não impedem os mapas coropléticos.

---

## 14. Dashboard (protótipo Streamlit)

- `app/main.py` — protótipo funcional, atualmente focado na **PAM**:
  - filtros de território, variável e produtos;
  - gráfico de linha (`st.line_chart`) da métrica escolhida ao longo dos anos;
  - tabela expandível com os dados.
- `docs/acompanhamento.pdf` descreve o **wireframe completo** (Pessoa 4), com:
  - painel lateral de filtros (município, período 2003–2024, culturas, rebanhos, variável de mapa);
  - 4 cartões de indicadores (taxa de frustração de safra, crescimento de rebanhos, municípios resilientes, participação do VAB agro no PIB);
  - série temporal (frustração × crescimento de caprinos/ovinos) + mapa coroplético;
  - cruzamento PAM × PPM × PIB em dispersão de bolhas, com abas de ranking e tabela exportável.

---

## 15. Limitações e cuidados metodológicos

1. **Defasagem temporal:** VAB (total/agropecuário/participação) só vai até **2021**; PIB até 2023; PAM/PPM até 2024. Cruzamentos que dependem de VAB param em 2021.
2. **Valores correntes (nominais):** PIB, VAB e valor da produção **não estão corrigidos pela inflação**. Crescimento "7,1×" é nominal, não real.
3. **Estoque vs. fluxo:** efetivo de rebanhos (estoque) não é comparável diretamente a produção agrícola (fluxo anual).
4. **Não somar:** rendimentos médios entre produtos; subcategorias de suínos/galináceos (já são totais); Brasil e Ceará nas somas municipais.
5. **Caráter observacional:** correlações são associações, **não causalidade**.
6. **Sigilo estatístico (`X`):** não ocorreu no nosso recorte, mas o pipeline o trata e cria a flag `valor_is_inibido`.
7. **Inconsistências de consolidação:** soma dos municípios difere do total oficial em 298 recortes (PAM) e 66 (PIB).
8. **Pecém é hipótese:** a atribuição do crescimento de São Gonçalo do Amarante ao Complexo do Pecém é interpretação da equipe, sustentada pela composição setorial, não uma conclusão direta dos dados.

---

## 16. Números-chave (resumo rápido)

| Indicador | Valor |
|---|---|
| Municípios analisados | 184 |
| Período | 2003–2024 (PIB até 2023; VAB até 2021) |
| PIB do Ceará (2003 → 2023) | R$ 32,7 bi → R$ 232,2 bi (**7,1×**) |
| Maior crescimento de PIB | São Gonçalo do Amarante (**70×**) |
| Indústria no VAB de SGA (2003 → 2021) | 9,8% → 74,3% (**592×**) |
| Correlação indústria × crescimento (estado) | -0,021 (nula) |
| Maior crescimento PAM | Banana (**8,7×**; 5ª → 1ª) |
| Menor crescimento PAM | Milho (1,6×; 1ª → 4ª) |
| Maior crescimento PPM | Galináceos (1,7×), Ovino (1,4×) |
| Correlação mais forte (entre bases) | Banana × VAB agro (**+0,64**, estável) |
| Registros tratados | PAM 143.220 · PPM 20.460 · PIB 15.624 |
| Linhas do cruzamento | 4.048 (95,5% com as 3 bases) |

---

## 17. Como rodar / reproduzir

```bash
# 1. (opcional) criar ambiente
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. rodar o pipeline de preparação (raw -> processed)
python src/pipeline.py

# 3. gerar o cruzamento (processed -> analytical)
python src/cruzamento_bases.py

# 4. análises exploratórias (geram gráficos/rankings no terminal)
python src/analise_exploratoria_pib.py
python src/analise_exploratoria_pam.py
python src/analise_exploratoria_ppm.py
python src/analise_exploratoria_pib_geoespacial.py
python src/analise_exploratoria_pam_geoespacial.py
python src/analise_exploratoria_ppm_geoespacial.py

# 5. dashboard (protótipo)
streamlit run app/main.py
```

> Os scripts `.py` são a versão exportada dos notebooks em `notebooks/`. Os notebooks são a fonte original das análises e gráficos.

---

## 18. Próximos passos

1. **Confirmar o Pecém:** cruzar com **RAIS/CAGED** (vínculos formais por CNAE e ano) ou histórico de investimentos/instalação de empresas do Complexo do Pecém.
2. **Crescimento real:** deflacionar PIB, VAB e valor da produção (correção de preços) para medir crescimento real, não nominal.
3. **Investigar a castanha de caju:** entender o choque 2003–2010 (clima, praga ou preço).
4. **Aprofundar a hipótese de resiliência:** modelar a relação entre frustração de safra e adoção de caprinos/ovinos, com cuidado para não inferir causalidade.
5. **Evoluir o dashboard:** implementar o wireframe completo (mapa interativo + cruzamento) além do protótipo atual focado na PAM.
6. **Correções de geometria:** aplicar `make_valid()` nas 5 feições da malha se forem necessárias operações espaciais.
