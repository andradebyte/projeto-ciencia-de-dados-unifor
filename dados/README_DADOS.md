# Dados do Tema 02 — Agropecuária

## Conteúdo do pacote

Os arquivos são recortes oficiais do SIDRA/IBGE. A PAM e a PPM abrangem **2003–2024**; o PIB dos Municípios abrange **2003–2023**. Todos contêm Brasil (`N1`, código `1`), Ceará (`N3`, código `23`) e os 184 municípios cearenses (`N6`, códigos de sete dígitos).

A tabela PAM 5457 foi baixada em cinco requisições, uma por variável. Isso mantém cada consulta abaixo do limite de observações da API e preserva a estrutura da resposta oficial.

| Arquivo | Conteúdo | Linhas |
|---|---|---:|
| `dados_originais/t5457_pam_area_plantada_2003_2024_ce_br.csv` | Área plantada ou destinada à colheita | 28.644 |
| `dados_originais/t5457_pam_area_colhida_2003_2024_ce_br.csv` | Área colhida | 28.644 |
| `dados_originais/t5457_pam_quantidade_produzida_2003_2024_ce_br.csv` | Quantidade produzida | 28.644 |
| `dados_originais/t5457_pam_rendimento_medio_2003_2024_ce_br.csv` | Rendimento médio | 28.644 |
| `dados_originais/t5457_pam_valor_producao_2003_2024_ce_br.csv` | Valor da produção | 28.644 |
| `dados_originais/t3939_ppm_efetivo_rebanhos_2003_2024_ce_br.csv` | Efetivo dos rebanhos | 20.460 |
| `dados_originais/t5938_pib_agropecuaria_2003_2023_ce_br.csv` | PIB, VAB total, VAB agropecuário e participação | 15.624 |

Não há dados limpos, indicadores calculados ou bases cruzadas neste pacote.

## Seleções realizadas

### PAM — tabela 5457

Variáveis: `8331` área plantada ou destinada à colheita; `216` área colhida; `214` quantidade produzida; `112` rendimento médio; `215` valor da produção.

Produtos da classificação `782`:

- `40122` — Milho (em grão);
- `40112` — Feijão (em grão);
- `40119` — Mandioca;
- `40106` — Cana-de-açúcar;
- `40136` — Banana (cacho);
- `40143` — Castanha de caju;
- `40121` — Melão.

### PPM — tabela 3939

Variável `105`, efetivo dos rebanhos. Tipos da classificação `79`: `2670` bovinos, `2681` caprinos, `2677` ovinos, `32794` suínos total e `32796` galináceos total.

### PIB dos Municípios — tabela 5938

Variáveis `37` PIB a preços correntes, `498` VAB total, `513` VAB agropecuário e `516` participação do VAB agropecuário no VAB total.

## Estrutura dos CSVs

Os arquivos estão em formato longo, separados por ponto e vírgula e codificados em UTF-8 com BOM. A resposta JSON da API foi transposta para CSV sem limpeza, arredondamento ou imputação.

Todos contêm as colunas territoriais, período, variável, unidade e `valor`. Os arquivos PAM acrescentam `produto_codigo` e `produto_nome`; o arquivo PPM acrescenta `tipo_rebanho_codigo` e `tipo_rebanho_nome`.

```python
import pandas as pd

df = pd.read_csv(
    "dados_originais/t5457_pam_area_colhida_2003_2024_ce_br.csv",
    sep=";",
    encoding="utf-8-sig",
    dtype={
        "territorio_codigo": "string",
        "variavel_codigo": "string",
        "produto_codigo": "string",
    },
    keep_default_na=False,
)
```

Chave sugerida da PAM: `nivel_territorial_codigo + territorio_codigo + ano_codigo + variavel_codigo + produto_codigo`. Na PPM, substituir produto por `tipo_rebanho_codigo`. No PIB, a chave não possui classificação.

## Cuidados obrigatórios

1. Os símbolos `-`, `0` e `...` foram preservados exatamente como fornecidos pelo SIDRA. Há seis registros `0` na variável de valor da produção da PAM; esse símbolo deve ser distinguido de `-`. Consultar a legenda do SIDRA antes de qualquer conversão e não substituir símbolos automaticamente por valores ausentes ou por zero numérico.
2. **Disponibilidade da tabela 5938:** o PIB, variável `37`, está preenchido até 2023. O VAB total (`498`), o VAB agropecuário (`513`) e a participação da agropecuária (`516`) estão preenchidos até 2021 e retornam `...` para todos os territórios em 2022 e 2023. Assim, o cruzamento com o PIB pode alcançar 2023, enquanto análises que dependam dessas três variáveis de VAB devem terminar em 2021. A PAM e a PPM podem ser analisadas separadamente até 2024.
3. PIB, VAB e valor da produção são valores correntes/nominais. Uma análise de crescimento monetário real exige correção de preços.
4. Efetivo de rebanhos é estoque de animais, enquanto produção agrícola é fluxo anual; as medidas não devem ser tratadas como conceitos equivalentes.
5. As categorias selecionadas de suínos e galináceos são totais. Não somar posteriormente suas subcategorias ao total.
6. Não somar rendimentos médios entre produtos. Manter a unidade de cada variável nas análises.
7. Brasil e Ceará servem como referências e não devem entrar em somas municipais.

## Validações realizadas

- todas as requisições responderam HTTP 200;
- 22 períodos, de 2003 a 2024, nos arquivos PAM e PPM; 21 períodos, de 2003 a 2023, no arquivo de PIB;
- exatamente 184 municípios distintos, Ceará e Brasil;
- variáveis, sete produtos e cinco tipos de rebanho conferidos pelos códigos oficiais;
- chaves sem duplicatas e 186 territórios em cada combinação período/variável/categoria;
- símbolos especiais preservados;
- UTF-8 com BOM, separador e hashes SHA-256 conferidos.

As URLs completas, filtros, horários, dimensões e hashes estão em `fontes.csv`.
