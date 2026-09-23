#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt


# In[2]:


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df = pd.read_csv('../dados/processed/pam_tratado.csv')
df.head()


# Como são os dados brutos do PAM?

# In[3]:


colunas_codigo = [c for c in df.columns if c.endswith('_codigo')]
df_nome = df.drop(columns=colunas_codigo)
df_nome.head()


# Como ficam os dados sem as colunas de código?

# In[4]:


df_nome.groupby('variavel_nome')['valor'].describe()


# Como se distribui o valor de cada variável (área, produção, rendimento, valor)?

# In[5]:


print("Valores nulos:", df_nome['valor'].isna().sum())
print("Valores inibidos (sigilo do IBGE):", df_nome['valor_is_inibido'].sum())
print("Linhas duplicadas:", df_nome.duplicated().sum())


# Os dados têm valores nulos, inibidos ou duplicados?

# In[6]:


territorios = df_nome['territorio_nome'].unique()
print(len(territorios))
print(territorios)


# Quantos e quais territórios temos no PAM?

# In[7]:


anos = df_nome['ano_nome'].unique()
print(len(anos))
print(anos)


# Quantos e quais anos o PAM cobre?

# In[8]:


variaveis = df_nome['variavel_nome'].unique()
print(len(variaveis))
print(variaveis)


# Quais variáveis o PAM mede?

# In[9]:


unidades = df_nome['unidade'].unique()
print(len(unidades))
print(unidades)


# Em quais unidades essas variáveis são medidas?

# In[10]:


produtos = df_nome['produto_nome'].unique()
print(len(produtos))
print(produtos)


# Quais produtos agrícolas o PAM cobre?

# ## Valor da produção (Mil Reais)

# ### Brasil

# Como evoluiu o valor da produção por produto, no Brasil?

# In[11]:


projecao_valor_brasil = df_nome[(df_nome['unidade'] == 'Mil Reais') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_valor_brasil


# In[12]:


projecao_area_plantada_brasil = df_nome[(df_nome['variavel_nome'] == 'Área plantada ou destinada à colheita') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_area_plantada_brasil


# In[13]:


projecao_area_colhida_brasil = df_nome[(df_nome['variavel_nome'] == 'Área colhida') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_area_colhida_brasil


# In[14]:


projecao_producao_brasil = df_nome[(df_nome['unidade'] == 'Toneladas') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_producao_brasil


# In[15]:


projecao_rendimento_brasil = df_nome[(df_nome['unidade'] == 'Quilogramas por Hectare') & (df_nome['territorio_nome'] == 'Brasil')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_rendimento_brasil


# In[16]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_valor_brasil.plot(ax=ax, marker='o')
ax.set_title('Valor da produção por produto (Brasil)')
ax.set_xlabel('Ano')
ax.set_ylabel('Mil Reais')
ax.set_xticks(projecao_valor_brasil.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[17]:


print(projecao_valor_brasil)


# ### Ceará

# E no Ceará?

# In[18]:


projecao_valor_ceara = df_nome[(df_nome['unidade'] == 'Mil Reais') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_valor_ceara


# In[19]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_valor_ceara.plot(ax=ax, marker='o')
ax.set_title('Valor da produção por produto (Ceará)')
ax.set_xlabel('Ano')
ax.set_ylabel('Mil Reais')
ax.set_xticks(projecao_valor_ceara.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[20]:


print(projecao_valor_ceara)


# ## Área plantada (Hectares)

# ### Brasil

# Como evoluiu a área plantada por produto, no Brasil?

# In[21]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_area_plantada_brasil.plot(ax=ax, marker='o')
ax.set_title('Área plantada por produto (Brasil)')
ax.set_xlabel('Ano')
ax.set_ylabel('Hectares')
ax.set_xticks(projecao_area_plantada_brasil.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[22]:


print(projecao_area_plantada_brasil)


# ### Ceará

# E no Ceará?

# In[23]:


projecao_area_plantada_ceara = df_nome[(df_nome['variavel_nome'] == 'Área plantada ou destinada à colheita') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_area_plantada_ceara


# In[24]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_area_plantada_ceara.plot(ax=ax, marker='o')
ax.set_title('Área plantada por produto (Ceará)')
ax.set_xlabel('Ano')
ax.set_ylabel('Hectares')
ax.set_xticks(projecao_area_plantada_ceara.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[25]:


print(projecao_area_plantada_ceara)


# ## Área colhida (Hectares)

# ### Brasil

# Como evoluiu a área colhida por produto, no Brasil?

# In[26]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_area_colhida_brasil.plot(ax=ax, marker='o')
ax.set_title('Área colhida por produto (Brasil)')
ax.set_xlabel('Ano')
ax.set_ylabel('Hectares')
ax.set_xticks(projecao_area_colhida_brasil.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[27]:


print(projecao_area_colhida_brasil)


# ### Ceará

# E no Ceará?

# In[28]:


projecao_area_colhida_ceara = df_nome[(df_nome['variavel_nome'] == 'Área colhida') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_area_colhida_ceara


# In[29]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_area_colhida_ceara.plot(ax=ax, marker='o')
ax.set_title('Área colhida por produto (Ceará)')
ax.set_xlabel('Ano')
ax.set_ylabel('Hectares')
ax.set_xticks(projecao_area_colhida_ceara.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[30]:


print(projecao_area_colhida_ceara)


# ## Quantidade produzida (Toneladas)

# ### Brasil

# Como evoluiu a quantidade produzida por produto, no Brasil?

# In[31]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_producao_brasil.plot(ax=ax, marker='o')
ax.set_title('Quantidade produzida por produto (Brasil)')
ax.set_xlabel('Ano')
ax.set_ylabel('Toneladas')
ax.set_xticks(projecao_producao_brasil.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[32]:


print(projecao_producao_brasil)


# ### Ceará

# E no Ceará?

# In[33]:


projecao_producao_ceara = df_nome[(df_nome['unidade'] == 'Toneladas') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_producao_ceara


# In[34]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_producao_ceara.plot(ax=ax, marker='o')
ax.set_title('Quantidade produzida por produto (Ceará)')
ax.set_xlabel('Ano')
ax.set_ylabel('Toneladas')
ax.set_xticks(projecao_producao_ceara.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[35]:


print(projecao_producao_ceara)


# ## Rendimento médio (Quilogramas por Hectare)

# ### Brasil

# Como evoluiu o rendimento médio por produto, no Brasil?

# In[36]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_rendimento_brasil.plot(ax=ax, marker='o')
ax.set_title('Rendimento médio por produto (Brasil)')
ax.set_xlabel('Ano')
ax.set_ylabel('Quilogramas por Hectare')
ax.set_xticks(projecao_rendimento_brasil.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[37]:


print(projecao_rendimento_brasil)


# ### Ceará

# E no Ceará?

# In[38]:


projecao_rendimento_ceara = df_nome[(df_nome['unidade'] == 'Quilogramas por Hectare') & (df_nome['territorio_nome'] == 'Ceará')].pivot_table(
    index='ano_nome', columns='produto_nome', values='valor', aggfunc='sum'
)
projecao_rendimento_ceara


# In[39]:


fig, ax = plt.subplots(figsize=(12, 6))
projecao_rendimento_ceara.plot(ax=ax, marker='o')
ax.set_title('Rendimento médio por produto (Ceará)')
ax.set_xlabel('Ano')
ax.set_ylabel('Quilogramas por Hectare')
ax.set_xticks(projecao_rendimento_ceara.index)
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[40]:


print(projecao_rendimento_ceara)


# ## Participação do Ceará no Brasil (%)

# ### Valor da produção

# Quanto o Ceará representa do valor da produção do Brasil, ano a ano?

# In[41]:


cores = {"Brasil": "#2a78d6", "Ceará": "#eb6834"}

percentual_valor = (projecao_valor_ceara.sum(axis=1) / projecao_valor_brasil.sum(axis=1)) * 100
resto_valor = 100 - percentual_valor

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_valor.index, percentual_valor, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_valor.index, resto_valor, left=percentual_valor, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_valor.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_valor.index)
ax.invert_yaxis()
ax.set_xlabel("% do valor da produção do Brasil")
ax.set_title("Participação do Ceará no valor da produção do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_valor)


# ### Área plantada

# Quanto o Ceará representa da área plantada do Brasil, ano a ano?

# In[42]:


percentual_area_plantada = (projecao_area_plantada_ceara.sum(axis=1) / projecao_area_plantada_brasil.sum(axis=1)) * 100
resto_area_plantada = 100 - percentual_area_plantada

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_area_plantada.index, percentual_area_plantada, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_area_plantada.index, resto_area_plantada, left=percentual_area_plantada, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_area_plantada.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_area_plantada.index)
ax.invert_yaxis()
ax.set_xlabel("% da área plantada do Brasil")
ax.set_title("Participação do Ceará na área plantada do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_area_plantada)


# ### Área colhida

# Quanto o Ceará representa da área colhida do Brasil, ano a ano?

# In[43]:


percentual_area_colhida = (projecao_area_colhida_ceara.sum(axis=1) / projecao_area_colhida_brasil.sum(axis=1)) * 100
resto_area_colhida = 100 - percentual_area_colhida

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_area_colhida.index, percentual_area_colhida, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_area_colhida.index, resto_area_colhida, left=percentual_area_colhida, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_area_colhida.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_area_colhida.index)
ax.invert_yaxis()
ax.set_xlabel("% da área colhida do Brasil")
ax.set_title("Participação do Ceará na área colhida do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_area_colhida)


# ### Quantidade produzida

# Quanto o Ceará representa da quantidade produzida do Brasil, ano a ano?

# In[44]:


percentual_producao = (projecao_producao_ceara.sum(axis=1) / projecao_producao_brasil.sum(axis=1)) * 100
resto_producao = 100 - percentual_producao

fig, ax = plt.subplots(figsize=(10, 9))
ax.barh(percentual_producao.index, percentual_producao, color=cores["Ceará"], label="Ceará")
ax.barh(percentual_producao.index, resto_producao, left=percentual_producao, color=cores["Brasil"], label="Resto do Brasil")

for ano, pct in percentual_producao.items():
    ax.annotate(
        f"{pct:.2f}%",
        (100, ano),
        textcoords="offset points", xytext=(6, 0), va="center", ha="left", fontsize=9, color="#0b0b0b",
    )

ax.set_yticks(percentual_producao.index)
ax.invert_yaxis()
ax.set_xlabel("% da quantidade produzida do Brasil")
ax.set_title("Participação do Ceará na quantidade produzida do Brasil")
ax.set_xlim(0, 100)
ax.grid(True, axis="x", color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right")

plt.show()

print(percentual_producao)


# ## Análise por Município

# ### Valor da produção

# Quais municípios têm maior e menor valor da produção, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[45]:


pivot_municipios_valor = df_nome[
    (df_nome['unidade'] == 'Mil Reais') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_valor


# In[46]:


total_municipios_valor = pivot_municipios_valor.sum(axis=0).sort_values(ascending=False)
top8_melhores_valor = total_municipios_valor.head(8)
top8_piores_valor = total_municipios_valor.tail(8).sort_values()

print("Top 8 melhores municípios - Valor da produção (soma 2003-2024):")
print(top8_melhores_valor)
print()
print("Top 8 piores municípios - Valor da produção (soma 2003-2024):")
print(top8_piores_valor)


# In[47]:


participacao_municipios_valor = pivot_municipios_valor.div(pivot_municipios_valor.sum(axis=1), axis=0) * 100
ordem_municipios_valor = total_municipios_valor.index
cmap_municipios = plt.colormaps["viridis"]
n_municipios = len(ordem_municipios_valor)
cor_por_municipio_valor = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_valor)}

anos_resumo = [2003, 2023]

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_valor:
        pct = participacao_municipios_valor.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_valor[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% do valor da produção do Ceará")
ax.set_title("Valor da produção do Ceará preenchido pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Área plantada

# Quais municípios têm maior e menor área plantada, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[48]:


pivot_municipios_area_plantada = df_nome[
    (df_nome['variavel_nome'] == 'Área plantada ou destinada à colheita') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_area_plantada


# In[49]:


total_municipios_area_plantada = pivot_municipios_area_plantada.sum(axis=0).sort_values(ascending=False)
top8_melhores_area_plantada = total_municipios_area_plantada.head(8)
top8_piores_area_plantada = total_municipios_area_plantada.tail(8).sort_values()

print("Top 8 melhores municípios - Área plantada (soma 2003-2024):")
print(top8_melhores_area_plantada)
print()
print("Top 8 piores municípios - Área plantada (soma 2003-2024):")
print(top8_piores_area_plantada)


# In[50]:


participacao_municipios_area_plantada = pivot_municipios_area_plantada.div(pivot_municipios_area_plantada.sum(axis=1), axis=0) * 100
ordem_municipios_area_plantada = total_municipios_area_plantada.index
n_municipios = len(ordem_municipios_area_plantada)
cor_por_municipio_area_plantada = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_area_plantada)}

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_area_plantada:
        pct = participacao_municipios_area_plantada.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_area_plantada[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% da área plantada do Ceará")
ax.set_title("Área plantada do Ceará preenchida pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Área colhida

# Quais municípios têm maior e menor área colhida, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[51]:


pivot_municipios_area_colhida = df_nome[
    (df_nome['variavel_nome'] == 'Área colhida') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_area_colhida


# In[52]:


total_municipios_area_colhida = pivot_municipios_area_colhida.sum(axis=0).sort_values(ascending=False)
top8_melhores_area_colhida = total_municipios_area_colhida.head(8)
top8_piores_area_colhida = total_municipios_area_colhida.tail(8).sort_values()

print("Top 8 melhores municípios - Área colhida (soma 2003-2024):")
print(top8_melhores_area_colhida)
print()
print("Top 8 piores municípios - Área colhida (soma 2003-2024):")
print(top8_piores_area_colhida)


# In[53]:


participacao_municipios_area_colhida = pivot_municipios_area_colhida.div(pivot_municipios_area_colhida.sum(axis=1), axis=0) * 100
ordem_municipios_area_colhida = total_municipios_area_colhida.index
n_municipios = len(ordem_municipios_area_colhida)
cor_por_municipio_area_colhida = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_area_colhida)}

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_area_colhida:
        pct = participacao_municipios_area_colhida.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_area_colhida[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% da área colhida do Ceará")
ax.set_title("Área colhida do Ceará preenchida pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ### Quantidade produzida

# Quais municípios têm maior e menor quantidade produzida, e como o Ceará se reparte entre eles (2003 x 2023)?

# In[54]:


pivot_municipios_producao = df_nome[
    (df_nome['unidade'] == 'Toneladas') & (~df_nome['territorio_nome'].isin(['Brasil', 'Ceará']))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')
pivot_municipios_producao


# In[55]:


total_municipios_producao = pivot_municipios_producao.sum(axis=0).sort_values(ascending=False)
top8_melhores_producao = total_municipios_producao.head(8)
top8_piores_producao = total_municipios_producao.tail(8).sort_values()

print("Top 8 melhores municípios - Quantidade produzida (soma 2003-2024):")
print(top8_melhores_producao)
print()
print("Top 8 piores municípios - Quantidade produzida (soma 2003-2024):")
print(top8_piores_producao)


# In[56]:


participacao_municipios_producao = pivot_municipios_producao.div(pivot_municipios_producao.sum(axis=1), axis=0) * 100
ordem_municipios_producao = total_municipios_producao.index
n_municipios = len(ordem_municipios_producao)
cor_por_municipio_producao = {m: cmap_municipios(i / n_municipios) for i, m in enumerate(ordem_municipios_producao)}

fig, ax = plt.subplots(figsize=(14, 4))
for ano in anos_resumo:
    esquerda = 0
    for municipio in ordem_municipios_producao:
        pct = participacao_municipios_producao.loc[ano, municipio]
        ax.barh(str(ano), pct, left=esquerda, color=cor_por_municipio_producao[municipio], edgecolor="#fcfcfb", linewidth=0.3)
        if pct > 3:
            ax.text(esquerda + pct / 2, str(ano), municipio.replace(" - CE", ""), ha="center", va="center", fontsize=7, color="white", rotation=90)
        esquerda += pct

ax.invert_yaxis()
ax.set_xlabel("% da quantidade produzida do Ceará")
ax.set_title("Quantidade produzida do Ceará preenchida pelos municípios — 2003 x 2023")
ax.set_xlim(0, 100)
ax.spines[["top", "right", "left"]].set_visible(False)

plt.show()


# ## Crescimento (2003 → 2023)

# ### Produtos (Ceará)

# Quais produtos mais cresceram no Ceará entre 2003 e 2023, em cada métrica?

# In[57]:


crescimento_produtos_valor = (projecao_valor_ceara.loc[2023] / projecao_valor_ceara.loc[2003]).sort_values(ascending=False)

print("Crescimento do valor da produção por produto (Ceará, 2003 → 2023):")
for produto, fator in crescimento_produtos_valor.items():
    print(f"{produto}: {fator:.2f}x")


# In[58]:


crescimento_produtos_area_plantada = (projecao_area_plantada_ceara.loc[2023] / projecao_area_plantada_ceara.loc[2003]).sort_values(ascending=False)

print("Crescimento da área plantada por produto (Ceará, 2003 → 2023):")
for produto, fator in crescimento_produtos_area_plantada.items():
    print(f"{produto}: {fator:.2f}x")


# In[59]:


crescimento_produtos_area_colhida = (projecao_area_colhida_ceara.loc[2023] / projecao_area_colhida_ceara.loc[2003]).sort_values(ascending=False)

print("Crescimento da área colhida por produto (Ceará, 2003 → 2023):")
for produto, fator in crescimento_produtos_area_colhida.items():
    print(f"{produto}: {fator:.2f}x")


# In[60]:


crescimento_produtos_producao = (projecao_producao_ceara.loc[2023] / projecao_producao_ceara.loc[2003]).sort_values(ascending=False)

print("Crescimento da quantidade produzida por produto (Ceará, 2003 → 2023):")
for produto, fator in crescimento_produtos_producao.items():
    print(f"{produto}: {fator:.2f}x")


# ### Municípios

# Quais municípios mais cresceram no Ceará entre 2003 e 2023, em cada métrica?

# In[61]:


crescimento_municipios_valor = (pivot_municipios_valor.loc[2023] / pivot_municipios_valor.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Valor da produção (2003 → 2023):")
for municipio, fator in crescimento_municipios_valor.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[62]:


crescimento_municipios_area_plantada = (pivot_municipios_area_plantada.loc[2023] / pivot_municipios_area_plantada.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Área plantada (2003 → 2023):")
for municipio, fator in crescimento_municipios_area_plantada.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[63]:


crescimento_municipios_area_colhida = (pivot_municipios_area_colhida.loc[2023] / pivot_municipios_area_colhida.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Área colhida (2003 → 2023):")
for municipio, fator in crescimento_municipios_area_colhida.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# In[64]:


crescimento_municipios_producao = (pivot_municipios_producao.loc[2023] / pivot_municipios_producao.loc[2003]).replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)

print("Top 10 municípios que mais cresceram - Quantidade produzida (2003 → 2023):")
for municipio, fator in crescimento_municipios_producao.head(10).items():
    print(f"{municipio}: {fator:.2f}x")


# ## Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia

# Como se compara a evolução de Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia nas métricas do PAM?

# In[65]:


cidades_investigar = ["Fortaleza - CE", "Maracanaú - CE", "São Gonçalo do Amarante - CE", "Caucaia - CE"]
cores_investigar = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
cor_por_cidade_investigar = dict(zip(cidades_investigar, cores_investigar))

serie_cidades_valor = df_nome[
    (df_nome['unidade'] == 'Mil Reais') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_valor[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Valor da produção (Mil Reais, escala log)")
ax.set_title("Valor da produção — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[66]:


serie_cidades_area_plantada = df_nome[
    (df_nome['variavel_nome'] == 'Área plantada ou destinada à colheita') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_area_plantada[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Área plantada (Hectares, escala log)")
ax.set_title("Área plantada — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[67]:


serie_cidades_area_colhida = df_nome[
    (df_nome['variavel_nome'] == 'Área colhida') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_area_colhida[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Área colhida (Hectares, escala log)")
ax.set_title("Área colhida — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# In[68]:


serie_cidades_producao = df_nome[
    (df_nome['unidade'] == 'Toneladas') & (df_nome['territorio_nome'].isin(cidades_investigar))
].pivot_table(index='ano_nome', columns='territorio_nome', values='valor', aggfunc='sum')

fig, ax = plt.subplots(figsize=(10, 6))
for municipio in cidades_investigar:
    serie = serie_cidades_producao[municipio]
    ax.plot(serie.index, serie.values, color=cor_por_cidade_investigar[municipio], linewidth=2, marker="o", markersize=3, label=municipio)

ax.set_yscale("log")
ax.set_xlabel("Ano")
ax.set_ylabel("Quantidade produzida (Toneladas, escala log)")
ax.set_title("Quantidade produzida — Fortaleza, Maracanaú, São Gonçalo do Amarante e Caucaia (2003–2024)")
ax.set_xticks(range(2003, 2025, 2))
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="upper left")

plt.show()


# ## Perda de Safra (Área colhida / Área plantada) — Ceará

# Existe perda de safra (diferença entre área plantada e colhida) no Ceará, ao longo dos anos?

# In[69]:


perda_safra_ceara = (projecao_area_colhida_ceara / projecao_area_plantada_ceara) * 100

fig, ax = plt.subplots(figsize=(12, 6))
perda_safra_ceara.plot(ax=ax, marker='o')
ax.set_title('% da área plantada efetivamente colhida por produto (Ceará)')
ax.set_xlabel('Ano')
ax.set_ylabel('% colhida da área plantada')
ax.set_xticks(perda_safra_ceara.index)
ax.axhline(100, color='gray', linewidth=0.8, linestyle='--')
ax.legend(title='Produto', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()


# In[70]:


print(perda_safra_ceara)


# ## Boxplot do Valor da Produção por Produto (Ceará)

# Como se distribui o valor da produção entre os produtos, e existem outliers?

# In[71]:


valor_ceara_por_produto = df_nome[(df_nome['unidade'] == 'Mil Reais') & (df_nome['territorio_nome'] == 'Ceará')]

fig, ax = plt.subplots(figsize=(12, 6))
sb.boxplot(data=valor_ceara_por_produto, x='produto_nome', y='valor', ax=ax)
ax.set_yscale('log')
ax.set_xlabel('Produto')
ax.set_ylabel('Valor da produção (Mil Reais, escala log)')
ax.set_title('Dispersão do valor da produção por produto (Ceará, 2003–2024)')
ax.tick_params(axis='x', rotation=30)
plt.tight_layout()
plt.show()


# ## Correlação entre Métricas (Ceará)

# As métricas do PAM se correlacionam entre si?

# In[72]:


metricas_ceara = df_nome[df_nome['territorio_nome'] == 'Ceará'].pivot_table(
    index=['ano_nome', 'produto_nome'], columns='variavel_nome', values='valor'
)

correlacao_metricas = metricas_ceara.corr()

fig, ax = plt.subplots(figsize=(8, 6))
sb.heatmap(correlacao_metricas, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
ax.set_title('Correlação entre métricas do PAM (Ceará, por ano/produto)')
plt.tight_layout()
plt.show()


# **Leitura da correlação:**
# 
# - **Área colhida × Área plantada (1.00):** correlação praticamente perfeita — quase tudo que é plantado acaba sendo colhido, coerente com a baixa perda de safra vista antes.
# - **Quantidade produzida × Rendimento médio (0.60):** positiva moderada — anos/produtos com rendimento (kg/ha) maior tendem a produzir mais em volume.
# - **Rendimento médio × Área plantada/colhida (-0.64):** negativa forte — produtos que ocupam mais área (Milho, Feijão) tendem a ter rendimento por hectare menor que produtos de área menor, puxando a correlação pra baixo.
# - **Valor da produção × demais métricas (0.23 com área, -0.08 com quantidade, -0.36 com rendimento):** todas fracas — o valor em Mil Reais é muito mais influenciado pelo preço de mercado do produto do que pelo volume/área plantada em si.
# 
# Importante: essa matriz mistura produtos diferentes (cada linha é ano × produto), então reflete o perfil de cada cultura (ex: Cana-de-açúcar tem área e rendimento grandes, Melão tem área pequena), não uma relação causal dentro de uma única safra.
