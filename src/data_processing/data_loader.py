"""
Data Loader Module - Simplified for Local CSV Files
Load and process ENEM data from local CSV files with intelligent sampling
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import (
    CSV_FILES, ESSENTIAL_COLUMNS, MAX_RECORDS,
    USE_CACHE, CACHE_TTL_DAYS, DEFAULT_YEAR
)
from src.data_processing.data_cache import DataCache


class DataLoader:
    """
    Load ENEM data from local CSV files with intelligent sampling
    
    Features:
    - Load from local CSV files only
    - Intelligent sampling (stratified by state)
    - Memory-efficient loading (only essential columns)
    - Cache support for processed data
    - Automatic data validation and cleaning
    """
    
    def __init__(self, data_dir: str = "data/raw", use_cache: bool = USE_CACHE):
        """
        Initialize data loader
        
        Args:
            data_dir: Directory containing raw CSV files
            use_cache: Enable cache system
        """
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.use_cache = use_cache
        
        # Initialize cache
        self.cache = DataCache(ttl_days=CACHE_TTL_DAYS) if use_cache else None
        
        if not self.data_dir.exists():
            self.logger.warning(f"Data directory does not exist: {data_dir}")
            os.makedirs(self.data_dir, exist_ok=True)
    
    def load_enem_data(
        self,
        year: int = DEFAULT_YEAR,
        max_records: int = MAX_RECORDS,
        states: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Load ENEM data from local CSV with intelligent sampling
        
        Args:
            year: Year to load (default: 2022)
            max_records: Maximum number of records to load
            states: List of state codes to filter (None = all states)
            force_refresh: Ignore cache and reload from CSV
            
        Returns:
            DataFrame with ENEM data
        """
        # Generate cache key
        cache_params = {
            'source': 'csv',
            'year': year,
            'max_records': max_records,
            'states': tuple(states) if states else None
        }
        
        # Try to load from cache first
        if self.use_cache and not force_refresh:
            self.logger.info("Checking cache...")
            df_cached = self.cache.load(cache_type="raw", **cache_params)
            if df_cached is not None:
                self.logger.info(f"[OK] Data loaded from cache: {len(df_cached):,} rows")
                return df_cached
        
        # Load from CSV
        self.logger.info(f"Loading ENEM {year} data from CSV...")
        csv_file = self.data_dir / CSV_FILES['microdados']
        
        if not csv_file.exists():
            raise FileNotFoundError(
                f"ENEM data file not found: {csv_file}\n"
                f"Please ensure {CSV_FILES['microdados']} is in {self.data_dir}"
            )
        
        try:
            # Read CSV with only essential columns for memory efficiency
            self.logger.info(f"Reading CSV (columns: {len(ESSENTIAL_COLUMNS)})...")
            
            df = pd.read_csv(
                csv_file,
                encoding='latin1',
                sep=';',
                usecols=ESSENTIAL_COLUMNS,
                low_memory=False
            )
            
            self.logger.info(f"[OK] Loaded {len(df):,} rows from CSV")
            
            # Filter by year if column exists
            if 'NU_ANO' in df.columns:
                df = df[df['NU_ANO'] == year]
                self.logger.info(f"Filtered to year {year}: {len(df):,} rows")
            
            # Filter by states if specified
            if states and 'SG_UF_PROVA' in df.columns:
                df = df[df['SG_UF_PROVA'].isin(states)]
                self.logger.info(f"Filtered to states {states}: {len(df):,} rows")
            
            # Filter out participants who didn't take any test
            df = self._filter_valid_participants(df)
            self.logger.info(f"After filtering valid participants: {len(df):,} rows")
            
            # Apply intelligent sampling if needed
            if len(df) > max_records:
                df = self._stratified_sample(df, max_records)
                self.logger.info(f"Sampled to {len(df):,} rows (stratified by state)")
            
            # Basic data cleaning
            df = self._clean_data(df)
            
            # Save to cache
            if self.use_cache:
                self.logger.info("Saving to cache...")
                self.cache.save(df, cache_type="raw", **cache_params)
            
            self.logger.info(f"[OK] Final dataset: {len(df):,} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load ENEM data: {e}")
            raise
    
    def _filter_valid_participants(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter out participants who didn't take any test
        
        Args:
            df: Input DataFrame
            
        Returns:
            Filtered DataFrame
        """
        presence_cols = ['TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT']
        
        # Check which presence columns exist
        existing_presence = [col for col in presence_cols if col in df.columns]
        
        if not existing_presence:
            self.logger.warning("No presence columns found, skipping filter")
            return df
        
        # Keep participants who took at least one test
        mask = df[existing_presence].sum(axis=1) > 0
        return df[mask].copy()
    
    def _stratified_sample(self, df: pd.DataFrame, n_samples: int) -> pd.DataFrame:
        """
        Perform stratified sampling by state to maintain geographic distribution
        
        Args:
            df: Input DataFrame
            n_samples: Number of samples to take
            
        Returns:
            Sampled DataFrame
        """
        if 'SG_UF_PROVA' not in df.columns:
            # If no state column, do simple random sampling
            return df.sample(n=n_samples, random_state=42)
        
        # Calculate samples per state proportionally
        state_counts = df['SG_UF_PROVA'].value_counts()
        state_proportions = state_counts / len(df)
        
        samples_per_state = (state_proportions * n_samples).round().astype(int)
        
        # Adjust to ensure we get exactly n_samples
        diff = n_samples - samples_per_state.sum()
        if diff > 0:
            # Add extra samples to largest states
            largest_states = state_counts.nlargest(diff).index
            for state in largest_states:
                samples_per_state[state] += 1
        elif diff < 0:
            # Remove samples from largest states
            largest_states = state_counts.nlargest(abs(diff)).index
            for state in largest_states:
                samples_per_state[state] = max(1, samples_per_state[state] - 1)
        
        # Sample from each state
        sampled_dfs = []
        for state, n in samples_per_state.items():
            state_df = df[df['SG_UF_PROVA'] == state]
            if len(state_df) > 0:
                n_to_sample = min(n, len(state_df))
                sampled_dfs.append(state_df.sample(n=n_to_sample, random_state=42))
        
        return pd.concat(sampled_dfs, ignore_index=True)
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Basic data cleaning and type conversion
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        # Convert numeric columns
        numeric_cols = [col for col in df.columns if col.startswith('NU_NOTA_')]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert categorical columns to string
        categorical_cols = [col for col in df.columns if col.startswith(('TP_', 'SG_', 'Q0'))]
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of loaded data
        
        Args:
            df: DataFrame to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'states': df['SG_UF_PROVA'].nunique() if 'SG_UF_PROVA' in df.columns else 0,
            'year': df['NU_ANO'].iloc[0] if 'NU_ANO' in df.columns and len(df) > 0 else None
        }
        
        # Add score statistics
        score_cols = [col for col in df.columns if col.startswith('NU_NOTA_')]
        for col in score_cols:
            if col in df.columns:
                summary[f'{col}_mean'] = df[col].mean()
                summary[f'{col}_median'] = df[col].median()
        
        return summary
    
    def list_available_files(self) -> List[str]:
        """
        List all CSV files in data directory
        
        Returns:
            List of CSV filenames
        """
        csv_files = list(self.data_dir.glob("*.csv"))
        return [f.name for f in csv_files]


def main():
    """Test data loader"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    loader = DataLoader()
    
    print("\n" + "="*80)
    print("DATA LOADER TEST")
    print("="*80)
    
    print("\nAvailable CSV files:")
    for file in loader.list_available_files():
        print(f"  - {file}")
    
    print("\nLoading ENEM data...")
    try:
        df = loader.load_enem_data(year=2022, max_records=10000)
        
        print("\n" + "-"*80)
        print("DATA SUMMARY")
        print("-"*80)
        summary = loader.get_data_summary(df)
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        print("\n" + "-"*80)
        print("SAMPLE DATA (first 5 rows)")
        print("-"*80)
        print(df.head())
        
        print("\n" + "-"*80)
        print("COLUMN TYPES")
        print("-"*80)
        print(df.dtypes)
        
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
