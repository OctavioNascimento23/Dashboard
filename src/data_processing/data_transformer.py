"""
Data Transformer Module
Transform and create new features from cleaned data
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.preprocessing import StandardScaler


class DataTransformer:
    """
    Transform data and create new features
    
    Features:
    - Create derived variables
    - Aggregate data
    - Standardize values
    - Create categorical variables
    - Calculate composite indices
    """
    
    def __init__(self):
        """Initialize data transformer"""
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
    
    def transform_enem_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform ENEM data
        
        Args:
            df: Cleaned ENEM DataFrame
            
        Returns:
            Transformed DataFrame with new features
        """
        self.logger.info("Starting ENEM data transformation")
        df_transformed = df.copy()
        
        # 1. Calculate average scores
        df_transformed = self._calculate_average_scores(df_transformed)
        
        # 2. Create performance categories
        df_transformed = self._create_performance_categories(df_transformed)
        
        # 3. Create socioeconomic index
        df_transformed = self._create_socioeconomic_index(df_transformed)
        
        # 4. Create demographic features
        df_transformed = self._create_demographic_features(df_transformed)
        
        # 5. Create regional groupings
        df_transformed = self._create_regional_groupings(df_transformed)
        
        # 6. Create age groups
        df_transformed = self._create_age_groups(df_transformed)
        
        self.logger.info(f"Transformation complete: {len(df_transformed.columns)} total columns")
        return df_transformed
    
    def transform_censo_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform Censo Escolar data
        
        Args:
            df: Cleaned Censo DataFrame
            
        Returns:
            Transformed DataFrame with new features
        """
        self.logger.info("Starting Censo data transformation")
        df_transformed = df.copy()
        
        # 1. Create infrastructure index
        df_transformed = self._create_infrastructure_index(df_transformed)
        
        # 2. Create school type categories
        df_transformed = self._create_school_categories(df_transformed)
        
        # 3. Create regional groupings
        df_transformed = self._create_regional_groupings(df_transformed)
        
        self.logger.info(f"Transformation complete: {len(df_transformed.columns)} total columns")
        return df_transformed
    
    def _calculate_average_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate average ENEM score across all subjects"""
        score_columns = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_REDACAO']
        
        # Check which columns exist
        existing_cols = [col for col in score_columns if col in df.columns]
        
        if existing_cols:
            # Calculate mean across available scores
            df['NOTA_MEDIA'] = df[existing_cols].mean(axis=1)
            self.logger.info("Created NOTA_MEDIA (average score)")
            
            # Calculate total score
            df['NOTA_TOTAL'] = df[existing_cols].sum(axis=1)
            self.logger.info("Created NOTA_TOTAL (total score)")
        
        return df
    
    def _create_performance_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create performance categories based on average score"""
        if 'NOTA_MEDIA' in df.columns:
            df['CATEGORIA_DESEMPENHO'] = pd.cut(
                df['NOTA_MEDIA'],
                bins=[0, 450, 550, 650, 1000],
                labels=['Baixo', 'Médio', 'Alto', 'Excelente'],
                include_lowest=True
            )
            self.logger.info("Created CATEGORIA_DESEMPENHO")
        
        return df
    
    def _create_socioeconomic_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create composite socioeconomic index"""
        # Map socioeconomic questionnaire responses to numeric values
        
        # Q006: Family income (A-Q scale)
        income_mapping = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7,
            'I': 8, 'J': 9, 'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16
        }
        
        # Q001/Q002: Parental education (A-H scale)
        education_mapping = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7
        }
        
        components = []
        
        if 'Q006' in df.columns:
            df['RENDA_NUMERICA'] = df['Q006'].map(income_mapping)
            components.append('RENDA_NUMERICA')
        
        if 'Q001' in df.columns:
            df['EDUCACAO_PAI'] = df['Q001'].map(education_mapping)
            components.append('EDUCACAO_PAI')
        
        if 'Q002' in df.columns:
            df['EDUCACAO_MAE'] = df['Q002'].map(education_mapping)
            components.append('EDUCACAO_MAE')
        
        # Create composite index
        if components:
            df['INDICE_SOCIOECONOMICO'] = df[components].mean(axis=1)
            
            # Normalize to 0-10 scale
            if df['INDICE_SOCIOECONOMICO'].notna().any():
                min_val = df['INDICE_SOCIOECONOMICO'].min()
                max_val = df['INDICE_SOCIOECONOMICO'].max()
                if max_val > min_val:
                    df['INDICE_SOCIOECONOMICO'] = ((df['INDICE_SOCIOECONOMICO'] - min_val) / 
                                                    (max_val - min_val) * 10)
            
            self.logger.info("Created INDICE_SOCIOECONOMICO")
            
            # Create socioeconomic quintiles
            df['QUINTIL_SOCIOECONOMICO'] = pd.qcut(
                df['INDICE_SOCIOECONOMICO'],
                q=5,
                labels=['Q1 (Mais Baixo)', 'Q2', 'Q3', 'Q4', 'Q5 (Mais Alto)'],
                duplicates='drop'
            )
            self.logger.info("Created QUINTIL_SOCIOECONOMICO")
        
        return df
    
    def _create_demographic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create demographic feature labels"""
        # Gender labels
        if 'TP_SEXO' in df.columns:
            df['SEXO_LABEL'] = df['TP_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})
        
        # Race/Ethnicity labels
        if 'TP_COR_RACA' in df.columns:
            race_mapping = {
                0: 'Não declarado',
                1: 'Branca',
                2: 'Preta',
                3: 'Parda',
                4: 'Amarela',
                5: 'Indígena',
                6: 'Não dispõe da informação'
            }
            df['COR_RACA_LABEL'] = df['TP_COR_RACA'].map(race_mapping)
        
        return df
    
    def _create_regional_groupings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create regional groupings from state codes"""
        # Try different state column names
        if 'SG_UF_RESIDENCIA' in df.columns:
            state_col = 'SG_UF_RESIDENCIA'
        elif 'SG_UF_PROVA' in df.columns:
            state_col = 'SG_UF_PROVA'
        elif 'SG_UF' in df.columns:
            state_col = 'SG_UF'
        else:
            state_col = None
        
        if state_col:
            region_mapping = {
                # Norte
                'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte',
                'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
                # Nordeste
                'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
                'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
                # Sudeste
                'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
                # Sul
                'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
                # Centro-Oeste
                'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste'
            }
            
            df['REGIAO'] = df[state_col].map(region_mapping)
            self.logger.info("Created REGIAO (regional grouping)")
        
        return df
    
    def _create_age_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create age group categories"""
        if 'NU_IDADE' in df.columns:
            df['FAIXA_ETARIA'] = pd.cut(
                df['NU_IDADE'],
                bins=[0, 17, 19, 24, 29, 100],
                labels=['Até 17', '18-19', '20-24', '25-29', '30+'],
                include_lowest=True
            )
            self.logger.info("Created FAIXA_ETARIA")
        
        return df
    
    def _create_infrastructure_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create school infrastructure index"""
        # Infrastructure columns
        infra_cols = [
            'IN_BIBLIOTECA', 'IN_LABORATORIO_INFORMATICA', 'IN_LABORATORIO_CIENCIAS',
            'IN_QUADRA_ESPORTES', 'IN_INTERNET', 'IN_BANDA_LARGA'
        ]
        
        # Check which columns exist
        existing_cols = [col for col in infra_cols if col in df.columns]
        
        if existing_cols:
            # Calculate infrastructure index (0-10 scale)
            df['INDICE_INFRAESTRUTURA'] = (df[existing_cols].sum(axis=1) / 
                                           len(existing_cols) * 10)
            self.logger.info("Created INDICE_INFRAESTRUTURA")
            
            # Create infrastructure categories
            df['CATEGORIA_INFRAESTRUTURA'] = pd.cut(
                df['INDICE_INFRAESTRUTURA'],
                bins=[0, 3, 6, 10],
                labels=['Baixa', 'Média', 'Alta'],
                include_lowest=True
            )
            self.logger.info("Created CATEGORIA_INFRAESTRUTURA")
        
        return df
    
    def _create_school_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create school type categories"""
        if 'TP_DEPENDENCIA' in df.columns:
            school_type_mapping = {
                1: 'Federal',
                2: 'Estadual',
                3: 'Municipal',
                4: 'Privada'
            }
            df['TIPO_ESCOLA'] = df['TP_DEPENDENCIA'].map(school_type_mapping)
            self.logger.info("Created TIPO_ESCOLA")
            
            # Create public/private binary
            df['ESCOLA_PUBLICA'] = df['TP_DEPENDENCIA'].isin([1, 2, 3]).astype(int)
            self.logger.info("Created ESCOLA_PUBLICA")
        
        return df
    
    def aggregate_by_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate data by state
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            State-level aggregated DataFrame
        """
        # Try different state column names
        if 'SG_UF_RESIDENCIA' in df.columns:
            state_col = 'SG_UF_RESIDENCIA'
        elif 'SG_UF_PROVA' in df.columns:
            state_col = 'SG_UF_PROVA'
        elif 'SG_UF' in df.columns:
            state_col = 'SG_UF'
        else:
            raise ValueError(f"State column not found in DataFrame. Available columns: {df.columns.tolist()}")
        
        self.logger.info("Aggregating data by state")
        
        # Define aggregation functions
        agg_dict = {
            'NU_INSCRICAO': 'count',  # Count of students
        }
        
        # Add score columns
        score_cols = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 
                      'NU_NOTA_REDACAO', 'NOTA_MEDIA']
        for col in score_cols:
            if col in df.columns:
                agg_dict[col] = ['mean', 'median', 'std']
        
        # Aggregate
        df_agg = df.groupby(state_col).agg(agg_dict).reset_index()
        
        # Flatten column names
        df_agg.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                          for col in df_agg.columns.values]
        
        # Rename count column
        df_agg = df_agg.rename(columns={'NU_INSCRICAO_count': 'TOTAL_ESTUDANTES'})
        
        self.logger.info(f"Created state aggregation: {len(df_agg)} states")
        return df_agg
    
    def aggregate_by_region(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate data by region
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            Region-level aggregated DataFrame
        """
        if 'REGIAO' not in df.columns:
            raise ValueError("REGIAO column not found. Run transform_enem_data first.")
        
        self.logger.info("Aggregating data by region")
        
        # Define aggregation functions
        agg_dict = {
            'NU_INSCRICAO': 'count',
        }
        
        # Add score columns
        score_cols = ['NU_NOTA_MT', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 
                      'NU_NOTA_REDACAO', 'NOTA_MEDIA']
        for col in score_cols:
            if col in df.columns:
                agg_dict[col] = ['mean', 'median', 'std']
        
        # Aggregate
        df_agg = df.groupby('REGIAO').agg(agg_dict).reset_index()
        
        # Flatten column names
        df_agg.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                          for col in df_agg.columns.values]
        
        # Rename count column
        df_agg = df_agg.rename(columns={'NU_INSCRICAO_count': 'TOTAL_ESTUDANTES'})
        
        self.logger.info(f"Created region aggregation: {len(df_agg)} regions")
        return df_agg


def main():
    """Test data transformer"""
    logging.basicConfig(level=logging.INFO)
    
    transformer = DataTransformer()
    
    print("Data Transformer initialized")
    print("Use transformer.transform_enem_data(df) or transformer.transform_censo_data(df)")


if __name__ == "__main__":
    main()
