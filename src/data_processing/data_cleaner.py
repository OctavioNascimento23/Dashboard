"""
Data Cleaner Module
Clean and treat raw data
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class DataCleaner:
    """
    Clean and treat data
    
    Features:
    - Handle missing values
    - Remove duplicates
    - Validate data ranges
    - Standardize formats
    - Remove inconsistencies
    """
    
    def __init__(self):
        """Initialize data cleaner"""
        self.logger = logging.getLogger(__name__)
        self.cleaning_report = {}
    
    def clean_enem_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean ENEM data
        
        Args:
            df: Raw ENEM DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        self.logger.info("Starting ENEM data cleaning")
        initial_rows = len(df)
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # 1. Remove duplicates
        df_clean = self._remove_duplicates(df_clean, subset=['NU_INSCRICAO'])
        
        # 2. Standardize column names
        df_clean = self._standardize_columns(df_clean)
        
        # 3. Handle missing values in scores
        score_columns = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
        df_clean = self._handle_missing_scores(df_clean, score_columns)
        
        # 4. Validate score ranges
        df_clean = self._validate_score_ranges(df_clean, score_columns)
        
        # 5. Clean demographic data
        df_clean = self._clean_demographics(df_clean)
        
        # 6. Clean geographic data
        df_clean = self._clean_geographic(df_clean)
        
        # 7. Remove rows with critical missing data
        df_clean = self._remove_critical_missing(df_clean)
        
        final_rows = len(df_clean)
        self.cleaning_report['enem'] = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'rows_removed': initial_rows - final_rows,
            'removal_percentage': ((initial_rows - final_rows) / initial_rows * 100)
        }
        
        self.logger.info(f"ENEM cleaning complete: {initial_rows:,} -> {final_rows:,} rows")
        return df_clean
    
    def clean_censo_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean Censo Escolar data
        
        Args:
            df: Raw Censo DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        self.logger.info("Starting Censo data cleaning")
        initial_rows = len(df)
        
        df_clean = df.copy()
        
        # 1. Remove duplicates
        df_clean = self._remove_duplicates(df_clean, subset=['CO_ENTIDADE'])
        
        # 2. Standardize column names
        df_clean = self._standardize_columns(df_clean)
        
        # 3. Clean school infrastructure data
        df_clean = self._clean_infrastructure(df_clean)
        
        # 4. Clean geographic data
        df_clean = self._clean_geographic(df_clean)
        
        # 5. Handle missing values
        df_clean = self._handle_missing_censo(df_clean)
        
        final_rows = len(df_clean)
        self.cleaning_report['censo'] = {
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'rows_removed': initial_rows - final_rows,
            'removal_percentage': ((initial_rows - final_rows) / initial_rows * 100)
        }
        
        self.logger.info(f"Censo cleaning complete: {initial_rows:,} -> {final_rows:,} rows")
        return df_clean
    
    def _remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """Remove duplicate rows"""
        initial = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep='first')
        removed = initial - len(df_clean)
        
        if removed > 0:
            self.logger.info(f"Removed {removed:,} duplicate rows")
        
        return df_clean
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        # Convert to uppercase and strip whitespace
        df.columns = df.columns.str.upper().str.strip()
        return df
    
    def _handle_missing_scores(self, df: pd.DataFrame, score_columns: List[str]) -> pd.DataFrame:
        """Handle missing values in score columns"""
        for col in score_columns:
            if col in df.columns:
                # Count missing
                missing = df[col].isna().sum()
                if missing > 0:
                    self.logger.info(f"{col}: {missing:,} missing values ({missing/len(df)*100:.1f}%)")
                
                # Replace invalid values (negative, > 1000) with NaN
                df.loc[df[col] < 0, col] = np.nan
                df.loc[df[col] > 1000, col] = np.nan
        
        return df
    
    def _validate_score_ranges(self, df: pd.DataFrame, score_columns: List[str]) -> pd.DataFrame:
        """Validate that scores are in valid range [0, 1000]"""
        for col in score_columns:
            if col in df.columns:
                # Remove rows with invalid scores
                invalid = ((df[col] < 0) | (df[col] > 1000)).sum()
                if invalid > 0:
                    self.logger.warning(f"{col}: Removing {invalid} rows with invalid scores")
                    df = df[(df[col].isna()) | ((df[col] >= 0) & (df[col] <= 1000))]
        
        return df
    
    def _clean_demographics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean demographic columns"""
        # Gender
        if 'TP_SEXO' in df.columns:
            # Standardize gender values
            df['TP_SEXO'] = df['TP_SEXO'].replace({'M': 'M', 'F': 'F', 'm': 'M', 'f': 'F'})
            df.loc[~df['TP_SEXO'].isin(['M', 'F']), 'TP_SEXO'] = np.nan
        
        # Age
        if 'NU_IDADE' in df.columns:
            # Valid age range for ENEM: 15-80
            df.loc[(df['NU_IDADE'] < 15) | (df['NU_IDADE'] > 80), 'NU_IDADE'] = np.nan
        
        # Race/Ethnicity
        if 'TP_COR_RACA' in df.columns:
            # Valid values: 0-6
            df.loc[~df['TP_COR_RACA'].isin([0, 1, 2, 3, 4, 5, 6]), 'TP_COR_RACA'] = np.nan
        
        return df
    
    def _clean_geographic(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean geographic columns"""
        # State codes
        state_col = 'SG_UF_RESIDENCIA' if 'SG_UF_RESIDENCIA' in df.columns else 'SG_UF'
        
        if state_col in df.columns:
            # Valid Brazilian state codes
            valid_states = [
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ]
            
            # Standardize to uppercase
            df[state_col] = df[state_col].str.upper().str.strip()
            
            # Remove invalid states
            invalid = ~df[state_col].isin(valid_states)
            if invalid.sum() > 0:
                self.logger.warning(f"Removing {invalid.sum()} rows with invalid state codes")
                df.loc[invalid, state_col] = np.nan
        
        return df
    
    def _clean_infrastructure(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean school infrastructure columns"""
        # Infrastructure columns are typically binary (0/1)
        infra_columns = [col for col in df.columns if col.startswith('IN_')]
        
        for col in infra_columns:
            # Ensure values are 0 or 1
            df.loc[~df[col].isin([0, 1]), col] = np.nan
        
        return df
    
    def _handle_missing_censo(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in Censo data"""
        # For infrastructure columns, missing often means "no"
        infra_columns = [col for col in df.columns if col.startswith('IN_')]
        
        for col in infra_columns:
            # Fill missing with 0 (no infrastructure)
            df[col] = df[col].fillna(0)
        
        return df
    
    def _remove_critical_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows with critical missing data"""
        # For ENEM, we need at least state and year
        critical_cols = []
        
        if 'SG_UF_RESIDENCIA' in df.columns:
            critical_cols.append('SG_UF_RESIDENCIA')
        elif 'SG_UF' in df.columns:
            critical_cols.append('SG_UF')
        
        if 'NU_ANO' in df.columns:
            critical_cols.append('NU_ANO')
        
        if critical_cols:
            initial = len(df)
            df = df.dropna(subset=critical_cols)
            removed = initial - len(df)
            
            if removed > 0:
                self.logger.info(f"Removed {removed:,} rows with critical missing data")
        
        return df
    
    def get_cleaning_report(self) -> Dict:
        """Get cleaning report"""
        return self.cleaning_report
    
    def print_cleaning_report(self):
        """Print cleaning report"""
        print("\n" + "="*60)
        print("DATA CLEANING REPORT")
        print("="*60)
        
        for dataset, report in self.cleaning_report.items():
            print(f"\n{dataset.upper()}:")
            print(f"  Initial rows: {report['initial_rows']:,}")
            print(f"  Final rows: {report['final_rows']:,}")
            print(f"  Rows removed: {report['rows_removed']:,}")
            print(f"  Removal %: {report['removal_percentage']:.2f}%")
        
        print("\n" + "="*60)


def main():
    """Test data cleaner"""
    logging.basicConfig(level=logging.INFO)
    
    cleaner = DataCleaner()
    
    # Example usage
    print("Data Cleaner initialized")
    print("Use cleaner.clean_enem_data(df) or cleaner.clean_censo_data(df)")


if __name__ == "__main__":
    main()
