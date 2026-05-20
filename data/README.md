# 📂 Diretório de Dados

Este diretório contém todos os arquivos de dados do projeto Dashboard ENEM.

## 📁 Estrutura de Diretórios

```
data/
├── raw/          # Dados brutos do INEP (CSV originais)
├── processed/    # Dados processados e limpos
└── cache/        # Cache em formato Parquet (gerado automaticamente)
```

---

## 📊 Dados Brutos (`raw/`)

Contém os arquivos CSV originais baixados do INEP:

### 1. MICRODADOS_ENEM_2022.csv ⭐ **ARQUIVO PRINCIPAL**
- **Tamanho:** 1.495 MB (~1.5 GB)
- **Registros:** 3.476.105 participantes
- **Colunas:** 76 (35 essenciais utilizadas)
- **Fonte:** INEP - Microdados do ENEM 2022
- **URL:** https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
- **Encoding:** latin1
- **Separador:** ; (ponto e vírgula)

**Colunas Principais:**
- Identificação: `NU_INSCRICAO`, `NU_ANO`
- Demográficas: `TP_SEXO`, `TP_COR_RACA`, `TP_FAIXA_ETARIA`
- Educação: `TP_ESCOLA`, `TP_DEPENDENCIA_ADM_ESC`
- Localização: `SG_UF_ESC`, `NO_MUNICIPIO_ESC`
- Notas: `NU_NOTA_CN`, `NU_NOTA_CH`, `NU_NOTA_LC`, `NU_NOTA_MT`, `NU_NOTA_REDACAO`
- Presença: `TP_PRESENCA_CN`, `TP_PRESENCA_CH`, `TP_PRESENCA_LC`, `TP_PRESENCA_MT`
- Socioeconômico: `Q001` a `Q025`

### 2. ITENS_PROVA_2022.csv
- **Tamanho:** 0.30 MB
- **Colunas:** 14
- **Descrição:** Informações sobre as questões das provas
- **Uso:** Análise complementar (não utilizado no dashboard principal)

**Colunas Principais:**
- `CO_POSICAO`: Posição do item na prova
- `SG_AREA`: Área do conhecimento (CH, CN, LC, MT)
- `CO_ITEM`: Código do item
- `TX_GABARITO`: Gabarito da questão
- `CO_HABILIDADE`: Código da habilidade avaliada
- `NU_PARAM_A`, `NU_PARAM_B`, `NU_PARAM_C`: Parâmetros TRI

### 3. QUEST_HAB_ESTUDO.csv
- **Tamanho:** 271.85 MB
- **Colunas:** 86
- **Descrição:** Questionário de hábitos de estudo
- **Status:** Redundante (dados já estão no arquivo principal)
- **Uso:** Não utilizado

---

## 🔄 Dados Processados (`processed/`)

Contém dados limpos e transformados, prontos para análise:

### enem_processed.csv
- Dados principais após limpeza e transformação
- Valores ausentes tratados
- Tipos de dados convertidos
- Novas variáveis calculadas (nota_media, regiao)

### aggregated_by_state.csv
- Agregações por estado (27 estados)
- Médias, medianas, contagens
- Estatísticas descritivas

### aggregated_by_region.csv
- Agregações por região (5 regiões)
- Norte, Nordeste, Centro-Oeste, Sudeste, Sul
- Comparações regionais

---

## ⚡ Cache (`cache/`)

Sistema de cache inteligente em formato Parquet:

### Características
- **Formato:** Apache Parquet (colunar, comprimido)
- **Vantagens:**
  - 5-10x menor que CSV
  - 10-100x mais rápido para leitura
  - Preserva tipos de dados
  - Leitura seletiva de colunas

### Arquivos de Cache
- `cache_*.parquet`: Dados em cache
- `cache_*_metadata.json`: Metadados (data de criação, expiração, tamanho)

### TTL (Time To Live)
- **Padrão:** 30 dias
- **Configurável em:** `config.py` (CACHE_EXPIRY_DAYS)

### Limpeza de Cache
```bash
# Limpar todo o cache
python pipeline.py --clear-cache

# Ou manualmente
rm -rf data/cache/*
```

---

## 📥 Como Obter os Dados

### Opção 1: Dados Já Incluídos
Se você clonou o repositório com os dados, eles já estão em `data/raw/`.

### Opção 2: Download Manual
1. Acesse: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
2. Baixe o arquivo ZIP do ENEM 2022
3. Extraia para `data/raw/`
4. Certifique-se de que o arquivo se chama `MICRODADOS_ENEM_2022.csv`

---

## 🔍 Qualidade dos Dados

### Requisitos Atendidos
- ✅ **Mínimo 10.000 registros:** 3.476.105 registros (347x o mínimo)
- ✅ **Pelo menos 2 arquivos:** 3 arquivos CSV distintos
- ✅ **Dados públicos oficiais:** INEP
- ✅ **Dados reais:** Não sintéticos

### Validações Implementadas
- Remoção de duplicatas
- Validação de ranges (notas 0-1000)
- Tratamento de valores ausentes
- Conversão de tipos de dados
- Verificação de consistência

---

## 📊 Estatísticas dos Dados

### Volume
- **Total de registros:** 3.476.105
- **Amostra utilizada:** 50.000 (configurável)
- **Colunas originais:** 76
- **Colunas utilizadas:** 35

### Distribuição Geográfica
- **Estados:** 27
- **Regiões:** 5
- **Municípios:** Milhares

### Áreas de Conhecimento
- Ciências da Natureza (CN)
- Ciências Humanas (CH)
- Linguagens e Códigos (LC)
- Matemática (MT)
- Redação

---

## 🔧 Pipeline de Processamento

### 1. Carregamento (`data_loader.py`)
- Lê CSV com encoding correto
- Seleciona apenas colunas essenciais
- Aplica amostragem estratificada

### 2. Limpeza (`data_cleaner.py`)
- Remove valores ausentes críticos
- Trata inconsistências
- Remove duplicatas

### 3. Transformação (`data_transformer.py`)
- Cria variáveis derivadas
- Padroniza formatos
- Calcula agregações

### 4. Integração (`data_integrator.py`)
- Merge de múltiplos arquivos
- Enriquecimento de dados
- Validação cruzada

### 5. Cache (`data_cache.py`)
- Salva em Parquet
- Gerencia TTL
- Otimiza performance

---

## 💾 Requisitos de Espaço

| Componente | Tamanho |
|------------|---------|
| Dados brutos (raw/) | ~1.8 GB |
| Dados processados (processed/) | ~200 MB |
| Cache (cache/) | ~50-100 MB |
| **Total** | **~2 GB** |

---

## 🔒 Privacidade e Segurança

- **Dados anonimizados:** Sem identificação pessoal
- **Dados públicos:** Disponíveis no portal do INEP
- **LGPD:** Conformidade com lei brasileira de proteção de dados
- **Uso educacional:** Projeto acadêmico

---

## 📚 Referências

- [INEP - Microdados ENEM](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)
- [Dicionário de Dados ENEM](https://download.inep.gov.br/microdados/enem_2022/dicionario_de_dados.xlsx)
- [Apache Parquet](https://parquet.apache.org/)

---

## ❓ Perguntas Frequentes

### Os dados estão incluídos no repositório?
Depende. Arquivos grandes (>100MB) geralmente não são versionados no Git. Você pode precisar baixá-los manualmente.

### Posso usar dados de outros anos?
Sim! Basta baixar os microdados de outros anos e ajustar o `config.py`.

### Como reduzir o uso de memória?
Ajuste `MAX_RECORDS` em `config.py` para usar menos registros.

### O cache expira?
Sim, após 30 dias (configurável). Execute `python pipeline.py` para renovar.

---

**Última atualização:** 20/05/2026  
**Versão:** 1.0.0