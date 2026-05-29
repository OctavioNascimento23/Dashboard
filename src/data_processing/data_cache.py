"""
Data Cache Module
Gerencia cache local de dados para otimização de performance
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
import json
import hashlib

logger = logging.getLogger(__name__)


class DataCache:
    """
    Gerenciador de cache local para dados do ENEM
    
    Funcionalidades:
    - Salvar/carregar dados em formato Parquet (eficiente)
    - Verificar validade do cache (TTL)
    - Limpar cache expirado
    - Metadados de cache
    """
    
    def __init__(self, cache_dir: str = "data/cache", ttl_days: int = 30):
        """
        Inicializa gerenciador de cache
        
        Args:
            cache_dir: Diretório base para cache
            ttl_days: Tempo de vida do cache em dias
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_days = ttl_days
        self.ttl_delta = timedelta(days=ttl_days)
        
        # Criar subdiretórios
        self.raw_dir = self.cache_dir / "raw"
        self.processed_dir = self.cache_dir / "processed"
        self.aggregated_dir = self.cache_dir / "aggregated"
        
        self._create_directories()
    
    def _create_directories(self):
        """Cria diretórios de cache se não existirem"""
        for directory in [self.raw_dir, self.processed_dir, self.aggregated_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Cache directory ready: {directory}")
    
    def _get_cache_key(self, **params) -> str:
        """
        Gera chave única para cache baseada em parâmetros
        
        Args:
            **params: Parâmetros da query (year, state, etc.)
            
        Returns:
            Hash MD5 dos parâmetros
        """
        # Ordenar parâmetros para consistência
        sorted_params = sorted(params.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        return hashlib.md5(param_string.encode()).hexdigest()
    
    def _get_metadata_path(self, cache_path: Path) -> Path:
        """Retorna caminho do arquivo de metadados"""
        return cache_path.parent / f"{cache_path.stem}_metadata.json"
    
    def _save_metadata(self, cache_path: Path, metadata: Dict[str, Any]):
        """
        Salva metadados do cache
        
        Args:
            cache_path: Caminho do arquivo de cache
            metadata: Dicionário com metadados
        """
        metadata_path = self._get_metadata_path(cache_path)
        
        # Adicionar timestamp
        metadata['cached_at'] = datetime.now().isoformat()
        metadata['ttl_days'] = self.ttl_days
        metadata['expires_at'] = (datetime.now() + self.ttl_delta).isoformat()
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Metadata saved: {metadata_path}")
    
    def _load_metadata(self, cache_path: Path) -> Optional[Dict[str, Any]]:
        """
        Carrega metadados do cache
        
        Args:
            cache_path: Caminho do arquivo de cache
            
        Returns:
            Dicionário com metadados ou None se não existir
        """
        metadata_path = self._get_metadata_path(cache_path)
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load metadata: {e}")
            return None
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Verifica se cache é válido (não expirado)
        
        Args:
            cache_path: Caminho do arquivo de cache
            
        Returns:
            True se cache é válido, False caso contrário
        """
        if not cache_path.exists():
            return False
        
        metadata = self._load_metadata(cache_path)
        if not metadata:
            logger.debug(f"No metadata found for {cache_path.name}")
            return False
        
        try:
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            is_valid = datetime.now() < expires_at
            
            if is_valid:
                logger.debug(f"Cache valid until {expires_at}")
            else:
                logger.debug(f"Cache expired at {expires_at}")
            
            return is_valid
            
        except (KeyError, ValueError) as e:
            logger.warning(f"Invalid metadata: {e}")
            return False
    
    def save(
        self,
        df: pd.DataFrame,
        cache_type: str = "raw",
        filename: Optional[str] = None,
        **params
    ) -> Path:
        """
        Salva DataFrame no cache
        
        Args:
            df: DataFrame para salvar
            cache_type: Tipo de cache (raw, processed, aggregated)
            filename: Nome do arquivo (opcional, gera automaticamente se None)
            **params: Parâmetros para gerar chave de cache
            
        Returns:
            Caminho do arquivo salvo
        """
        # Determinar diretório
        if cache_type == "raw":
            cache_dir = self.raw_dir
        elif cache_type == "processed":
            cache_dir = self.processed_dir
        elif cache_type == "aggregated":
            cache_dir = self.aggregated_dir
        else:
            raise ValueError(f"Invalid cache_type: {cache_type}")
        
        # Gerar nome do arquivo
        if filename is None:
            cache_key = self._get_cache_key(**params)
            filename = f"cache_{cache_key}.parquet"
        
        cache_path = cache_dir / filename
        
        try:
            # Salvar DataFrame em Parquet (mais eficiente que CSV)
            df.to_parquet(cache_path, index=False, compression='snappy')
            
            # Salvar metadados
            metadata = {
                'cache_type': cache_type,
                'filename': filename,
                'rows': len(df),
                'columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
                'params': params
            }
            self._save_metadata(cache_path, metadata)
            
            logger.info(f"[OK] Cache saved: {cache_path.name} ({len(df):,} rows)")
            return cache_path
            
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            raise
    
    def load(
        self,
        cache_type: str = "raw",
        filename: Optional[str] = None,
        force_refresh: bool = False,
        **params
    ) -> Optional[pd.DataFrame]:
        """
        Carrega DataFrame do cache
        
        Args:
            cache_type: Tipo de cache (raw, processed, aggregated)
            filename: Nome do arquivo (opcional, gera automaticamente se None)
            force_refresh: Se True, ignora cache e retorna None
            **params: Parâmetros para gerar chave de cache
            
        Returns:
            DataFrame ou None se cache não existe/inválido
        """
        if force_refresh:
            logger.info("Force refresh enabled, skipping cache")
            return None
        
        # Determinar diretório
        if cache_type == "raw":
            cache_dir = self.raw_dir
        elif cache_type == "processed":
            cache_dir = self.processed_dir
        elif cache_type == "aggregated":
            cache_dir = self.aggregated_dir
        else:
            raise ValueError(f"Invalid cache_type: {cache_type}")
        
        # Gerar nome do arquivo
        if filename is None:
            cache_key = self._get_cache_key(**params)
            filename = f"cache_{cache_key}.parquet"
        
        cache_path = cache_dir / filename
        
        # Verificar se cache existe e é válido
        if not self._is_cache_valid(cache_path):
            logger.debug(f"Cache not valid: {filename}")
            return None
        
        try:
            # Carregar DataFrame
            df = pd.read_parquet(cache_path)
            
            metadata = self._load_metadata(cache_path)
            if metadata:
                logger.info(f"[OK] Cache loaded: {filename} ({len(df):,} rows, cached {metadata.get('cached_at', 'unknown')})")
            else:
                logger.info(f"[OK] Cache loaded: {filename} ({len(df):,} rows)")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return None
    
    def clear_cache(self, cache_type: Optional[str] = None, older_than_days: Optional[int] = None):
        """
        Limpa cache
        
        Args:
            cache_type: Tipo específico para limpar (None = todos)
            older_than_days: Limpar apenas caches mais antigos que X dias (None = todos)
        """
        if cache_type:
            dirs_to_clear = [getattr(self, f"{cache_type}_dir")]
        else:
            dirs_to_clear = [self.raw_dir, self.processed_dir, self.aggregated_dir]
        
        total_cleared = 0
        total_size_mb = 0
        
        for cache_dir in dirs_to_clear:
            if not cache_dir.exists():
                continue
            
            for file_path in cache_dir.glob("*.parquet"):
                should_delete = False
                
                if older_than_days is None:
                    should_delete = True
                else:
                    metadata = self._load_metadata(file_path)
                    if metadata:
                        try:
                            cached_at = datetime.fromisoformat(metadata['cached_at'])
                            age_days = (datetime.now() - cached_at).days
                            should_delete = age_days > older_than_days
                        except (KeyError, ValueError):
                            should_delete = True
                    else:
                        should_delete = True
                
                if should_delete:
                    # Obter tamanho antes de deletar
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    total_size_mb += size_mb
                    
                    # Deletar arquivo e metadados
                    file_path.unlink()
                    metadata_path = self._get_metadata_path(file_path)
                    if metadata_path.exists():
                        metadata_path.unlink()
                    
                    total_cleared += 1
                    logger.debug(f"Deleted: {file_path.name}")
        
        logger.info(f"[OK] Cache cleared: {total_cleared} files, {total_size_mb:.2f} MB freed")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre o cache
        
        Returns:
            Dicionário com estatísticas do cache
        """
        info = {
            'cache_dir': str(self.cache_dir),
            'ttl_days': self.ttl_days,
            'types': {}
        }
        
        for cache_type, cache_dir in [
            ('raw', self.raw_dir),
            ('processed', self.processed_dir),
            ('aggregated', self.aggregated_dir)
        ]:
            if not cache_dir.exists():
                continue
            
            files = list(cache_dir.glob("*.parquet"))
            total_size = sum(f.stat().st_size for f in files)
            
            valid_count = sum(1 for f in files if self._is_cache_valid(f))
            expired_count = len(files) - valid_count
            
            info['types'][cache_type] = {
                'total_files': len(files),
                'valid_files': valid_count,
                'expired_files': expired_count,
                'total_size_mb': total_size / (1024 * 1024)
            }
        
        return info
    
    def print_cache_info(self):
        """Imprime informações do cache de forma formatada"""
        info = self.get_cache_info()
        
        print("\n" + "="*60)
        print("CACHE INFORMATION")
        print("="*60)
        print(f"Cache Directory: {info['cache_dir']}")
        print(f"TTL: {info['ttl_days']} days")
        print()
        
        for cache_type, stats in info['types'].items():
            print(f"{cache_type.upper()}:")
            print(f"  Total files: {stats['total_files']}")
            print(f"  Valid: {stats['valid_files']}")
            print(f"  Expired: {stats['expired_files']}")
            print(f"  Size: {stats['total_size_mb']:.2f} MB")
            print()
        
        print("="*60)


def main():
    """Test cache functionality"""
    import numpy as np
    
    logging.basicConfig(level=logging.INFO)
    
    # Create cache manager
    cache = DataCache()
    
    # Create sample data
    df = pd.DataFrame({
        'ano': [2022] * 1000,
        'estado': np.random.choice(['SP', 'RJ', 'MG'], 1000),
        'nota': np.random.randint(300, 900, 1000)
    })
    
    print("\n1. Saving to cache...")
    cache.save(df, cache_type="raw", year=2022, state="SP")
    
    print("\n2. Loading from cache...")
    df_loaded = cache.load(cache_type="raw", year=2022, state="SP")
    print(f"Loaded: {len(df_loaded) if df_loaded is not None else 0} rows")
    
    print("\n3. Cache info:")
    cache.print_cache_info()
    
    print("\n4. Clearing cache...")
    cache.clear_cache()
    
    print("\n5. Cache info after clear:")
    cache.print_cache_info()


if __name__ == "__main__":
    main()