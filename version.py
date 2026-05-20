"""
Informações de versão do Dashboard ENEM
"""

__version__ = "1.0.0"
__date__ = "2026-05-20"
__author__ = "Grupo 08"
__description__ = "Dashboard Interativo de Análise do ENEM 2022"
__status__ = "Production"

# Histórico de versões
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2026-05-20",
        "description": "Versão final com CSV local",
        "changes": [
            "Remoção completa do módulo de scraping",
            "Migração de BigQuery para CSV local",
            "Otimizações de performance",
            "Documentação completa",
            "Sistema de versionamento"
        ]
    },
    "0.9.0": {
        "date": "2026-05-19",
        "description": "Migração para CSV, remoção BigQuery",
        "changes": [
            "Suporte completo para CSV local",
            "Remoção de dependências de nuvem",
            "Documentação de migração"
        ]
    },
    "0.8.0": {
        "date": "2026-05-18",
        "description": "Otimizações de performance",
        "changes": [
            "Sistema de cache com Parquet",
            "Compressão de dados",
            "Lazy loading"
        ]
    },
    "0.7.0": {
        "date": "2026-05-17",
        "description": "Dashboard detalhado completo",
        "changes": [
            "Análise por região",
            "Análise por tipo de escola",
            "Filtros avançados"
        ]
    }
}

def get_version_info():
    """Retorna informações completas da versão atual"""
    return {
        "version": __version__,
        "date": __date__,
        "author": __author__,
        "description": __description__,
        "status": __status__
    }

def get_version_string():
    """Retorna string formatada da versão"""
    return f"v{__version__} ({__date__})"

if __name__ == "__main__":
    print(f"Dashboard ENEM - Versão {__version__}")
    print(f"Data: {__date__}")
    print(f"Status: {__status__}")
    print(f"\n{__description__}")
