# infra/solution_exporter.py
import json
import os
from datetime import datetime

from route_helpers import (
    calculate_route_weight,
    calculate_route_distance,
    select_vehicle,
)

def _delivery_to_dict(d):
    # Delivery do seu loader_resources/delivery_loader.py
    if hasattr(d, "__dict__"):
        return {
            "id": getattr(d, "id", None),
            "medicine_name": getattr(d, "medicine_name", None),
            "quantity": getattr(d, "quantity", None),
            "total_weight": getattr(d, "total_weight", None),
            "city": getattr(d, "city", None),
            "location_name": getattr(d, "location_name", None),
            "priority": getattr(d, "priority", None),
        }
    # fallback (se algum dia vier dict)
    return dict(d)

def _ensure_tuple_coords(route):
    # garante coords hashable p/ coord_to_city
    return [tuple(c) for c in route] if route else []

def export_solution_to_json(data, solution, mode, depot_city=None, export_path="best_solution.json"):
    """
    Exporta a solução para JSON, compatível com:
    - TSP: solution = route (lista de coords)
    - VRP: solution = lista[VRPRoute]
    """

    mode = (mode or "").upper()

    if mode == "TSP":
        deliveries_by_city = data["deliveries_by_city"]
        coord_to_city = data["coord_to_city"]
        distance_lookup = data["distance_lookup"]
        vehicles = data["vehicles"]

        best_route = _ensure_tuple_coords(solution)

        route_cities = [coord_to_city[coord] for coord in best_route]

        total_weight = calculate_route_weight(best_route, coord_to_city, deliveries_by_city)
        total_distance_km = calculate_route_distance(best_route, coord_to_city, distance_lookup)
        vehicle = select_vehicle(total_weight, total_distance_km, vehicles)

        route_details = []
        all_deliveries = []

        for i, city in enumerate(route_cities):
            deliveries = deliveries_by_city.get(city, [])
            city_weight = sum(getattr(d, "total_weight", 0.0) for d in deliveries) if deliveries else 0.0

            all_deliveries.extend(deliveries)

            route_details.append({
                "sequence": i + 1,
                "city": city,
                "delivery_count": len(deliveries),
                "total_weight": city_weight,
                "deliveries": [_delivery_to_dict(d) for d in deliveries],
            })

        priority_counts = {}
        for d in all_deliveries:
            p = getattr(d, "priority", None)
            priority_counts[p] = priority_counts.get(p, 0) + 1

        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "mode": "TSP",
                "algorithm": "Genetic Algorithm",
                "total_cities": len(best_route),
            },
            "constraints": {
                "vehicles_available": [
                    {
                        "id": v.vehicle_id,
                        "name": v.name,
                        "max_weight": v.max_weight,
                        "cost_per_km": v.cost_per_km,
                        "max_distance": v.max_distance,
                    } for v in vehicles
                ],
                "selected_vehicle": None if vehicle is None else {
                    "id": vehicle.vehicle_id,
                    "name": vehicle.name,
                    "max_weight": vehicle.max_weight,
                    "cost_per_km": vehicle.cost_per_km,
                    "max_distance": vehicle.max_distance,
                    "is_sufficient": total_weight <= vehicle.max_weight and total_distance_km <= vehicle.max_distance,
                }
            },
            "solution": {
                "route_coordinates": best_route,
                "route_cities": route_cities,
                "route_details": route_details,
                "total_weight": total_weight,
                "total_distance_km": total_distance_km,
                "estimated_cost": None if vehicle is None else total_distance_km * vehicle.cost_per_km,
            },
            "analysis": {
                "delivery_statistics": {
                    "total_deliveries": len(all_deliveries),
                    "priority_distribution": priority_counts,
                    "avg_weight_per_delivery": (total_weight / len(all_deliveries)) if all_deliveries else 0,
                }
            }
        }

    elif mode == "VRP":
        deliveries_by_city = data["deliveries_by_city"]
        coord_to_city = data["coord_to_city"]
        distance_lookup = data["distance_lookup"]
        vehicles = data["vehicles"]

        vrp_routes = solution or []  # no seu zip é lista[VRPRoute]

        routes_details = []
        total_distance = 0.0
        total_cost = 0.0
        total_weight = 0.0
        all_deliveries = []
        vehicle_usage = {}

        for route_idx, r in enumerate(vrp_routes):
            vehicle = r.vehicle
            route_coords = _ensure_tuple_coords(r.route)

            # garante stats atualizados
            if hasattr(r, "calculate_stats"):
                r.route = route_coords
                r.calculate_stats(coord_to_city, deliveries_by_city, distance_lookup)

            route_distance = getattr(r, "total_distance", 0.0)
            route_weight = getattr(r, "total_weight", 0.0)
            route_cost = getattr(r, "total_cost", 0.0)

            total_distance += route_distance
            total_cost += route_cost
            total_weight += route_weight

            vid = vehicle.vehicle_id
            if vid not in vehicle_usage:
                vehicle_usage[vid] = {
                    "vehicle": {
                        "id": vehicle.vehicle_id,
                        "name": vehicle.name,
                        "max_weight": vehicle.max_weight,
                        "cost_per_km": vehicle.cost_per_km,
                        "max_distance": vehicle.max_distance,
                    },
                    "count": 0,
                    "total_distance": 0.0,
                    "total_weight": 0.0,
                    "total_cost": 0.0,
                }

            vehicle_usage[vid]["count"] += 1
            vehicle_usage[vid]["total_distance"] += route_distance
            vehicle_usage[vid]["total_weight"] += route_weight
            vehicle_usage[vid]["total_cost"] += route_cost

            city_details = []
            route_deliveries = []

            for coord in route_coords:
                city = coord_to_city.get(coord)
                deliveries = deliveries_by_city.get(city, []) if city else []
                city_weight = sum(getattr(d, "total_weight", 0.0) for d in deliveries) if deliveries else 0.0

                route_deliveries.extend(deliveries)

                city_details.append({
                    "city": city,
                    "delivery_count": len(deliveries),
                    "total_weight": city_weight,
                    "deliveries": [_delivery_to_dict(d) for d in deliveries],
                })

            # [CORREÇÃO] Sem depósito: adicionar primeira cidade no final para mostrar retorno
            if not depot_city and route_coords and len(route_coords) > 1:
                first_coord = route_coords[0]
                first_city = coord_to_city.get(first_coord)
                if first_city:
                    # Adicionar entrada de retorno (sem entregas, apenas para mostrar o retorno)
                    city_details.append({
                        "city": first_city,
                        "delivery_count": 0,
                        "total_weight": 0.0,
                        "deliveries": [],
                    })

            all_deliveries.extend(route_deliveries)

            is_weight_valid = route_weight <= vehicle.max_weight
            is_distance_valid = (route_distance <= vehicle.max_distance) if vehicle.max_distance else True
            is_route_valid = is_weight_valid and is_distance_valid

            routes_details.append({
                "route_id": route_idx + 1,
                "vehicle": {
                    "id": vehicle.vehicle_id,
                    "name": vehicle.name,
                    "max_weight": vehicle.max_weight,
                    "cost_per_km": vehicle.cost_per_km,
                    "max_distance": vehicle.max_distance,
                },
                "route_sequence_coords": route_coords,
                "route_details": city_details,
                "metrics": {
                    "distance_km": route_distance,
                    "total_weight": route_weight,
                    "cost": route_cost,
                    "vehicle_utilization": (route_weight / vehicle.max_weight) if vehicle.max_weight else 0,
                    "is_valid": is_route_valid,
                    "weight_constraint_satisfied": is_weight_valid,
                    "distance_constraint_satisfied": is_distance_valid,
                }
            })

        priority_counts = {}
        for d in all_deliveries:
            p = getattr(d, "priority", None)
            priority_counts[p] = priority_counts.get(p, 0) + 1

        valid_routes = sum(1 for r in routes_details if r["metrics"]["is_valid"])

        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "mode": "VRP",
                "algorithm": "Genetic Algorithm",
                "depot_city": depot_city,
                "total_routes": len(routes_details),
                "valid_routes": valid_routes,
            },
            "constraints": {
                "vehicles_available": [
                    {
                        "id": v.vehicle_id,
                        "name": v.name,
                        "max_weight": v.max_weight,
                        "cost_per_km": v.cost_per_km,
                        "max_distance": v.max_distance,
                    } for v in vehicles
                ],
                "problem_constraints": {
                    "depot_city": depot_city,
                    "vehicle_capacity_constraints": True,
                    "vehicle_distance_constraints": True,
                    "total_deliveries": len(all_deliveries),
                }
            },
            "solution": {
                "routes": routes_details,
                "overall_metrics": {
                    "total_distance_km": total_distance,
                    "total_cost": total_cost,
                    "total_weight": total_weight,
                    "avg_distance_per_route": (total_distance / len(routes_details)) if routes_details else 0,
                    "avg_weight_per_route": (total_weight / len(routes_details)) if routes_details else 0,
                    "avg_cost_per_route": (total_cost / len(routes_details)) if routes_details else 0,
                },
                "vehicle_usage": vehicle_usage,
            },
            "analysis": {
                "delivery_statistics": {
                    "total_deliveries": len(all_deliveries),
                    "priority_distribution": priority_counts,
                    "avg_weight_per_delivery": (total_weight / len(all_deliveries)) if all_deliveries else 0,
                },
                "route_quality": {
                    "valid_route_percentage": (valid_routes / len(routes_details)) if routes_details else 0,
                    "routes_with_weight_violations": sum(1 for r in routes_details if not r["metrics"]["weight_constraint_satisfied"]),
                    "routes_with_distance_violations": sum(1 for r in routes_details if not r["metrics"]["distance_constraint_satisfied"]),
                },
            }
        }

    else:
        raise ValueError(f"Modo desconhecido: {mode}")

    # Criar pasta solutions se não existir
    solutions_dir = "solutions"
    if not os.path.exists(solutions_dir):
        os.makedirs(solutions_dir)
    
    # Se apenas o nome do arquivo foi fornecido, colocar na pasta solutions
    if not os.path.dirname(export_path):
        export_path = os.path.join(solutions_dir, export_path)
    
    export_dir = os.path.dirname(export_path)
    if export_dir and not os.path.exists(export_dir):
        os.makedirs(export_dir)

    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    return True
