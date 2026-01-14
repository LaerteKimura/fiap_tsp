# Documentação do Sistema

Bem-vindo à documentação completa do Sistema de Otimização de Rotas!

---

## Documentos Disponíveis

### 1. [ARQUITETURA.md](ARQUITETURA.md)
**Visão geral da arquitetura do sistema**

Conteúdo:
- Arquitetura de alto nível (4 camadas)
- Estrutura de diretórios completa
- Componentes principais e suas responsabilidades
- Fluxo de dados (TSP, VRP, Análise IA)
- Padrões de projeto utilizados
- Decisões arquiteturais e justificativas
- Métricas de performance
- Segurança e validação
- Extensibilidade
- Dependências externas

**Quando usar**: Para entender a estrutura geral do projeto e como os componentes se relacionam.

---

### 2. [DIAGRAMAS.md](DIAGRAMAS.md)
**Diagramas visuais do sistema (Mermaid)**

Conteúdo:
- Diagrama de componentes
- Fluxo principal do sistema
- Fluxo do Algoritmo Genético
- Função Fitness
- Fluxo VRP Solver
- Diagrama de sequência (Análise IA)
- Estrutura de dados JSON
- Diagrama de estados da interface
- Pipeline de otimização VRP
- Interação com Gemini AI

**Quando usar**: Para visualizar fluxos, interações e estruturas de dados. Todos os diagramas são renderizáveis no GitHub.

---

### 3. [COMPONENTES.md](COMPONENTES.md)
**Documentação detalhada de cada componente**

Conteúdo:
- Camada de Dados (Loaders, estruturas)
- Camada de Lógica (GA, VRP Solver, Route Helpers)
- Camada de Serviços (Route Analyzer, IA)
- Camada de Apresentação (Views, UI)
- Infraestrutura (Export)
- Configuração
- Dependências entre componentes

**Quando usar**: Para detalhes de implementação de módulos específicos, assinaturas de funções e estruturas de dados.

---

### 4. [TESTING.md](TESTING.md)
**Documentação de testes automatizados**

Conteúdo:
- Estrutura de testes
- Como executar testes
- Cobertura de código
- Fixtures disponíveis
- Categorias de testes
- Exemplos práticos
- Boas práticas
- Depuração
- Troubleshooting

**Quando usar**: Para executar, criar ou entender os testes automatizados do projeto.

---

## Glossário

**TSP**: Traveling Salesman Problem - Problema do Caixeiro Viajante

**VRP**: Vehicle Routing Problem - Problema de Roteamento de Veículos

**AG/GA**: Algoritmo Genético / Genetic Algorithm

**Fitness**: Função que avalia qualidade de uma solução

**Crossover**: Operador de cruzamento que combina dois pais

**Mutação**: Operador que introduz variação em uma solução

**Seleção**: Operador que escolhe pais para reprodução

**População**: Conjunto de soluções candidatas

**Geração**: Iteração do algoritmo evolutivo

**Embedding**: Representação vetorial de texto para IA

**LLM**: Large Language Model (Gemini, GPT, etc)

---

## Convenções

### Diagramas Mermaid

Todos os diagramas em [DIAGRAMAS.md](DIAGRAMAS.md) usam sintaxe Mermaid e são renderizáveis no GitHub.

**Para visualizar localmente**:
- Extensão VSCode: Markdown Preview Mermaid Support
- Ou online: https://mermaid.live/

### Código nos Documentos

Código Python em blocos com sintaxe destacada:
```python
def example():
    pass
```

Estruturas de dados em JSON:
```json
{"key": "value"}
```

### Referências Cruzadas

Links internos entre documentos:
- `[ARQUITETURA.md](ARQUITETURA.md)` - link relativo
- Seções específicas: `[Título](#título)` - âncora

---

## Licença

Este projeto é desenvolvido para fins acadêmicos (FIAP - Pós Tech).

---

