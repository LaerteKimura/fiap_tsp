# Sistema de Otimização de Rotas com Algoritmos Genéticos

Sistema completo de otimização de rotas de entrega utilizando **Algoritmos Genéticos** para resolver problemas de **TSP (Traveling Salesman Problem)** e **VRP (Vehicle Routing Problem)**, com análise avançada usando **Google Gemini AI** e interface de chat interativa.
O sitema comtempla apenas o Estado de São Paulo - Como exemplo academico

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

---

## Índice

- [Características](#-características)
- [Instalação](#-instalação)
- [Início Rápido](#-início-rápido)
- [Menu Principal e Navegação](#-menu-principal-e-navegação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Algoritmos Genéticos](#-algoritmos-genéticos)
  - [Operadores de Mutação](#operadores-de-mutação)
  - [Métodos de Seleção](#métodos-de-seleção)
  - [Tipos de Crossover](#tipos-de-crossover)
- [Modos de Operação](#-modos-de-operação)
  - [TSP - Problema do Caixeiro Viajante](#tsp---problema-do-caixeiro-viajante)
  - [VRP - Roteamento de Veículos](#vrp---roteamento-de-veículos)
- [Configuração de Parâmetros](#-configuração-de-parâmetros)
  - [Parâmetros do Algoritmo Genético](#parâmetros-do-algoritmo-genético)
  - [Parâmetros do VRP](#parâmetros-do-vrp)
  - [Como Alterar Parâmetros](#como-alterar-parâmetros)
- [Análise com IA e Chat Interativo](#-análise-com-ia-e-chat-interativo)
  - [Uso Acadêmico da LLM](#uso-acadêmico-da-llm)
  - [Configuração da API](#configuração-da-api)
  - [Análise de Soluções Existentes](#análise-de-soluções-existentes)
  - [Chat Interativo com LLM](#chat-interativo-com-llm)
  - [Geração de Relatórios PDF](#geração-de-relatórios-pdf)
- [Controles e Interface](#-controles-e-interface)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Arquivos de Dados](#-arquivos-de-dados)
- [Troubleshooting](#-troubleshooting)

---

## Características

- **Dois modos de otimização**: TSP (rota única) e VRP (múltiplas rotas)
- **Algoritmos Genéticos customizáveis**: 3 mutações, 3 seleções, 3 crossovers
- **Visualização em tempo real**: Mapa de São Paulo com rotas animadas
- **Sistema de prioridades**: Entregas alta (P0), média (P1) e baixa (P2)
- **Restrições realistas**: Capacidade de peso e autonomia de veículos
- **Análise com IA**: Relatórios executivos usando Google Gemini AI
- **Chat interativo**: Interface de conversação com LLM usando embeddings semânticos
- **Exportação de dados**: JSON estruturado e relatórios PDF profissionais
- **Interface interativa**: Controles em tempo real e gráficos de evolução

---

## Instalação

### 1. Requisitos do Sistema

- Python 3.8 ou superior
- pip (gerenciador de pacotes)
- 2GB de RAM disponível
- Sistema operacional: Windows, Linux ou macOS

### 2. Clonar ou Baixar o Projeto

```bash
git clone https://github.com/LaerteKimura/fiap_tsp.git
cd tsp
```

### 3. Criar Ambiente Virtual (Recomendado)

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 4. Instalar Dependências

```bash
# Dependências de produção
pip install -r requirements.txt

# Dependências de desenvolvimento (incluindo testes)
pip install -r requirements-dev.txt
```

**Dependências principais:**
- `pygame` - Interface gráfica e visualização
- `matplotlib` - Gráficos de evolução
- `numpy` - Operações matemáticas
- `pandas` - Processamento de dados
- `reportlab` - Geração de PDFs
- `google-generativeai` - Análise com IA (opcional)
- `pyperclip` - Suporte a clipboard (opcional)

### 5. Verificar Instalação

```bash
python --version  # Deve mostrar Python 3.8+
pip list          # Verifica pacotes instalados
```

---

## Início Rápido

### Execução Básica

```bash
python main.py
```

### Fluxo Rápido (3 passos)

1. **Escolha a opção no menu inicial**
   - `Analisar solução existente` - Para analisar JSONs exportados
   - `Abrir relatório existente` - Para visualizar PDFs gerados
   - `Criar nova solução` - Para otimizar novas rotas

2. **Configure o algoritmo** (se criando nova solução)
   - Escolha tipo de **Mutação** (Swap, Inversion, Scramble)
   - Escolha método de **Seleção** (Tournament, Roulette, Rank)
   - Escolha tipo de **Crossover** (OX, PMX, CX)

3. **Selecione o problema**
   - **TSP**: Rota única com um veículo
   - **VRP**: Múltiplas rotas com vários veículos

### Exemplo Completo (5 minutos)

```bash
# 1. Iniciar o sistema
python main.py

# 2. Escolher "Criar nova solução"

# 3. Configurar algoritmo (exemplo):
#    - Mutação: Swap
#    - Seleção: Tournament
#    - Crossover: Order (OX)

# 4. Escolher modo VRP

# 5. Selecionar depósito (ou "Sem Depósito")

# 6. Aguardar otimização (1-2 minutos)

# 7. Exportar solução: pressionar tecla "E"

# 8. Analisar: executar novamente e escolher "Analisar solução existente"
```

---

## Menu Principal e Navegação

### Menu Inicial

Ao executar `python main.py`, você verá o menu principal com 4 opções:

1. **Analisar solução existente**
   - Permite analisar soluções JSON exportadas anteriormente
   - Oferece duas opções:
     - **Gerar relatório PDF**: Cria relatório executivo com análise da LLM
     - **Chat com LLM**: Interface interativa para fazer perguntas sobre a solução
   - Requer API Key do Google Gemini (solicitada na primeira execução)

2. **Abrir relatório existente**
   - Lista todos os relatórios PDF gerados anteriormente
   - Permite abrir e visualizar relatórios diretamente no visualizador padrão
   - Não requer API Key

3. **Criar nova solução**
   - Inicia o fluxo de otimização de rotas
   - Passa por:
     - Seleção de modo (TSP ou VRP)
     - Configuração do Algoritmo Genético
     - Seleção de depósito (apenas VRP)
     - Execução da otimização

4. **Sair**
   - Encerra a aplicação

### Navegação entre Menus

- **Setas do teclado** (↑↓): Navegar entre opções
- **Enter**: Confirmar seleção
- **Esc**: Voltar ao menu anterior
- **Mouse**: Clicar para selecionar opções

---

## Estrutura do Projeto

```
tsp/
│
├── main.py                          # Script principal
├── genetic_algorithm.py             # Core do Algoritmo Genético
├── vrp_solver.py                    # Solver VRP
├── route_analyzer.py                # Análise com IA
├── route_helpers.py                 # Funções auxiliares
├── sp_map.py                        # Renderização de mapa
│
├── config/                          # Configurações
│   ├── ga_config.py                # Config AG
│   ├── ui_layout.py                # Layout UI
│   └── ui_theme.py                 # Tema visual
│
├── views/                           # Camada de apresentação
│   ├── menu_inicial.py             # Menu principal
│   ├── mode_selection.py           # Seleção TSP/VRP
│   ├── ga_menu.py                  # Menu AG
│   ├── tsp_view.py                 # Execução TSP
│   ├── vrp_view.py                 # Execução VRP
│   ├── vrp_depot_selection.py      # Seleção de depósito
│   ├── analyze_view.py             # Análise e chat
│   └── open_report_view.py         # Abrir relatórios
│
├── ui_resources/                    # Recursos de UI
│   ├── ui_renderer.py              # Renderização principal
│   ├── draw_functions.py           # Funções de desenho
│   └── vrp_details_renderer.py     # Detalhes VRP
│
├── loader_resources/                # Carregadores de dados
│   ├── data_loader.py              # Loader principal
│   ├── delivery_loader.py          # Entregas
│   ├── vehicle_loader.py           # Veículos
│   └── city_loader.py              # Cidades
│
├── infra/                           # Infraestrutura
│   └── solution_exporter.py        # Export JSON
│
├── data_files/                      # Dados do problema
│   ├── deliveries.csv              # Entregas
│   ├── veiculos.csv                # Veículos
│   ├── cidades_sp.tsv               # Distâncias
│   ├── worldcities.csv             # Coordenadas
│   └── geojs-35-mun.json           # GeoJSON SP
│
├── solutions/                       # Soluções exportadas (JSON)
├── reports/                         # Relatórios PDF gerados
│
├── requirements.txt                 # Dependências produção
├── requirements-dev.txt            # Dependências dev
└── README.md                        # Este arquivo
```

---

## Algoritmos Genéticos

O sistema utiliza **Algoritmos Genéticos** para encontrar soluções ótimas ou próximas do ótimo. Você pode customizar três componentes principais:

### Operadores de Mutação

A **mutação** introduz diversidade genética na população, evitando convergência prematura.

#### 1. **Swap Mutation** (Troca)

**Como funciona:**
- Seleciona duas posições aleatórias na rota
- Troca as cidades nessas posições

**Exemplo:**
```
Antes:  [A, B, C, D, E, F]
Após:   [A, D, C, B, E, F]
        (trocou B e D)
```

**Quando usar:**
- Exploração local eficiente
- Bom para ajustes finos
- Funciona bem com seleção por torneio

**Parâmetros:**
- Taxa de mutação: 0.4 (40% de chance por gene)

---

#### 2. **Inversion Mutation** (Inversão)

**Como funciona:**
- Seleciona um segmento aleatório da rota
- Inverte a ordem das cidades nesse segmento

**Exemplo:**
```
Antes:  [A, B, C, D, E, F]
        (seleciona segmento C-D-E)
Após:   [A, B, E, D, C, F]
        (inverte para E-D-C)
```

**Quando usar:**
- Ótimo para TSP
- Resolve cruzamentos de rotas
- Mantém adjacências locais

**Vantagens:**
- Pode desfazer "nós" na rota
- Preserva boa parte da estrutura
- Menor impacto que Scramble

---

#### 3. **Scramble Mutation** (Embaralhamento)

**Como funciona:**
- Seleciona um segmento aleatório
- Embaralha completamente as cidades desse segmento

**Exemplo:**
```
Antes:  [A, B, C, D, E, F]
        (seleciona C-D-E)
Após:   [A, B, D, E, C, F]
        (embaralha aleatoriamente)
```

**Quando usar:**
- Alta exploração
- Escapar de mínimos locais
- Problemas muito complexos

**Atenção:**
- Pode destruir boas soluções
- Use taxa de mutação menor (0.2-0.3)

---

### Métodos de Seleção

A **seleção** determina quais indivíduos se reproduzem, favorecendo os mais aptos.

#### 1. **Tournament Selection** (Seleção por Torneio)

**Como funciona:**
1. Seleciona K indivíduos aleatoriamente (K=3 padrão)
2. Escolhe os 2 melhores do torneio
3. Estes se tornam pais

**Exemplo:**
```
População: [A:100, B:80, C:120, D:90, E:110]
           (fitness menor é melhor)

Torneio 1: [A:100, D:90, E:110] → Vencedor: D (90)
Torneio 2: [B:80, C:120, E:110] → Vencedor: B (80)

Pais selecionados: D e B
```

**Vantagens:**
- **Simples e eficiente**
- Não precisa ordenar toda população
- Pressão seletiva ajustável (via K)
- Funciona bem com qualquer função fitness

**Quando usar:**
- **Recomendado para iniciantes**
- Problemas de médio porte
- Boa diversidade + elitismo

**Parâmetros:**
- K (tamanho do torneio): 3
- Maior K = mais pressão seletiva

---

#### 2. **Roulette Wheel Selection** (Seleção por Roleta)

**Como funciona:**
1. Inverte fitness (menor fitness = maior chance)
2. Calcula probabilidade proporcional ao fitness
3. Gira a "roleta" para escolher pais

**Exemplo:**
```
População: [A:100, B:80, C:120, D:90]

Fitness invertido:
A: 120-100 = 20
B: 120-80  = 40
C: 120-120 = 0
D: 120-90  = 30
Total: 90

Probabilidades:
A: 20/90 = 22%
B: 40/90 = 44%  ← Maior chance
C: 0/90  = 0%
D: 30/90 = 33%
```

**Vantagens:**
- Seleção proporcional ao fitness
- Todos têm chance (diversidade)
- Intuitivo de entender

**Desvantagens:**
- Pode convergir rápido se houver um super-indivíduo
- Sensível à escala do fitness

**Quando usar:**
- Fitness bem distribuído
- Quer diversidade alta
- População grande (100+)

---

#### 3. **Rank Selection** (Seleção por Ranking)

**Como funciona:**
1. Ordena população por fitness
2. Atribui ranks (1, 2, 3, ...)
3. Seleciona baseado no rank, não no fitness

**Exemplo:**
```
População ordenada:
1. B: 80  → Rank 1 (melhor)
2. D: 90  → Rank 2
3. A: 100 → Rank 3
4. C: 120 → Rank 4 (pior)

Probabilidades baseadas em rank:
Rank 1: 4/10 = 40%
Rank 2: 3/10 = 30%
Rank 3: 2/10 = 20%
Rank 4: 1/10 = 10%
```

**Vantagens:**
- **Não sofre com diferenças extremas de fitness**
- Pressão seletiva constante
- Evita convergência prematura

**Quando usar:**
- Fitness com valores muito diferentes
- Problemas com platôs
- Quer controle fino da pressão seletiva

**Melhor para:**
- VRP com muitas restrições
- Fitness com penalidades grandes

---

### Tipos de Crossover

O **crossover** combina características de dois pais para criar filhos.

#### 1. **Order Crossover (OX)** - Recomendado

**Como funciona:**
1. Seleciona segmento do Pai 1
2. Copia para o filho na mesma posição
3. Preenche o resto com cidades do Pai 2 na ordem

**Exemplo:**
```
Pai 1: [A, B, C, D, E, F, G, H]
Pai 2: [D, G, B, F, A, E, C, H]

Passo 1: Seleciona segmento (posições 3-5)
Filho:  [_, _, C, D, E, _, _, _]

Passo 2: Preenche com Pai 2 (D, G, B, F...)
         Pula C, D, E (já estão)
Filho:  [G, B, C, D, E, F, A, H]
```

**Vantagens:**
- **Preserva ordem relativa**
- Sempre gera soluções válidas
- Melhor para TSP
- Mantém "vizinhanças" boas

**Quando usar:**
- **Primeira escolha para TSP**
- Prioridades importam
- Sequência é crítica

---

#### 2. **Partially Mapped Crossover (PMX)**

**Como funciona:**
1. Seleciona segmento e copia do Pai 1
2. Cria mapeamento entre pais
3. Usa mapeamento para preencher resto

**Exemplo:**
```
Pai 1: [A, B, C, D, E, F, G, H]
Pai 2: [D, G, B, F, A, E, C, H]

Segmento (3-5):
Filho: [_, _, C, D, E, _, _, _]

Mapeamento:
C ↔ B (posição 3)
D ↔ F (posição 4)
E ↔ A (posição 5)

Preenche usando mapeamento:
Filho: [F, G, C, D, E, B, A, H]
```

**Vantagens:**
- Preserva relações entre genes
- Bom para estruturas complexas
- Menos disruptivo que OX

**Quando usar:**
- VRP com múltiplas rotas
- Relações entre cidades importam
- Estrutura hierárquica

---

#### 3. **Cycle Crossover (CX)**

**Como funciona:**
1. Começa com primeira posição
2. Segue ciclos entre pais
3. Alterna pais a cada ciclo

**Exemplo:**
```
Pai 1: [A, B, C, D, E, F, G, H]
Pai 2: [D, G, B, F, A, E, C, H]

Ciclo 1: posição 0
A (Pai1) → D (Pai2 pos0) → D (Pai1 pos3) → F (Pai2 pos3) → F (Pai1 pos5) → E (Pai2 pos5) → E (Pai1 pos4) → A (volta)

Filho: [A, _, _, D, E, F, _, _]

Preenche resto com Pai 2:
Filho: [A, G, B, D, E, F, C, H]
```

**Vantagens:**
- Cada gene vem de um pai específico
- Preserva posições absolutas
- Único em sua abordagem

**Quando usar:**
- Posição absoluta importa
- Problemas com restrições de ordem
- Estruturas circulares

---

### Recomendações de Combinações

| Problema | Mutação | Seleção | Crossover | Por quê |
|----------|---------|---------|-----------|---------|
| **TSP Simples** | Swap | Tournament | OX | Rápido e eficiente |
| **TSP com Prioridades** | Inversion | Tournament | OX | Preserva sequências |
| **VRP Pequeno** | Swap | Tournament | PMX | Balanceado |
| **VRP Grande** | Inversion | Rank | PMX | Controle de pressão |
| **Exploração Alta** | Scramble | Roulette | CX | Máxima diversidade |

---

## Modos de Operação

### TSP - Problema do Caixeiro Viajante

**Objetivo:** Encontrar a menor rota que visita todas as cidades exatamente uma vez.

**Características:**
- Um único veículo
- Uma única rota
- Todas as cidades devem ser visitadas
- Prioridades influenciam a ordem

**Restrições:**
- Peso total ≤ Capacidade do veículo
- Distância total ≤ Autonomia do veículo

**Função Fitness:**
```
fitness = distância_total 
        + penalidade_prioridade 
        + penalidade_peso (se exceder)
        + penalidade_distância (se exceder)
```

**Quando usar TSP:**
- Um único veículo disponível
- Rota pequena/média (até 15 cidades)
- Foco em ordem de visita
- Aprendizado do algoritmo

**Exemplo de Solução TSP:**
```
Veículo: Caminhão Grande (5000kg, 800km)

Rota: São Paulo → Campinas → Piracicaba → 
      São Carlos → Ribeirão Preto → Bauru → 
      Sorocaba → Santos → São Paulo

Distância: 724 km
Peso Total: 4.250 kg
Custo: R$ 2.172,00
Prioridades: 3x P0, 5x P1, 4x P2
```

---

### VRP - Roteamento de Veículos

**Objetivo:** Distribuir as cidades entre múltiplos veículos minimizando custo total.

**Características:**
- Múltiplos veículos
- Múltiplas rotas simultâneas
- Cada cidade visitada uma vez
- Depósito central (opcional)

**Restrições:**
- Cada rota: peso ≤ capacidade do veículo
- Cada rota: distância ≤ autonomia do veículo
- Cada veículo usado no máximo uma vez
- Se há depósito: todas rotas partem/retornam dele
- Se não há depósito: rotas são fechadas (retornam à primeira cidade)

**Função Fitness VRP:**
```
fitness = Σ(custo_rota_i)
        + penalidade_veículos_extras
        + penalidade_violações_capacidade
        + penalidade_prioridades_mal_sequenciadas
        + penalidade_subutilização (peso e distância)
        + PENALIDADE_MASSIVA (se inviável)
```

**Quando usar VRP:**
- Muitas cidades (10+)
- Múltiplos veículos disponíveis
- Necessidade de otimizar frota
- Problema real de logística

**Exemplo de Solução VRP:**
```
Depósito: São Paulo

Rota 1 (Van - 1500kg, 400km):
  São Paulo → Guarulhos → São José dos Campos → 
  Taubaté → São Paulo
  Distância: 312km | Peso: 1.420kg | Custo: R$ 936

Rota 2 (Caminhão Médio - 3000kg, 600km):
  São Paulo → Sorocaba → Campinas → 
  Piracicaba → São Paulo
  Distância: 387km | Peso: 2.850kg | Custo: R$ 1.161

Rota 3 (Caminhão Grande - 5000kg, 800km):
  São Paulo → Santos → Registro → Iguape → 
  Cananéia → São Paulo
  Distância: 542km | Peso: 3.200kg | Custo: R$ 1.626

Custo Total: R$ 3.723
Veículos: 3
Todas rotas viáveis: Sim
```

---

## Configuração de Parâmetros

### Parâmetros do Algoritmo Genético

Arquivo: `config/ga_config.py`

```python
# Tamanho da população
POPULATION_SIZE = 100  # Aumentar para melhor qualidade (50-200)

# Taxa de mutação
MUTATION_RATE = 0.4    # 0.2-0.5 recomendado

# Peso de prioridade
PRIORITY_WEIGHT = 20   # Aumentar para forçar prioridades

# Elitismo: porcentagem da população mantida como elite
ELITE_PERCENTAGE = 0.1  # 10% da população mantida como elite

# Interface
DEFAULT_SHOW_PLOT = True
DEFAULT_SHOW_LIST = True
DEFAULT_SHOW_ATTEMPTS = True
DEFAULT_SHOW_COORDINATES = False
```

**Descrição dos Parâmetros:**

- **`POPULATION_SIZE`**: Número de indivíduos na população
  - Valores menores (50-80): Convergência rápida, menor qualidade
  - Valores médios (100-150): Balanceado (recomendado)
  - Valores maiores (200+): Melhor qualidade, mais lento

- **`MUTATION_RATE`**: Probabilidade de mutação por gene
  - Valores baixos (0.2-0.3): Menos diversidade, convergência rápida
  - Valores médios (0.4): Balanceado (recomendado)
  - Valores altos (0.5+): Alta diversidade, pode não convergir

- **`PRIORITY_WEIGHT`**: Peso da penalidade de prioridades
  - Valores baixos (10-15): Prioridades menos importantes
  - Valores médios (20-30): Balanceado (recomendado)
  - Valores altos (50+): Prioridades muito importantes

- **`ELITE_PERCENTAGE`**: Porcentagem de melhores indivíduos mantidos
  - 0.05 (5%): Menos elitismo, mais exploração
  - 0.1 (10%): Balanceado (recomendado)
  - 0.2 (20%): Mais elitismo, menos exploração

---

### Parâmetros do VRP

Arquivo: `config/ga_config.py` (parâmetros gerais) e `vrp_solver.py` (parâmetros específicos)

#### Parâmetros em `config/ga_config.py`:

```python
# Gerações por rota no VRP
VRP_GENERATIONS_PER_ROUTE = 200  # Aumentar para VRP complexo (100-500)

# Custo fixo por rota (independente do veículo)
VRP_FIXED_COST_PER_ROUTE = 1500  # Custo fixo em R$ adicionado ao custo de cada rota

# Critérios de parada VRP
VRP_MAX_GENERATIONS = 2000  # Máximo de gerações para VRP (evita execução infinita)
VRP_CONVERGENCE_GENERATIONS = 100  # Gerações sem melhoria para considerar convergência
VRP_CONVERGENCE_THRESHOLD = 0.002  # Melhoria mínima para resetar contador de convergência
```

**Descrição dos Parâmetros:**

- **`VRP_GENERATIONS_PER_ROUTE`**: Número de gerações para otimizar cada rota
  - Valores menores (100-150): Rápido, menor qualidade
  - Valores médios (200-300): Balanceado (recomendado)
  - Valores maiores (400-500): Melhor qualidade, muito lento

- **`VRP_FIXED_COST_PER_ROUTE`**: Custo fixo adicionado a cada rota
  - Incentiva usar menos veículos
  - Ajuste conforme seu modelo de negócio

- **`VRP_MAX_GENERATIONS`**: Limite máximo de gerações
  - Evita execução infinita
  - Aumentar apenas se necessário

- **`VRP_CONVERGENCE_GENERATIONS`**: Gerações sem melhoria para parar
  - Valores menores (50-80): Para mais rápido
  - Valores maiores (100-150): Mais tempo para convergir

- **`VRP_CONVERGENCE_THRESHOLD`**: Melhoria mínima para resetar contador
  - Valores menores (0.001): Mais sensível
  - Valores maiores (0.005): Menos sensível

#### Parâmetros em `vrp_solver.py` (classe `VRPOptions`):

```python
class VRPOptions:
    def __init__(self):
        # PENALIDADES para violações
        self.WEIGHTS = {
            'distance': 0.1,                    # Peso da distância
            'priority': 50.0,                   # Peso das prioridades
            'vehicle_count': 800,                # Penalidade por número de veículos
            'vehicle_use': 300,                  # Penalidade por usar veículos extras
            'uncovered_city': 50000,            # Penalidade por cidade não coberta
            'capacity_violation': 100000,        # Penalidade base por violação de capacidade
            'duplicate_vehicle': 1000000,        # Penalidade por usar mesmo veículo duas vezes
            'weight_violation': 200000,         # Penalidade por violação de peso
            'distance_violation': 200000,        # Penalidade por violação de distância
            'underutilization': 500.0,          # Penalidade por subutilização de capacidade (peso)
            'distance_underutilization': 100.0, # Penalidade por subutilização de distância
        }
        
        # Threshold de utilização mínima
        self.MIN_UTILIZATION_THRESHOLD = 0.6  # 60% de utilização mínima de peso
        self.MIN_DISTANCE_UTILIZATION_THRESHOLD = 0.5  # 50% de utilização mínima de distância
        
        # Taxas de mutação específicas do VRP
        self.MUTATION_RATES = {
            'swap_between_routes': 0.4,  # Trocar cidade entre rotas
            'move_city': 0.4,             # Mover cidade para outra rota
            'swap_within_route': 0.5,     # Trocar cidades dentro da mesma rota
            'reverse_segment': 0.3,        # Inverter segmento de rota
            'split_route': 0.2,            # Dividir rota em duas
        }
```

**Descrição dos Pesos (WEIGHTS):**

- **`distance`**: Peso da distância total no fitness
  - Valores menores (0.05-0.1): Distância menos importante
  - Valores maiores (0.2-0.5): Distância mais importante

- **`priority`**: Peso das prioridades
  - Valores menores (30-40): Prioridades menos importantes
  - Valores maiores (50-100): Prioridades muito importantes

- **`vehicle_count`**: Penalidade por cada veículo usado
  - Incentiva usar menos veículos
  - Aumentar para forçar menos veículos

- **`underutilization`**: Penalidade por subutilização de peso
  - Aplicada quando veículo usa menos de 60% da capacidade
  - Incentiva melhor utilização dos veículos

- **`distance_underutilization`**: Penalidade por subutilização de distância
  - Aplicada quando veículo percorre menos de 50% da autonomia
  - Incentiva usar veículos com alcance adequado

**Descrição dos Thresholds:**

- **`MIN_UTILIZATION_THRESHOLD`**: Utilização mínima de peso (0.0-1.0)
  - 0.5 (50%): Mais tolerante
  - 0.6 (60%): Balanceado (recomendado)
  - 0.7 (70%): Mais rigoroso

- **`MIN_DISTANCE_UTILIZATION_THRESHOLD`**: Utilização mínima de distância (0.0-1.0)
  - 0.4 (40%): Mais tolerante
  - 0.5 (50%): Balanceado (recomendado)
  - 0.6 (60%): Mais rigoroso

---

### Como Alterar Parâmetros

#### 1. Parâmetros do Algoritmo Genético

Edite o arquivo `config/ga_config.py`:

```python
# Exemplo: Aumentar população para melhor qualidade
POPULATION_SIZE = 200

# Exemplo: Reduzir taxa de mutação para convergência mais rápida
MUTATION_RATE = 0.3

# Exemplo: Aumentar peso de prioridades
PRIORITY_WEIGHT = 50
```

#### 2. Parâmetros do VRP

**Parâmetros gerais** - Edite `config/ga_config.py`:

```python
# Exemplo: Aumentar gerações por rota
VRP_GENERATIONS_PER_ROUTE = 300

# Exemplo: Aumentar custo fixo para incentivar menos veículos
VRP_FIXED_COST_PER_ROUTE = 2000
```

**Parâmetros específicos** - Edite `vrp_solver.py` (classe `VRPOptions`):

```python
class VRPOptions:
    def __init__(self):
        self.WEIGHTS = {
            # Exemplo: Aumentar penalidade por subutilização
            'underutilization': 1000.0,
            
            # Exemplo: Aumentar threshold de utilização
            # (edite também MIN_UTILIZATION_THRESHOLD)
        }
        
        # Exemplo: Aumentar threshold de utilização mínima
        self.MIN_UTILIZATION_THRESHOLD = 0.7  # 70%
```

#### 3. Ajuste Fino

**Para convergência rápida:**
```python
POPULATION_SIZE = 50
MUTATION_RATE = 0.3
VRP_GENERATIONS_PER_ROUTE = 100
```

**Para qualidade máxima:**
```python
POPULATION_SIZE = 200
MUTATION_RATE = 0.4
VRP_GENERATIONS_PER_ROUTE = 300
```

**Para problemas grandes:**
```python
POPULATION_SIZE = 150
MUTATION_RATE = 0.5
VRP_GENERATIONS_PER_ROUTE = 200
```

---

## Análise com IA e Chat Interativo

O sistema inclui análise avançada usando **Google Gemini AI** com embeddings semânticos e interface de chat interativa.

### Uso Acadêmico da LLM

A integração da LLM (Large Language Model) no sistema foi implementada seguindo princípios acadêmicos de **Recuperação de Informação (Information Retrieval)** e **RAG (Retrieval-Augmented Generation)**:

#### 1. **Embeddings Semânticos**

**Conceito Acadêmico:** Utilização de modelos de embeddings para representação vetorial de texto, permitindo busca semântica ao invés de busca exata por palavras-chave.

**Implementação:**
- **Modelo utilizado**: `models/embedding-001` (Google Gemini)
- **Processo**: 
  1. O JSON da solução é dividido em **chunks de texto** estruturados
  2. Cada chunk recebe um **embedding vetorial** (representação numérica)
  3. Os embeddings são armazenados para busca rápida

**Chunks criados:**
- Resumo Geral (metadados)
- Estatísticas Agregadas (métricas principais)
- Detalhes de cada rota (cidades, entregas, métricas)
- Informações de veículos utilizados

**Benefício Acadêmico:** Demonstra aplicação prática de **NLP (Natural Language Processing)** e **Representação Distribuída de Texto**.

#### 2. **Busca por Similaridade Semântica**

**Conceito Acadêmico:** Utilização de **similaridade de cosseno** para encontrar contexto relevante baseado no significado, não apenas em palavras-chave.

**Implementação:**
- Quando o usuário faz uma pergunta, ela é convertida em embedding
- O sistema calcula a **similaridade de cosseno** entre o embedding da pergunta e todos os chunks
- Os **top-K chunks mais similares** (K=7) são selecionados como contexto

**Benefício Acadêmico:** Demonstra aplicação de **Métricas de Similaridade** e **Information Retrieval**.

#### 3. **RAG (Retrieval-Augmented Generation)**

**Conceito Acadêmico:** Técnica que combina recuperação de informações com geração de texto, garantindo que a LLM tenha acesso a contexto relevante e específico.

**Implementação:**
- **Retrieval**: Busca semântica nos chunks da solução
- **Augmentation**: Contexto relevante é incluído no prompt
- **Generation**: LLM gera resposta baseada no contexto recuperado

**Estrutura do Prompt:**
```
1. Instruções para a LLM (papel, formato de resposta)
2. Contexto recuperado (chunks relevantes)
3. Dados completos do JSON (limitado para evitar overflow)
4. Pergunta do usuário
```

**Benefício Acadêmico:** Demonstra aplicação prática de **RAG**, técnica state-of-the-art em sistemas de Q&A.

#### 4. **Análise Estruturada para Relatórios**

**Conceito Acadêmico:** Geração de análises estruturadas usando **prompt engineering** para extrair insights específicos.

**Implementação:**
- A LLM é solicitada a gerar **6 análises especializadas**:
  1. Resumo Executivo
  2. Análise de Viabilidade
  3. Distribuição de Prioridades
  4. Eficiência de Custos
  5. Pontos Críticos
  6. Recomendações

- Cada análise usa **prompts específicos** com instruções claras
- O contexto relevante é recuperado para cada tipo de análise

**Benefício Acadêmico:** Demonstra **Prompt Engineering** e **Análise de Dados com IA**.

#### 5. **Interface de Chat Interativa**

**Conceito Acadêmico:** Sistema de conversação onde a LLM mantém contexto da solução através de embeddings.

**Implementação:**
- Interface gráfica de chat (estilo chat moderno)
- Cada pergunta do usuário:
  1. É convertida em embedding
  2. Busca chunks relevantes na solução
  3. Gera resposta contextualizada
  4. Mantém histórico da conversa

**Benefício Acadêmico:** Demonstra aplicação de **Sistemas de Conversação** e **Context Management**.

---

### Configuração da API

1. **Obter API Key:**
   - Acesse: https://makersuite.google.com/app/apikey
   - Crie ou selecione projeto
   - Copie a API Key

2. **Configurar variável de ambiente:**

**Linux/Mac:**
```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

**Windows (CMD):**
```cmd
set GEMINI_API_KEY=sua_chave_aqui
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="sua_chave_aqui"
```

**Alternativa:** A API Key pode ser inserida diretamente na interface quando solicitada.

---

### Análise de Soluções Existentes

#### Acessando a Análise

1. Execute `python main.py`
2. Selecione **"Analisar solução existente"**
3. Se necessário, insira a API Key do Google Gemini
4. Selecione o arquivo JSON da solução desejada

#### Opções Disponíveis

Após selecionar o arquivo JSON, você terá duas opções:

##### 1. **Gerar Relatório PDF**

**O que faz:**
- Cria embeddings semânticos do JSON
- Gera 6 análises especializadas usando a LLM
- Cria visualizações (gráficos) automáticas
- Gera relatório PDF profissional

**Análises geradas:**
1. **Resumo Executivo**: Visão geral da solução
2. **Análise de Viabilidade**: Verificação de restrições e violações
3. **Distribuição de Prioridades**: Análise de entregas por prioridade
4. **Eficiência de Custos**: Análise de custos e otimizações
5. **Pontos Críticos**: Identificação de problemas e gargalos
6. **Recomendações**: Sugestões de melhorias

**Visualizações geradas:**
- **TSP**: 4 gráficos (distribuição de prioridades, custos, etc.)
- **VRP**: 6 gráficos (distribuição de rotas, utilização de veículos, etc.)

**Arquivo gerado:**
- Localização: `reports/`
- Nome: `report_YYYYMMDD_HHMMSS.pdf`

##### 2. **Chat com LLM**

**O que faz:**
- Cria embeddings semânticos do JSON
- Abre interface de chat interativa
- Permite fazer perguntas sobre a solução
- LLM responde usando o JSON como base de conhecimento

**Funcionalidades do Chat:**
- Interface moderna estilo chat
- Histórico de conversa
- Scrollbar visível
- Suporte a Ctrl+V para colar texto
- Respostas contextualizadas baseadas no JSON

---

### Chat Interativo com LLM

#### Como Usar o Chat

1. Selecione **"Analisar solução existente"** no menu principal
2. Escolha o arquivo JSON
3. Selecione **"Chat com LLM"**
4. Aguarde o processamento dos embeddings (pode levar alguns segundos)
5. Digite sua pergunta e pressione **Enter**

#### Controles do Chat

- **Enter**: Enviar mensagem
- **Esc**: Voltar ao menu anterior
- **Ctrl+V**: Colar texto da área de transferência
- **Mouse Wheel**: Rolar mensagens
- **Scrollbar**: Arrastar para navegar

#### Exemplos de Perguntas

**Sobre métricas gerais:**
- "Quantas rotas existem nesta solução?"
- "Qual é o custo total?"
- "Quantas cidades foram visitadas?"

**Sobre rotas específicas:**
- "Qual rota tem maior distância?"
- "Quais veículos foram utilizados?"
- "Há alguma violação de capacidade?"

**Sobre prioridades:**
- "Quantas entregas de prioridade alta existem?"
- "Como estão distribuídas as prioridades?"

**Análises mais complexas:**
- "Analise a eficiência desta solução"
- "Quais são os pontos críticos?"
- "Faça recomendações de melhoria"

#### Como Funciona (Tecnicamente)

1. **Embedding da Pergunta**: A pergunta do usuário é convertida em embedding vetorial
2. **Busca Semântica**: O sistema busca os 7 chunks mais similares no JSON
3. **Construção do Prompt**: 
   - Instruções para a LLM
   - Chunks relevantes recuperados
   - Dados essenciais do JSON (Resumo Geral, Estatísticas Agregadas, Métricas Principais)
   - Pergunta do usuário
4. **Geração da Resposta**: A LLM gera resposta baseada no contexto
5. **Renderização**: A resposta é renderizada na interface

**Modelo utilizado:**
- **Embeddings**: `models/embedding-001`
- **Geração**: `gemini-3-flash-preview`

---

### Geração de Relatórios PDF

#### Processo de Geração

1. **Criação de Embeddings**: JSON é dividido em chunks e convertido em embeddings
2. **Análises Especializadas**: Para cada tipo de análise:
   - Busca chunks relevantes
   - Gera prompt específico
   - LLM gera análise contextualizada
3. **Geração de Visualizações**: 
   - Gráficos são criados usando matplotlib
   - Salvos como imagens em `reports/`
4. **Montagem do PDF**: 
   - Usa ReportLab para criar PDF
   - Inclui metadados, análises, gráficos
   - Formatação profissional

#### Estrutura do Relatório PDF

1. **Capa**: Título e metadados
2. **Tabela de Metadados**: Modo, data, algoritmo, etc.
3. **Visualizações**: Gráficos gerados automaticamente
4. **Análises**: 6 seções com análises da LLM
5. **Formatação**: Estilo executivo profissional

---

## Controles e Interface

### Controles Durante Execução

#### Modo TSP

| Tecla | Função |
|-------|--------|
| `G` | Toggle gráficos de evolução |
| `L` | Toggle lista de cidades |
| `T` | Toggle visualização de tentativas |
| `C` | Toggle coordenadas geográficas |
| `P` | Pausar/Continuar |
| `R` | Reiniciar população |
| `E` | **Exportar solução para JSON** |
| `Q` | Sair |

#### Modo VRP

| Tecla | Função |
|-------|--------|
| `G` | Toggle gráficos de evolução |
| `L` | Toggle lista de rotas |
| `V` | Toggle cidades detalhadas |
| `D` | Toggle painel de detalhes |
| `C` | Toggle coordenadas |
| `P` | Pausar/Continuar |
| `R` | Recalcular solução VRP |
| `E` | **Exportar solução para JSON** |
| `Q` | Sair |

### Elementos da Interface

**Painel Esquerdo (400px):**
- Gráficos de evolução (fitness e distância)
- Lista de cidades/rotas
- Informações de veículos
- Métricas em tempo real
- Controles e dicas

**Área Central (1080px):**
- Mapa de São Paulo
- Cidades plotadas com cores de prioridade
- Rotas desenhadas (azul para TSP, cores diferentes para VRP)
- Animação em tempo real
- Legenda

**Painel Direito (800px - VRP com D):**
- Detalhes completos de cada rota
- Sequência de cidades com distâncias
- Estatísticas por rota
- Alertas de violações
- Prioridades por entrega

---

## Exemplos de Uso

### Exemplo 1: TSP Básico

```bash
# 1. Iniciar
python main.py

# 2. Menu inicial: pressionar "Criar nova solução"

# 3. Configuração GA:
#    Mutação: Swap
#    Seleção: Tournament
#    Crossover: OX (Order)

# 4. Escolher: TSP

# 5. Aguardar 30-60 segundos

# 6. Observar:
#    - Fitness diminuindo
#    - Rota se otimizando no mapa
#    - Lista de cidades ordenadas

# 7. Exportar: pressionar "E"
#    Arquivo gerado: solutions/tsp_solution_YYYYMMDD_HHMMSS.json

# 8. Analisar (opcional):
#    python main.py → "Analisar solução existente" → escolher arquivo
```

### Exemplo 2: VRP com Depósito

```bash
# 1. Iniciar
python main.py → "Criar nova solução"

# 2. Configurar GA:
#    Mutação: Inversion
#    Seleção: Tournament
#    Crossover: PMX

# 3. Escolher: VRP

# 4. Selecionar depósito: "São Paulo"

# 5. Aguardar 1-3 minutos

# 6. Observar:
#    - Múltiplas rotas coloridas
#    - Cada veículo uma cor
#    - Depósito marcado com "D"

# 7. Detalhes: pressionar "D"
#    Ver todas rotas, cidades, pesos, distâncias

# 8. Exportar: "E"
#    Arquivo: solutions/vrp_solution_YYYYMMDD_HHMMSS.json

# 9. Analisar:
#    python main.py → "Analisar solução existente" → escolher arquivo
#    Escolher "Gerar relatório PDF" ou "Chat com LLM"
```

### Exemplo 3: Análise com Chat

```bash
# 1. Iniciar
python main.py

# 2. Selecionar "Analisar solução existente"

# 3. Inserir API Key (se necessário)

# 4. Selecionar arquivo JSON

# 5. Escolher "Chat com LLM"

# 6. Aguardar processamento dos embeddings

# 7. Fazer perguntas:
#    - "Quantas rotas existem?"
#    - "Qual é o custo total?"
#    - "Há violações de capacidade?"
#    - "Analise a eficiência desta solução"

# 8. Ver respostas contextualizadas baseadas no JSON
```

### Exemplo 4: Comparação de Algoritmos

**Teste 1: Swap + Tournament**
```bash
python main.py → Criar nova solução → Swap, Tournament, OX → TSP
# Anotar: Fitness final, tempo
```

**Teste 2: Inversion + Tournament**
```bash
python main.py → Criar nova solução → Inversion, Tournament, OX → TSP
# Comparar resultados
```

**Teste 3: Scramble + Roulette**
```bash
python main.py → Criar nova solução → Scramble, Roulette, OX → TSP
# Ver diferença na exploração
```

---

## Arquivos de Dados

### Estrutura dos CSVs

#### `deliveries.csv`

```csv
id,medicine_name,quantity,total_weight,city,location_name,priority
1,Paracetamol,100,15.5,São Paulo,Hospital Central,0
2,Ibuprofeno,50,8.2,Campinas,Clínica Norte,1
...
```

**Campos:**
- `id`: Identificador único
- `medicine_name`: Nome do medicamento
- `quantity`: Quantidade de unidades
- `total_weight`: Peso total em kg
- `city`: Cidade destino
- `location_name`: Local específico
- `priority`: 0 (alta), 1 (média), 2 (baixa)

#### `veiculos.csv`

```csv
id,name,max_capacity,max_distance,max_weight,cost_per_km
V1,Van Pequena,1500,300,1500,2.5
V2,Caminhão Médio,3000,600,3000,3.0
...
```

**Campos:**
- `id`: Identificador do veículo
- `name`: Nome descritivo
- `max_capacity`: Capacidade em kg
- `max_distance`: Autonomia em km
- `max_weight`: Peso máximo em kg
- `cost_per_km`: Custo por quilômetro em R$

#### `cidades_sp.tsv`

```tsv
origem	destino	distancia
São Paulo	Campinas	92.5
São Paulo	Santos	72.3
...
```

**Campos (separados por TAB):**
- `origem`: Cidade origem
- `destino`: Cidade destino
- `distancia`: Distância real em km

### Personalização de Dados

Para usar seus próprios dados:

1. **Mantenha o formato dos CSVs**
2. **Adicione cidades em `cidades_sp.tsv`**
3. **Configure coordenadas em `worldcities.csv`**
4. **Ajuste veículos conforme sua frota**

---

## Troubleshooting

### Problema: "Module 'pygame' not found"

**Solução:**
```bash
pip install pygame
```

### Problema: Pygame não inicia janela

**Linux:**
```bash
sudo apt-get install python3-pygame
```

**Mac:**
```bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
pip install pygame
```

### Problema: Erro ao carregar dados

**Verificar:**
- Pasta `data_files/` existe?
- Todos os CSVs estão presentes?
- Encoding UTF-8?

**Solução:**
```bash
ls data_files/
# Deve mostrar: deliveries.csv, veiculos.csv, etc.
```

### Problema: Fitness não melhora

**Causas comuns:**
- População muito pequena (aumentar em `config/ga_config.py`)
- Taxa de mutação muito alta (diminuir)
- Problema sem solução viável

**Solução:**
```python
# config/ga_config.py
POPULATION_SIZE = 200  # Aumentar
MUTATION_RATE = 0.3    # Ajustar
```

### Problema: VRP não encontra solução viável

**Soluções:**
1. Adicionar mais veículos em `veiculos.csv`
2. Aumentar capacidade dos veículos
3. Aumentar `VRP_GENERATIONS_PER_ROUTE` em `config/ga_config.py`
4. Usar modo "Sem depósito"

### Problema: Análise com IA falha

**Verificar:**
1. API Key configurada?
   ```bash
   echo $GEMINI_API_KEY  # Linux/Mac
   echo %GEMINI_API_KEY% # Windows
   ```

2. Pacote instalado?
   ```bash
   pip install google-generativeai
   ```

3. Conexão com internet?

4. API Key válida? (teste em https://makersuite.google.com)

### Problema: Chat não responde

**Soluções:**
1. Verificar se embeddings foram criados (mensagem de progresso)
2. Verificar conexão com internet
3. Verificar API Key válida
4. Tentar perguntas mais simples primeiro

### Problema: Relatório PDF vazio

**Soluções:**
1. Verificar se JSON tem dados válidos
2. Verificar se API Key está configurada
3. Verificar permissões de escrita em `reports/`
4. Verificar logs de erro no console

---

## Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/MinhaFuncionalidade`)
5. Abra um Pull Request

---

## Autores

- Desenvolvido como projeto acadêmico FIAP - Em desenvolvimento para estudos

---

## Agradecimentos

- Dados de cidades: IBGE e GeoJSON
- Visualizações: Pygame e Matplotlib
- IA: Google Gemini API
- Inspiração: Problemas reais de logística brasileira

---
