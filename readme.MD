# Sistema de Otimização de Rotas com Algoritmos Genéticos

Sistema completo de otimização de rotas de entrega utilizando **Algoritmos Genéticos** para resolver problemas de **TSP (Traveling Salesman Problem)** e **VRP (Vehicle Routing Problem)**, com análise avançada usando **Google Gemini AI**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-success.svg)

---

## Índice

- [Características](#-características)
- [Instalação](#-instalação)
- [Início Rápido](#-início-rápido)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Algoritmos Genéticos](#-algoritmos-genéticos)
  - [Operadores de Mutação](#operadores-de-mutação)
  - [Métodos de Seleção](#métodos-de-seleção)
  - [Tipos de Crossover](#tipos-de-crossover)
- [Modos de Operação](#-modos-de-operação)
  - [TSP - Problema do Caixeiro Viajante](#tsp---problema-do-caixeiro-viajante)
  - [VRP - Roteamento de Veículos](#vrp---roteamento-de-veículos)
- [Análise com IA](#-análise-com-ia)
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
- **Análise com IA**: Relatórios executivos usando Google Gemini
- **Exportação de dados**: JSON estruturado e relatórios PDF
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
cd otimizacao-rotas
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

### 5. Verificar Instalação

```bash
python --version  # Deve mostrar Python 3.8+
pip list          # Verifica pacotes instalados
```

---

## Início Rápido

### Execução Básica

```bash
python tsp.py
```

### Fluxo Rápido (3 passos)

1. **Escolha o modo**
   - Pressione `A` para **analisar** solução existente
   - Pressione `N` para **criar nova** solução

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

# 2. Escolher "N" (Nova solução)

# 3. Configurar algoritmo (exemplo):
#    - Mutação: Swap
#    - Seleção: Tournament
#    - Crossover: Order (OX)

# 4. Escolher modo VRP

# 5. Selecionar depósito (ou "Sem Depósito")

# 6. Aguardar otimização (1-2 minutos)

# 7. Exportar solução: pressionar tecla "E"

# 8. Analisar: executar novamente e escolher "A"
```

---

## Estrutura do Projeto

```
fiap_tsp/
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
│   ├── cidades_sp.tsv              # Distâncias
│   ├── worldcities.csv             # Coordenadas
│   └── geojs-35-mun.json           # GeoJSON SP
│
├── tests/                           # Testes automatizados
│   ├── conftest.py                 # Fixtures
│   ├── test_loaders.py             # Testes loaders
│   ├── test_genetic_algorithm.py   # Testes AG
│   ├── test_constraints.py         # Testes restrições
│   ├── test_export.py              # Testes export
│   ├── test_vrp_solver.py          # Testes VRP
│   └── README.md                   # Doc testes
│
├── docs/                            # Documentação
│   ├── README.md                   # Índice documentação
│   ├── ARQUITETURA.md              # Arquitetura detalhada
│   ├── DIAGRAMAS.md                # Diagramas Mermaid
│   ├── COMPONENTES.md              # Doc componentes
│   └── TESTING.md                  # Doc testes
│
├── solutions/                       # Soluções exportadas
├── reports/                         # Relatórios PDF
│
├── requirements.txt                 # Dependências produção
├── requirements-dev.txt             # Dependências dev
├── pytest.ini                       # Config pytest
├── run_tests.py                     # Script auxiliar testes
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

**Função Fitness VRP:**
```
fitness = Σ(custo_rota_i)
        + penalidade_veículos_extras
        + penalidade_violações_capacidade
        + penalidade_prioridades_mal_sequenciadas
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

## Análise com IA

O sistema inclui análise avançada usando **Google Gemini AI** com embeddings.

### Configuração

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

### Como Usar

**Opção 1: Menu Inicial**
```bash
python tsp.py
# Pressione "A" para análise
```

**Opção 2: Análise Direta**
```bash
python route_analyzer.py
```

### O que a Análise Gera

1. **Embeddings inteligentes** - Busca semântica no contexto
2. **6 Análises especializadas:**
   - Resumo Executivo
   - Análise de Viabilidade
   - Distribuição de Prioridades
   - Eficiência de Custos
   - Pontos Críticos
   - Recomendações

3. **Visualizações automáticas:**
   - TSP: 4 gráficos
   - VRP: 6 gráficos

4. **Relatório PDF profissional**
   - Formatação executiva
   - Tabelas e gráficos integrados
   - Análises detalhadas

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
- Sequência de cidades
- Estatísticas por rota
- Alertas de violações
- Prioridades por entrega

---

## Exemplos de Uso

### Exemplo 1: TSP Básico

```bash
# 1. Iniciar
python tsp.py

# 2. Menu inicial: pressionar "N"

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
#    Arquivo gerado: tsp_solution_YYYYMMDD_HHMMSS.json

# 8. Analisar (opcional):
#    python tsp.py → "A" → escolher arquivo
```

### Exemplo 2: VRP com Depósito

```bash
# 1. Iniciar
python tsp.py → "N"

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
#    Ver todas rotas, cidades, pesos

# 8. Exportar: "E"
#    Arquivo: vrp_solution_YYYYMMDD_HHMMSS.json

# 9. Analisar:
#    python route_analyzer.py → escolher arquivo
#    Relatório PDF gerado automaticamente
```

### Exemplo 3: Comparação de Algoritmos

**Teste 1: Swap + Tournament**
```bash
python tsp.py → N → Swap, Tournament, OX → TSP
# Anotar: Fitness final, tempo
```

**Teste 2: Inversion + Tournament**
```bash
python tsp.py → N → Inversion, Tournament, OX → TSP
# Comparar resultados
```

**Teste 3: Scramble + Roulette**
```bash
python tsp.py → N → Scramble, Roulette, OX → TSP
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

## Testes Automatizados

O projeto inclui uma suíte completa de testes automatizados para garantir a qualidade do código.

### Executar Testes

```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura
pytest --cov=. --cov-report=html

# Script auxiliar interativo
python run_tests.py
```

### Cobertura de Testes

**42 testes** cobrindo:
- Carregamento e validação de dados (9 testes)
- Operadores do algoritmo genético (10 testes)
- Validação de restrições (9 testes)
- Função fitness TSP e VRP (incluído)
- Exportação de soluções para JSON (6 testes)
- Solver VRP e suas restrições (8 testes)

**Status**: 100% dos testes passando | Tempo: ~0.33s

Documentação completa: [docs/TESTING.md](docs/TESTING.md)

---

## Documentação

O projeto possui documentação completa e detalhada:

### Documentos Principais

1. **[docs/ARQUITETURA.md](docs/ARQUITETURA.md)**
   - Arquitetura do sistema (4 camadas)
   - Componentes e responsabilidades
   - Fluxos de dados (TSP, VRP, IA)
   - Padrões de projeto
   - Decisões arquiteturais

2. **[docs/DIAGRAMAS.md](docs/DIAGRAMAS.md)**
   - 10 diagramas Mermaid
   - Fluxogramas completos
   - Diagramas de sequência
   - Estruturas de dados
   - Pipelines de otimização

3. **[docs/COMPONENTES.md](docs/COMPONENTES.md)**
   - Documentação detalhada de cada módulo
   - Assinaturas de funções
   - Estruturas de dados
   - Dependências entre componentes

4. **[docs/TESTING.md](docs/TESTING.md)**
   - Guia completo de testes
   - Fixtures e exemplos
   - Boas práticas
   - Troubleshooting

**Ver índice completo**: [docs/README.md](docs/README.md)

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
- População muito pequena (aumentar em `config.py`)
- Taxa de mutação muito alta (diminuir)
- Problema sem solução viável

**Solução:**
```python
# config.py
POPULATION_SIZE = 200  # Aumentar
MUTATION_RATE = 0.3    # Ajustar
```

### Problema: VRP não encontra solução viável

**Soluções:**
1. Adicionar mais veículos em `veiculos.csv`
2. Aumentar capacidade dos veículos
3. Aumentar `VRP_GENERATIONS_PER_ROUTE` em `config.py`
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

---

## Parâmetros de Configuração

### `config.py`

```python
# Tamanho da população
POPULATION_SIZE = 100  # Aumentar para melhor qualidade

# Taxa de mutação
MUTATION_RATE = 0.4    # 0.2-0.5 recomendado

# Peso de prioridade
PRIORITY_WEIGHT = 20   # Aumentar para forçar prioridades

# Gerações VRP
VRP_GENERATIONS_PER_ROUTE = 100  # Aumentar para VRP complexo

# Interface
DEFAULT_SHOW_PLOT = True
DEFAULT_SHOW_LIST = True
```

### Ajuste Fino

**Para convergência rápida:**
```python
POPULATION_SIZE = 50
MUTATION_RATE = 0.3
```

**Para qualidade máxima:**
```python
POPULATION_SIZE = 200
MUTATION_RATE = 0.4
VRP_GENERATIONS_PER_ROUTE = 200
```

**Para problemas grandes:**
```python
POPULATION_SIZE = 150
MUTATION_RATE = 0.5
```

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
