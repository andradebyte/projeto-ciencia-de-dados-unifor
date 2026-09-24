# Projeto de Ciência de Dados — Agropecuária do Ceará (IBGE)

Análise exploratória e dashboard sobre a agropecuária dos 184 municípios do Ceará, com base em dados oficiais do IBGE (SIDRA): Produção Agrícola Municipal (PAM), Pesquisa da Pecuária Municipal (PPM) e PIB dos Municípios, no recorte 2003–2024.

O projeto cobre o ciclo completo de um trabalho de dados: coleta a partir da API do IBGE, diagnóstico e tratamento de qualidade, análise exploratória (incluindo geoespacial), cruzamento das três bases e um dashboard interativo para consulta dos resultados.

## Estrutura do repositório

```
.
├── app/            # Dashboard (Streamlit): telas em views/
├── dados/          # Dados brutos, tratados e analíticos
│   ├── raw/            # Dados originais baixados do SIDRA/IBGE
│   ├── processed/      # Dados tratados pelo pipeline (saída de src/pipeline.py)
│   └── analytical/     # Bases cruzadas (PAM x PPM x PIB)
├── docs/           # Relatórios e documentação das análises
├── notebooks/      # Notebooks de exploração, tratamento e cruzamento dos dados
├── src/            # Pipeline de dados e scripts .py gerados a partir dos notebooks
└── requirements.txt
```

### Dados

Os arquivos brutos são recortes oficiais do SIDRA/IBGE (tabelas 5457, 3939 e 5938), abrangendo Brasil, Ceará e os 184 municípios cearenses. Detalhes sobre variáveis, seleções, chaves e cuidados obrigatórios de interpretação estão documentados em [`dados/README_DADOS.md`](dados/README_DADOS.md); a proveniência de cada arquivo (URL da API, filtros, hash) está em [`dados/fontes.csv`](dados/fontes.csv).

### Pipeline de preparação de dados

O pipeline em `src/` lê os dados brutos, remove duplicatas, trata símbolos de ausência do IBGE (`-`, `0`, `..`, `...`, `X`) e padroniza colunas e categorias:

- `src/data_loader.py`: leitura dos dados brutos (PAM, PPM, PIB).
- `src/data_cleaner.py`: remoção de registros duplicados.
- `src/data_standardizer.py`: padronização de ausências, símbolos e variáveis.
- `src/pipeline.py`: orquestra leitura, limpeza e padronização, e salva os dados tratados.
- `src/cruzamento_bases.py`: cruza PAM, PPM e PIB pelo código do município.

As decisões de tratamento e a validação dos resultados estão detalhadas em [`docs/relatorio_preparacao_dados.md`](docs/relatorio_preparacao_dados.md).

Para rodar o pipeline e gerar as bases tratadas a partir dos dados brutos, execute na raiz do projeto:

```bash
python src/pipeline.py
```

Os dados tratados são salvos em `dados/processed/` em formato `.csv`.

### Notebooks e análises

Em `notebooks/` estão as análises exploratórias (incluindo recortes geoespaciais) de cada base e o cruzamento entre elas; as versões `.py` correspondentes, geradas a partir dos notebooks, ficam em `src/`. Os principais achados estão consolidados em `docs/`, como a análise de crescimento do PIB municipal em [`docs/analise_crescimento_pib_municipios.md`](docs/analise_crescimento_pib_municipios.md).

### Dashboard

O dashboard interativo fica em `app/` e é um app **Streamlit** com sete telas: Visão geral, Agricultura (PAM), Pecuária (PPM), Economia municipal (PIB), Território, Cruzamentos e Fontes/metodologia. As telas ficam em `app/views/` e compartilham os dados carregados por `app/data.py`.

Para executar:

```bash
streamlit run app/app.py
```

## Requisitos

```bash
pip install -r requirements.txt
```

Principais dependências: `pandas`, `numpy` e `streamlit`.
