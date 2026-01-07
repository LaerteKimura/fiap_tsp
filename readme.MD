# Análise de Rotas com Gemini AI

Sistema de análise avançada de soluções de roteamento usando embeddings e IA generativa.

## 📦 Instalação

### Dependências Necessárias

```bash
# Instalar Google Generative AI
pip install -U google-generativeai

# Instalar ReportLab para geração de PDFs
pip install reportlab

# Instalar Matplotlib (se ainda não tiver)
pip install matplotlib

# Instalar pandas e numpy (geralmente já incluídos)
pip install pandas numpy
```

### Configuração da API Key

**Opção 1: Variável de Ambiente (Recomendado)**

```bash
# Linux/Mac
export GEMINI_API_KEY="sua_chave_api_aqui"

# Windows (PowerShell)
$env:GEMINI_API_KEY="sua_chave_api_aqui"

# Windows (CMD)
set GEMINI_API_KEY=sua_chave_api_aqui
```

**Opção 2: Inserir no prompt**

O sistema solicitará a chave se ela não estiver configurada.

### Obter API Key do Gemini

1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Get API Key"
4. Crie um novo projeto ou use um existente
5. Copie sua API Key

## 🚀 Como Usar

### Modo 1: Menu Inicial

```bash
python tsp.py
```

**Ao iniciar, você verá:**

- **Pressione A** - Analisar solução existente (abre route_analyzer)
- **Pressione N** - Criar nova solução (fluxo normal TSP/VRP)
- **ESC** - Sair

### Modo 2: Análise Direta

```bash
python route_analyzer.py
```

## 📊 Fluxo de Análise

### 1. Seleção de Arquivo

O sistema lista todos os arquivos JSON de solução no diretório:

```
📂 Arquivos de solução encontrados:
   1. tsp_solution_20250107_143022.json
   2. vrp_solution_20250107_145130.json
   
Escolha o arquivo para analisar (número): 
```

### 2. Processamento

O sistema realiza automaticamente:

✅ **Carregamento da solução**
- Lê arquivo JSON
- Valida estrutura de dados
- Extrai metadados

✅ **Geração de embeddings**
- Divide conteúdo em chunks semânticos
- Gera embeddings usando `embedding-001`
- Armazena em cache para reuso

✅ **Análise com Gemini**
- Usa embeddings para contexto relevante
- Gera 6 análises especializadas:
  1. Resumo Executivo
  2. Análise de Viabilidade
  3. Distribuição de Prioridades
  4. Eficiência de Custos
  5. Pontos Críticos
  6. Recomendações

✅ **Criação de visualizações**
- Gráficos de distribuição
- Análises por rota (VRP)
- Métricas principais
- Utilização de recursos

✅ **Geração de PDF**
- Relatório completo estruturado
- Tabelas de metadados
- Visualizações integradas
- Análises detalhadas por seção

### 3. Saída

```
✅ ANÁLISE CONCLUÍDA COM SUCESSO!
====================================

📄 Relatório PDF: relatorio_tsp_20250107_150245.pdf
📊 Visualizações: tsp_analysis.png

```

## 📄 Estrutura do Relatório

### Para TSP (Traveling Salesman Problem)

**Seções:**
1. **Metadados** - Informações gerais da solução
2. **Visualizações** - 4 gráficos principais:
   - Distribuição de prioridades
   - Peso acumulado ao longo da rota
   - Prioridades por sequência
   - Métricas principais
3. **Resumo Executivo** - Visão geral da solução
4. **Análise de Viabilidade** - Verificação de restrições
5. **Distribuição de Prioridades** - Análise de ordenação
6. **Eficiência de Custos** - Otimização de recursos
7. **Pontos Críticos** - Identificação de problemas
8. **Recomendações** - Sugestões de melhorias

### Para VRP (Vehicle Routing Problem)

**Seções:**
1. **Metadados** - Informações gerais (número de rotas, depósito, etc.)
2. **Visualizações** - 6 gráficos principais:
   - Custo por rota
   - Distância por rota
   - Peso por rota
   - Utilização de veículos (peso e distância)
   - Viabilidade (pizza chart)
   - Distribuição global de prioridades
3. **Resumo Executivo** - Visão geral multi-rota
4. **Análise de Viabilidade** - Verificação por rota
5. **Distribuição de Prioridades** - Análise global e por rota
6. **Eficiência de Custos** - Otimização e balanceamento
7. **Pontos Críticos** - Gargalos operacionais
8. **Recomendações** - Melhorias específicas por rota

## 🎯 Funcionalidades Avançadas

### Embeddings Inteligentes

O sistema usa embeddings para:
- **Busca semântica** - Encontra contexto relevante para cada análise
- **Cache eficiente** - Reutiliza embeddings já calculados
- **Top-K retrieval** - Seleciona os 5 chunks mais relevantes por query

### Análises Especializadas

Cada análise é gerada com:
- **Contexto relevante** - Baseado em embeddings
- **Dados completos** - Acesso ao JSON inteiro
- **Prompt especializado** - Pergunta específica para cada seção
- **Resposta estruturada** - Formato claro e acionável

### Visualizações Customizadas

**Para TSP:**
- Barras de prioridade
- Linha de peso acumulado
- Scatter de prioridades por posição
- Barras de métricas principais

**Para VRP:**
- Comparação entre rotas
- Utilização dupla (peso + distância)
- Viabilidade agregada
- Distribuição consolidada

## ⚙️ Configurações Avançadas

### Modelos Utilizados

```python
embedding_model = 'models/embedding-001'  # Para embeddings
generation_model = 'gemini-1.5-pro'       # Para análise
```

### Parâmetros de Retrieval

```python
top_k = 5  # Número de chunks mais relevantes por query
```

### Customização de Prompts

Edite `route_analyzer.py` na função `generate_analysis()`:

```python
queries = {
    'sua_analise': 'Sua pergunta personalizada aqui',
    # ...
}
```

## 🐛 Troubleshooting

### Erro: "Module not found: google.generativeai"

```bash
pip install -U google-generativeai
```

### Erro: "API Key não configurada"

Configure a variável de ambiente ou forneça no prompt.

### Erro: "Arquivo JSON inválido"

Certifique-se de exportar a solução usando a tecla **E** durante a execução.

### Erro: "ReportLab não encontrado"

```bash
pip install reportlab
```

### Timeout ou erro 503 da API

- Aguarde alguns segundos e tente novamente
- Verifique se sua API Key está ativa
- Verifique limites de rate na sua conta Gemini

## 📝 Exemplos de Uso

### Caso 1: Análise Rápida

```bash
# 1. Execute o solver e exporte (pressione E)
python tsp.py

# 2. Analise o arquivo gerado
python route_analyzer.py
# Escolha o arquivo mais recente
```

### Caso 2: Análise em Lote

```bash
# Para analisar múltiplos arquivos
for file in tsp_solution_*.json; do
    python route_analyzer.py
    # Escolha cada arquivo
done
```

### Caso 3: Integração com Scripts

```python
from route_analyzer import RouteAnalyzer
import os

api_key = os.getenv('GEMINI_API_KEY')
analyzer = RouteAnalyzer(api_key)

analyzer.load_solution('minha_solucao.json')
chunks = analyzer.create_text_chunks()
df = analyzer.generate_embeddings(chunks)
analyses = analyzer.generate_analysis(df)
viz_files = analyzer.create_visualizations()
pdf_path = analyzer.generate_pdf_report(analyses, viz_files)

print(f"Relatório gerado: {pdf_path}")
```

## 🔒 Segurança

- **Nunca** commite sua API Key no código
- Use variáveis de ambiente
- Mantenha `.env` no `.gitignore`
- Revogue keys vazadas imediatamente

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique os logs do console
2. Confirme que todas as dependências estão instaladas
3. Valide o formato do JSON de entrada
4. Teste sua API Key com um script simples

## 🚀 Próximas Funcionalidades

- [ ] Comparação entre múltiplas soluções
- [ ] Export para Excel além de PDF
- [ ] Dashboard interativo web
- [ ] Análise temporal de evolução
- [ ] Sugestões automáticas de re-otimização
- [ ] Integração com banco de dados

## 📄 Licença

Este módulo segue a mesma licença do projeto principal.
