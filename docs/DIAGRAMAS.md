# Diagramas do Sistema

Este documento contém todos os diagramas do sistema de otimização de rotas em formato Mermaid (visualizável no GitHub).

---

## 1. Diagrama de Componentes

```mermaid
graph TB
    subgraph "Interface do Usuário"
        UI[Menu Principal]
        TSP_VIEW[TSP View]
        VRP_VIEW[VRP View]
        ANALYZE[Analyze View]
        CHAT[Chat Interface]
    end
    
    subgraph "Camada de Lógica"
        GA[Genetic Algorithm]
        VRP[VRP Solver]
        FITNESS[Fitness Functions]
        HELPERS[Route Helpers]
    end
    
    subgraph "Serviços"
        ANALYZER[Route Analyzer]
        GEMINI[Gemini AI]
        PDF[PDF Generator]
    end
    
    subgraph "Dados"
        LOADERS[Data Loaders]
        CSV[CSV Files]
        JSON[JSON Export]
    end
    
    UI --> TSP_VIEW
    UI --> VRP_VIEW
    UI --> ANALYZE
    
    TSP_VIEW --> GA
    VRP_VIEW --> VRP
    VRP --> GA
    
    GA --> FITNESS
    GA --> HELPERS
    VRP --> FITNESS
    VRP --> HELPERS
    
    TSP_VIEW --> JSON
    VRP_VIEW --> JSON
    
    ANALYZE --> ANALYZER
    ANALYZE --> CHAT
    ANALYZER --> GEMINI
    ANALYZER --> PDF
    
    LOADERS --> CSV
    TSP_VIEW --> LOADERS
    VRP_VIEW --> LOADERS
    ANALYZER --> JSON
    
    style UI fill:#e1f5fe
    style TSP_VIEW fill:#e1f5fe
    style VRP_VIEW fill:#e1f5fe
    style GA fill:#fff9c4
    style VRP fill:#fff9c4
    style ANALYZER fill:#f3e5f5
    style GEMINI fill:#f3e5f5
```

---

## 2. Fluxo Principal do Sistema

```mermaid
flowchart TD
    START([Iniciar Sistema]) --> LOAD[Carregar Dados]
    LOAD --> MENU{Menu Principal}
    
    MENU -->|Analisar| ANALYZE[Análise de Solução]
    MENU -->|Nova Solução| MODE{Escolher Modo}
    MENU -->|Sair| END([Fim])
    
    MODE -->|TSP| GA_CONFIG[Configurar GA]
    MODE -->|VRP| GA_CONFIG
    
    GA_CONFIG --> TSP_MODE{Modo?}
    
    TSP_MODE -->|TSP| TSP_EXEC[Executar TSP]
    TSP_MODE -->|VRP| DEPOT[Selecionar Depósito]
    
    DEPOT --> VRP_EXEC[Executar VRP]
    
    TSP_EXEC --> VISUALIZE[Visualização Tempo Real]
    VRP_EXEC --> VISUALIZE
    
    VISUALIZE --> EXPORT{Exportar?}
    EXPORT -->|Sim - Tecla E| SAVE[Salvar JSON]
    EXPORT -->|Não| CONTINUE{Continuar?}
    
    SAVE --> CONTINUE
    CONTINUE -->|Sim| MENU
    CONTINUE -->|Não| END
    
    ANALYZE --> SELECT[Selecionar JSON]
    SELECT --> AI[Análise com IA]
    AI --> REPORT[Gerar Relatório PDF]
    REPORT --> CHAT_OPT{Chat?}
    CHAT_OPT -->|Sim| CHAT[Chat Q&A]
    CHAT_OPT -->|Não| MENU
    CHAT --> MENU
    
    style START fill:#4caf50
    style END fill:#f44336
    style MENU fill:#2196f3
    style TSP_EXEC fill:#ff9800
    style VRP_EXEC fill:#ff9800
    style AI fill:#9c27b0
```

---

## 3. Fluxo do Algoritmo Genético (TSP)

```mermaid
flowchart TD
    START([Iniciar AG]) --> INIT[Gerar População Inicial]
    INIT --> SIZE[n rotas aleatórias]
    SIZE --> GEN_LOOP{Geração < Max?}
    
    GEN_LOOP -->|Sim| EVAL[Avaliar Fitness de Todos]
    GEN_LOOP -->|Não| BEST[Retornar Melhor]
    
    EVAL --> SORT[Ordenar por Fitness]
    SORT --> ELITE[Manter Elite - 20%]
    
    ELITE --> NEW_POP[Criar Nova População]
    
    NEW_POP --> SELECT[Selecionar Pais]
    SELECT --> CROSS[Crossover]
    CROSS --> MUTATE[Mutação]
    MUTATE --> ADD[Adicionar Filho]
    
    ADD --> FULL{População Completa?}
    FULL -->|Não| SELECT
    FULL -->|Sim| INCREMENT[Geração++]
    
    INCREMENT --> UPDATE[Atualizar Visualização]
    UPDATE --> GEN_LOOP
    
    BEST --> END([Fim])
    
    style START fill:#4caf50
    style END fill:#4caf50
    style EVAL fill:#ff9800
    style SELECT fill:#2196f3
    style CROSS fill:#9c27b0
    style MUTATE fill:#e91e63
```

---

## 4. Função Fitness

```mermaid
flowchart LR
    ROUTE[Rota] --> CALC_DIST[Calcular Distância]
    ROUTE --> CALC_WEIGHT[Calcular Peso]
    ROUTE --> CALC_PRIOR[Calcular Prioridade]
    
    CALC_DIST --> DIST[Distância Total]
    CALC_WEIGHT --> WEIGHT[Peso Total]
    CALC_PRIOR --> PRIOR[Penalidade Prioridade]
    
    WEIGHT --> CHECK_CAP{Peso > Capacidade?}
    CHECK_CAP -->|Sim| PEN_CAP[+ 10000 * excesso]
    CHECK_CAP -->|Não| NO_PEN_CAP[+ 0]
    
    DIST --> CHECK_DIST{Dist > Autonomia?}
    CHECK_DIST -->|Sim| PEN_DIST[+ 10000 * excesso]
    CHECK_DIST -->|Não| NO_PEN_DIST[+ 0]
    
    DIST --> FITNESS[FITNESS]
    PRIOR --> FITNESS
    PEN_CAP --> FITNESS
    NO_PEN_CAP --> FITNESS
    PEN_DIST --> FITNESS
    NO_PEN_DIST --> FITNESS
    
    FITNESS --> RETURN([Retornar Fitness])
    
    style ROUTE fill:#e3f2fd
    style FITNESS fill:#fff9c4
    style PEN_CAP fill:#ffcdd2
    style PEN_DIST fill:#ffcdd2
    style RETURN fill:#c8e6c9
```

---

## 5. Fluxo VRP Solver

```mermaid
flowchart TD
    START([Iniciar VRP]) --> INIT[Criar População Inicial]
    
    INIT --> DIST1[1/3: 1 veículo grande]
    INIT --> DIST2[1/3: 2 veículos médios]
    INIT --> DIST3[1/3: Aleatório]
    
    DIST1 --> LOOP{Geração < Max?}
    DIST2 --> LOOP
    DIST3 --> LOOP
    
    LOOP -->|Sim| CALC_STATS[Calcular Stats de Rotas]
    LOOP -->|Não| OPTIMIZE[Otimização Final]
    
    CALC_STATS --> FITNESS[Calcular Fitness VRP]
    
    FITNESS --> CHECK{Tem Violações?}
    CHECK -->|Sim| HIGH_FIT[Fitness Alto - Penalidades²]
    CHECK -->|Não| NORMAL_FIT[Fitness Normal]
    
    HIGH_FIT --> SELECT[Seleção por Torneio]
    NORMAL_FIT --> SELECT
    
    SELECT --> CROSSOVER[Crossover Adaptativo]
    CROSSOVER --> MUTATE[Mutação Corretiva]
    
    MUTATE --> FIX{Ainda Inviável?}
    FIX -->|Sim| SPLIT[Dividir Rotas]
    FIX -->|Não| NEXT[Próxima Geração]
    
    SPLIT --> MOVE[Mover Cidades Pesadas]
    MOVE --> NEXT
    
    NEXT --> UPDATE[Atualizar Melhor]
    UPDATE --> LOOP
    
    OPTIMIZE --> FORCE{Viável?}
    FORCE -->|Não| FORCE_FIX[Force Feasibility]
    FORCE -->|Sim| ORDER[Ordenar por Prioridade]
    
    FORCE_FIX --> ORDER
    ORDER --> REMOVE[Remover Rotas Vazias]
    REMOVE --> END([Retornar Solução])
    
    style START fill:#4caf50
    style END fill:#4caf50
    style CHECK fill:#ff9800
    style HIGH_FIT fill:#f44336
    style FORCE_FIX fill:#e91e63
```

---

## 6. Diagrama de Sequência - Análise com IA

```mermaid
sequenceDiagram
    actor User
    participant View as Analyze View
    participant Analyzer as Route Analyzer
    participant Gemini as Gemini AI
    participant PDF as PDF Generator
    
    User->>View: Escolhe "Analisar"
    View->>View: Solicita arquivo JSON
    User->>View: Seleciona arquivo
    
    View->>Analyzer: load_solution(json_path)
    Analyzer->>Analyzer: Parse JSON
    Analyzer-->>View: Solução carregada
    
    View->>Analyzer: create_text_chunks()
    Analyzer->>Analyzer: Divide em chunks
    Analyzer-->>View: Chunks criados
    
    View->>Analyzer: generate_embeddings(chunks)
    loop Para cada chunk
        Analyzer->>Gemini: embed_content(chunk)
        Gemini-->>Analyzer: embedding
    end
    Analyzer-->>View: DataFrame com embeddings
    
    View->>Analyzer: generate_analysis(df)
    loop Para cada query (6x)
        Analyzer->>Analyzer: find_relevant_context(query)
        Analyzer->>Gemini: generate_content(prompt)
        Gemini-->>Analyzer: Análise em texto
    end
    Analyzer-->>View: Análises completas
    
    View->>Analyzer: create_visualizations()
    Analyzer->>Analyzer: Matplotlib gera gráficos
    Analyzer-->>View: Arquivos PNG
    
    View->>Analyzer: generate_pdf_report()
    Analyzer->>PDF: Criar documento
    PDF->>PDF: Adicionar análises
    PDF->>PDF: Inserir gráficos
    PDF-->>Analyzer: PDF gerado
    Analyzer-->>View: Caminho do PDF
    
    View-->>User: Relatório pronto!
    
    alt Chat Q&A
        User->>View: Faz pergunta
        View->>Analyzer: find_relevant_context(pergunta)
        Analyzer-->>View: Contexto relevante
        View->>Gemini: generate_content(prompt + contexto)
        Gemini-->>View: Resposta
        View-->>User: Mostra resposta
    end
```

---

## 7. Estrutura de Dados - JSON Export

```mermaid
classDiagram
    class SolutionJSON {
        +metadata: Metadata
        +constraints: Constraints
        +solution: Solution
        +analysis: Analysis
        +llm_instructions: Instructions
    }
    
    class Metadata {
        +export_timestamp: string
        +mode: TSP|VRP
        +description: string
        +algorithm: string
        +total_cities: int
    }
    
    class Constraints {
        +vehicles_available: Vehicle[]
        +selected_vehicle: Vehicle
        +depot_city: string
    }
    
    class Solution {
        +route: CityInfo[]
        +routes: RouteInfo[]
        +total_distance_km: float
        +total_weight_kg: float
        +total_cost: float
    }
    
    class CityInfo {
        +sequence: int
        +city: string
        +coordinates: tuple
        +deliveries: Delivery[]
    }
    
    class Delivery {
        +id: int
        +medicine: string
        +quantity: int
        +weight: float
        +priority: int
        +priority_label: string
    }
    
    class RouteInfo {
        +route_id: int
        +vehicle: Vehicle
        +route_details: CityInfo[]
        +metrics: Metrics
        +feasibility: Feasibility
    }
    
    SolutionJSON *-- Metadata
    SolutionJSON *-- Constraints
    SolutionJSON *-- Solution
    Solution *-- CityInfo
    Solution *-- RouteInfo
    CityInfo *-- Delivery
    RouteInfo *-- CityInfo
```

---

## 8. Diagrama de Estados - Interface

```mermaid
stateDiagram-v2
    [*] --> MenuInicial
    
    MenuInicial --> Analisar: Escolhe "A"
    MenuInicial --> NovoSolver: Escolhe "N"
    MenuInicial --> [*]: ESC/Sair
    
    Analisar --> SelecionarJSON
    SelecionarJSON --> ProcessandoIA: JSON válido
    SelecionarJSON --> MenuInicial: Voltar
    
    ProcessandoIA --> RelatórioGerado
    RelatórioGerado --> ChatQA: Escolhe Chat
    RelatórioGerado --> MenuInicial: Voltar
    ChatQA --> MenuInicial: ESC
    
    NovoSolver --> SelecionarModo
    SelecionarModo --> ConfigurarGA: TSP/VRP escolhido
    SelecionarModo --> MenuInicial: Voltar
    
    ConfigurarGA --> SelecionarDepósito: Se VRP
    ConfigurarGA --> ExecutandoTSP: Se TSP
    SelecionarDepósito --> ExecutandoVRP
    
    ExecutandoTSP --> VisualizandoTSP
    ExecutandoVRP --> VisualizandoVRP
    
    VisualizandoTSP --> VisualizandoTSP: Tecla G/L/T/C
    VisualizandoTSP --> ExportandoJSON: Tecla E
    VisualizandoTSP --> MenuInicial: Tecla Q
    
    VisualizandoVRP --> VisualizandoVRP: Tecla G/L/V/D/C
    VisualizandoVRP --> RecalculandoVRP: Tecla R
    VisualizandoVRP --> ExportandoJSON: Tecla E
    VisualizandoVRP --> MenuInicial: Tecla Q
    
    RecalculandoVRP --> VisualizandoVRP
    
    ExportandoJSON --> VisualizandoTSP: TSP
    ExportandoJSON --> VisualizandoVRP: VRP
```

---

## 9. Pipeline de Otimização VRP

```mermaid
graph LR
    subgraph "Entrada"
        CITIES[Cidades]
        VEHICLES[Veículos]
        DELIVERIES[Entregas]
        DEPOT[Depósito]
    end
    
    subgraph "Inicialização"
        POP1[Pop: 1 veículo]
        POP2[Pop: 2 veículos]
        POP3[Pop: Aleatório]
    end
    
    subgraph "Evolução"
        EVAL[Avaliar Fitness]
        SEL[Selecionar]
        CROSS[Cruzar]
        MUT[Mutar]
    end
    
    subgraph "Correção"
        CHECK[Verificar Viabilidade]
        SPLIT[Dividir Rotas]
        MOVE[Mover Cidades]
        FORCE[Force Feasibility]
    end
    
    subgraph "Saída"
        VALID[Solução Viável]
        ROUTES[Rotas Otimizadas]
        JSON[Export JSON]
    end
    
    CITIES --> POP1
    VEHICLES --> POP1
    DELIVERIES --> POP1
    DEPOT --> POP1
    
    CITIES --> POP2
    VEHICLES --> POP2
    DELIVERIES --> POP2
    
    CITIES --> POP3
    VEHICLES --> POP3
    DELIVERIES --> POP3
    
    POP1 --> EVAL
    POP2 --> EVAL
    POP3 --> EVAL
    
    EVAL --> SEL
    SEL --> CROSS
    CROSS --> MUT
    MUT --> CHECK
    
    CHECK -->|Inviável| SPLIT
    CHECK -->|Viável| VALID
    
    SPLIT --> MOVE
    MOVE --> FORCE
    FORCE --> VALID
    
    VALID --> ROUTES
    ROUTES --> JSON
```

---

## 10. Interação com Gemini AI

```mermaid
flowchart TD
    JSON[Arquivo JSON] --> CHUNKS[Criar Chunks de Texto]
    
    CHUNKS --> CHUNK1[Chunk: Resumo Geral]
    CHUNKS --> CHUNK2[Chunk: Métricas]
    CHUNKS --> CHUNK3[Chunk: Rotas]
    CHUNKS --> CHUNK4[Chunk: Cidades]
    
    CHUNK1 --> EMBED[Gerar Embeddings]
    CHUNK2 --> EMBED
    CHUNK3 --> EMBED
    CHUNK4 --> EMBED
    
    EMBED --> GEMINI1[Gemini Embedding API]
    GEMINI1 --> DF[DataFrame com Embeddings]
    
    DF --> QUERY1[Query: Resumo Executivo]
    DF --> QUERY2[Query: Viabilidade]
    DF --> QUERY3[Query: Prioridades]
    DF --> QUERY4[Query: Custos]
    DF --> QUERY5[Query: Pontos Críticos]
    DF --> QUERY6[Query: Recomendações]
    
    QUERY1 --> SEARCH1[Busca Semântica]
    QUERY2 --> SEARCH2[Busca Semântica]
    QUERY3 --> SEARCH3[Busca Semântica]
    QUERY4 --> SEARCH4[Busca Semântica]
    QUERY5 --> SEARCH5[Busca Semântica]
    QUERY6 --> SEARCH6[Busca Semântica]
    
    SEARCH1 --> CTX1[Top-5 Contextos]
    SEARCH2 --> CTX2[Top-5 Contextos]
    SEARCH3 --> CTX3[Top-5 Contextos]
    SEARCH4 --> CTX4[Top-5 Contextos]
    SEARCH5 --> CTX5[Top-5 Contextos]
    SEARCH6 --> CTX6[Top-5 Contextos]
    
    CTX1 --> PROMPT1[Montar Prompt]
    CTX2 --> PROMPT2[Montar Prompt]
    CTX3 --> PROMPT3[Montar Prompt]
    CTX4 --> PROMPT4[Montar Prompt]
    CTX5 --> PROMPT5[Montar Prompt]
    CTX6 --> PROMPT6[Montar Prompt]
    
    PROMPT1 --> GEMINI2[Gemini Generation API]
    PROMPT2 --> GEMINI2
    PROMPT3 --> GEMINI2
    PROMPT4 --> GEMINI2
    PROMPT5 --> GEMINI2
    PROMPT6 --> GEMINI2
    
    GEMINI2 --> ANALYSIS[6 Análises Completas]
    ANALYSIS --> VIZ[Criar Visualizações]
    VIZ --> PDF[Gerar PDF]
    
    PDF --> REPORT[Relatório Final]
    
    style JSON fill:#e3f2fd
    style GEMINI1 fill:#f3e5f5
    style GEMINI2 fill:#f3e5f5
    style REPORT fill:#c8e6c9
```

---

**Versão**: 1.0  
**Última atualização**: 2026-01-14
