# route_analyzer.py
import os
import json
import textwrap
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Google Generative AI não instalado.")
    print("   Execute: pip install -U google-generativeai")
    exit(1)

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    print("❌ ReportLab não instalado.")
    print("   Execute: pip install reportlab")
    exit(1)

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    print("❌ Matplotlib não instalado.")
    print("   Execute: pip install matplotlib")
    exit(1)


class RouteAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.embedding_model = 'models/embedding-001'
        self.generation_model = 'gemini-3-flash-preview'
        self.solution_data = None
        self.embeddings_cache = {}
        
    def load_solution(self, json_path: str) -> Dict:
        """Carrega arquivo JSON da solução."""
        print(f"\n📂 Carregando solução: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.solution_data = json.load(f)
        
        print(f"✅ Solução carregada: {self.solution_data['metadata']['mode']}")
        return self.solution_data
    
    def create_text_chunks(self) -> List[Dict[str, str]]:
        """Cria chunks de texto para embeddings."""
        print("\n📝 Criando chunks de texto...")
        
        chunks = []
        mode = self.solution_data['metadata']['mode']
        
        chunks.append({
            'title': 'Resumo Geral',
            'text': f"""
Modo: {mode}
Data: {self.solution_data['metadata']['export_timestamp']}
Descrição: {self.solution_data['metadata']['description']}
            """.strip()
        })
        
        if mode == 'TSP':
            solution = self.solution_data['solution']
            chunks.append({
                'title': 'Métricas Principais',
                'text': f"""
Veículo: {solution['selected_vehicle']['name']}
Distância Total: {solution['total_distance_km']} km
Peso Total: {solution['total_weight_kg']} kg
Custo Total: R$ {solution['total_cost']}
Número de Cidades: {len(solution['route'])}
                """.strip()
            })
            
            for i, city_info in enumerate(solution['route'][:10]):
                deliveries_text = "\n".join([
                    f"  - {d['medicine']} (P{d['priority']}, {d['weight']}kg)"
                    for d in city_info['deliveries']
                ])
                chunks.append({
                    'title': f"Cidade {i+1}: {city_info['city']}",
                    'text': f"""
Sequência: {city_info['sequence']}
Entregas:
{deliveries_text}
                    """.strip()
                })
        
        else:
            aggregate = self.solution_data['solution']['aggregate_stats']
            chunks.append({
                'title': 'Estatísticas Agregadas',
                'text': f"""
Número de Rotas: {aggregate['average_vehicles_used']}
Custo Total: R$ {aggregate['total_cost']}
Distância Total: {aggregate['total_distance_km']} km
Peso Total: {aggregate['total_weight_kg']} kg
Custo Médio por Veículo: R$ {aggregate['cost_per_vehicle']}
                """.strip()
            })
            
            for route in self.solution_data['solution']['routes']:
                route_text = f"""
Rota {route['route_id']}
Veículo: {route['vehicle']['name']} (ID: {route['vehicle']['id']})
Distância: {route['stats']['total_distance_km']} km
Peso: {route['stats']['total_weight_kg']} kg
Custo: R$ {route['stats']['total_cost']}
Prioridade Máxima: {route['stats']['max_priority']}
Cidades: {len(route['cities'])}
Viável: {'Sim' if route['feasibility']['is_feasible'] else 'Não'}
                """.strip()
                chunks.append({
                    'title': f"Rota {route['route_id']}",
                    'text': route_text
                })
        
        print(f"✅ {len(chunks)} chunks criados")
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict[str, str]]) -> pd.DataFrame:
        """Gera embeddings para os chunks."""
        print("\n🔄 Gerando embeddings...")
        
        df = pd.DataFrame(chunks)
        
        def embed_fn(title, text):
            cache_key = f"{title}:{text[:100]}"
            if cache_key in self.embeddings_cache:
                return self.embeddings_cache[cache_key]
            
            embedding = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document",
                title=title
            )["embedding"]
            
            self.embeddings_cache[cache_key] = embedding
            return embedding
        
        df['Embeddings'] = df.apply(
            lambda row: embed_fn(row['title'], row['text']), 
            axis=1
        )
        
        print(f"✅ {len(df)} embeddings gerados")
        return df
    
    def find_relevant_context(self, query: str, df: pd.DataFrame, top_k: int = 5) -> str:
        """Encontra contexto relevante usando embeddings."""
        query_embedding = genai.embed_content(
            model=self.embedding_model,
            content=query,
            task_type="retrieval_query"
        )["embedding"]
        
        dot_products = np.dot(
            np.stack(df['Embeddings']), 
            query_embedding
        )
        
        top_indices = np.argsort(dot_products)[-top_k:][::-1]
        
        context_parts = []
        for idx in top_indices:
            context_parts.append(f"### {df.iloc[idx]['title']}\n{df.iloc[idx]['text']}")
        
        return "\n\n".join(context_parts)
    
    def generate_analysis(self, df: pd.DataFrame) -> Dict[str, str]:
        """Gera análises usando Gemini."""
        print("\n🤖 Gerando análises com Gemini...")
        
        model = genai.GenerativeModel(self.generation_model)
        analyses = {}
        
        queries = {
            'resumo_executivo': 'Faça um resumo executivo completo da solução de roteamento',
            'analise_viabilidade': 'Analise a viabilidade técnica e operacional desta solução',
            'distribuicao_prioridades': 'Analise a distribuição e sequenciamento das prioridades de entrega',
            'eficiencia_custos': 'Analise a eficiência de custos e utilize dos recursos',
            'pontos_criticos': 'Identifique pontos críticos e possíveis gargalos operacionais',
            'recomendacoes': 'Forneça recomendações específicas para otimização'
        }
        
        for key, query in queries.items():
            print(f"   Gerando: {key}")
            
            context = self.find_relevant_context(query, df, top_k=5)
            
            prompt = textwrap.dedent(f"""
            Você é um especialista em logística e otimização de rotas.
            
            Analise os dados fornecidos e responda à seguinte questão em português:
            
            QUESTÃO: {query}
            
            CONTEXTO DA SOLUÇÃO:
            {context}
            
            DADOS COMPLETOS:
            {json.dumps(self.solution_data, indent=2, ensure_ascii=False)}
            
            Forneça uma análise detalhada, técnica e prática. Use dados específicos do contexto.
            Estruture sua resposta de forma clara com tópicos e subtópicos quando apropriado.
            """).strip()
            
            response = model.generate_content(prompt)
            analyses[key] = response.text
        
        print("✅ Análises geradas")
        return analyses
    
    def create_visualizations(self) -> Dict[str, str]:
        """Cria visualizações da solução."""
        print("\n📊 Criando visualizações...")
        
        viz_files = {}
        mode = self.solution_data['metadata']['mode']
        
        if mode == 'TSP':
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Análise da Rota TSP', fontsize=16, fontweight='bold')
            
            priorities = [d['priority'] for city in self.solution_data['solution']['route'] 
                         for d in city['deliveries']]
            priority_counts = pd.Series(priorities).value_counts().sort_index()
            
            axes[0, 0].bar(['Alta (P0)', 'Média (P1)', 'Baixa (P2)'], 
                          [priority_counts.get(i, 0) for i in range(3)],
                          color=['red', 'orange', 'green'])
            axes[0, 0].set_title('Distribuição de Prioridades')
            axes[0, 0].set_ylabel('Quantidade')
            
            weights = [sum(d['weight'] for d in city['deliveries']) 
                      for city in self.solution_data['solution']['route']]
            axes[0, 1].plot(range(1, len(weights)+1), np.cumsum(weights), 
                           marker='o', color='blue')
            axes[0, 1].set_title('Peso Acumulado ao Longo da Rota')
            axes[0, 1].set_xlabel('Sequência de Cidades')
            axes[0, 1].set_ylabel('Peso Acumulado (kg)')
            axes[0, 1].grid(True, alpha=0.3)
            
            priority_positions = [(city['sequence'], 
                                  min(d['priority'] for d in city['deliveries']))
                                 for city in self.solution_data['solution']['route']
                                 if city['deliveries']]
            if priority_positions:
                seq, prio = zip(*priority_positions)
                colors_map = {0: 'red', 1: 'orange', 2: 'green'}
                for s, p in zip(seq, prio):
                    axes[1, 0].scatter(s, p, c=colors_map[p], s=100, alpha=0.6)
                axes[1, 0].set_title('Prioridades ao Longo da Rota')
                axes[1, 0].set_xlabel('Sequência na Rota')
                axes[1, 0].set_ylabel('Prioridade')
                axes[1, 0].set_yticks([0, 1, 2])
                axes[1, 0].set_yticklabels(['Alta', 'Média', 'Baixa'])
                axes[1, 0].grid(True, alpha=0.3)
            
            vehicle = self.solution_data['solution']['selected_vehicle']
            metrics = {
                'Distância': self.solution_data['solution']['total_distance_km'],
                'Peso': self.solution_data['solution']['total_weight_kg'],
                'Custo': self.solution_data['solution']['total_cost']
            }
            axes[1, 1].bar(metrics.keys(), metrics.values(), color='steelblue')
            axes[1, 1].set_title('Métricas Principais')
            axes[1, 1].set_ylabel('Valores')
            
            plt.tight_layout()
            viz_path = 'tsp_analysis.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files['main'] = viz_path
        
        else:
            routes = self.solution_data['solution']['routes']
            
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            fig.suptitle('Análise VRP - Múltiplas Rotas', fontsize=16, fontweight='bold')
            
            route_costs = [r['stats']['total_cost'] for r in routes]
            axes[0, 0].bar(range(1, len(route_costs)+1), route_costs, color='steelblue')
            axes[0, 0].set_title('Custo por Rota')
            axes[0, 0].set_xlabel('Rota')
            axes[0, 0].set_ylabel('Custo (R$)')
            
            route_distances = [r['stats']['total_distance_km'] for r in routes]
            axes[0, 1].bar(range(1, len(route_distances)+1), route_distances, color='green')
            axes[0, 1].set_title('Distância por Rota')
            axes[0, 1].set_xlabel('Rota')
            axes[0, 1].set_ylabel('Distância (km)')
            
            route_weights = [r['stats']['total_weight_kg'] for r in routes]
            axes[0, 2].bar(range(1, len(route_weights)+1), route_weights, color='orange')
            axes[0, 2].set_title('Peso por Rota')
            axes[0, 2].set_xlabel('Rota')
            axes[0, 2].set_ylabel('Peso (kg)')
            
            vehicle_util = self.solution_data['analysis']['vehicle_utilization']
            weight_utils = [v['weight_utilization_percent'] for v in vehicle_util]
            distance_utils = [v['distance_utilization_percent'] for v in vehicle_util]
            
            x = np.arange(len(vehicle_util))
            width = 0.35
            axes[1, 0].bar(x - width/2, weight_utils, width, label='Peso', color='orange')
            axes[1, 0].bar(x + width/2, distance_utils, width, label='Distância', color='blue')
            axes[1, 0].set_title('Utilização de Veículos (%)')
            axes[1, 0].set_xlabel('Rota')
            axes[1, 0].set_ylabel('Utilização (%)')
            axes[1, 0].legend()
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels([f"R{i+1}" for i in range(len(vehicle_util))])
            
            feasible = sum(1 for r in routes if r['feasibility']['is_feasible'])
            infeasible = len(routes) - feasible
            axes[1, 1].pie([feasible, infeasible], labels=['Viável', 'Inviável'],
                          colors=['green', 'red'], autopct='%1.1f%%')
            axes[1, 1].set_title('Viabilidade das Rotas')
            
            all_priorities = []
            for route in routes:
                for city in route['cities']:
                    all_priorities.extend([d['priority'] for d in city['deliveries']])
            
            priority_counts = pd.Series(all_priorities).value_counts().sort_index()
            axes[1, 2].bar(['Alta (P0)', 'Média (P1)', 'Baixa (P2)'],
                          [priority_counts.get(i, 0) for i in range(3)],
                          color=['red', 'orange', 'green'])
            axes[1, 2].set_title('Distribuição de Prioridades')
            axes[1, 2].set_ylabel('Quantidade')
            
            plt.tight_layout()
            viz_path = 'vrp_analysis.png'
            plt.savefig(viz_path, dpi=300, bbox_inches='tight')
            plt.close()
            viz_files['main'] = viz_path
        
        print(f"✅ Visualizações criadas: {list(viz_files.keys())}")
        return viz_files
    
    def generate_pdf_report(self, analyses: Dict[str, str], 
                          viz_files: Dict[str, str], 
                          output_path: str = None):
        """Gera relatório em PDF."""
        print("\n📄 Gerando relatório PDF...")
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            mode = self.solution_data['metadata']['mode'].lower()
            output_path = f"relatorio_{mode}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story.append(Paragraph("Relatório de Análise de Rotas", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        metadata = self.solution_data['metadata']
        meta_data = [
            ['Modo', metadata['mode']],
            ['Data de Exportação', metadata['export_timestamp']],
            ['Algoritmo', metadata.get('algorithm', 'Genetic Algorithm')],
            ['Total de Cidades', str(metadata.get('total_cities', 'N/A'))]
        ]
        
        if metadata['mode'] == 'VRP':
            meta_data.append(['Total de Rotas', str(metadata.get('total_routes', 'N/A'))])
            if 'depot' in metadata and metadata['depot']:
                meta_data.append(['Depósito', metadata['depot']])
        
        meta_table = Table(meta_data, colWidths=[2.5*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(meta_table)
        story.append(Spacer(1, 0.3*inch))
        
        if 'main' in viz_files and os.path.exists(viz_files['main']):
            story.append(Paragraph("Visualizações", heading_style))
            img = Image(viz_files['main'], width=6.5*inch, height=5.5*inch)
            story.append(img)
            story.append(PageBreak())
        
        sections = [
            ('resumo_executivo', 'Resumo Executivo'),
            ('analise_viabilidade', 'Análise de Viabilidade'),
            ('distribuicao_prioridades', 'Distribuição de Prioridades'),
            ('eficiencia_custos', 'Eficiência de Custos'),
            ('pontos_criticos', 'Pontos Críticos'),
            ('recomendacoes', 'Recomendações')
        ]
        
        for key, title in sections:
            if key in analyses:
                story.append(Paragraph(title, heading_style))
                
                text = analyses[key].replace('\n', '<br/>')
                story.append(Paragraph(text, styles['BodyText']))
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        print(f"✅ Relatório gerado: {output_path}")
        return output_path


def main():
    print("=" * 60)
    print("ANÁLISE DE ROTAS COM GEMINI AI")
    print("=" * 60)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n⚠️  Variável de ambiente GEMINI_API_KEY não encontrada")
        api_key = input("Digite sua chave API do Gemini: ").strip()
        
        if not api_key:
            print("❌ API Key é necessária para continuar")
            return
    
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 
                 ('solution' in f or 'vrp' in f or 'tsp' in f)]
    
    if not json_files:
        print("\n❌ Nenhum arquivo de solução encontrado no diretório atual")
        return
    
    print("\n📂 Arquivos de solução encontrados:")
    for i, file in enumerate(json_files, 1):
        print(f"   {i}. {file}")
    
    while True:
        try:
            choice = int(input("\nEscolha o arquivo para analisar (número): "))
            if 1 <= choice <= len(json_files):
                json_path = json_files[choice - 1]
                break
            print("Opção inválida")
        except ValueError:
            print("Digite um número válido")
    
    analyzer = RouteAnalyzer(api_key)
    
    analyzer.load_solution(json_path)
    
    chunks = analyzer.create_text_chunks()
    
    df = analyzer.generate_embeddings(chunks)
    
    analyses = analyzer.generate_analysis(df)
    
    viz_files = analyzer.create_visualizations()
    
    output_pdf = analyzer.generate_pdf_report(analyses, viz_files)
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print(f"\n📄 Relatório PDF: {output_pdf}")
    if viz_files:
        print(f"📊 Visualizações: {', '.join(viz_files.values())}")
    print("\n")


if __name__ == "__main__":
    main()