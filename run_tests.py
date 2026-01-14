#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script auxiliar para executar testes do projeto.
"""
import sys
import subprocess
import os


def run_command(cmd, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n{'='*60}")
    print(f">>> {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n[ERRO] {description}")
        return False
    else:
        print(f"\n[OK] {description} - Concluído com sucesso!")
        return True


def main():
    """Função principal."""
    print("""
╔══════════════════════════════════════════════════════════╗
║  Sistema de Otimização de Rotas - Executor de Testes    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Verificar se pytest está instalado
    try:
        import pytest
        print(f"[OK] pytest {pytest.__version__} encontrado")
    except ImportError:
        print("[ERRO] pytest não encontrado!")
        print("   Execute: pip install -r requirements-dev.txt")
        sys.exit(1)
    
    # Menu de opções
    print("\nEscolha uma opção:")
    print("1. Executar todos os testes")
    print("2. Executar testes com cobertura")
    print("3. Executar testes de loaders")
    print("4. Executar testes de algoritmo genético")
    print("5. Executar testes de restrições")
    print("6. Executar testes de exportação")
    print("7. Executar testes VRP")
    print("8. Executar testes rápidos (sem cobertura)")
    print("9. Gerar relatório de cobertura HTML")
    print("0. Sair")
    
    choice = input("\nOpção: ").strip()
    
    commands = {
        "1": ("pytest -v", "Executando todos os testes"),
        "2": ("pytest --cov=. --cov-report=term-missing --cov-report=html", "Executando testes com cobertura"),
        "3": ("pytest tests/test_loaders.py -v", "Executando testes de loaders"),
        "4": ("pytest tests/test_genetic_algorithm.py -v", "Executando testes de algoritmo genético"),
        "5": ("pytest tests/test_constraints.py -v", "Executando testes de restrições"),
        "6": ("pytest tests/test_export.py -v", "Executando testes de exportação"),
        "7": ("pytest tests/test_vrp_solver.py -v", "Executando testes VRP"),
        "8": ("pytest -v --no-cov", "Executando testes rápidos"),
        "9": ("pytest --cov=. --cov-report=html && start htmlcov/index.html", "Gerando relatório HTML"),
    }
    
    if choice == "0":
        print("Até logo!")
        sys.exit(0)
    
    if choice in commands:
        cmd, description = commands[choice]
        success = run_command(cmd, description)
        
        if success and choice in ["2", "9"]:
            print("\n[INFO] Relatório de cobertura gerado em: htmlcov/index.html")
        
        sys.exit(0 if success else 1)
    else:
        print("[ERRO] Opção inválida!")
        sys.exit(1)


if __name__ == "__main__":
    main()
