# Testes Automatizados - Sistema de Otimização de Rotas

Este diretório contém todos os testes automatizados do projeto.

## Estrutura de Testes

```
tests/
├── __init__.py                 # Pacote de testes
├── conftest.py                 # Fixtures compartilhadas
├── test_loaders.py             # Testes de carregamento de dados
├── test_genetic_algorithm.py   # Testes de operadores genéticos
├── test_constraints.py         # Testes de restrições (peso, distância)
├── test_export.py              # Testes de exportação JSON
├── test_vrp_solver.py          # Testes do solver VRP
└── README.md                   # Este arquivo
```

## Como Executar os Testes

### Instalação das Dependências de Teste

```bash
pip install -r requirements-dev.txt
```

### Executar Todos os Testes

```bash
pytest
```

### Executar com Relatório de Cobertura

```bash
pytest --cov=. --cov-report=html
```

Depois, abra `htmlcov/index.html` no navegador para ver o relatório detalhado.

### Executar Testes Específicos

```bash
# Executar apenas testes de loaders
pytest tests/test_loaders.py

# Executar apenas testes de algoritmo genético
pytest tests/test_genetic_algorithm.py

# Executar apenas testes de restrições
pytest tests/test_constraints.py

# Executar teste específico
pytest tests/test_loaders.py::TestDeliveryLoader::test_delivery_creation
```

### Executar com Mais Verbosidade

```bash
pytest -v
```

### Executar com Output Detalhado

```bash
pytest -vv -s
```

## Categorias de Testes

### 1. Testes de Carregamento de Dados (`test_loaders.py`)
- Validação de criação de objetos Delivery e Vehicle
- Verificação de integridade dos dados
- Validação de prioridades e capacidades

### 2. Testes de Algoritmo Genético (`test_genetic_algorithm.py`)
- Geração de população
- Cálculo de distância e peso
- Função fitness
- Operadores de mutação (Swap, Inversion)
- Operadores de crossover (Order Crossover)
- Operadores de seleção (Tournament)

### 3. Testes de Restrições (`test_constraints.py`)
- Validação de restrição de peso
- Validação de restrição de distância
- Seleção de veículo adequado
- Tratamento de prioridades

### 4. Testes de Exportação (`test_export.py`)
- Exportação de soluções TSP
- Exportação de soluções VRP
- Validação de formato JSON
- Casos extremos (rotas vazias)

### 5. Testes do Solver VRP (`test_vrp_solver.py`)
- Criação e estatísticas de rotas VRP
- Função fitness VRP
- Validação de restrições específicas do VRP
- Penalidades (veículos duplicados, cidades não cobertas)

## Fixtures Disponíveis

As fixtures estão definidas em `conftest.py`:

- `sample_deliveries`: Lista de entregas de exemplo
- `sample_vehicles`: Lista de veículos de exemplo
- `sample_cities`: Lista de cidades de exemplo
- `sample_coords`: Coordenadas de exemplo
- `sample_coord_to_city`: Mapeamento coordenadas → cidades
- `sample_city_to_coord`: Mapeamento cidades → coordenadas
- `sample_deliveries_by_city`: Mapeamento cidade → entregas
- `sample_distance_lookup`: Distâncias entre cidades
- `sample_route`: Rota de exemplo
- `vrp_route_mock`: Mock de VRPRoute

## Cobertura de Código

O objetivo é manter cobertura de código acima de **80%** para os módulos principais:

- `genetic_algorithm.py`
- `route_helpers.py`
- `vrp_solver.py`
- `infra/solution_exporter.py`
- `loader_resources/*.py`

## Integração Contínua

Os testes são executados automaticamente em:
- Cada commit
- Cada pull request
- Antes de releases

## Adicionando Novos Testes

Para adicionar novos testes:

1. Crie um arquivo `test_<modulo>.py` no diretório `tests/`
2. Use o padrão de nomenclatura `test_<funcionalidade>`
3. Use fixtures do `conftest.py` quando possível
4. Documente o propósito de cada teste
5. Execute os testes localmente antes de commitar

Exemplo:

```python
def test_nova_funcionalidade(sample_deliveries, sample_vehicles):
    """Testa a nova funcionalidade X."""
    # Arrange
    data = preparar_dados()
    
    # Act
    resultado = funcao_testada(data)
    
    # Assert
    assert resultado == esperado
```

## Depuração de Testes Falhando

```bash
# Executar com pdb (debugger)
pytest --pdb

# Parar no primeiro teste que falhar
pytest -x

# Mostrar variáveis locais em falhas
pytest -l

# Executar apenas testes que falharam anteriormente
pytest --lf
```

## Relatórios

### HTML
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Terminal
```bash
pytest --cov=. --cov-report=term-missing
```

### XML (para CI/CD)
```bash
pytest --cov=. --cov-report=xml
```

## Contato

Para dúvidas sobre os testes, consulte a documentação principal do projeto ou abra uma issue.
