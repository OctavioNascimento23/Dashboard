# 📊 Dashboard ENEM - Análise Educacional Brasileira

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)
![Last Update](https://img.shields.io/badge/last%20update-2026--05--20-orange.svg)

## 🎯 Sobre o Projeto

Dashboard interativo para análise compreensiva dos dados do ENEM (Exame Nacional do Ensino Médio), utilizando dados públicos do INEP em formato CSV. Este projeto oferece visualizações avançadas, análises estatísticas e insights automáticos sobre o desempenho educacional brasileiro.

**Desenvolvido como projeto da disciplina de Banco de Dados**

---

## ✨ Funcionalidades Principais

- 📈 **Dashboard Executivo** com 4 KPIs e insights automáticos
- 🔍 **Análise Detalhada** com 4 abas temáticas especializadas
- 🗺️ **Visualizações Geográficas** por estado e região
- 💰 **Análise Socioeconômica** detalhada
- ⚖️ **Análise de Equidade** educacional
- 📊 **10+ Tipos de Visualizações** interativas (mapas, gráficos de barras, linhas, dispersão, etc.)
- 🔄 **Filtros Avançados** combinados (região, estado, tipo de escola, gênero)
- 📥 **Exportação de Dados** filtrados em CSV
- ⚡ **Sistema de Cache Inteligente** (15x mais rápido)

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.8 ou superior
- Git (opcional)
- 2GB de espaço em disco

### Instalação

```bash
# 1. Clonar o repositório (ou baixar ZIP)
git clone [URL_DO_REPOSITORIO]
cd Dashboard

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar pipeline (primeira vez - processa os dados)
python pipeline.py

# 4. Iniciar o dashboard
python app.py
```

### Acesso

Abra o navegador em: **http://localhost:8050**

---

## 📊 Dados

**Fonte:** INEP - Microdados do ENEM 2022

- **Formato:** CSV Local
- **Volume:** 3.476.105 registros (347x o mínimo exigido)
- **Arquivos:**
  - `MICRODADOS_ENEM_2022.csv` (1.5 GB - arquivo principal)
  - `ITENS_PROVA_2022.csv` (0.3 MB - informações das questões)
  - `QUEST_HAB_ESTUDO.csv` (271 MB - questionário socioeconômico)
- **Tipo:** Dados públicos oficiais
- **Ano:** 2022
- **Localização:** `data/raw/`

### Pipeline de Processamento

O projeto implementa um pipeline completo de Ciência de Dados:

1. **Aquisição** (`data_loader.py`): Leitura eficiente de CSV com 76 colunas
2. **Integração** (`data_integrator.py`): Merge de múltiplos arquivos
3. **Limpeza** (`data_cleaner.py`): Tratamento de valores ausentes e inconsistências
4. **Transformação** (`data_transformer.py`): Criação de variáveis e agregações
5. **Análise** (`app.py`): Visualizações e insights automáticos

---

## 🎨 Estrutura do Dashboard

### Dashboard 1: Visão Executiva

- **4 KPIs Principais:**
  - Média Geral Nacional
  - Total de Participantes
  - Taxa de Presença
  - Desempenho por Tipo de Escola

- **4 Insights Automáticos** baseados em análise estatística
- **Visualizações de Alto Nível** (mapas, gráficos sintéticos)

### Dashboard 2: Análise Detalhada

#### 1️⃣ Visão Geral
- Distribuição de notas por região
- Mapa coroplético do Brasil
- Análise temporal de desempenho

#### 2️⃣ Por Área de Conhecimento
- Comparação entre as 5 áreas (CN, CH, LC, MT, Redação)
- Análise por tipo de escola
- Correlações entre áreas

#### 3️⃣ Análise Socioeconômica
- Desempenho por faixa de renda
- Impacto da escolaridade dos pais
- Análise de acesso a recursos

#### 4️⃣ Análise de Equidade
- Comparação por gênero
- Análise por raça/cor
- Gaps educacionais

### Filtros Interativos

- **Região:** Norte, Nordeste, Centro-Oeste, Sudeste, Sul
- **Estado:** Todos os 27 estados
- **Tipo de Escola:** Pública, Privada
- **Gênero:** Masculino, Feminino

---

## 📁 Estrutura do Projeto

```
Dashboard/
├── README.md                        # Este arquivo
├── REQUIREMENTS_CHECKLIST.md        # Validação de requisitos
├── PRESENTATION_GUIDE.md            # Guia de apresentação
├── CHANGELOG.md                     # Histórico de versões
├── requirements.txt                 # Dependências Python
├── .gitignore                       # Arquivos ignorados pelo Git
│
├── app.py                           # Aplicação principal do dashboard
├── pipeline.py                      # Pipeline de processamento de dados
├── config.py                        # Configurações globais
├── version.py                       # Informações de versão
├── VERSION                          # Número da versão (1.0.0)
│
├── src/                             # Código fonte
│   └── data_processing/             # Módulos de processamento
│       ├── __init__.py
│       ├── data_cache.py            # Sistema de cache
│       ├── data_cleaner.py          # Limpeza de dados
│       ├── data_integrator.py       # Integração de fontes
│       ├── data_loader.py           # Carregamento de dados
│       └── data_transformer.py      # Transformações
│
├── data/                            # Dados
│   ├── README.md                    # Documentação dos dados
│   ├── raw/                         # Dados brutos CSV (INEP)
│   │   ├── MICRODADOS_ENEM_2022.csv
│   │   ├── ITENS_PROVA_2022.csv
│   │   └── QUEST_HAB_ESTUDO.csv
│   ├── processed/                   # Dados processados
│   │   ├── enem_processed.csv
│   │   ├── aggregated_by_state.csv
│   │   └── aggregated_by_region.csv
│   └── cache/                       # Cache Parquet (gerado automaticamente)
│
├── docs/                            # Documentação completa
│   ├── INSIGHTS.md                  # Análises e descobertas
│   ├── CSV_ANALYSIS.md              # Estrutura dos dados CSV
│   └── MIGRATION_TO_CSV.md          # Histórico de migração
│
└── assets/                          # Recursos estáticos
    └── styles.css                   # Estilos CSS customizados
```

---

## 🛠️ Tecnologias

- **Backend:** Python 3.8+
- **Dashboard:** Dash + Plotly
- **Dados:** CSV Local (INEP/ENEM 2022)
- **Cache:** Apache Parquet
- **UI:** Bootstrap 5
- **Visualizações:** Plotly Express & Graph Objects
- **Processamento:** Pandas, NumPy, SciPy

---

## 📚 Documentação Completa

- [✅ Checklist de Requisitos](REQUIREMENTS_CHECKLIST.md) - Validação de todos os requisitos
- [🎤 Guia de Apresentação](PRESENTATION_GUIDE.md) - Como apresentar o projeto
- [💡 Insights](docs/INSIGHTS.md) - Análises e descobertas (221 linhas)
- [📋 Análise CSV](docs/CSV_ANALYSIS.md) - Estrutura dos dados
- [🔄 Migração](docs/MIGRATION_TO_CSV.md) - Histórico de migração
- [📝 Changelog](CHANGELOG.md) - Histórico de versões
- [📊 Dados](data/README.md) - Documentação dos dados

---

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

Edite `config.py` para personalizar:

```python
# Cache
CACHE_DIR = "data/cache"
CACHE_EXPIRY_DAYS = 30

# Dashboard
DASH_HOST = "0.0.0.0"
DASH_PORT = 8050
DASH_DEBUG = True

# Performance
MAX_RECORDS = 50000  # Limite de registros para performance
```

### Comandos do Pipeline

```bash
# Processar dados
python pipeline.py

# Limpar cache
python pipeline.py --clear-cache

# Forçar atualização
python pipeline.py --force-update

# Modo verboso
python pipeline.py --verbose
```

---

## 📈 Performance

- **Cache Ativo:** ~2-3 segundos para carregar dashboard
- **Sem Cache:** ~60-90 segundos (primeira execução)
- **Speedup:** 15x mais rápido com cache
- **Tamanho do Cache:** ~50-100 MB (dados agregados em Parquet)
- **Memória em Uso:** ~50 MB (amostra de 50.000 registros)

---

## ✅ Requisitos Atendidos

Este projeto atende e **supera** todos os requisitos da disciplina:

### Pipeline de Ciência de Dados
- ✅ **Aquisição:** Leitura de CSV com Pandas (1.5 GB, 76 colunas)
- ✅ **Integração:** Merge de 3 arquivos distintos
- ✅ **Limpeza:** Tratamento de valores ausentes e inconsistências
- ✅ **Transformação:** Padronização, novas variáveis, agregações
- ✅ **Análise:** 10+ visualizações, estatísticas, insights

### Dashboards
- ✅ **Dashboard 1:** Visão Executiva (4 KPIs + 4 insights + gráficos)
- ✅ **Dashboard 2:** Análise Interativa (10 visualizações + 4 filtros)
- ✅ **Design:** Interface moderna, responsiva, cores consistentes

### Dados
- ✅ **Volume:** 3.476.105 registros (347x o mínimo de 10.000)
- ✅ **Fontes:** 3 arquivos CSV distintos do INEP

### Entregáveis
- ✅ **Código:** 7 módulos + aplicação principal
- ✅ **Dados:** Raw + Processed + Cache
- ✅ **Documentação:** 6 arquivos (1.500+ linhas)

**Ver detalhes completos em:** [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md)

---

## 🐛 Troubleshooting

### Dashboard não carrega
```bash
# 1. Verificar se o pipeline foi executado
python pipeline.py

# 2. Verificar se há dados em cache
ls data/cache/

# 3. Ver logs
cat pipeline.log
```

### Erro de Memória
- Reduza `MAX_RECORDS` em `config.py` (padrão: 50.000)
- Feche outros programas
- Use amostragem menor

### Performance Lenta
```bash
# Certifique-se de que o cache está ativo
python pipeline.py

# Verifique espaço em disco
df -h
```

### Arquivo CSV não encontrado
```bash
# Verificar se os arquivos existem
ls -lh data/raw/

# Se não existir, baixar do INEP:
# https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
```

---

## 📊 Estatísticas do Projeto

- **Linhas de Código:** ~3.000+
- **Módulos:** 7
- **Visualizações:** 10+
- **Filtros:** 4
- **Documentação:** 6 arquivos (1.500+ linhas)
- **Registros Processados:** 3.476.105
- **Tempo de Desenvolvimento:** 1 mês (pesquisas, desenvolvimento, refatorações, testes , etc.)

---

## 🤝 Contribuindo

Este é um projeto acadêmico, mas sugestões são bem-vindas:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é desenvolvido para fins educacionais como parte do curso de Sistemas de Informação da PUC-Campinas, 5o semestre de 2026.

---

## 👥 Autores

**Equipe Dashboard ENEM:**
EDUARDA PICOLO BARBOZA
EDUARDO SANVIDO APOLINARIO
LAURA NOGUEIRA PEREIRA
NANDO BALZANELI PORZIA
OCTÁVIO AUGUSTO DOS SANTOS NASCIMENTO

---

## 🙏 Agradecimentos

- [INEP](https://www.gov.br/inep/) - Pelos dados públicos do ENEM
- Comunidade Dash/Plotly - Pelas excelentes ferramentas de visualização
- Professor Jose Guilherme Picolo - Pelo lecionamento e orientação
- PUC-Campinas - Pelas oportunidades de ensino e pesquisa

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte a [documentação completa](docs/)
2. Verifique o [guia de troubleshooting](#-troubleshooting)
3. Consulte o [CHANGELOG.md](CHANGELOG.md) para histórico de versões
4. Revise o [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md)

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**

**Versão 1.0.0** - Lançamento em 20/05/2026

---

## 📌 Links Úteis

- [INEP - Microdados ENEM](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)
- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)