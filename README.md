# projeto-ciencia-de-dados

## Pipeline de Preparação de Dados

Este repositório contém um pipeline automatizado para a preparação e tratamento de dados de qualidade, refatorado a partir dos notebooks de análise.

### Estrutura de Arquivos

- `src/data_loader.py`: Funções para ler os dados brutos (PAM, PPM, PIB).
- `src/data_cleaner.py`: Funções para remover registros duplicados.
- `src/data_standardizer.py`: Funções para padronizar ausências e formatar variáveis.
- `src/pipeline.py`: Script principal que orquestra a leitura, limpeza, padronização e salva os dados finais.

### Como executar

Para rodar o pipeline inteiro do zero e gerar as bases tratadas, execute o seguinte comando na raiz do projeto:

```bash
python src/pipeline.py
```

Os dados tratados serão salvos automaticamente na pasta `data/processed/` em formato `.csv`.
