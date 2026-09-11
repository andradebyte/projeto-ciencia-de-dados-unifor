# avaliação
Avaliação Teórica: Unidade 1 – Visão sistêmica de ciência de dados

Projeto Prático: Projeto 1 – Análise de Dados

Orientações do Projeto: 28/08

Acompanhamento do Projeto: 11/09

Avaliação Teórica: 18/09

Apresentações do Projeto: 25/09



# pontos que vi no pdf

Desenvolver uma análise exploratória reproduzível e um dashboard interativo a partir de dados municipais 
do IBGE, integrando diferentes tabelas do SIDRA (Banco de dados público do IBGE) para gerar informação útil à sociedade

Objetivos específicos 
●  Compreender a missão temática e convertê-la em perguntas claras de análise. 
●  Inventariar e caracterizar todas as bases fornecidas à equipe. 
●  Preservar os dados originais e criar um fluxo rastreável de preparação. 
●  Avaliar granularidade, cardinalidade, duplicatas, ausências, unidades e símbolos especiais. 
●  Integrar tabelas por código IBGE do município, medindo correspondências e não correspondências. 
●  Produzir visualizações adequadas, pelo menos quatro insights relevantes e recomendações prudentes. 
●  Publicar um dashboard acessível remotamente e documentar fontes, metodologia e limitações. 
●  Comunicar o projeto a públicos técnico e não técnico por meio do pitch e da atividade extensionista. 


4. Requisitos técnicos comuns 
●  Utilizar Python para carregar, tratar, analisar e visualizar os dados. 
●  Manter um repositório público ou acessível ao professor no GitHub. 
●  Preservar integralmente os arquivos fornecidos na camada raw, sem sobrescrevê-los. 
●  Organizar os dados em raw, processed e, quando necessário, analytical. 
●  Carregar, caracterizar e usar todas as bases obrigatórias do tema. 
●  O uso de fontes adicionais é permitido, desde que sejam devidamente versionadas e documentadas. 
Vale ressaltar que as fontes extras não substituem as tabelas obrigatórias. 
●  Integrar efetivamente pelo menos três tabelas SIDRA. 
●  Usar o código IBGE do município como chave de pareamento; não parear por nome. 
●  Documentar granularidade, cardinalidade, chaves, duplicatas, ausências, unidades e linhas sem 
correspondência. 
●  Tratar explicitamente os símbolos especiais do SIDRA: -, 0, X, .. e ... 
●  Manter a rastreabilidade das transformações e justificar as decisões de limpeza. 
●  Produzir pelo menos quatro insights relevantes, sendo no mínimo dois derivados do cruzamento 
entre bases. 
●  Não utilizar aprendizado de máquina neste projeto. 
●  Não formular conclusões causais a partir de associações observacionais. 
●  Alinhar períodos, universos e unidades nos indicadores; qualquer defasagem temporal deverá ser 
identificada e justificada.
●  Fazer o dashboard ler arquivos estáticos do repositório; chamadas ao SIDRA em tempo de execução são 
proibidas. 
●  Implementar o dashboard com Streamlit ou Dash/Plotly e publicar uma URL acessível sem 
autenticação.


----
raw  | Arquivos exatamente como fornecidos no ZIP. | Somente leitura; nunca sobrescrever. 

processed | Dados tipados, padronizados e com qualidade documentada. | Transformações reproduzíveis por código. 

analytical | Tabelas integradas no grão necessário a uma análise ou visual. | Chaves e granularidade declaradas. 
----


Rastreabilidade mínima 
●  README com objetivo, estrutura, instruções de execução e links publicados. 
●  requirements.txt ou pyproject.toml com dependências necessárias. 
●  Código executável do início ao fim a partir dos arquivos raw. 
●  Dicionário de dados ou inventário das colunas utilizadas. 
●  Registro das regras de limpeza, agregação e integração. 
 
Projeto 1  |  IBGE / SIDRA  p. 7 
 
CIÊNCIA DE DADOS  |  PROJETO 1 
●  No README do repositório e na seção Fontes e metodologia do dashboard, identificar tabelas, 
períodos, unidades, transformações relevantes e limitações que afetem a interpretação, como 
diferenças temporais, valores indisponíveis e cobertura dos dados.


Todos os pacotes incluem o arquivo dados_comuns/malha_municipal_ce_2022.geojson, que representa os 
limites  dos  184  municípios  cearenses  e  permite  construir  mapas  temáticos.  Esse  arquivo  é  um  dado 
geográfico  auxiliar  e  não  conta  como uma das três tabelas SIDRA exigidas para integração



Usar GeoPandas
