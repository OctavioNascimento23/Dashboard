"""
Dashboard ENEM - Visualização Interativa de Dados Locais
Dashboard completo com visão executiva e análise detalhada
Carregamento direto de arquivos CSV locais
"""

import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask_caching import Cache
import logging

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar configuracao e carregador de dados
import config
from src.data_processing.data_loader import DataLoader
import version

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CARREGAMENTO DE DADOS
# ============================================================================

print("\n" + "="*80)
print("ENEM DASHBOARD - CARREGANDO DADOS LOCAIS")
print("="*80)

# Inicializar carregador
loader = DataLoader()

# Carregar dados do CSV local
print(f"Carregando dados do ENEM {config.DEFAULT_YEAR} do CSV local...")
print(f"Arquivo: {config.CSV_FILES['microdados']}")
print(f"Limite de registros: {config.MAX_RECORDS:,}")

try:
    # Carregar dados do CSV com amostragem inteligente
    df_main = loader.load_enem_data(
        year=config.DEFAULT_YEAR,
        max_records=config.MAX_RECORDS
    )
    
    print(f"[OK] Dados carregados com sucesso: {len(df_main):,} registros")
    print(f"[OK] Colunas: {len(df_main.columns)}")
    print(f"[OK] Memória: {df_main.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
except Exception as e:
    logger.error(f"Erro ao carregar dados do CSV: {e}")
    print("\n❌ ERRO: Não foi possível carregar os dados!")
    print(f"Verifique se o arquivo existe em: {config.LOCAL_RAW_DIR / config.CSV_FILES['microdados']}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
# Padronizar nomes de colunas para minúsculas
df_main.columns = df_main.columns.str.lower()

# Mapear colunas CSV para nomes amigáveis
column_mapping = {
    'nu_nota_mt': 'nota_matematica',
    'nu_nota_cn': 'nota_ciencias_natureza',
    'nu_nota_ch': 'nota_ciencias_humanas',
    'nu_nota_lc': 'nota_linguagens',
    'nu_nota_redacao': 'nota_redacao',
    'sg_uf_prova': 'sigla_uf',
    'tp_sexo': 'sexo',
    'tp_faixa_etaria': 'idade',
    'tp_cor_raca': 'cor_raca',
    'tp_escola': 'tipo_escola',
    'tp_localizacao_esc': 'localizacao_escola',
    'q001': 'escolaridade_pai',
    'q002': 'escolaridade_mae',
    'q006': 'renda_familiar'  # Q006 é a faixa de renda familiar (A-Q)
}

df_main = df_main.rename(columns=column_mapping)

# Calcular nota média (média das 5 áreas)
score_cols = ['nota_matematica', 'nota_ciencias_natureza', 'nota_ciencias_humanas',
              'nota_linguagens', 'nota_redacao']
existing_score_cols = [col for col in score_cols if col in df_main.columns]

if existing_score_cols:
    df_main['nota_media'] = df_main[existing_score_cols].mean(axis=1)
    print(f"[OK] Nota média calculada a partir de {len(existing_score_cols)} áreas")

# Adicionar região se não existir
if 'regiao' not in df_main.columns and 'sigla_uf' in df_main.columns:
    df_main['regiao'] = df_main['sigla_uf'].map(
        lambda uf: config.get_region_for_state(uf) if pd.notna(uf) else None
    )
    print(f"[OK] Região adicionada para {df_main['regiao'].notna().sum():,} registros")

print("\n" + "="*80)
print(f"[OK] DADOS PRONTOS PARA O DASHBOARD")
print("="*80)
print(f"Total de registros: {len(df_main):,}")
print(f"Total de colunas: {len(df_main.columns)}")
print(f"Estados únicos: {df_main['sigla_uf'].nunique() if 'sigla_uf' in df_main.columns else 0}")
print(f"Regiões únicas: {df_main['regiao'].nunique() if 'regiao' in df_main.columns else 0}")
print(f"Nota média geral: {df_main['nota_media'].mean():.2f}" if 'nota_media' in df_main.columns else "")
print("="*80 + "\n")

# ============================================================================
# INICIALIZAR APLICAÇÃO DASH
# ============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

# Configurar cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'data/cache/dash',
    'CACHE_THRESHOLD': 100
})

app.title = "ENEM Dashboard - Análise Educacional"

# ============================================================================
# MAPEAMENTOS DE VARIÁVEIS CATEGÓRICAS
# ============================================================================

# Mapeamento para tipo de escola (TP_ESCOLA)
# Mapeamento para tipo de escola (TP_ESCOLA)
# Nota: As chaves são strings porque o data_loader converte colunas categóricas para string
TIPO_ESCOLA_MAP = {
    '1': 'Não Respondeu',
    '2': 'Pública',
    '3': 'Privada',
    1: 'Não Respondeu',
    2: 'Pública',
    3: 'Privada'
}

# Mapeamento para cor/raça (TP_COR_RACA)
COR_RACA_MAP = {
    '0': 'Não declarado',
    '1': 'Branca',
    '2': 'Preta',
    '3': 'Parda',
    '4': 'Amarela',
    '5': 'Indígena',
    '6': 'Não dispõe da informação',
    0: 'Não declarado',
    1: 'Branca',
    2: 'Preta',
    3: 'Parda',
    4: 'Amarela',
    5: 'Indígena',
    6: 'Não dispõe da informação'
}

# Mapeamento para localização da escola (TP_LOCALIZACAO_ESC)
LOCALIZACAO_ESCOLA_MAP = {
    '1': 'Urbana',
    '2': 'Rural',
    1: 'Urbana',
    2: 'Rural',
    1.0: 'Urbana',
    2.0: 'Rural'
}

# Mapeamento para faixa de renda familiar (Q006)
RENDA_FAMILIAR_MAP = {
    'A': 'Nenhuma renda',
    'B': 'Até R$ 1.212,00',
    'C': 'De R$ 1.212,01 até R$ 1.818,00',
    'D': 'De R$ 1.818,01 até R$ 2.424,00',
    'E': 'De R$ 2.424,01 até R$ 3.030,00',
    'F': 'De R$ 3.030,01 até R$ 3.636,00',
    'G': 'De R$ 3.636,01 até R$ 4.848,00',
    'H': 'De R$ 4.848,01 até R$ 6.060,00',
    'I': 'De R$ 6.060,01 até R$ 7.272,00',
    'J': 'De R$ 7.272,01 até R$ 8.484,00',
    'K': 'De R$ 8.484,01 até R$ 9.696,00',
    'L': 'De R$ 9.696,01 até R$ 10.908,00',
    'M': 'De R$ 10.908,01 até R$ 12.120,00',
    'N': 'De R$ 12.120,01 até R$ 14.544,00',
    'O': 'De R$ 14.544,01 até R$ 18.180,00',
    'P': 'De R$ 18.180,01 até R$ 24.240,00',
    'Q': 'Mais de R$ 24.240,00'
}

# Mapeamento para sexo
SEXO_MAP = {
    'M': 'Masculino',
    'F': 'Feminino'
}

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def create_kpi_card(title, value, subtitle, color, icon=""):
    """Criar um componente de cartão KPI"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-2x text-{color} mb-2") if icon else None,
                html.H6(title, className="text-muted mb-2"),
                html.H3(value, className=f"text-{color} mb-1 fw-bold"),
                html.P(subtitle, className="text-muted small mb-0")
            ], className="text-center")
        ])
    ], className="shadow-sm h-100")


def generate_insights(df):
    """Gerar insights automáticos a partir dos dados"""
    insights = []
    
    try:
        # Insight 1: Best performing state
        if 'sigla_uf' in df.columns:
            state_avg = df.groupby('sigla_uf')['nota_media'].mean()
            best_state = state_avg.idxmax()
            best_score = state_avg.max()
            insights.append({
                'icon': 'fa-trophy',
                'color': 'success',
                'title': 'Melhor Desempenho',
                'text': f"{best_state} lidera com média de {best_score:.1f} pontos"
            })
        
        # Insight 2: Gender gap
        if 'sexo' in df.columns:
            gender_avg = df.groupby('sexo')['nota_media'].mean()
            if len(gender_avg) >= 2:
                gap = abs(gender_avg.iloc[0] - gender_avg.iloc[1])
                insights.append({
                    'icon': 'fa-balance-scale',
                    'color': 'warning',
                    'title': 'Gap de Gênero',
                    'text': f"Diferença de {gap:.1f} pontos entre gêneros"
                })
        
        # Insight 3: School type gap
        if 'tipo_escola' in df.columns:
            school_avg = df.groupby('tipo_escola')['nota_media'].mean()
            if len(school_avg) >= 2:
                gap = abs(school_avg.iloc[0] - school_avg.iloc[1])
                insights.append({
                    'icon': 'fa-school',
                    'color': 'info',
                    'title': 'Gap Público-Privado',
                    'text': f"Diferença de {gap:.1f} pontos entre tipos de escola"
                })
        
        # Insight 4: Regional disparity
        if 'regiao' in df.columns:
            region_avg = df.groupby('regiao')['nota_media'].mean()
            disparity = region_avg.max() - region_avg.min()
            insights.append({
                'icon': 'fa-map-marked-alt',
                'color': 'danger',
                'title': 'Disparidade Regional',
                'text': f"Diferença de {disparity:.1f} pontos entre regiões"
            })
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
    
    return insights


def create_advanced_filters():
    """Criar componente de filtros avançados"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                html.I(className="fas fa-filter me-2"),
                "Filtros Avançados"
            ])
        ]),
        dbc.CardBody([
            # Region filter
            html.Label("Região:", className="fw-bold"),
            dcc.Dropdown(
                id='region-filter',
                options=[{'label': 'Todas', 'value': 'ALL'}] + 
                        [{'label': r, 'value': r} for r in sorted(df_main['regiao'].unique()) if pd.notna(r)],
                value='ALL',
                className="mb-3"
            ),
            
            # State filter
            html.Label("Estado:", className="fw-bold"),
            dcc.Dropdown(
                id='state-filter',
                options=[{'label': 'Todos', 'value': 'ALL'}] + 
                        [{'label': s, 'value': s} for s in sorted(df_main['sigla_uf'].unique())],
                value='ALL',
                className="mb-3"
            ),
            
            # School type filter
            html.Label("Tipo de Escola:", className="fw-bold"),
            dcc.Dropdown(
                id='school-type-filter',
                options=[{'label': 'Todos', 'value': 'ALL'}] + 
                        [{'label': t, 'value': t} for t in sorted(df_main['tipo_escola'].unique()) if pd.notna(t)],
                value='ALL',
                className="mb-3"
            ),
            
            # Gender filter
            html.Label("Gênero:", className="fw-bold"),
            dcc.Dropdown(
                id='gender-filter',
                options=[
                    {'label': 'Todos', 'value': 'ALL'},
                    {'label': 'Masculino', 'value': 'M'},
                    {'label': 'Feminino', 'value': 'F'}
                ],
                value='ALL',
                className="mb-3"
            ),
            
            # Botão aplicar
            dbc.Button(
                [html.I(className="fas fa-check me-2"), "Aplicar Filtros"],
                id="apply-filters",
                color="primary",
                className="w-100"
            )
        ])
    ], className="shadow-sm")

# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

def create_subject_comparison(df):
    """Gráfico radar comparando desempenho entre disciplinas"""
    subjects = {
        'Matemática': 'nota_matematica',
        'Ciências Natureza': 'nota_ciencias_natureza',
        'Ciências Humanas': 'nota_ciencias_humanas',
        'Linguagens': 'nota_linguagens',
        'Redação': 'nota_redacao'
    }
    
    means = [df[col].mean() for col in subjects.values()]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=means,
        theta=list(subjects.keys()),
        fill='toself',
        name='Média Nacional',
        line_color='#636EFA'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(means) * 1.1]
            )
        ),
        showlegend=True,
        title="Desempenho por Área de Conhecimento",
        height=400
    )
    
    return fig


def create_subject_bars(df):
    """Gráfico de barras agrupadas para comparação de disciplinas"""
    subjects = {
        'Matemática': 'nota_matematica',
        'C. Natureza': 'nota_ciencias_natureza',
        'C. Humanas': 'nota_ciencias_humanas',
        'Linguagens': 'nota_linguagens',
        'Redação': 'nota_redacao'
    }
    
    data = []
    for name, col in subjects.items():
        data.append({
            'Área': name,
            'Média': df[col].mean(),
            'Mediana': df[col].median(),
            'Desvio': df[col].std()
        })
    
    df_subjects = pd.DataFrame(data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Média',
        x=df_subjects['Área'],
        y=df_subjects['Média'],
        marker_color='#636EFA'
    ))
    
    fig.add_trace(go.Bar(
        name='Mediana',
        x=df_subjects['Área'],
        y=df_subjects['Mediana'],
        marker_color='#EF553B'
    ))
    
    fig.update_layout(
        barmode='group',
        title="Comparação de Médias e Medianas por Área",
        xaxis_title="Área de Conhecimento",
        yaxis_title="Nota",
        height=400
    )
    
    return fig


def create_socioeconomic_analysis(df):
    """Box plot para análise socioeconômica"""
    if 'renda_familiar' not in df.columns or df['renda_familiar'].isna().all():
        return go.Figure().add_annotation(
            text="Dados de renda não disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Criar cópia do dataframe e mapear valores de renda
    df_plot = df.copy()
    df_plot['renda_familiar_label'] = df_plot['renda_familiar'].map(RENDA_FAMILIAR_MAP)
    
    # Remover valores não mapeados
    df_plot = df_plot[df_plot['renda_familiar_label'].notna()]
    
    if len(df_plot) == 0:
        return go.Figure().add_annotation(
            text="Dados de renda não disponíveis após mapeamento",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
    
    # Define the ascending order for income categories
    income_order = [
        'Nenhuma renda',
        'Até R$ 1.212,00',
        'De R$ 1.212,01 até R$ 1.818,00',
        'De R$ 1.818,01 até R$ 2.424,00',
        'De R$ 2.424,01 até R$ 3.030,00',
        'De R$ 3.030,01 até R$ 3.636,00',
        'De R$ 3.636,01 até R$ 4.848,00',
        'De R$ 4.848,01 até R$ 6.060,00',
        'De R$ 6.060,01 até R$ 7.272,00',
        'De R$ 7.272,01 até R$ 8.484,00',
        'De R$ 8.484,01 até R$ 9.696,00',
        'De R$ 9.696,01 até R$ 10.908,00',
        'De R$ 10.908,01 até R$ 12.120,00',
        'De R$ 12.120,01 até R$ 14.544,00',
        'De R$ 14.544,01 até R$ 18.180,00',
        'De R$ 18.180,01 até R$ 24.240,00',
        'Mais de R$ 24.240,00'
    ]
    
    fig = px.box(
        df_plot,
        x='renda_familiar_label',
        y='nota_media',
        title="Desempenho por Faixa de Renda Familiar",
        labels={'nota_media': 'Nota Média', 'renda_familiar_label': 'Faixa de Renda'},
        color='renda_familiar_label',
        color_discrete_sequence=px.colors.qualitative.Set3,
        category_orders={'renda_familiar_label': income_order}
    )
    
    fig.update_layout(height=450, showlegend=False)
    fig.update_xaxes(tickangle=45)
    
    return fig


def create_equity_analysis(df):
    """Múltiplos gráficos mostrando gaps de equidade"""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            'Gap de Gênero', 'Gap Público-Privado',
            'Gap por Cor/Raça'
        ),
        specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Gender gap
    if 'sexo' in df.columns:
        df_temp = df.copy()
        df_temp['sexo_label'] = df_temp['sexo'].map(SEXO_MAP)
        gender_data = df_temp.groupby('sexo_label')['nota_media'].mean().reset_index()
        gender_data = gender_data[gender_data['sexo_label'].notna()]
        
        if len(gender_data) > 0:
            fig.add_trace(
                go.Bar(x=gender_data['sexo_label'], y=gender_data['nota_media'],
                       marker_color=['#636EFA', '#EF553B'], showlegend=False),
                row=1, col=1
            )
    
    # School type gap
    if 'tipo_escola' in df.columns:
        df_temp = df.copy()
        df_temp['tipo_escola_label'] = df_temp['tipo_escola'].map(TIPO_ESCOLA_MAP)
        school_data = df_temp.groupby('tipo_escola_label')['nota_media'].mean().reset_index()
        school_data = school_data[school_data['tipo_escola_label'].notna()]
        
        if len(school_data) > 0:
            fig.add_trace(
                go.Bar(x=school_data['tipo_escola_label'], y=school_data['nota_media'],
                       marker_color=['#00CC96', '#AB63FA', '#FFA15A'], showlegend=False),
                row=1, col=2
            )
    
    # Race gap
    if 'cor_raca' in df.columns:
        df_temp = df.copy()
        df_temp['cor_raca_label'] = df_temp['cor_raca'].map(COR_RACA_MAP)
        race_data = df_temp.groupby('cor_raca_label')['nota_media'].mean().reset_index()
        race_data = race_data[race_data['cor_raca_label'].notna()]
        
        if len(race_data) > 0:
            fig.add_trace(
                go.Bar(x=race_data['cor_raca_label'], y=race_data['nota_media'],
                       marker_color=px.colors.qualitative.Pastel, showlegend=False),
                row=1, col=3
            )
    
    fig.update_layout(height=500, title_text="Análise de Equidade Educacional")
    fig.update_yaxes(title_text="Nota Média")
    
    return fig


def create_state_ranking(df):
    """Gráfico de barras horizontal ranqueando estados"""
    state_avg = df.groupby('sigla_uf')['nota_media'].mean().sort_values(ascending=True).reset_index()
    
    fig = px.bar(
        state_avg,
        y='sigla_uf',
        x='nota_media',
        orientation='h',
        title="Ranking de Estados por Desempenho",
        labels={'nota_media': 'Nota Média', 'sigla_uf': 'Estado'},
        color='nota_media',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=600, showlegend=False)
    return fig


def create_regional_boxplot(df):
    """Box plot comparando regiões"""
    fig = px.box(
        df,
        x='regiao',
        y='nota_media',
        title="Distribuição de Notas por Região",
        labels={'nota_media': 'Nota Média', 'regiao': 'Região'},
        color='regiao',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(height=450, showlegend=False)
    return fig


def create_distribution_histogram(df):
    """Histograma da distribuição de notas"""
    fig = px.histogram(
        df,
        x='nota_media',
        nbins=50,
        title="Distribuição de Notas",
        labels={'nota_media': 'Nota Média'},
        color_discrete_sequence=['#636EFA']
    )
    
    mean_score = df['nota_media'].mean()
    fig.add_vline(
        x=mean_score,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média Nacional: {mean_score:.1f}",
        annotation_position="top"
    )
    
    # Atualizar labels dos eixos explicitamente
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Nota Média",
        yaxis_title="Quantidade de Estudantes"
    )
    return fig

# ============================================================================
# LAYOUT DA APLICAÇÃO
# ============================================================================

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='filtered-data-store'),
    
    # Cabeçalho
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-graduation-cap me-3"),
                    "ENEM Dashboard"
                ], className="text-center mb-2 mt-4"),
                html.P(
                    "Análise Compreensiva do Desempenho Educacional no Brasil",
                    className="text-center text-muted mb-1"
                ),
                html.P(
                    f"Dados: ENEM {config.DEFAULT_YEAR} | Fonte: Microdados INEP (CSV Local) | {len(df_main):,} registros",
                    className="text-center text-muted small mb-4"
                )
            ])
        ])
    ]),
    
    # Abas de navegação
    dbc.Row([
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="📊 Geral", tab_id="executive"),
                dbc.Tab(label="🔍 Avançado", tab_id="detailed"),
            ], id="tabs", active_tab="executive", className="mb-4")
        ])
    ]),
    
    # Indicador de carregamento
    dcc.Loading(
        id="loading",
        type="default",
        children=html.Div(id='page-content')
    ),
    
    # Componente de download
    dcc.Download(id="download-data"),
    
    # Rodapé com informações de versão
    html.Hr(className="mt-5"),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.P([
                    html.Strong("Dashboard ENEM"),
                    f" - Versão {version.__version__} ({version.__date__})"
                ], className="text-center text-muted small mb-1"),
                html.P([
                    html.I(className="fas fa-database me-2"),
                    f"Fonte: INEP - Microdados ENEM {config.DEFAULT_YEAR} | ",
                    html.I(className="fas fa-chart-line me-2"),
                    f"{len(df_main):,} registros processados | ",
                    html.I(className="fas fa-code me-2"),
                    f"Desenvolvido pelo {version.__author__}"
                ], className="text-center text-muted small mb-1"),
                html.P([
                    html.I(className="fas fa-info-circle me-2"),
                    "Status: ",
                    html.Span(version.__status__, className="badge bg-success"),
                    " | ",
                    html.A("Documentação", href="https://github.com/OctavioNascimento23/Dashboard/blob/main/docs/CODE_DOCUMENTATION.md", target="_blank", className="text-decoration-none me-2"),
                    " | ",
                    html.A("Changelog", href="https://github.com/OctavioNascimento23/Dashboard/blob/main/CHANGELOG.md", target="_blank", className="text-decoration-none")
                ], className="text-center text-muted small mb-3")
            ])
        ])
    ])
    
], fluid=True)

# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('tabs', 'active_tab')
)
def render_content(active_tab):
    """Renderizar dashboard baseado na aba selecionada"""
    
    if active_tab == "executive":
        # Calcular KPIs
        total_students = len(df_main)
        avg_score = df_main['nota_media'].mean()
        state_means = df_main.groupby('sigla_uf')['nota_media'].mean()
        perf_gap = state_means.max() - state_means.min()
        n_states = df_main['sigla_uf'].nunique()
        
        # Gerar insights
        insights = generate_insights(df_main)
        
        return dbc.Container([
            # Cartões KPI
            dbc.Row([
                dbc.Col([
                    create_kpi_card(
                        "Média Nacional", 
                        f"{avg_score:.1f}", 
                        "pontos", 
                        "primary",
                        "fa-chart-line"
                    )
                ], width=12, md=6, lg=3),
                dbc.Col([
                    create_kpi_card(
                        "Total Estudantes", 
                        f"{total_students:,}", 
                        "analisados", 
                        "success",
                        "fa-users"
                    )
                ], width=12, md=6, lg=3),
                dbc.Col([
                    create_kpi_card(
                        "Gap Desempenho", 
                        f"{perf_gap:.1f}", 
                        "pontos", 
                        "warning",
                        "fa-exclamation-triangle"
                    )
                ], width=12, md=6, lg=3),
                dbc.Col([
                    create_kpi_card(
                        "Estados", 
                        f"{n_states}", 
                        "UFs analisadas", 
                        "info",
                        "fa-map"
                    )
                ], width=12, md=6, lg=3),
            ], className="mb-4"),
            
            # Cartões de Insights
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-lightbulb me-2"),
                                "Insights Rápidos"
                            ])
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Alert([
                                        html.I(className=f"fas {insight['icon']} me-2"),
                                        html.Strong(f"{insight['title']}: "),
                                        insight['text']
                                    ], color=insight['color'], className="mb-2")
                                ], width=12, lg=6)
                                for insight in insights
                            ])
                        ])
                    ], className="shadow-sm")
                ], width=12, className="mb-4")
            ]),
            
            # Linha de Gráficos Principais 1
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Ranking de Estados")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_state_ranking(df_main), 
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Distribuição de Notas")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_distribution_histogram(df_main), 
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
            ]),
            
            # Linha de Gráficos Principais 2
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Comparação Regional")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_regional_boxplot(df_main), 
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Desempenho por Área")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_subject_comparison(df_main), 
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
            ]),
        ], fluid=True)
    
    elif active_tab == "detailed":
        # Aba de análise detalhada com sub-abas temáticas
        return dbc.Container([
            html.H4([
                html.I(className="fas fa-microscope me-2"),
                "Análise Detalhada"
            ], className="mb-4"),
            
            dbc.Row([
                # Barra lateral de filtros
                dbc.Col([
                    create_advanced_filters(),
                    html.Br(),
                    dbc.Card([
                        dbc.CardHeader(html.H6("Exportar Dados")),
                        dbc.CardBody([
                            dbc.Button(
                                [html.I(className="fas fa-download me-2"), "Baixar CSV"],
                                id="export-button",
                                color="success",
                                className="w-100"
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=3, className="mb-4"),
                
                # Área de conteúdo principal
                dbc.Col([
                    # Sub-abas para diferentes análises
                    dbc.Tabs([
                        dbc.Tab(label="📊 Visão Geral", tab_id="overview"),
                        dbc.Tab(label="📚 Por Área", tab_id="subjects"),
                        dbc.Tab(label="💰 Socioeconômico", tab_id="socioeconomic"),
                        dbc.Tab(label="⚖️ Equidade", tab_id="equity"),
                    ], id="detailed-tabs", active_tab="overview", className="mb-3"),
                    
                    # Conteúdo para sub-abas
                    html.Div(id='detailed-content')
                ], width=12, lg=9)
            ])
        ], fluid=True)
    
    return html.Div("Selecione uma aba")


@callback(
    Output('detailed-content', 'children'),
    [Input('detailed-tabs', 'active_tab'),
     Input('apply-filters', 'n_clicks')],
    [State('region-filter', 'value'),
     State('state-filter', 'value'),
     State('school-type-filter', 'value'),
     State('gender-filter', 'value')]
)
def update_detailed_content(active_tab, n_clicks, region, state, school_type, gender):
    """Atualizar conteúdo de análise detalhada baseado em sub-aba e filtros"""
    
    # Filtrar dados
    filtered_df = df_main.copy()
    
    if region != 'ALL':
        filtered_df = filtered_df[filtered_df['regiao'] == region]
    
    if state != 'ALL':
        filtered_df = filtered_df[filtered_df['sigla_uf'] == state]
    
    if school_type != 'ALL':
        filtered_df = filtered_df[filtered_df['tipo_escola'] == school_type]
    
    if gender != 'ALL':
        filtered_df = filtered_df[filtered_df['sexo'] == gender]
    
    # Cartão de estatísticas resumidas
    summary_card = dbc.Card([
        dbc.CardHeader(html.H6("Estatísticas dos Dados Filtrados")),
        dbc.CardBody([
            html.H5(f"{len(filtered_df):,} registros", className="text-primary"),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    html.P([html.Strong("Média: "), f"{filtered_df['nota_media'].mean():.2f}"]),
                    html.P([html.Strong("Mediana: "), f"{filtered_df['nota_media'].median():.2f}"]),
                    html.P([html.Strong("Desvio Padrão: "), f"{filtered_df['nota_media'].std():.2f}"]),
                ], width=6),
                dbc.Col([
                    html.P([html.Strong("Mínimo: "), f"{filtered_df['nota_media'].min():.2f}"]),
                    html.P([html.Strong("Máximo: "), f"{filtered_df['nota_media'].max():.2f}"]),
                    html.P([html.Strong("Amplitude: "), f"{filtered_df['nota_media'].max() - filtered_df['nota_media'].min():.2f}"]),
                ], width=6),
            ])
        ])
    ], className="shadow-sm mb-4")
    
    if active_tab == "overview":
        return html.Div([
            summary_card,
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Distribuição de Notas")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_distribution_histogram(filtered_df),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Comparação Regional")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_regional_boxplot(filtered_df),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
            ])
        ])
    
    elif active_tab == "subjects":
        return html.Div([
            summary_card,
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Radar - Áreas de Conhecimento")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_subject_comparison(filtered_df),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Comparação Média vs Mediana")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_subject_bars(filtered_df),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6, className="mb-4"),
            ])
        ])
    
    elif active_tab == "socioeconomic":
        return html.Div([
            summary_card,
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Desempenho por Renda Familiar")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_socioeconomic_analysis(filtered_df),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, className="mb-4"),
            ])
        ])
    
    elif active_tab == "equity":
        return html.Div([
            summary_card,
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H5("Análise de Equidade")),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_equity_analysis(filtered_df),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="shadow-sm")
                ], width=12, className="mb-4"),
            ])
        ])
    
    return html.Div("Selecione uma análise")


@callback(
    Output("download-data", "data"),
    Input("export-button", "n_clicks"),
    [State('region-filter', 'value'),
     State('state-filter', 'value'),
     State('school-type-filter', 'value'),
     State('gender-filter', 'value')],
    prevent_initial_call=True
)
def export_data(n_clicks, region, state, school_type, gender):
    """Exportar dados filtrados para CSV"""
    # Prevenir download automático - só exporta se o botão foi clicado
    if not n_clicks or n_clicks == 0:
        raise PreventUpdate
    
    # Filtrar dados
    filtered_df = df_main.copy()
    
    if region != 'ALL':
        filtered_df = filtered_df[filtered_df['regiao'] == region]
    
    if state != 'ALL':
        filtered_df = filtered_df[filtered_df['sigla_uf'] == state]
    
    if school_type != 'ALL':
        filtered_df = filtered_df[filtered_df['tipo_escola'] == school_type]
    
    if gender != 'ALL':
        filtered_df = filtered_df[filtered_df['sexo'] == gender]
    
    return dcc.send_data_frame(filtered_df.to_csv, "enem_data_filtered.csv", index=False)


# ============================================================================
# EXECUTAR APLICAÇÃO
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("ENEM DASHBOARD - SERVIDOR INICIADO")
    print("="*80)
    print(f"Dados carregados: {len(df_main):,} registros")
    print(f"Ano: {config.DEFAULT_YEAR}")
    print(f"Estados: {df_main['sigla_uf'].nunique()}")
    print(f"Regiões: {df_main['regiao'].nunique()}")
    print("\nAcesse o dashboard em: http://localhost:8050")
    print("Pressione Ctrl+C para parar o servidor")
    print("="*80 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=8050)
