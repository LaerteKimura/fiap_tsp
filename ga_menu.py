from genetic_algorithm import (
    MUTATION_TYPES,
    SELECTION_TYPES,
    CROSSOVER_TYPES
)


def choose_mutation():
    print("\nEscolha o tipo de mutação:")
    print("1 - Swap")
    print("2 - Inversion")
    print("3 - Scramble")

    choice = input("Opção: ").strip()

    mutation_map = {
        "1": "swap",
        "2": "inversion",
        "3": "scramble"
    }

    key = mutation_map.get(choice, "swap")
    print(f"Mutação selecionada: {key}")

    return MUTATION_TYPES[key], key


def choose_selection():
    print("\nEscolha o método de seleção:")
    print("1 - Tournament")
    print("2 - Roulette")
    print("3 - Rank")

    choice = input("Opção: ").strip()

    selection_map = {
        "1": "tournament",
        "2": "roulette",
        "3": "rank"
    }

    key = selection_map.get(choice, "tournament")
    print(f"Seleção selecionada: {key}")

    return SELECTION_TYPES[key], key


def choose_crossover():
    print("\nEscolha o tipo de crossover:")
    print("1 - Order Crossover (OX)")
    print("2 - PMX")
    print("3 - Cycle Crossover (CX)")

    choice = input("Opção: ").strip()

    crossover_map = {
        "1": "ox",
        "2": "pmx",
        "3": "cx"
    }

    key = crossover_map.get(choice, "ox")
    print(f"Crossover selecionado: {key}")

    return CROSSOVER_TYPES[key], key


def choose_ga_config():
    """
    Retorna todas as funções GA escolhidas
    """
    mutation_fn, mutation_key = choose_mutation()
    selection_fn, selection_key = choose_selection()
    crossover_fn, crossover_key = choose_crossover()

    return {
        "mutation_fn": mutation_fn,
        "selection_fn": selection_fn,
        "crossover_fn": crossover_fn,
        "mutation_key": mutation_key,
        "selection_key": selection_key,
        "crossover_key": crossover_key,
    }
