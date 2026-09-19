# Relatório de Inventário, Diagnóstico e Preparação de Dados

Este documento centraliza as descobertas, decisões e validações realizadas durante as fases de Compreensão dos Dados e Preparação de Dados do projeto.

---

## Parte 1: Compreensão e Inventário dos Dados
*Referente ao Épico: Compreensão e Inventário de Dados*

### 1.1. Diagnóstico de Qualidade
Durante a fase de exploração inicial das bases do IBGE (PAM, PPM e PIB), identificamos as seguintes características e anomalias na qualidade dos dados brutos:

- **Símbolos Textuais em Colunas Numéricas**: A coluna `valor` continha caracteres especiais em vez de números (`-`, `0`, `X`, `..`, `...`).
- **Resultados Empíricos de Ausências**: Após o processamento e rastreio de toda a base, obtivemos a quantificação exata destas anomalias:
  - Foram localizados **1.116 registros ausentes** mascarados por símbolos (`..` ou `...`), estando 100% deles concentrados na base do PIB. As bases PAM e PPM não apresentaram buracos desse tipo (0 ocorrências nulas).
  - **Sigilo Estatístico (`X`)**: O caractere `X` representa uma omissão intencional do IBGE para preservar o sigilo das fontes. O diagnóstico empírico demonstrou que, para o nosso recorte de dados atual, ocorreram **0 incidências** de sigilo estatístico em todas as 3 bases.
- **Inconsistências Hierárquicas**: Na validação matemática agregada, diagnosticou-se que a soma dos valores dos municípios não batia perfeitamente com o total consolidado oficial do Estado em 298 recortes no PAM e 66 recortes no PIB.
- **Integridade das Chaves**: Constatou-se a necessidade de preservar zeros à esquerda em códigos de municípios, exigindo tipagem forçada no momento da leitura.

---

## Parte 2: Higienização e Preparação
*Referente ao Épico: Higienização e Preparação de Dados*

### 2.1. Documentação das Decisões de Tratamento

Com base no diagnóstico acima, as seguintes regras de negócio foram implementadas no código (`src/data_cleaner.py` e `src/data_standardizer.py`):

1. **Tratamento de Duplicatas**: 
   - A decisão de remoção foi tomada após avaliarmos três cenários teóricos de duplicidade:
     - **Cenário A: Falha Técnica ou de Ingestão**: Duplo envio ou erro de extração. Exige remoção obrigatória (`keep='first'` ou `'last'`).
     - **Cenário B: Eventos Repetidos Legítimos**: Múltiplas ocorrências que deveriam ser somadas (Agregação/GroupBy).
     - **Cenário C: Duplicação Indesejada em Junções**: Multiplicação de linhas após um `merge` ou `join` mal feito.
   - **Nossa Decisão**: Como os dados do IBGE são fontes consolidadas, qualquer duplicação nas chaves primárias recai estritamente no **Cenário A (Falha de Ingestão)**. Por isso, adotamos a regra de remoção obrigatória preservando o último registro (`keep='last'`), assumindo que a ingestão mais recente (a última linha lida) corrige um erro da anterior.
2. **Padronização de Colunas e Categorias**:
   - Os nomes das colunas foram forçados para formato `snake_case` (letras minúsculas e sem espaços). 
   - Todas as colunas textuais categóricas passaram por remoção de espaços em branco invisíveis nas bordas (`.strip()`).
   - Os códigos do IBGE (`territorio_codigo`) foram lidos rigidamente como `string` para impedir o truncamento numérico do Pandas.
3. **Tratamento de Ausências e Símbolos**:
   - **`-` (Hífen)** e **`0`**: Convertidos matematicamente para `0.0`, pois representam contagens zeradas observadas (ausência real do evento).
   - **`..` (Não se aplica)** e **`...` (Não disponível)**: Convertidos para `NaN` para evitar a contaminação do cálculo de médias e medianas.
   - **`X` (Dado inibido)**: Convertido para `NaN`, mas para evitar a perda da informação analítica de que houve censura, foi criada uma nova coluna binária `valor_is_inibido` indicando `1` sempre que o valor era 'X'.

### 2.2. Comparação Antes e Depois (Saída Válida)

O pipeline automatizado garante que a base `raw` saia do estado caótico para um padrão analítico na camada `processed`.

**ANTES (Camada Raw)**:
- Múltiplos arquivos soltos de PAM, PPM e PIB.
- Coluna `valor` tipada como string (texto).
- Erros matemáticos ao tentar agregar dados.
- Espaços e caracteres imprevisíveis.

**DEPOIS (Camada Processed)**:
- 3 Arquivos consolidados (`pam_tratado.csv`, `ppm_tratado.csv`, `pib_tratado.csv`).
- Coluna `valor` totalmente numérica (`float64`).
- Adição da feature `valor_is_inibido`.
- Estrutura de strings e nomes perfeitamente encaixada nos padrões e limites.

### 2.3. Validação dos Outputs (Volumetria Final)

Durante a execução da rotina, a saída dos arquivos recriados na camada de processamento foi validada e se comprovou idêntica aos experimentos manuais originais:

- **PAM**: Base final consolidada com exatos **143.220 registros**.
- **PPM**: Base final consolidada com exatos **20.460 registros**.
- **PIB**: Base final consolidada com exatos **15.624 registros**.
- Os logs do pipeline apontam com exatidão a volumetria de falhas substituídas por Nulos e a contagem precisa das flags criadas para os inibidos.
