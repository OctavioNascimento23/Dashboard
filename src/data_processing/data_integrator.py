"""
Data Integrator Module
Integrate multiple datasets using merge and concatenation
"""

import logging
import pandas as pd
from typing import List, Optional


class DataIntegrator:
    """
    Integrate multiple datasets
    
    Features:
    - Concatenate multiple years of data
    - Merge ENEM with Censo Escolar
    - Merge with socioeconomic data
    - Handle different join types
    """
    
    def __init__(self):
        """Initialize data integrator"""
        self.logger = logging.getLogger(__name__)
    
    def concatenate_years(self, dataframes: List[pd.DataFrame], 
                         year_column: str = 'NU_ANO') -> pd.DataFrame:
        """
        Concatenate multiple years of data vertically
        
        Args:
            dataframes: List of DataFrames to concatenate
            year_column: Name of year column for validation
            
        Returns:
            Concatenated DataFrame
        """
        self.logger.info(f"Concatenating {len(dataframes)} DataFrames")
        
        if not dataframes:
            raise ValueError("No dataframes provided for concatenation")
        
        # Concatenate vertically
        df_concat = pd.concat(dataframes, ignore_index=True)
        
        self.logger.info(f"Concatenation complete: {len(df_concat):,} total rows")
        
        # Log year distribution if year column exists
        if year_column in df_concat.columns:
            year_counts = df_concat[year_column].value_counts().sort_index()
            self.logger.info("Year distribution:")
            for year, count in year_counts.items():
                self.logger.info(f"  {year}: {count:,} rows")
        
        return df_concat
    
    def merge_enem_censo(self, 
                        df_enem: pd.DataFrame, 
                        df_censo: pd.DataFrame,
                        how: str = 'left') -> pd.DataFrame:
        """
        Merge ENEM data with Censo Escolar data
        
        Args:
            df_enem: ENEM DataFrame
            df_censo: Censo Escolar DataFrame
            how: Type of merge ('left', 'right', 'inner', 'outer')
            
        Returns:
            Merged DataFrame
        """
        self.logger.info(f"Merging ENEM ({len(df_enem):,} rows) with Censo ({len(df_censo):,} rows)")
        
        # Identify merge keys
        enem_school_col = 'CO_ESCOLA' if 'CO_ESCOLA' in df_enem.columns else None
        censo_school_col = 'CO_ENTIDADE' if 'CO_ENTIDADE' in df_censo.columns else None
        
        if not enem_school_col or not censo_school_col:
            self.logger.warning("School code columns not found, cannot merge")
            return df_enem
        
        # Perform merge
        df_merged = pd.merge(
            df_enem,
            df_censo,
            left_on=enem_school_col,
            right_on=censo_school_col,
            how=how,
            suffixes=('_enem', '_censo')
        )
        
        self.logger.info(f"Merge complete: {len(df_merged):,} rows")
        
        # Calculate merge statistics
        merge_rate = (len(df_merged) / len(df_enem)) * 100
        self.logger.info(f"Merge rate: {merge_rate:.1f}%")
        
        return df_merged
    
    def merge_with_state_data(self,
                             df: pd.DataFrame,
                             df_state: pd.DataFrame,
                             how: str = 'left') -> pd.DataFrame:
        """
        Merge with state-level data (e.g., socioeconomic indicators)
        
        Args:
            df: Main DataFrame
            df_state: State-level DataFrame
            how: Type of merge
            
        Returns:
            Merged DataFrame
        """
        self.logger.info(f"Merging with state data ({len(df_state):,} states)")
        
        # Identify state columns
        main_state_col = None
        for col in ['SG_UF_RESIDENCIA', 'SG_UF', 'UF']:
            if col in df.columns:
                main_state_col = col
                break
        
        state_col = None
        for col in ['SG_UF', 'UF', 'ESTADO']:
            if col in df_state.columns:
                state_col = col
                break
        
        if not main_state_col or not state_col:
            self.logger.warning("State columns not found, cannot merge")
            return df
        
        # Perform merge
        df_merged = pd.merge(
            df,
            df_state,
            left_on=main_state_col,
            right_on=state_col,
            how=how,
            suffixes=('', '_state')
        )
        
        self.logger.info(f"Merge complete: {len(df_merged):,} rows")
        
        return df_merged
    
    def create_integrated_dataset(self,
                                 df_enem_list: List[pd.DataFrame],
                                 df_censo: Optional[pd.DataFrame] = None,
                                 df_state: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Create fully integrated dataset
        
        Args:
            df_enem_list: List of ENEM DataFrames (different years)
            df_censo: Censo Escolar DataFrame (optional)
            df_state: State-level data DataFrame (optional)
            
        Returns:
            Fully integrated DataFrame
        """
        self.logger.info("="*60)
        self.logger.info("Creating integrated dataset")
        self.logger.info("="*60)
        
        # Step 1: Concatenate ENEM years
        self.logger.info("Step 1: Concatenating ENEM years")
        df_integrated = self.concatenate_years(df_enem_list)
        
        # Step 2: Merge with Censo if provided
        if df_censo is not None:
            self.logger.info("Step 2: Merging with Censo Escolar")
            df_integrated = self.merge_enem_censo(df_integrated, df_censo)
        else:
            self.logger.info("Step 2: Skipped (no Censo data provided)")
        
        # Step 3: Merge with state data if provided
        if df_state is not None:
            self.logger.info("Step 3: Merging with state data")
            df_integrated = self.merge_with_state_data(df_integrated, df_state)
        else:
            self.logger.info("Step 3: Skipped (no state data provided)")
        
        self.logger.info("="*60)
        self.logger.info(f"Integration complete: {len(df_integrated):,} rows, {len(df_integrated.columns)} columns")
        self.logger.info("="*60)
        
        return df_integrated
    
    def validate_integration(self, df: pd.DataFrame) -> dict:
        """
        Validate integrated dataset
        
        Args:
            df: Integrated DataFrame
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Validating integrated dataset")
        
        validation = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_percentage': (df.isna().sum().sum() / (len(df) * len(df.columns)) * 100),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        # Check for required columns
        required_cols = ['NU_ANO', 'NOTA_MEDIA']
        validation['has_required_columns'] = all(col in df.columns for col in required_cols)
        
        # Check minimum records
        validation['meets_minimum_records'] = len(df) >= 10000
        
        self.logger.info("Validation results:")
        for key, value in validation.items():
            if isinstance(value, float):
                self.logger.info(f"  {key}: {value:.2f}")
            else:
                self.logger.info(f"  {key}: {value}")
        
        return validation
    
    def save_integrated_data(self, df: pd.DataFrame, filepath: str):
        """
        Save integrated dataset
        
        Args:
            df: Integrated DataFrame
            filepath: Path to save file
        """
        self.logger.info(f"Saving integrated data to {filepath}")
        
        # Determine format from extension
        if filepath.endswith('.csv'):
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif filepath.endswith('.parquet'):
            df.to_parquet(filepath, index=False)
        elif filepath.endswith('.xlsx'):
            df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
        
        self.logger.info(f"Data saved successfully")


def main():
    """Test data integrator"""
    logging.basicConfig(level=logging.INFO)
    
    integrator = DataIntegrator()
    
    print("Data Integrator initialized")
    print("Use integrator.create_integrated_dataset() to integrate data")


if __name__ == "__main__":
    main()
