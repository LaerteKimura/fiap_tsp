# Documentação de Testes

## Visão Geral

O projeto possui uma suíte completa de testes automatizados que valida:
- Carregamento e integridade de dados
- Lógica dos algoritmos genéticos
- Validação de restrições de negócio
- Exportação de soluções
- Solver VRP

## Estrutura de Testes

```
tests/
├── conftest.py                 # Fixtures compartilhadas (dados de exemplo)
├── test_loaders.py             # Testes de carregamento de dados
├── test_genetic_algorithm.py   # Testes de operadores genéticos
├── test_constraints.py         # Testes de restrições de negócio
├── test_export.py              # Testes de exportação JSON
└── test_vrp_solver.py          # Testes do solver VRP
```

## Executar Testes

### Todos os Testes
```bash
pytest
```

### Com Verbosidade
```bash
pytest -v
```

### Com Cobertura
```bash
pytest --cov=. --cov-report=html
```

### Testes Específicos
```bash
# Por arquivo
pytest tests/test_loaders.py

# Por classe
pytest tests/test_loaders.py::TestDeliveryLoader

# Por teste específico
pytest tests/test_loaders.py::TestDeliveryLoader::test_delivery_creation
```

## Cobertura de Código

### Visualizar Relatório HTML
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html  # Windows
```

### Meta de Cobertura
- **Objetivo**: ≥ 80% de cobertura
- **Módulos críticos**: ≥ 90%
  - `genetic_algorithm.py`
  - `vrp_solver.py`
  - `route_helpers.py`

## Fixtures Disponíveis

### Dados de Exemplo

#### `sample_deliveries`
Lista de 5 entregas com diferentes prioridades:
```python
[
    Delivery(1, "Paracetamol", 100, 15.5, "São Paulo", "Hospital Central", 0),
    Delivery(2, "Ibuprofeno", 50, 8.2, "Campinas", "Clínica Norte", 1),
    ...
]
```

#### `sample_vehicles`
Lista de 3 veículos com capacidades diferentes:
```python
[
    Vehicle("V1", "Van Pequena", "van", 1500, 300, 1500, 2.5),
    Vehicle("V2", "Caminhão Médio", "caminhao", 3000, 600, 3000, 3.0),
    ...
]
```

#### `sample_cities`
```python
["São Paulo", "Campinas", "Santos", "São José dos Campos", "Ribeirão Preto"]
```

#### `sample_coords`
```python
[(100, 100), (150, 120), (110, 180), (180, 110), (250, 150)]
```

### Mapeamentos

- `sample_coord_to_city`: Coordenadas → Cidades
- `sample_city_to_coord`: Cidades → Coordenadas
- `sample_deliveries_by_city`: Cidade → Lista de entregas
- `sample_distance_lookup`: (Cidade1, Cidade2) → Distância

### Objetos Complexos

- `sample_route`: Rota completa de exemplo
- `vrp_route_mock`: VRPRoute configurado para testes

## Categorias de Testes

### 1. Testes de Unidade

Testam funções/métodos isoladamente:

```python
def test_calculate_distance_returns_positive():
    """Testa que cálculo de distância é sempre positivo."""
    distance = calculate_route_distance(route, ...)
    assert distance >= 0
```

### 2. Testes de Integração

Testam interação entre componentes:

```python
def test_vrp_solver_with_real_data():
    """Testa solver VRP com dados reais."""
    solution = solve_vrp(cities, vehicles, ...)
    assert all(route.is_feasible for route in solution)
```

### 3. Testes de Validação

Testam regras de negócio:

```python
def test_route_respects_weight_limit():
    """Testa que rota respeita limite de peso."""
    weight = calculate_route_weight(route, ...)
    vehicle = select_vehicle(weight, ...)
    assert weight <= vehicle.max_weight
```

## Exemplos de Testes

### Teste Simples
```python
def test_delivery_has_positive_weight(sample_deliveries):
    """Testa que entregas têm peso positivo."""
    for delivery in sample_deliveries:
        assert delivery.total_weight > 0
```

### Teste com Mock
```python
def test_vrp_route_calculates_stats(vrp_route_mock):
    """Testa cálculo de estatísticas da rota VRP."""
    vrp_route_mock.calculate_stats(...)
    
    assert vrp_route_mock.total_distance >= 0
    assert vrp_route_mock.total_weight >= 0
```

### Teste de Exceção
```python
def test_invalid_vehicle_raises_error():
    """Testa que veículo inválido levanta erro."""
    with pytest.raises(ValueError):
        select_vehicle(weight=-100, distance=100, vehicles=[])
```

### Teste Parametrizado
```python
@pytest.mark.parametrize("priority,expected", [
    (0, "ALTA"),
    (1, "MÉDIA"),
    (2, "BAIXA"),
])
def test_priority_label(priority, expected):
    """Testa conversão de prioridade para label."""
    label = get_priority_label(priority)
    assert label == expected
```

## Boas Práticas

### Fazer

- **Arrange-Act-Assert**: Estruture testes claramente
- **Um conceito por teste**: Cada teste valida uma coisa
- **Nomes descritivos**: `test_<o_que>_<contexto>_<resultado>`
- **Use fixtures**: Reutilize dados de teste
- **Docstrings**: Explique o propósito do teste

###  Evitar

- Testes dependentes de ordem de execução
- Testes que modificam estado global
- Testes muito longos (> 20 linhas)
- Asserções múltiplas não relacionadas
- Testes sem documentação

## Depuração

### Executar com Debugger
```bash
pytest --pdb
```

### Mostrar Prints
```bash
pytest -s
```

### Parar no Primeiro Erro
```bash
pytest -x
```

### Mostrar Variáveis Locais
```bash
pytest -l
```

### Executar Apenas Testes que Falharam
```bash
pytest --lf
```

## Integração Contínua

Os testes são executados automaticamente via GitHub Actions:

```yaml
- Python 3.8, 3.9, 3.10, 3.11
- Ubuntu, Windows, macOS
- Em cada push/pull request
```

### Badge de Status
```markdown
![Tests](https://github.com/LaerteKimura/fiap_tsp/workflows/Tests/badge.svg)
```

## Métricas

### Tempo de Execução
```bash
pytest --durations=10  # Mostrar 10 testes mais lentos
```

### Estatísticas
```bash
pytest --verbose --tb=short
```

## Troubleshooting

### Problema: ImportError
```bash
# Solução: Instalar dependências
pip install -r requirements-dev.txt
```

### Problema: Testes Lentos
```bash
# Solução: Executar apenas testes rápidos
pytest -m "not slow"
```

### Problema: Fixtures Não Encontradas
```bash
# Solução: Verificar conftest.py
pytest --fixtures  # Listar todas as fixtures
```

## Referências

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

---
