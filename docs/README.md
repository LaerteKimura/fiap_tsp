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

## Navegação Rápida

### Para Desenvolvedores

**Iniciando no projeto**:
1. Leia [ARQUITETURA.md](ARQUITETURA.md) - seção "Visão Geral"
2. Veja [DIAGRAMAS.md](DIAGRAMAS.md) - "Diagrama de Componentes"
3. Execute os testes - [TESTING.md](TESTING.md)

**Entendendo algoritmos**:
1. [COMPONENTES.md](COMPONENTES.md) - seção "2.1 Genetic Algorithm"
2. [DIAGRAMAS.md](DIAGRAMAS.md) - "Fluxo do Algoritmo Genético"
3. [DIAGRAMAS.md](DIAGRAMAS.md) - "Função Fitness"

**Trabalhando com VRP**:
1. [COMPONENTES.md](COMPONENTES.md) - seção "2.2 VRP Solver"
2. [DIAGRAMAS.md](DIAGRAMAS.md) - "Fluxo VRP Solver"
3. [DIAGRAMAS.md](DIAGRAMAS.md) - "Pipeline de Otimização VRP"

**Integrando IA**:
1. [COMPONENTES.md](COMPONENTES.md) - seção "3.1 Route Analyzer"
2. [DIAGRAMAS.md](DIAGRAMAS.md) - "Interação com Gemini AI"
3. [DIAGRAMAS.md](DIAGRAMAS.md) - "Diagrama de Sequência - Análise com IA"

---

### Para Pesquisadores/Acadêmicos

**Entendendo o problema**:
- [ARQUITETURA.md](ARQUITETURA.md) - Seções "Visão Geral" e "Decisões Arquiteturais"
- README principal do projeto (na raiz)

**Algoritmos implementados**:
- [COMPONENTES.md](COMPONENTES.md) - Seção "2. Camada de Lógica de Negócio"
- README principal - Seção "Algoritmos Genéticos"

**Validação experimental**:
- [TESTING.md](TESTING.md) - Testes automatizados
- [ARQUITETURA.md](ARQUITETURA.md) - Seção "Métricas e Performance"

---

### Para Usuários/Stakeholders

**Como usar o sistema**:
- README principal (raiz) - Seção "Início Rápido"
- README principal - Seção "Controles e Interface"

**Capacidades do sistema**:
- [ARQUITETURA.md](ARQUITETURA.md) - Seção "Visão Geral"
- README principal - Seção "Características"

**Análise com IA**:
- [COMPONENTES.md](COMPONENTES.md) - Seção "3.1 Route Analyzer"
- README principal - Seção "Análise com IA"

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

## Contribuindo com a Documentação

### Adicionando Novo Documento

1. Criar arquivo em `docs/`
2. Adicionar referência neste README
3. Seguir template:
```markdown
# Título do Documento

## Seção 1
Conteúdo...

## Seção 2
Conteúdo...

---
**Versão**: 1.0
**Última atualização**: YYYY-MM-DD
```

### Atualizando Diagramas

1. Editar código Mermaid em [DIAGRAMAS.md](DIAGRAMAS.md)
2. Testar em https://mermaid.live/
3. Commit alterações

### Melhorando Documentação

Pull requests bem-vindos para:
- Correções de typos
- Clarificações
- Exemplos adicionais
- Traduções
- Novos diagramas

---

## Versionamento

**Versão atual da documentação**: 1.0

**Última atualização**: 2026-01-14

**Changelog**:
- v1.0 (2026-01-14): Documentação inicial completa
  - ARQUITETURA.md
  - DIAGRAMAS.md
  - COMPONENTES.md
  - TESTING.md
  - README.md (este arquivo)

---

## Contato e Suporte

**Projeto**: Sistema de Otimização de Rotas - Tech Challenge Fase 2

**Repositório**: https://github.com/LaerteKimura/fiap_tsp

**Issues**: https://github.com/LaerteKimura/fiap_tsp/issues

Para dúvidas sobre documentação, abra uma issue com a tag `documentation`.

---

## Licença

Este projeto é desenvolvido para fins acadêmicos (FIAP - Pós Tech).

---

**Navegue pelos documentos e bom desenvolvimento!** 🚀
