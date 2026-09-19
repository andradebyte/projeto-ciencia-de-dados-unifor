# Dados comuns — malha municipal do Ceará

## Arquivo

- `malha_municipal_ce_2022.geojson`: malha simplificada dos municípios do Ceará, referente a 2022, em formato GeoJSON.
- Formato: `FeatureCollection` com 184 feições do tipo `Polygon`.
- Tamanho: 1.329.507 bytes.
- SHA-256: `6fecef647b8028bc9c2deb9a9de03ae91787a040bf2c3f4bb62ef82c3683b62c`.

## Fonte oficial

- Instituição: Instituto Brasileiro de Geografia e Estatística (IBGE).
- Serviço: [API de Malhas Geográficas, versão 3](https://servicodados.ibge.gov.br/api/docs/malhas?versao=3).
- Extração estática: [Ceará, período 2022, intrarregião município, GeoJSON e qualidade máxima](https://servicodados.ibge.gov.br/api/v3/malhas/estados/23?formato=application/vnd.geo%2Bjson&qualidade=maxima&intrarregiao=municipio&periodo=2022).
- Data de acesso e download: 17 de agosto de 2026.

O serviço do IBGE foi utilizado somente durante a preparação do material. O arquivo foi armazenado neste pacote para que as análises e os dashboards não façam consultas à API em tempo de execução.

## Chave para integração

Cada feição possui a propriedade `codarea`, que contém o código de sete dígitos do município no IBGE. Essa é a chave que deve ser utilizada para cruzar a malha com as tabelas do SIDRA.

Exemplo:

```json
"properties": { "codarea": "2300101" }
```

Ao carregar os dados, preserve `codarea` e os códigos municipais das demais bases como texto. Não remova zeros, não converta a chave para número decimal e não faça o pareamento pelo nome do município.

## Uso com GeoPandas

O [GeoPandas](https://geopandas.org/) é uma opção recomendada para carregar, integrar e visualizar o arquivo GeoJSON em Python:

```python
import geopandas as gpd

malha = gpd.read_file("dados/raw/dados_comuns/malha_municipal_ce_2022.geojson")
malha["codarea"] = malha["codarea"].astype("string")
```

Antes da junção, mantenha também o código municipal da tabela analítica como texto. A junção deverá usar `codarea` e o código IBGE de sete dígitos, com validação da cardinalidade e das linhas sem correspondência.

O arquivo deve permanecer intacto na camada `raw`. Se a equipe fizer correções geométricas, reprojeções ou simplificações adicionais, deverá salvar o resultado em `processed` e documentar a transformação. Para mapas temáticos, o sistema de coordenadas geográficas do GeoJSON é suficiente. Para operações de distância ou área, é necessário usar uma projeção adequada; para os indicadores do projeto, prefira a área oficial fornecida nas tabelas do IBGE.

## Validação realizada

- 184 feições geográficas.
- 184 valores únicos de `codarea`.
- Todos os códigos têm sete dígitos e começam por `23`, prefixo da Unidade da Federação Ceará.
- Nenhuma geometria ausente.
- Comparação com o [cadastro oficial de municípios do Ceará](https://servicodados.ibge.gov.br/api/v1/localidades/estados/23/municipios): 184 códigos correspondentes, nenhum ausente e nenhum excedente.

A validação estrutural acima não equivale à validade topológica. Na versão simplificada fornecida atualmente pelo próprio IBGE, o teste `GeoSeries.is_valid` identifica pequenas auto-interseções em cinco feições: Acaraú (`2300200`), Barbalha (`2301901`), Crateús (`2304103`), Limoeiro do Norte (`2307601`) e Mauriti (`2308104`). Isso normalmente não impede a criação de mapas coropléticos, mas pode afetar operações espaciais. Caso seja necessário corrigir essas geometrias, a equipe poderá usar `GeoSeries.make_valid()` e deverá preservar o arquivo original e registrar a correção.

## Observação cartográfica

A API fornece uma malha simplificada, apropriada para visualizações e aplicações web. Ela deve ser usada como suporte para mapas temáticos do projeto, não para medições cartográficas de precisão, demarcação legal ou cálculo oficial de área.
