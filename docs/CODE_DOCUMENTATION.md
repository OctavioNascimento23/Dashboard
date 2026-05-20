# Documentação Técnica do Código - Dashboard ENEM

## Índice

1. [Arquitetura Geral](#arquitetura-geral)
2. [Módulos Principais](#módulos-principais)
3. [Fluxo de Dados](#fluxo-de-dados)
4. [Callbacks do Dash](#callbacks-do-dash)
5. [Sistema de Cache](#sistema-de-cache)
6. [Exemplos de Uso](#exemplos-de-uso)

---

## Arquitetura Geral

O Dashboard ENEM é uma aplicação web interativa construída com Dash/Plotly para análise de dados educacionais do ENEM 2022. A arquitetura segue o padrão ETL (Extract, Transform, Load) com componentes modulares.

```
Dashboard ENEM
│
├── Camada de Apresentação (app.py)
│   ├── Interface Dash
│   ├── Visualizações Plotly
│   └── Callbacks Interativos
│
├── Camada de Processamento (src/data_processing/)
│   ├── DataLoader: Carregamento de dados
│   ├── DataCleaner: Limpeza e validação
│   ├── DataTransformer: Transformações e features
│   ├── DataIntegrator: Integração de datasets
│   └── DataCache: Sistema de cache
│
├── Camada de Configuração
│   ├── config.py: Configurações globais
│   └── version.py: Versionamento
│
└── Pipeline ETL (pipeline.py)
    └── Orquestração do fluxo completo
```

### Tecnologias Principais

- **Dash/Plotly**: Framework web e visualizações
- **Pandas**: Manipulação de dados
- **Parquet**: Formato de cache eficiente
- **Bootstrap**: Estilização UI

---

## Módulos Principais

### 1. app.py

**Descrição**: Aplicação principal do dashboard com interface web completa.

**Responsabilidades**:
- Inicialização da aplicação Dash
- Carregamento inicial dos dados
- Definição do layout (UI)
- Implementação de callbacks interativos
- Geração de visualizações

**Funções Principais**:

#### `create_kpi_card(title, value, subtitle, color, icon="")`
Cria um cartão KPI (Key Performance Indicator) estilizado.

**Parâmetros**:
- `title` (str): Título do KPI
- `value` (str): Valor principal a exibir
- `subtitle` (str): Texto descritivo
- `color` (str): Cor do tema (primary, success, warning, info, danger)
- `icon` (str): Classe do ícone FontAwesome

**Retorna**: Componente `dbc.Card`

**Exemplo**:
```python
card = create_kpi_card(
    "Média Nacional", 
    "542.3", 
    "pontos", 
    "primary",
    "fa-chart-line"
)
```

#### `generate_insights(df)`
Gera insights automáticos a partir dos dados.

**Parâmetros**:
- `df` (pd.DataFrame): DataFrame com dados do ENEM

**Retorna**: Lista de dicionários com insights

**Lógica**:
1. Identifica melhor estado por desempenho
2. Calcula gap de gênero
3. Analisa diferença público-privado
4. Mede disparidade regional

#### `create_subject_comparison(df)`
Cria gráfico radar comparando desempenho entre disciplinas.

**Parâmetros**:
- `df` (pd.DataFrame): Dados do ENEM

**Retorna**: `plotly.graph_objects.Figure`

**Visualização**: Gráfico radar com 5 áreas (Matemática, Ciências Natureza, Ciências Humanas, Linguagens, Redação)

#### `create_state_ranking(df)`
Gera ranking horizontal de estados por desempenho.

**Parâmetros**:
- `df` (pd.DataFrame): Dados do ENEM

**Retorna**: `plotly.express.Figure`

**Características**:
- Ordenação por nota média
- Escala de cores (RdYlGn)
- Orientação horizontal para melhor legibilidade

#### `create_equity_analysis(df)`
Cria análise multi-dimensional de equidade educacional.

**Parâmetros**:
- `df` (pd.DataFrame): Dados do ENEM

**Retorna**: `plotly.graph_objects.Figure` com subplots

**Análises**:
1. Gap de gênero
2. Gap público-privado
3. Gap por cor/raça
4. Gap urbano-rural

**Callbacks Principais**:

1. **`render_content(active_tab)`**: Renderiza conteúdo baseado na aba ativa
2. **`update_detailed_content(active_tab, n_clicks, ...)`**: Atualiza análise detalhada com filtros
3. **`export_data(n_clicks, ...)`**: Exporta dados filtrados para CSV

---

### 2. config.py

**Descrição**: Configurações centralizadas do sistema.

**Constantes Principais**:

```python
# Arquivos CSV
CSV_FILES = {
    'microdados': 'MICRODADOS_ENEM_2022.csv',
    'itens_prova': 'ITENS_PROVA_2022.csv',
    'questionario': 'QUEST_HAB_ESTUDO.csv'
}

# Performance
DEFAULT_YEAR = 2022
MAX_RECORDS = 50000
CHUNK_SIZE = 10000

# Cache
USE_CACHE = True
CACHE_TTL_DAYS = 30
CACHE_FORMAT = "parquet"

# Colunas essenciais (35 de 76 totais)
ESSENTIAL_COLUMNS = [
    'NU_INSCRICAO', 'NU_ANO', 'TP_FAIXA_ETARIA',
    'TP_SEXO', 'TP_COR_RACA', 'SG_UF_PROVA',
    'NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH',
    'NU_NOTA_LC', 'NU_NOTA_REDACAO', ...
]
```

**Funções Auxiliares**:

#### `create_directories()`
Cria estrutura de diretórios necessária.

#### `get_region_for_state(state: str) -> str`
Retorna região brasileira para um estado.

**Exemplo**:
```python
regiao = get_region_for_state('SP')  # Retorna: 'Sudeste'
```

#### `validate_config() -> List[str]`
Valida configurações e retorna lista de problemas encontrados.

---

### 3. pipeline.py

**Descrição**: Pipeline ETL completo para processamento de dados.

**Função Principal**:

#### `run_pipeline(args=None)`
Executa pipeline completo de dados.

**Etapas**:

1. **STEP 1: LOAD RAW DATA**
   - Carrega dados do CSV local
   - Aplica filtros (ano, estados, limite)
   - Usa cache se disponível

2. **STEP 2: CLEAN DATA**
   - Remove duplicatas
   - Valida ranges de notas
   - Limpa dados demográficos e geográficos

3. **STEP 3: TRANSFORM DATA**
   - Calcula notas médias
   - Cria categorias de desempenho
   - Gera índice socioeconômico
   - Adiciona features derivadas

4. **STEP 4: CREATE AGGREGATIONS**
   - Agregação por estado
   - Agregação por região

5. **STEP 5: SAVE PROCESSED DATA**
   - Salva em `data/processed/`
   - Formato CSV para compatibilidade

6. **STEP 6: VALIDATION**
   - Valida integridade dos dados
   - Verifica requisitos mínimos

**Argumentos de Linha de Comando**:

```bash
# Usar dados locais
python pipeline.py --source local

# Processar ano específico
python pipeline.py --source local --year 2022

# Limitar registros
python pipeline.py --source local --limit 10000

# Forçar refresh do cache
python pipeline.py --source local --force-refresh

# Pular agregações (mais rápido)
python pipeline.py --source local --skip-aggregations
```

---

### 4. version.py

**Descrição**: Gerenciamento de versões do sistema.

**Constantes**:
```python
__version__ = "1.0.0"
__date__ = "2026-05-20"
__author__ = "Grupo 08"
__status__ = "Production"
```

**Funções**:

#### `get_version_info() -> dict`
Retorna informações completas da versão.

#### `get_version_string() -> str`
Retorna string formatada: "v1.0.0 (2026-05-20)"

---

## Módulos de Processamento de Dados

### src/data_processing/data_loader.py

**Classe**: `DataLoader`

**Descrição**: Carrega dados do ENEM de arquivos CSV locais com amostragem inteligente.

**Características**:
- Carregamento eficiente (apenas colunas essenciais)
- Amostragem estratificada por estado
- Suporte a cache
- Validação automática

**Métodos Principais**:

#### `__init__(data_dir="data/raw", use_cache=True)`
Inicializa o carregador de dados.

#### `load_enem_data(year=2022, max_records=50000, states=None, force_refresh=False)`
Carrega dados do ENEM com amostragem inteligente.

**Fluxo**:
1. Verifica cache
2. Lê CSV com colunas essenciais
3. Filtra por ano e estados
4. Remove participantes inválidos
5. Aplica amostragem estratificada
6. Limpa dados básicos
7. Salva em cache

**Exemplo**:
```python
loader = DataLoader()
df = loader.load_enem_data(
    year=2022,
    max_records=50000,
    states=['SP', 'RJ', 'MG']
)
```

#### `_stratified_sample(df, n_samples)`
Amostragem estratificada por estado para manter distribuição geográfica.

**Algoritmo**:
1. Calcula proporção de cada estado
2. Distribui amostras proporcionalmente
3. Ajusta para atingir exatamente n_samples
4. Amostra de cada estado

#### `_filter_valid_participants(df)`
Remove participantes que não fizeram nenhuma prova.

#### `get_data_summary(df) -> dict`
Retorna estatísticas resumidas dos dados carregados.

---

### src/data_processing/data_cleaner.py

**Classe**: `DataCleaner`

**Descrição**: Limpa e valida dados brutos.

**Métodos Principais**:

#### `clean_enem_data(df) -> pd.DataFrame`
Limpa dados do ENEM.

**Etapas**:
1. Remove duplicatas (por NU_INSCRICAO)
2. Padroniza nomes de colunas
3. Trata valores ausentes em notas
4. Valida ranges de notas (0-1000)
5. Limpa dados demográficos
6. Limpa dados geográficos
7. Remove linhas com dados críticos ausentes

**Exemplo**:
```python
cleaner = DataCleaner()
df_clean = cleaner.clean_enem_data(df_raw)
cleaner.print_cleaning_report()
```

#### `_validate_score_ranges(df, score_columns)`
Valida que notas estão no range válido [0, 1000].

#### `_clean_demographics(df)`
Limpa colunas demográficas:
- Gênero: padroniza para 'M' ou 'F'
- Idade: valida range 15-80 anos
- Cor/Raça: valida códigos 0-6

#### `_clean_geographic(df)`
Limpa códigos de estados (UF):
- Padroniza para maiúsculas
- Valida contra lista de 27 UFs brasileiras
- Remove códigos inválidos

#### `print_cleaning_report()`
Imprime relatório detalhado da limpeza.

---

### src/data_processing/data_transformer.py

**Classe**: `DataTransformer`

**Descrição**: Transforma dados e cria novas features.

**Métodos Principais**:

#### `transform_enem_data(df) -> pd.DataFrame`
Transforma dados do ENEM criando features derivadas.

**Transformações**:
1. Calcula notas médias e totais
2. Cria categorias de desempenho
3. Gera índice socioeconômico
4. Cria labels demográficas
5. Adiciona agrupamentos regionais
6. Cria faixas etárias

**Exemplo**:
```python
transformer = DataTransformer()
df_transformed = transformer.transform_enem_data(df_clean)
```

#### `_calculate_average_scores(df)`
Calcula NOTA_MEDIA e NOTA_TOTAL.

**Fórmula**:
```python
NOTA_MEDIA = mean(NU_NOTA_MT, NU_NOTA_CN, NU_NOTA_CH, 
                  NU_NOTA_LC, NU_NOTA_REDACAO)
NOTA_TOTAL = sum(todas as notas)
```

#### `_create_performance_categories(df)`
Cria categorias de desempenho:
- Baixo: 0-450
- Médio: 450-550
- Alto: 550-650
- Excelente: 650-1000

#### `_create_socioeconomic_index(df)`
Cria índice socioeconômico composto (0-10).

**Componentes**:
- Q006: Renda familiar (A-Q → 0-16)
- Q001: Escolaridade do pai (A-H → 0-7)
- Q002: Escolaridade da mãe (A-H → 0-7)

**Fórmula**:
```python
INDICE_SOCIOECONOMICO = normalize(mean(RENDA, EDUC_PAI, EDUC_MAE))
```

Também cria quintis socioeconômicos (Q1-Q5).

#### `_create_regional_groupings(df)`
Mapeia estados para regiões:
- Norte: AC, AP, AM, PA, RO, RR, TO
- Nordeste: AL, BA, CE, MA, PB, PE, PI, RN, SE
- Sudeste: ES, MG, RJ, SP
- Sul: PR, RS, SC
- Centro-Oeste: DF, GO, MT, MS

#### `aggregate_by_state(df) -> pd.DataFrame`
Agrega dados por estado.

**Métricas**:
- Contagem de estudantes
- Média, mediana e desvio padrão de cada nota

**Exemplo de saída**:
```
SG_UF | TOTAL_ESTUDANTES | NU_NOTA_MT_mean | NU_NOTA_MT_median | ...
SP    | 15000           | 542.3           | 538.0             | ...
RJ    | 8000            | 535.1           | 531.5             | ...
```

#### `aggregate_by_region(df) -> pd.DataFrame`
Agrega dados por região (mesma estrutura que por estado).

---

### src/data_processing/data_integrator.py

**Classe**: `DataIntegrator`

**Descrição**: Integra múltiplos datasets.

**Métodos Principais**:

#### `concatenate_years(dataframes, year_column='NU_ANO')`
Concatena múltiplos anos de dados verticalmente.

**Exemplo**:
```python
integrator = DataIntegrator()
df_multi_year = integrator.concatenate_years([df_2020, df_2021, df_2022])
```

#### `merge_enem_censo(df_enem, df_censo, how='left')`
Merge ENEM com Censo Escolar por código da escola.

**Chaves de merge**:
- ENEM: CO_ESCOLA
- Censo: CO_ENTIDADE

#### `validate_integration(df) -> dict`
Valida dataset integrado.

**Validações**:
- Total de linhas e colunas
- Percentual de dados ausentes
- Linhas duplicadas
- Uso de memória
- Presença de colunas obrigatórias
- Requisito mínimo de registros (10,000+)

**Exemplo de retorno**:
```python
{
    'total_rows': 50000,
    'total_columns': 45,
    'missing_percentage': 2.5,
    'duplicate_rows': 0,
    'memory_usage_mb': 125.3,
    'has_required_columns': True,
    'meets_minimum_records': True
}
```

---

### src/data_processing/data_cache.py

**Classe**: `DataCache`

**Descrição**: Sistema de cache local para otimização de performance.

**Características**:
- Formato Parquet (eficiente)
- TTL (Time To Live) configurável
- Metadados de cache
- Limpeza automática de cache expirado

**Métodos Principais**:

#### `__init__(cache_dir="data/cache", ttl_days=30)`
Inicializa gerenciador de cache.

**Estrutura de diretórios**:
```
data/cache/
├── raw/          # Dados brutos
├── processed/    # Dados processados
└── aggregated/   # Dados agregados
```

#### `save(df, cache_type="raw", filename=None, **params)`
Salva DataFrame no cache.

**Parâmetros**:
- `df`: DataFrame para salvar
- `cache_type`: Tipo (raw, processed, aggregated)
- `filename`: Nome opcional (gera hash se None)
- `**params`: Parâmetros para gerar chave única

**Exemplo**:
```python
cache = DataCache()
cache.save(df, cache_type="raw", year=2022, state="SP")
```

**Formato de arquivo**:
- Dados: `cache_{hash}.parquet` (compressão Snappy)
- Metadados: `cache_{hash}_metadata.json`

#### `load(cache_type="raw", filename=None, force_refresh=False, **params)`
Carrega DataFrame do cache.

**Retorna**: DataFrame ou None se cache inválido/inexistente

**Validações**:
1. Verifica se arquivo existe
2. Valida TTL (não expirado)
3. Carrega dados

#### `_get_cache_key(**params) -> str`
Gera chave única (hash MD5) baseada em parâmetros.

**Exemplo**:
```python
# Parâmetros: {'year': 2022, 'state': 'SP'}
# Retorna: '9eb1a81f3a97aa111b5024ae842696fa'
```

#### `clear_cache(cache_type=None, older_than_days=None)`
Limpa cache.

**Opções**:
- `cache_type=None`: Limpa todos os tipos
- `older_than_days=None`: Limpa todos (independente da idade)
- `older_than_days=7`: Limpa apenas caches com mais de 7 dias

#### `get_cache_info() -> dict`
Retorna estatísticas do cache.

**Exemplo de retorno**:
```python
{
    'cache_dir': 'data/cache',
    'ttl_days': 30,
    'types': {
        'raw': {
            'total_files': 5,
            'valid_files': 4,
            'expired_files': 1,
            'total_size_mb': 245.8
        },
        'processed': {...},
        'aggregated': {...}
    }
}
```

#### `print_cache_info()`
Imprime informações formatadas do cache.

---

## Fluxo de Dados

### Fluxo Completo do Pipeline

```
1. CARREGAMENTO (DataLoader)
   ├── Lê CSV local (MICRODADOS_ENEM_2022.csv)
   ├── Seleciona apenas colunas essenciais (35/76)
   ├── Filtra por ano e estados (se especificado)
   ├── Remove participantes inválidos
   ├── Aplica amostragem estratificada (se necessário)
   └── Verifica/salva em cache
   
2. LIMPEZA (DataCleaner)
   ├── Remove duplicatas
   ├── Padroniza nomes de colunas
   ├── Valida ranges de notas (0-1000)
   ├── Limpa dados demográficos
   ├── Limpa dados geográficos
   └── Remove dados críticos ausentes
   
3. TRANSFORMAÇÃO (DataTransformer)
   ├── Calcula notas médias e totais
   ├── Cria categorias de desempenho
   ├── Gera índice socioeconômico
   ├── Adiciona labels demográficas
   ├── Cria agrupamentos regionais
   └── Define faixas etárias
   
4. AGREGAÇÃO (DataTransformer)
   ├── Agrega por estado (27 UFs)
   │   └── Média, mediana, desvio padrão por nota
   └── Agrega por região (5 regiões)
       └── Mesmas métricas
   
5. INTEGRAÇÃO (DataIntegrator)
   ├── Concatena múltiplos anos (se aplicável)
   ├── Merge com Censo Escolar (opcional)
   ├── Merge com dados estaduais (opcional)
   └── Valida integridade final
   
6. PERSISTÊNCIA
   ├── Salva dados processados (CSV)
   ├── Salva agregações (CSV)
   └── Atualiza cache (Parquet)
   
7. VISUALIZAÇÃO (app.py)
   ├── Carrega dados processados
   ├── Gera visualizações interativas
   ├── Aplica filtros dinâmicos
   └── Exporta dados filtrados
```

### Fluxo de Dados no Dashboard

```
Usuário → Interface Dash
    ↓
Seleção de Aba/Filtros
    ↓
Callback Acionado
    ↓
Filtragem de Dados (df_main)
    ↓
Geração de Visualizações
    ↓
Atualização da UI
```

---

## Callbacks do Dash

### 1. render_content(active_tab)

**Trigger**: Mudança de aba (executive/detailed)

**Input**: `tabs.active_tab`

**Output**: `page-content.children`

**Lógica**:
- Se `executive`: Renderiza visão executiva com KPIs e insights
- Se `detailed`: Renderiza análise detalhada com filtros

**Componentes Gerados**:

**Visão Executiva**:
- 4 cartões KPI (Média Nacional, Total Estudantes, Gap, Estados)
- Cartão de insights automáticos
- Ranking de estados
- Distribuição de notas
- Comparação regional
- Desempenho por área

**Análise Detalhada**:
- Filtros avançados (região, estado, tipo escola, gênero)
- Sub-abas temáticas (Visão Geral, Por Área, Socioeconômico, Equidade)
- Botão de exportação

---

### 2. update_detailed_content(active_tab, n_clicks, region, state, school_type, gender)

**Trigger**: Mudança de sub-aba ou clique em "Aplicar Filtros"

**Inputs**:
- `detailed-tabs.active_tab`
- `apply-filters.n_clicks`
- `region-filter.value`
- `state-filter.value`
- `school-type-filter.value`
- `gender-filter.value`

**Output**: `detailed-content.children`

**Lógica**:

1. **Filtragem**:
```python
filtered_df = df_main.copy()
if region != 'ALL':
    filtered_df = filtered_df[filtered_df['regiao'] == region]
if state != 'ALL':
    filtered_df = filtered_df[filtered_df['sigla_uf'] == state]
# ... outros filtros
```

2. **Geração de Conteúdo por Sub-aba**:
   - `overview`: Distribuição e comparação regional
   - `subjects`: Radar e barras por área
   - `socioeconomic`: Box plot por renda
   - `equity`: Análise multi-dimensional de gaps

3. **Cartão de Estatísticas**:
   - Total de registros filtrados
   - Média, mediana, desvio padrão
   - Mínimo, máximo, amplitude

---

### 3. export_data(n_clicks, region, state, school_type, gender)

**Trigger**: Clique no botão "Baixar CSV"

**Inputs**:
- `export-button.n_clicks`
- Valores dos filtros (States)

**Output**: `download-data.data`

**Lógica**:
1. Previne execução inicial (`prevent_initial_call=True`)
2. Aplica mesmos filtros da análise detalhada
3. Retorna arquivo CSV para download

**Exemplo de uso**:
```python
# Usuário clica em "Baixar CSV"
# Sistema aplica filtros ativos
# Gera: enem_data_filtered.csv
```

---

## Sistema de Cache

### Arquitetura do Cache

```
DataCache
├── Diretórios
│   ├── data/cache/raw/          # Dados brutos do CSV
│   ├── data/cache/processed/    # Dados após limpeza/transformação
│   └── data/cache/aggregated/   # Dados agregados
│
├── Arquivos
│   ├── cache_{hash}.parquet     # Dados (formato Parquet + Snappy)
│   └── cache_{hash}_metadata.json  # Metadados
│
└── Metadados
    ├── cached_at: timestamp de criação
    ├── expires_at: timestamp de expiração
    ├── ttl_days: tempo de vida
    ├── rows: número de linhas
    ├── columns: número de colunas
    ├── memory_mb: uso de memória
    └── params: parâmetros da query
```

### Estratégia de Cache

**Quando usar cache**:
- Carregamento de dados brutos (CSV grande)
- Dados processados (após limpeza/transformação)
- Agregações (por estado/região)

**Quando invalidar cache**:
- TTL expirado (padrão: 30 dias)
- Force refresh (`--force-refresh`)
- Mudança nos parâmetros de query

**Benefícios**:
- Reduz tempo de carregamento de ~30s para ~2s
- Economiza processamento
- Formato Parquet é 5-10x menor que CSV

### Exemplo de Uso do Cache

```python
# Inicializar cache
cache = DataCache(ttl_days=30)

# Salvar dados
cache.save(df, cache_type="raw", year=2022, max_records=50000)

# Carregar dados (verifica validade automaticamente)
df_cached = cache.load(cache_type="raw", year=2022, max_records=50000)

# Verificar informações
cache.print_cache_info()

# Limpar cache expirado
cache.clear_cache(older_than_days=30)

# Limpar todo o cache
cache.clear_cache()
```

---

## Exemplos de Uso

### Exemplo 1: Executar Pipeline Completo

```bash
# Pipeline completo com dados locais
python pipeline.py --source local

# Com limite de registros (para testes)
python pipeline.py --source local --limit 10000

# Forçar refresh do cache
python pipeline.py --source local --force-refresh

# Processar estados específicos
python pipeline.py --source local --states SP RJ MG
```

### Exemplo 2: Carregar e Processar Dados Programaticamente

```python
from src.data_processing.data_loader import DataLoader
from src.data_processing.data_cleaner import DataCleaner
from src.data_processing.data_transformer import DataTransformer

# 1. Carregar dados
loader = DataLoader()
df_raw = loader.load_enem_data(year=2022, max_records=50000)

# 2. Limpar dados
cleaner = DataCleaner()
df_clean = cleaner.clean_enem_data(df_raw)
cleaner.print_cleaning_report()

# 3. Transformar dados
transformer = DataTransformer()
df_transformed = transformer.transform_enem_data(df_clean)

# 4. Criar agregações
df_state = transformer.aggregate_by_state(df_transformed)
df_region = transformer.aggregate_by_region(df_transformed)

# 5. Salvar resultados
df_transformed.to_csv('data/processed/enem_processed.csv', index=False)
df_state.to_csv('data/processed/aggregated_by_state.csv', index=False)
df_region.to_csv('data/processed/aggregated_by_region.csv', index=False)
```

### Exemplo 3: Usar Cache Manualmente

```python
from src.data_processing.data_cache import DataCache
import pandas as pd

# Inicializar cache
cache = DataCache(ttl_days=30)

# Salvar DataFrame
df = pd.read_csv('data/raw/MICRODADOS_ENEM_2022.csv', nrows=10000)
cache.save(df, cache_type="raw", year=2022, sample=True)

# Carregar do cache
df_cached = cache.load(cache_type="raw", year=2022, sample=True)

if df_cached is not None:
    print(f"Carregado do cache: {len(df_cached)} linhas")
else:
    print("Cache não encontrado ou expirado")

# Ver informações do cache
cache.print_cache_info()

# Limpar cache antigo (mais de 7 dias)
cache.clear_cache(older_than_days=7)
```

### Exemplo 4: Criar Visualização Customizada

```python
import plotly.express as px
import pandas as pd

# Carregar dados processados
df = pd.read_csv('data/processed/enem_processed.csv')

# Criar visualização customizada
fig = px.scatter(
    df,
    x='nota_matematica',
    y='nota_redacao',
    color='regiao',
    size='nota_media',
    hover_data=['sigla_uf', 'tipo_escola'],
    title='Relação entre Matemática e Redação por Região'
)

fig.show()
```

### Exemplo 5: Análise Exploratória

```python
import pandas as pd
import numpy as np

# Carregar dados
df = pd.read_csv('data/processed/enem_processed.csv')

# Estatísticas descritivas
print(df[['nota_matematica', 'nota_ciencias_natureza', 
          'nota_ciencias_humanas', 'nota_linguagens', 
          'nota_redacao']].describe())

# Correlação entre notas
correlation = df[['nota_matematica', 'nota_ciencias_natureza', 
                  'nota_ciencias_humanas', 'nota_linguagens', 
                  'nota_redacao']].corr()
print(correlation)

# Análise por região
regional_stats = df.groupby('regiao').agg({
    'nota_media': ['mean', 'median', 'std'],
    'nota_matematica': 'mean',
    'nota_redacao': 'mean'
}).round(2)
print(regional_stats)

# Top 10 estados por desempenho
top_states = df.groupby('sigla_uf')['nota_media'].mean().sort_values(ascending=False).head(10)
print(top_states)
```

### Exemplo 6: Executar Dashboard

```bash
# Executar dashboard localmente
python app.py

# Dashboard estará disponível em:
# http://localhost:8050

# Para produção (com Gunicorn):
gunicorn app:server -b 0.0.0.0:8050 --workers 4
```

---

## Estrutura de Dados

### DataFrame Principal (df_main)

**Colunas Originais** (do CSV):
- `NU_INSCRICAO`: Número de inscrição
- `NU_ANO`: Ano do ENEM
- `SG_UF_PROVA`: Sigla do estado
- `TP_SEXO`: Sexo (M/F)
- `TP_FAIXA_ETARIA`: Código da faixa etária
- `TP_COR_RACA`: Código de cor/raça
- `TP_ESCOLA`: Tipo de escola
- `TP_LOCALIZACAO_ESC`: Localização (urbana/rural)
- `NU_NOTA_MT`: Nota de Matemática
- `NU_NOTA_CN`: Nota de Ciências da Natureza
- `NU_NOTA_CH`: Nota de Ciências Humanas
- `NU_NOTA_LC`: Nota de Linguagens
- `NU_NOTA_REDACAO`: Nota de Redação
- `Q001`: Escolaridade do pai
- `Q002`: Escolaridade da mãe
- `Q005`: Renda familiar

**Colunas Derivadas** (após transformação):
- `nota_media`: Média das 5 notas
- `nota_total`: Soma das 5 notas
- `regiao`: Região brasileira
- `CATEGORIA_DESEMPENHO`: Baixo/Médio/Alto/Excelente
- `INDICE_SOCIOECONOMICO`: Índice 0-10
- `QUINTIL_SOCIOECONOMICO`: Q1-Q5
- `FAIXA_ETARIA`: Grupos de idade

### DataFrame Agregado por Estado

**Estrutura**:
```
SG_UF | TOTAL_ESTUDANTES | NU_NOTA_MT_mean | NU_NOTA_MT_median | NU_NOTA_MT_std | ...
```

### DataFrame Agregado por Região

**Estrutura**:
```
REGIAO | TOTAL_ESTUDANTES | NU_NOTA_MT_mean | NU_NOTA_MT_median | NU_NOTA_MT_std | ...
```

---

## Otimizações de Performance

### 1. Carregamento Seletivo de Colunas
```python
# Carrega apenas 35 de 76 colunas
df = pd.read_csv(csv_file, usecols=ESSENTIAL_COLUMNS)
# Reduz uso de memória em ~50%
```

### 2. Amostragem Estratificada
```python
# Mantém distribuição geográfica
df_sampled = _stratified_sample(df, max_records=50000)
# Reduz dados de 3M+ para 50K mantendo representatividade
```

### 3. Cache em Parquet
```python
# Parquet é 5-10x menor e mais rápido que CSV
df.to_parquet(cache_path, compression='snappy')
# Carregamento: 30s → 2s
```

### 4. Lazy Loading
```python
# Dashboard carrega dados apenas uma vez na inicialização
# Callbacks trabalham com dados em memória
```

### 5. Tipos de Dados Otimizados
```python
# Converte categorias para strings (mais eficiente)
df['TP_SEXO'] = df['TP_SEXO'].astype('category')
```

---

## Tratamento de Erros

### Erros Comuns e Soluções

**1. Arquivo CSV não encontrado**
```
FileNotFoundError: ENEM data file not found
```
**Solução**: Verificar se `MICRODADOS_ENEM_2022.csv` está em `data/raw/`

**2. Memória insuficiente**
```
MemoryError: Unable to allocate array
```
**Solução**: Reduzir `MAX_RECORDS` em `config.py`

**3. Cache corrompido**
```
Failed to load cache: ...
```
**Solução**: Limpar cache com `cache.clear_cache()`

**4. Encoding de caracteres**
```
UnicodeDecodeError: ...
```
**Solução**: CSV usa `encoding='latin1'` (já configurado)

---

## Manutenção e Extensão

### Adicionar Nova Visualização

1. Criar função de visualização em `app.py`:
```python
def create_my_chart(df):
    fig = px.bar(df, x='categoria', y='valor')
    return fig
```

2. Adicionar ao layout:
```python
dcc.Graph(figure=create_my_chart(df_main))
```

### Adicionar Novo Filtro

1. Adicionar dropdown em `create_advanced_filters()`:
```python
dcc.Dropdown(
    id='my-filter',
    options=[...],
    value='ALL'
)
```

2. Atualizar callback `update_detailed_content()`:
```python
@callback(
    ...,
    State('my-filter', 'value')
)
def update_detailed_content(..., my_filter):
    if my_filter != 'ALL':
        filtered_df = filtered_df[filtered_df['coluna'] == my_filter]
```

### Adicionar Nova Transformação

1. Criar método em `DataTransformer`:
```python
def _create_my_feature(self, df):
    df['MY_FEATURE'] = df['col1'] + df['col2']
    return df
```

2. Adicionar em `transform_enem_data()`:
```python
df_transformed = self._create_my_feature(df_transformed)
```

---

## Referências

- **Dash Documentation**: https://dash.plotly.com/
- **Plotly Python**: https://plotly.com/python/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **INEP - Microdados ENEM**: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

---

**Última Atualização**: 2026-05-20
**Versão**: 1.0.0  
**Autor**: Grupo 08