# Documentação Detalhada dos Componentes

Este documento detalha cada componente do sistema, suas responsabilidades, interfaces e dependências.

---

## 1. Camada de Dados

### 1.1 Data Loaders

#### delivery_loader.py
**Responsabilidade**: Carrega e estrutura dados de entregas

**Estrutura de Dados**:
```python
@dataclass
class Delivery:
    id: int                    # Identificador único
    medicine_name: str         # Nome do medicamento
    quantity: int              # Quantidade de unidades
    total_weight: float        # Peso total em kg
    city: str                  # Cidade de destino
    location_name: str         # Local específico (hospital, clínica)
    priority: int              # 0=alta, 1=média, 2=baixa
```

**Fonte de Dados**: `data_files/deliveries.csv`

**Validações**:
- Priority deve ser 0, 1 ou 2
- Weight deve ser > 0
- City deve existir no mapa

---

#### vehicle_loader.py
**Responsabilidade**: Carrega e gerencia frota de veículos

**Estrutura de Dados**:
```python
@dataclass
class Vehicle:
    vehicle_id: str            # Identificador (V1, V2, ...)
    max_load: float            # Capacidade de carga (kg)
    max_distance: float        # Autonomia (km)
    type: str                  # Tipo (van, caminhao, ...)
    max_weight: float          # Peso máximo (kg)
    cost_per_km: float         # Custo por km (R$)
    name: str                  # Nome descritivo
```

**Fonte de Dados**: `data_files/veiculos.csv`

**Funcionalidades**:
- Ordenação por capacidade
- Filtro por tipo
- Seleção do veículo adequado para uma rota

---

#### city_loader.py
**Responsabilidade**: Carrega cidades e distâncias

**Estruturas**:
```python
cities: List[str]                           # Lista de cidades
distance_lookup: Dict[Tuple[str,str], float] # Distâncias (km)
city_latlng: Dict[str, Tuple[float,float]]  # Coordenadas geográficas
```

**Fontes de Dados**:
- `cidades_sp.tsv` - Distâncias reais entre cidades
- `worldcities.csv` - Coordenadas lat/lng
- `geojs-35-mun.json` - GeoJSON para mapa

**Processamento**:
- Validação de simetria (dist A→B = dist B→A)
- Conversão lat/lng para coordenadas Pygame
- Criação de lookup table para performance

---

### 1.2 Data Structures

**coord_to_city**: Mapeia coordenadas Pygame para nomes de cidades
```python
{(100, 100): "São Paulo", (150, 120): "Campinas", ...}
```

**deliveries_by_city**: Agrupa entregas por cidade
```python
{"São Paulo": [delivery1, delivery2], "Campinas": [delivery3], ...}
```

---

## 2. Camada de Lógica de Negócio

### 2.1 Genetic Algorithm (genetic_algorithm.py)

#### Funções de População

**generate_random_population()**
```python
def generate_random_population(cities: List[Coord], size: int) -> Population
```
- Gera `size` permutações aleatórias de cidades
- Garante que todas cidades aparecem em cada rota
- Retorna lista de rotas (indivíduos)

---

#### Funções de Fitness

**calculate_fitness()**
```python
def calculate_fitness(
    route: Route,
    coord_to_city: Dict,
    deliveries_by_city: Dict,
    vehicles: List[Vehicle],
    distance_lookup: Dict,
    priority_weight: float = 20
) -> float
```

**Componentes do Fitness**:
1. **Distância base**: Soma de distâncias entre cidades consecutivas
2. **Penalidade de prioridade**: 
   - P0 no início: penalidade baixa
   - P0 no final: penalidade alta (position * weight * 1000)
   - P1, P2: penalidades menores
3. **Penalidade de peso**: 
   - Se peso > capacidade: +10,000 * excesso
4. **Penalidade de distância**: 
   - Se distância > autonomia: +10,000 * excesso

**Fórmula**:
```
fitness = distância_total 
        + Σ(priority_penalty[cidade_i] * posição_i * weight)
        + (peso_excedente > 0 ? 10000 * peso_excedente : 0)
        + (dist_excedente > 0 ? 10000 * dist_excedente : 0)
```

---

**calculate_priority_penalty()**
```python
def calculate_priority_penalty(route, coord_to_city, deliveries_by_city) -> float
```
- Penaliza entregas de alta prioridade que aparecem tarde na rota
- Usa posição normalizada (0.0 a 1.0)
- Pesos: P0=1000, P1=300, P2=50

---

#### Operadores de Crossover

**crossover_ox() - Order Crossover**
```python
def crossover_ox(parent1: Route, parent2: Route) -> Route
```
1. Seleciona segmento aleatório do parent1
2. Copia para child na mesma posição
3. Preenche restante com genes do parent2 em ordem
4. **Preserva ordem relativa** - bom para prioridades

**Exemplo**:
```
Parent1: [A, B, C, D, E, F]
Parent2: [D, F, B, E, A, C]
Segment: [C, D, E] (pos 2-4)
Child:   [F, B, C, D, E, A]
```

---

**crossover_pmx() - Partially Mapped Crossover**
```python
def crossover_pmx(parent1: Route, parent2: Route) -> Route
```
1. Seleciona segmento e cria mapeamento
2. Usa mapeamento para resolver conflitos
3. **Preserva relações entre genes**

---

**crossover_cx() - Cycle Crossover**
```python
def crossover_cx(parent1: Route, parent2: Route) -> Route
```
1. Identifica ciclos entre pais
2. Alterna pais a cada ciclo
3. **Preserva posições absolutas**

---

#### Operadores de Mutação

**mutate_swap()**
```python
def mutate_swap(individual: Route, probability: float) -> Route
```
- Troca duas posições aleatórias
- Taxa controlada por probabilidade
- Simples e eficaz para ajustes locais

---

**mutate_inversion()**
```python
def mutate_inversion(individual: Route, probability: float) -> Route
```
- Inverte segmento da rota
- Resolve cruzamentos
- Mantém adjacências locais

---

**mutate_scramble()**
```python
def mutate_scramble(individual: Route, probability: float) -> Route
```
- Embaralha segmento aleatório
- Alta exploração
- Pode ser disruptivo

---

#### Operadores de Seleção

**selection_tournament()**
```python
def selection_tournament(population, fitness, k=3) -> Tuple[Route, Route]
```
- Seleciona k indivíduos aleatórios
- Retorna os 2 melhores
- Pressão seletiva ajustável (k)

---

**selection_roulette()**
```python
def selection_roulette(population, fitness) -> Tuple[Route, Route]
```
- Probabilidade proporcional ao fitness invertido
- Todos têm chance
- Sensível a outliers

---

**selection_rank()**
```python
def selection_rank(population, fitness) -> Tuple[Route, Route]
```
- Baseado em ranking, não fitness absoluto
- Pressão constante
- Evita convergência prematura

---

### 2.2 VRP Solver (vrp_solver.py)

#### Classe VRPRoute

```python
@dataclass
class VRPRoute:
    vehicle: Vehicle              # Veículo atribuído
    route: List[Coord]            # Sequência de cidades
    depot_coord: Optional[Coord]  # Depósito (se houver)
    
    # Métricas calculadas
    total_distance: float = 0.0
    total_weight: float = 0.0
    total_cost: float = 0.0
    max_priority: int = 2
    avg_priority: float = 2.0
    cities: Set[str] = field(default_factory=set)
    priority_score: float = 0.0
    
    # Violações
    weight_violation: float = 0.0
    distance_violation: float = 0.0
    is_feasible: bool = True
```

**Método calculate_stats()**:
- Calcula todas métricas da rota
- Verifica violações de restrições
- Atualiza is_feasible

---

#### Função calculate_vrp_fitness()

```python
def calculate_vrp_fitness(
    solution: List[VRPRoute],
    coord_to_city: Dict,
    deliveries_by_city: Dict,
    distance_lookup: Dict,
    all_cities_coords: Set,
    options: VRPOptions,
    generation: int = 0,
    max_generations: int = 200
) -> float
```

**Penalidades**:
1. **Veículo duplicado**: 1,000,000 (bloqueio total)
2. **Violação de peso**: 200,000 * (excesso²)
3. **Violação de distância**: 200,000 * (excesso²)
4. **Cidade não coberta**: 50,000 por cidade
5. **Múltiplos veículos**: 800 por veículo (preferência por menos)

**Estratégia**:
- Se inviável: penalidades massivas
- Se viável: otimizar custo + prioridades

---

#### Adaptive Crossover

```python
def adaptive_crossover(parent_a, parent_b, depot_coord, options, generation, max_gen)
```
- Herda veículos de ambos pais
- 50% chance de herdar atribuição cidade→veículo de cada pai
- Garante que todas cidades são cobertas

---

#### Feasibility Mutation

```python
def feasibility_mutation(solution, depot_coord, options, generation, ...)
```

**Operações**:
1. **Dividir rotas sobrecarregadas** (split_route)
2. **Mover cidades pesadas** (move_city)
3. **Trocar entre rotas** (swap_between_routes)
4. **Trocar dentro da rota** (swap_within_route) - para prioridades
5. **Inverter segmento** (reverse_segment)

**Taxa adaptativa**: Aumenta se houver violações

---

#### Force Feasibility

```python
def force_feasibility(solution, vehicles, depot, coord_to_city, ...)
```
- Algoritmo First-Fit
- Redistribui cidades respeitando capacidades
- Usa veículos por ordem de capacidade (maior primeiro)
- Garante viabilidade ou falha explicitamente

---

### 2.3 Route Helpers (route_helpers.py)

**calculate_route_weight()**
```python
def calculate_route_weight(route, coord_to_city, deliveries_by_city) -> float
```
- Soma pesos de todas entregas na rota
- Retorna peso total em kg

---

**calculate_route_distance()**
```python
def calculate_route_distance(route, coord_to_city, distance_lookup) -> float
```
- Usa distâncias reais (não euclidianas)
- Lookup em tabela pré-calculada
- Retorna distância total em km

---

**select_vehicle()**
```python
def select_vehicle(weight, distance, vehicles) -> Optional[Vehicle]
```
- Encontra menor veículo que atende restrições
- Prefere eficiência (menor = mais barato)
- Retorna None se nenhum atender

---

## 3. Camada de Serviços

### 3.1 Route Analyzer (route_analyzer.py)

#### Classe RouteAnalyzer

**Inicialização**:
```python
def __init__(self, api_key: str, progress_callback: Optional[Callable] = None)
```
- Configura Gemini AI
- Define modelos (embedding + generation)
- Inicializa cache de embeddings

---

**load_solution()**:
```python
def load_solution(self, json_path: str) -> Dict
```
- Parse JSON exportado
- Valida estrutura
- Armazena em self.solution_data

---

**create_text_chunks()**:
```python
def create_text_chunks(self) -> List[Dict[str, str]]
```
- Divide solução em chunks semânticos
- Chunk 1: Resumo geral
- Chunk 2: Métricas principais
- Chunks 3+: Detalhes por cidade/rota
- Retorna lista de {"title": str, "text": str}

---

**generate_embeddings()**:
```python
def generate_embeddings(self, chunks: List[Dict]) -> pd.DataFrame
```
- Gera embedding para cada chunk
- Usa Gemini Embedding Model
- Cache para evitar reprocessamento
- Retorna DataFrame com coluna 'Embeddings'

---

**find_relevant_context()**:
```python
def find_relevant_context(self, query: str, df: pd.DataFrame, top_k: int = 5) -> str
```
- Gera embedding da query
- Calcula produto escalar com todos chunks
- Retorna top-k contextos mais relevantes

---

**generate_analysis()**:
```python
def generate_analysis(self, df: pd.DataFrame) -> Dict[str, str]
```

**6 Análises geradas**:
1. **resumo_executivo**: Visão geral da solução
2. **analise_viabilidade**: Restrições atendidas?
3. **distribuicao_prioridades**: Como prioridades estão distribuídas
4. **eficiencia_custos**: Análise custo-benefício
5. **pontos_criticos**: Problemas e gargalos
6. **recomendacoes**: Sugestões de melhoria

Para cada:
- Busca contexto relevante
- Monta prompt com contexto + JSON completo
- Gemini gera análise
- Retorna texto estruturado

---

**create_visualizations()**:
```python
def create_visualizations(self) -> Dict[str, str]
```

**TSP (4 gráficos)**:
1. Distribuição de prioridades (pizza)
2. Peso por cidade (barras)
3. Sequência e prioridades (linha)
4. Utilização do veículo (gauge)

**VRP (6 gráficos)**:
1. Distribuição de prioridades (pizza)
2. Custo por rota (barras)
3. Distância por rota (barras)
4. Peso por rota (barras)
5. Utilização de veículos (barras)
6. Viabilidade das rotas (status)

Retorna: {"grafico_1": "path/to/image.png", ...}

---

**generate_pdf_report()**:
```python
def generate_pdf_report(self, analyses: Dict, viz_files: Dict, output_path: str = None) -> str
```
- ReportLab para geração
- Formatação profissional
- Seções para cada análise
- Inserção de gráficos
- Salva em reports/

---

## 4. Camada de Apresentação

### 4.1 Views (views/)

#### menu_inicial.py
**show_analyze_menu()**
- Menu principal com 3 opções
- Retorna: "analyze", "open_report", "skip"

---

#### mode_selection.py
**show_mode_selection()**
- Escolha entre TSP e VRP
- Retorna: "tsp", "vrp", "back"

---

#### ga_menu.py
**show_ga_menu()**
- Configuração de mutação, seleção, crossover
- Retorna: dict com funções selecionadas
```python
{
    "mutation_fn": mutate_swap,
    "selection_fn": selection_tournament,
    "crossover_fn": crossover_ox
}
```

---

#### tsp_view.py
**run_tsp_mode()**
- Loop principal do TSP
- Visualização em tempo real
- Controles de teclado
- Export JSON

---

#### vrp_view.py
**run_vrp_mode()**
- Loop principal do VRP
- Visualização de múltiplas rotas
- Painel de detalhes
- Recálculo dinâmico

---

#### analyze_view.py
**run_analyze_mode()**
- Fluxo de análise completo
- Escolha entre relatório ou chat
- Integração com RouteAnalyzer
- Interface de chat Q&A

---

### 4.2 UI Resources (ui_resources/)

#### ui_renderer.py
Funções de renderização:
- `render_evolution_plots()` - Gráficos de fitness
- `render_route_list()` - Lista de cidades
- `render_vehicle_info()` - Informações do veículo
- `render_footer()` - Rodapé com métricas
- `render_map_with_routes()` - Mapa com rotas

---

#### vrp_details_renderer.py
**render_vrp_details_panel()**
- Painel lateral com detalhes
- Lista todas rotas
- Mostra violações
- Estatísticas por rota

---

## 5. Infraestrutura

### 5.1 Solution Exporter (infra/solution_exporter.py)

**export_solution_to_json()**
```python
def export_solution_to_json(
    data: Dict,
    solution: Union[Route, List[VRPRoute]],
    mode: str,
    depot_city: Optional[str] = None,
    export_path: str = "best_solution.json"
) -> bool
```

**Estrutura do JSON**:
```json
{
  "metadata": {...},
  "constraints": {...},
  "solution": {...},
  "analysis": {...},
  "llm_instructions": {...}
}
```

**LLM Instructions**:
- Task description
- Sections to include
- Key points to highlight
- Output format
- Target audience

---

## 6. Configuração (config/)

### ga_config.py
Mapeamento de operadores GA

### ui_layout.py
Dimensões e posições de UI

### ui_theme.py
Cores e estilos

---

## Dependências entre Componentes

```
main.py
├─→ views/
│   ├─→ ui_resources/
│   ├─→ genetic_algorithm.py
│   ├─→ vrp_solver.py
│   ├─→ route_helpers.py
│   └─→ infra/solution_exporter.py
│
├─→ loader_resources/
│   └─→ data_files/
│
└─→ route_analyzer.py
    ├─→ google.generativeai
    ├─→ reportlab
    └─→ matplotlib
```

---

**Versão**: 1.0  
**Última atualização**: 2026-01-14
