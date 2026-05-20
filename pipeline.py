"""
Dashboard ENEM - Pipeline de Dados
Pipeline ETL completo de dados brutos para dados processados prontos para dashboards
Suporta BigQuery, arquivos locais e cache
"""

import os
import logging
from pathlib import Path
import sys
import argparse

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import DEFAULT_YEAR, SAMPLE_SIZE
from data_processing.data_loader import DataLoader
from data_processing.data_cleaner import DataCleaner
from data_processing.data_transformer import DataTransformer
from data_processing.data_integrator import DataIntegrator


def setup_logging():
    """Configurar logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """Processar argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='ENEM Data Pipeline - ETL with BigQuery and Cache support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use BigQuery with sample data
  python pipeline.py --source bigquery --sample
  
  # Process specific year from BigQuery
  python pipeline.py --source bigquery --year 2022
  
  # Force refresh cache
  python pipeline.py --source bigquery --year 2022 --force-refresh
  
  # Use local files (fallback)
  python pipeline.py --source local
  
  # Process specific states
  python pipeline.py --source bigquery --year 2022 --states SP RJ MG
  
  # Limit records for testing
  python pipeline.py --source bigquery --year 2022 --limit 10000
        """
    )
    
    parser.add_argument(
        '--source',
        type=str,
        choices=['bigquery', 'local'],
        default='bigquery',
        help='Data source (default: bigquery)'
    )
    
    parser.add_argument(
        '--year',
        type=int,
        default=None,
        help=f'Specific year to process (default: {DEFAULT_YEAR})'
    )
    
    parser.add_argument(
        '--years',
        type=int,
        nargs='+',
        default=None,
        help='Multiple years to process (e.g., --years 2020 2021 2022)'
    )
    
    parser.add_argument(
        '--states',
        type=str,
        nargs='+',
        default=None,
        help='Specific states to process (e.g., --states SP RJ MG)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of records to process'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help=f'Use sample data for development (size: {SAMPLE_SIZE})'
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='Force refresh cache (ignore existing cache)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable cache system'
    )
    
    parser.add_argument(
        '--skip-aggregations',
        action='store_true',
        help='Skip aggregation steps (faster for testing)'
    )
    
    return parser.parse_args()


def run_pipeline(args=None):
    """
    Executar pipeline completo de dados
    
    Args:
        args: Argumentos de linha de comando (None = processar de sys.argv)
    """
    logger = setup_logging()
    
    # Processar argumentos
    if args is None:
        args = parse_arguments()
    
    logger.info("="*80)
    logger.info("ENEM DASHBOARD - DATA PIPELINE")
    logger.info("="*80)
    logger.info(f"Source: {args.source}")
    logger.info(f"Year: {args.year or 'All available'}")
    logger.info(f"Sample mode: {args.sample}")
    logger.info(f"Force refresh: {args.force_refresh}")
    logger.info(f"Cache: {'Disabled' if args.no_cache else 'Enabled'}")
    logger.info("="*80)
    
    try:
        # Inicializar componentes
        use_cache = not args.no_cache
        loader = DataLoader(use_cache=use_cache)
        cleaner = DataCleaner()
        transformer = DataTransformer()
        integrator = DataIntegrator()
        
        # ========================================
        # STEP 1: LOAD RAW DATA
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 1: LOADING RAW DATA")
        logger.info("="*80)
        
        # Load data using new unified method
        try:
            df_enem = loader.load_data(
                source=args.source,
                year=args.year,
                years=args.years,
                states=args.states,
                limit=args.limit,
                sample=args.sample,
                force_refresh=args.force_refresh
            )
            logger.info(f"✓ Data loaded: {len(df_enem):,} rows, {len(df_enem.columns)} columns")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
        
        # ========================================
        # STEP 2: CLEAN DATA
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 2: CLEANING DATA")
        logger.info("="*80)
        
        df_enem_clean = cleaner.clean_enem_data(df_enem)
        cleaner.print_cleaning_report()
        
        # ========================================
        # STEP 3: TRANSFORM DATA
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 3: TRANSFORMING DATA")
        logger.info("="*80)
        
        df_enem_transformed = transformer.transform_enem_data(df_enem_clean)
        logger.info(f"✓ Transformation complete: {len(df_enem_transformed.columns)} columns")
        
        # ========================================
        # STEP 4: CREATE AGGREGATIONS
        # ========================================
        if not args.skip_aggregations:
            logger.info("\n" + "="*80)
            logger.info("STEP 4: CREATING AGGREGATIONS")
            logger.info("="*80)
            
            # Try to load from BigQuery first (more efficient)
            if args.source == "bigquery":
                logger.info("Attempting to load pre-aggregated data from BigQuery...")
                try:
                    df_state_agg = loader.load_aggregated_by_state(
                        year=args.year,
                        years=args.years,
                        force_refresh=args.force_refresh
                    )
                    df_region_agg = loader.load_aggregated_by_region(
                        year=args.year,
                        years=args.years,
                        force_refresh=args.force_refresh
                    )
                    
                    if df_state_agg is not None and df_region_agg is not None:
                        logger.info(f"✓ State aggregation from BigQuery: {len(df_state_agg)} records")
                        logger.info(f"✓ Region aggregation from BigQuery: {len(df_region_agg)} records")
                    else:
                        raise ValueError("BigQuery aggregations returned None")
                        
                except Exception as e:
                    logger.warning(f"BigQuery aggregations failed: {e}")
                    logger.info("Falling back to local aggregation...")
                    df_state_agg = transformer.aggregate_by_state(df_enem_transformed)
                    df_region_agg = transformer.aggregate_by_region(df_enem_transformed)
                    logger.info(f"✓ State aggregation (local): {len(df_state_agg)} states")
                    logger.info(f"✓ Regional aggregation (local): {len(df_region_agg)} regions")
            else:
                # Local aggregation
                df_state_agg = transformer.aggregate_by_state(df_enem_transformed)
                df_region_agg = transformer.aggregate_by_region(df_enem_transformed)
                logger.info(f"✓ State aggregation: {len(df_state_agg)} states")
                logger.info(f"✓ Regional aggregation: {len(df_region_agg)} regions")
        else:
            logger.info("\n" + "="*80)
            logger.info("STEP 4: SKIPPING AGGREGATIONS (--skip-aggregations)")
            logger.info("="*80)
            df_state_agg = None
            df_region_agg = None
        
        # ========================================
        # STEP 5: SAVE PROCESSED DATA
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 5: SAVING PROCESSED DATA")
        logger.info("="*80)
        
        # Create processed directory if it doesn't exist
        os.makedirs('data/processed', exist_ok=True)
        
        # Save main dataset
        output_file = 'data/processed/enem_processed.csv'
        logger.info(f"Saving to {output_file}...")
        df_enem_transformed.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"✓ Saved: {output_file}")
        
        # Save aggregations (if created)
        if df_state_agg is not None:
            df_state_agg.to_csv('data/processed/aggregated_by_state.csv', index=False)
            logger.info("✓ Saved: data/processed/aggregated_by_state.csv")
        
        if df_region_agg is not None:
            df_region_agg.to_csv('data/processed/aggregated_by_region.csv', index=False)
            logger.info("✓ Saved: data/processed/aggregated_by_region.csv")
        
        # ========================================
        # STEP 6: VALIDATION
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("STEP 6: VALIDATION")
        logger.info("="*80)
        
        validation = integrator.validate_integration(df_enem_transformed)
        
        if validation['meets_minimum_records']:
            logger.info("✓ Dataset meets minimum record requirement (10,000+)")
        else:
            logger.warning("✗ Dataset does not meet minimum record requirement")
        
        # ========================================
        # PIPELINE SUMMARY
        # ========================================
        logger.info("\n" + "="*80)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*80)
        logger.info(f"Total records processed: {len(df_enem_transformed):,}")
        logger.info(f"Total columns: {len(df_enem_transformed.columns)}")
        if df_state_agg is not None:
            logger.info(f"States: {len(df_state_agg)}")
        if df_region_agg is not None:
            logger.info(f"Regions: {len(df_region_agg)}")
        logger.info(f"Memory usage: {validation['memory_usage_mb']:.2f} MB")
        logger.info(f"Missing data: {validation['missing_percentage']:.2f}%")
        logger.info(f"Data source: {args.source}")
        logger.info(f"Cache used: {not args.no_cache}")
        logger.info("="*80)
        logger.info("✓ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        
        logger.info("\nNext steps:")
        logger.info("1. Run exploratory analysis: jupyter notebook notebooks/exploratory_analysis.ipynb")
        logger.info("2. Launch dashboard: python app.py")
        logger.info("\nCache management:")
        logger.info("- View cache info: python -m src.data_processing.data_cache")
        logger.info("- Clear cache: Add --force-refresh flag to next run")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


def create_sample_data():
    """Criar dados de amostra para demonstração"""
    import pandas as pd
    import numpy as np
    
    logger = logging.getLogger(__name__)
    logger.info("Creating sample dataset for demonstration...")
    
    # Create sample data with 15,000 records
    n_records = 15000
    
    states = ['SP', 'RJ', 'MG', 'BA', 'PR', 'RS', 'PE', 'CE', 'PA', 'SC']
    
    data = {
        'NU_INSCRICAO': range(1, n_records + 1),
        'NU_ANO': np.random.choice([2020, 2021, 2022], n_records),
        'SG_UF_RESIDENCIA': np.random.choice(states, n_records),
        'NU_NOTA_MT': np.random.normal(500, 100, n_records).clip(0, 1000),
        'NU_NOTA_CN': np.random.normal(500, 100, n_records).clip(0, 1000),
        'NU_NOTA_CH': np.random.normal(500, 100, n_records).clip(0, 1000),
        'NU_NOTA_LC': np.random.normal(500, 100, n_records).clip(0, 1000),
        'NU_NOTA_REDACAO': np.random.normal(500, 150, n_records).clip(0, 1000),
        'TP_SEXO': np.random.choice(['M', 'F'], n_records),
        'NU_IDADE': np.random.randint(16, 25, n_records),
        'TP_COR_RACA': np.random.choice([1, 2, 3, 4, 5], n_records),
        'Q006': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'], n_records),
        'Q001': np.random.choice(['A', 'B', 'C', 'D', 'E'], n_records),
        'Q002': np.random.choice(['A', 'B', 'C', 'D', 'E'], n_records),
    }
    
    df = pd.DataFrame(data)
    logger.info(f"✓ Sample data created: {len(df):,} rows")
    
    return df


if __name__ == "__main__":
    run_pipeline()
