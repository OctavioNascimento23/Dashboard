# Análise dos Arquivos CSV Locais

## Resumo da Análise

### 1. ITENS_PROVA_2022.csv
- **Tamanho**: 0.30 MB
- **Colunas**: 14
- **Descrição**: Informações sobre os itens (questões) das provas
- **Colunas principais**:
  - CO_POSICAO: Posição do item na prova
  - SG_AREA: Área do conhecimento (CH, CN, LC, MT)
  - CO_ITEM: Código do item
  - TX_GABARITO: Gabarito da questão
  - CO_HABILIDADE: Código da habilidade avaliada
  - NU_PARAM_A, NU_PARAM_B, NU_PARAM_C: Parâmetros TRI
  - CO_PROVA: Código da prova
  - TX_COR: Cor da prova

### 2. MICRODADOS_ENEM_2022.csv ⭐ **ARQUIVO PRINCIPAL**
- **Tamanho**: 1495.51 MB (~1.5 GB)
- **Colunas**: 76
- **Descrição**: Dados completos dos participantes do ENEM 2022
- **Colunas essenciais para o dashboard**:
  
  **Identificação:**
  - NU_INSCRICAO: Número de inscrição
  - NU_ANO: Ano (2022)
  
  **Demográficas:**
  - TP_FAIXA_ETARIA: Faixa etária
  - TP_SEXO: Sexo (M/F)
  - TP_COR_RACA: Cor/Raça
  - TP_ESTADO_CIVIL: Estado civil
  
  **Educação:**
  - TP_ST_CONCLUSAO: Status de conclusão
  - TP_ANO_CONCLUIU: Ano de conclusão
  - TP_ESCOLA: Tipo de escola
  - TP_ENSINO: Tipo de ensino
  - TP_DEPENDENCIA_ADM_ESC: Dependência administrativa
  
  **Localização:**
  - SG_UF_ESC: UF da escola
  - NO_MUNICIPIO_ESC: Município da escola
  - SG_UF_PROVA: UF da prova
  - NO_MUNICIPIO_PROVA: Município da prova
  
  **Notas:**
  - NU_NOTA_CN: Nota Ciências da Natureza
  - NU_NOTA_CH: Nota Ciências Humanas
  - NU_NOTA_LC: Nota Linguagens e Códigos
  - NU_NOTA_MT: Nota Matemática
  - NU_NOTA_REDACAO: Nota da redação
  
  **Presença:**
  - TP_PRESENCA_CN, TP_PRESENCA_CH, TP_PRESENCA_LC, TP_PRESENCA_MT
  
  **Questionário Socioeconômico:**
  - Q001-Q025: Respostas do questionário (já incluídas no arquivo principal)

### 3. QUEST_HAB_ESTUDO.csv
- **Tamanho**: 271.85 MB
- **Colunas**: 86
- **Descrição**: Questionário de hábitos de estudo (dados duplicados)
- **Observação**: As colunas Q001-Q025 já estão no MICRODADOS_ENEM_2022.csv
- **Status**: Arquivo redundante, não será usado

## Recomendações

### Arquivo Principal
Use apenas **MICRODADOS_ENEM_2022.csv** como fonte de dados principal.

### Colunas Essenciais (35 colunas)
```python
ESSENTIAL_COLUMNS = [
    # Identificação
    'NU_INSCRICAO', 'NU_ANO',
    
    # Demográficas
    'TP_FAIXA_ETARIA', 'TP_SEXO', 'TP_COR_RACA', 'TP_ESTADO_CIVIL',
    
    # Educação
    'TP_ST_CONCLUSAO', 'TP_ANO_CONCLUIU', 'TP_ESCOLA', 'TP_ENSINO',
    'TP_DEPENDENCIA_ADM_ESC', 'TP_LOCALIZACAO_ESC',
    
    # Localização
    'SG_UF_ESC', 'NO_MUNICIPIO_ESC', 'SG_UF_PROVA', 'NO_MUNICIPIO_PROVA',
    
    # Presença
    'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
    
    # Notas
    'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
    
    # Questionário Socioeconômico (principais)
    'Q001', 'Q002', 'Q005', 'Q006', 'Q024', 'Q025',
    
    # Redação
    'TP_STATUS_REDACAO', 'NU_NOTA_COMP1', 'NU_NOTA_COMP2', 
    'NU_NOTA_COMP3', 'NU_NOTA_COMP4', 'NU_NOTA_COMP5'
]
```

### Estratégia de Amostragem
- **Limite**: 50.000 registros (para performance)
- **Método**: Amostragem aleatória estratificada por UF
- **Filtro**: Apenas participantes que fizeram pelo menos uma prova (TP_PRESENCA_* = 1)

### Otimizações
1. Ler apenas as colunas essenciais (35 de 76)
2. Usar `dtype` específico para economizar memória
3. Filtrar dados inválidos (notas nulas, ausentes)
4. Cachear dados processados