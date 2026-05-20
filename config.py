"""
Configurações do Sistema de Dados ENEM
Configurações para dados locais CSV, Cache e Performance
"""

import os
from pathlib import Path

# ============================================================================
# CONFIGURAÇÕES DE ARQUIVOS CSV LOCAIS
# ============================================================================

# Diretório de dados brutos
LOCAL_RAW_DIR = Path("data/raw")
LOCAL_PROCESSED_DIR = Path("data/processed")

# Arquivos CSV disponíveis
CSV_FILES = {
    'microdados': 'MICRODADOS_ENEM_2022.csv',  # Arquivo principal
    'itens_prova': 'ITENS_PROVA_2022.csv',     # Informações das questões
    'questionario': 'QUEST_HAB_ESTUDO.csv'      # Questionário (redundante)
}

# ============================================================================
# CONFIGURAÇÕES DE CACHE
# ============================================================================

# Diretório base para cache
CACHE_DIR = Path("data/cache")
CACHE_RAW_DIR = CACHE_DIR / "raw"
CACHE_PROCESSED_DIR = CACHE_DIR / "processed"
CACHE_AGGREGATED_DIR = CACHE_DIR / "aggregated"

# Tempo de vida do cache (em dias)
CACHE_TTL_DAYS = 30

# Habilitar/desabilitar cache
USE_CACHE = True

# Formato do cache (parquet é mais eficiente que CSV)
CACHE_FORMAT = "parquet"  # ou "csv"

# ============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ============================================================================

# Ano padrão para análise
DEFAULT_YEAR = 2022

# Limite máximo de registros (para performance)
MAX_RECORDS = 50000

# Chunk size para processamento em lotes
CHUNK_SIZE = 10000

# ============================================================================
# COLUNAS ESSENCIAIS DO CSV
# ============================================================================

# Colunas essenciais do MICRODADOS_ENEM_2022.csv (35 colunas de 76 totais)
ESSENTIAL_COLUMNS = [
    # Identificação
    'NU_INSCRICAO',
    'NU_ANO',
    
    # Demográficas
    'TP_FAIXA_ETARIA',
    'TP_SEXO',
    'TP_COR_RACA',
    'TP_ESTADO_CIVIL',
    
    # Educação
    'TP_ST_CONCLUSAO',
    'TP_ANO_CONCLUIU',
    'TP_ESCOLA',
    'TP_ENSINO',
    'TP_DEPENDENCIA_ADM_ESC',
    'TP_LOCALIZACAO_ESC',
    
    # Localização
    'SG_UF_ESC',
    'NO_MUNICIPIO_ESC',
    'SG_UF_PROVA',
    'NO_MUNICIPIO_PROVA',
    
    # Presença nas provas
    'TP_PRESENCA_CN',
    'TP_PRESENCA_CH',
    'TP_PRESENCA_LC',
    'TP_PRESENCA_MT',
    
    # Notas
    'NU_NOTA_CN',
    'NU_NOTA_CH',
    'NU_NOTA_LC',
    'NU_NOTA_MT',
    'NU_NOTA_REDACAO',
    
    # Questionário Socioeconômico (principais)
    'Q001',  # Escolaridade do pai
    'Q002',  # Escolaridade da mãe
    'Q005',  # Renda familiar
    'Q006',  # Pessoas na residência
    'Q024',  # Acesso à internet
    'Q025',  # Possui computador
    
    # Redação (componentes)
    'TP_STATUS_REDACAO',
    'NU_NOTA_COMP1',
    'NU_NOTA_COMP2',
    'NU_NOTA_COMP3',
    'NU_NOTA_COMP4',
    'NU_NOTA_COMP5'
]

# Mapeamento de colunas CSV para nomes amigáveis
COLUMN_MAPPING = {
    'NU_ANO': 'ano',
    'SG_UF_PROVA': 'sigla_uf',
    'NO_MUNICIPIO_PROVA': 'municipio',
    'NU_NOTA_MT': 'nota_matematica',
    'NU_NOTA_CN': 'nota_ciencias_natureza',
    'NU_NOTA_CH': 'nota_ciencias_humanas',
    'NU_NOTA_LC': 'nota_linguagens',
    'NU_NOTA_REDACAO': 'nota_redacao',
    'TP_SEXO': 'sexo',
    'TP_FAIXA_ETARIA': 'faixa_etaria',
    'TP_COR_RACA': 'cor_raca',
    'TP_ESCOLA': 'tipo_escola',
    'TP_LOCALIZACAO_ESC': 'localizacao_escola',
    'Q005': 'renda_familiar',
}

# Descrições das colunas
COLUMN_DESCRIPTIONS = {
    'TP_SEXO': {'M': 'Masculino', 'F': 'Feminino'},
    'TP_FAIXA_ETARIA': {
        1: 'Menor de 17 anos',
        2: '17 anos',
        3: '18 anos',
        4: '19 anos',
        5: '20 anos',
        6: '21 anos',
        7: '22 anos',
        8: '23 anos',
        9: '24 anos',
        10: '25 anos',
        11: 'Entre 26 e 30 anos',
        12: 'Entre 31 e 35 anos',
        13: 'Entre 36 e 40 anos',
        14: 'Entre 41 e 45 anos',
        15: 'Entre 46 e 50 anos',
        16: 'Entre 51 e 55 anos',
        17: 'Entre 56 e 60 anos',
        18: 'Entre 61 e 65 anos',
        19: 'Entre 66 e 70 anos',
        20: 'Maior de 70 anos'
    },
    'TP_COR_RACA': {
        0: 'Não declarado',
        1: 'Branca',
        2: 'Preta',
        3: 'Parda',
        4: 'Amarela',
        5: 'Indígena',
        6: 'Não dispõe da informação'
    },
    'TP_ESCOLA': {
        1: 'Não respondeu',
        2: 'Pública',
        3: 'Privada',
        4: 'Exterior'
    },
    'TP_LOCALIZACAO_ESC': {
        1: 'Urbana',
        2: 'Rural'
    },
    'TP_DEPENDENCIA_ADM_ESC': {
        1: 'Federal',
        2: 'Estadual',
        3: 'Municipal',
        4: 'Privada'
    }
}

# ============================================================================
# CONFIGURAÇÕES DE AGREGAÇÃO
# ============================================================================

# Estados brasileiros por região
ESTADOS_POR_REGIAO = {
    'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}

# Métricas para agregação
AGGREGATION_METRICS = [
    'NU_NOTA_CN',
    'NU_NOTA_CH',
    'NU_NOTA_LC',
    'NU_NOTA_MT',
    'NU_NOTA_REDACAO',
]

# ============================================================================
# CONFIGURAÇÕES DE LOGGING
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = "pipeline.log"

# ============================================================================
# CONFIGURAÇÕES DO DASHBOARD
# ============================================================================

# Título do dashboard
DASHBOARD_TITLE = "Dashboard ENEM 2022 - Análise de Desempenho"

# Porta do servidor Dash
DASHBOARD_PORT = 8050

# Modo debug
DEBUG_MODE = True

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def create_directories():
    """Cria diretórios necessários se não existirem"""
    LOCAL_RAW_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_RAW_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_AGGREGATED_DIR.mkdir(parents=True, exist_ok=True)

def get_region_for_state(state: str) -> str:
    """Retorna a região de um estado"""
    for region, states in ESTADOS_POR_REGIAO.items():
        if state in states:
            return region
    return 'Desconhecido'

def get_csv_path(file_key: str) -> Path:
    """Retorna o caminho completo de um arquivo CSV"""
    if file_key not in CSV_FILES:
        raise ValueError(f"Arquivo CSV não encontrado: {file_key}")
    return LOCAL_RAW_DIR / CSV_FILES[file_key]

def validate_config():
    """Valida configurações básicas"""
    issues = []
    
    # Verificar diretórios
    if not LOCAL_RAW_DIR.exists():
        issues.append(f"Diretório de dados não existe: {LOCAL_RAW_DIR}")
    
    # Verificar arquivo principal
    main_csv = get_csv_path('microdados')
    if not main_csv.exists():
        issues.append(f"Arquivo principal não encontrado: {main_csv}")
    
    # Verificar ano
    if DEFAULT_YEAR < 1998 or DEFAULT_YEAR > 2030:
        issues.append(f"Ano inválido: {DEFAULT_YEAR}")
    
    # Verificar limite de registros
    if MAX_RECORDS and MAX_RECORDS < 1000:
        issues.append(f"MAX_RECORDS muito baixo: {MAX_RECORDS}")
    
    return issues

def get_config_summary() -> dict:
    """Retorna resumo das configurações"""
    return {
        'ano_padrao': DEFAULT_YEAR,
        'max_registros': MAX_RECORDS,
        'cache_habilitado': USE_CACHE,
        'cache_ttl_dias': CACHE_TTL_DAYS,
        'total_colunas_essenciais': len(ESSENTIAL_COLUMNS),
        'arquivo_principal': CSV_FILES['microdados'],
        'diretorio_dados': str(LOCAL_RAW_DIR),
        'diretorio_cache': str(CACHE_DIR)
    }

# Criar diretórios ao importar
create_directories()

# Validar configuração
config_issues = validate_config()
if config_issues:
    import warnings
    for issue in config_issues:
        warnings.warn(f"Configuração: {issue}")
