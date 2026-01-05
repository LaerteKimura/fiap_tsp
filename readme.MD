🚚 TSP/VRP Genetic Algorithm Solver
Pharmaceutical Delivery Optimization System

https://img.shields.io/badge/Python-3.8%252B-blue
https://img.shields.io/badge/Pygame-2.5%252B-green
https://img.shields.io/badge/License-MIT-yellow
https://img.shields.io/badge/Status-Active-success

A sophisticated Python application that uses Genetic Algorithms to solve Traveling Salesman Problem (TSP) and Vehicle Routing Problem (VRP) for pharmaceutical deliveries in São Paulo, Brazil. The system optimizes delivery routes considering priority levels, vehicle constraints, and operational costs.

📋 Table of Contents
Overview

Features

Installation

Project Structure

Usage

Data Files

Algorithms

Configuration

Export Features

Keyboard Controls

Troubleshooting

Contributing

License

🎯 Overview
This system addresses complex logistics challenges for pharmaceutical deliveries, providing two operational modes:

TSP Mode - Single vehicle route optimization

VRP Mode - Multiple vehicle route optimization with depot management

The system considers:

✅ Delivery priorities (High, Medium, Low)

✅ Vehicle constraints (Weight, Distance, Capacity)

✅ Cost optimization (Distance, Fuel, Vehicle usage)

✅ Real-world constraints (Unique vehicles, Capacity limits)

✨ Features
Core Features
Dual Mode Operation: TSP (single vehicle) and VRP (multiple vehicles)

Priority-Based Optimization: High, medium, low priority deliveries

Real Constraints: Vehicle weight, distance, and capacity limits

Genetic Algorithm: Customizable crossover, mutation, and selection operators

Interactive Visualization: Real-time route visualization with PyGame

Export Functionality: JSON export for LLM analysis and reporting

Multiple Vehicle Support: Different vehicle types with unique constraints

Advanced Features
Adaptive Mutation Rates: Self-adjusting based on solution quality

Violation Penalties: Exponential penalties for constraint violations

Local Search Optimization: 2-opt algorithm for route refinement

Feasibility Enforcement: Automatic correction of invalid solutions

Detailed Reporting: Comprehensive solution analysis and metrics

📦 Installation
Prerequisites
Python 3.8 or higher

Git

Step-by-Step Installation
Clone the repository

bash
git clone https://github.com/yourusername/tsp-vrp-solver.git
cd tsp-vrp-solver
Create virtual environment (recommended)

bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
Install dependencies

bash
pip install -r requirements.txt
Dependencies
The requirements.txt includes:

text
pygame==2.5.0      # GUI and visualization
numpy==1.24.3      # Numerical operations
pandas==2.0.3      # Data processing
matplotlib==3.7.2  # Plotting (for future features)
📁 Project Structure
text
tsp-vrp-solver/
├── 📂 data/                    # Data files
│   ├── cidades_sp.csv         # City coordinates and names
│   ├── deliveries.csv         # Delivery information
│   ├── distances.csv          # Pre-calculated distances
│   └── vehicles.csv           # Vehicle specifications
├── 📂 src/                    # Source code
│   ├── main.py               # Main application file
│   ├── config.py             # Configuration constants
│   ├── data_loader.py        # Data loading utilities
│   ├── genetic_algorithm.py  # Core GA implementation
│   ├── vrp_solver.py         # VRP-specific algorithms
│   ├── route_helpers.py      # Route calculation utilities
│   ├── ui_renderer.py        # PyGame UI rendering
│   ├── vrp_menu_gui.py       # VRP mode GUI
│   ├── ga_menu_gui.py        # GA configuration GUI
│   └── vrp_details_renderer.py # VRP details panel
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
└── .gitignore              # Git ignore rules
📊 Data Files
1. cidades_sp.csv
Contains city information for São Paulo state:

csv
city,lat,lng
São Paulo,-23.550520,-46.633308
Campinas,-22.9056,-47.0608
Santos,-23.9608,-46.3336
...
2. deliveries.csv
Delivery information with priorities:

csv
id,medicine_name,quantity,total_weight,city,location_name,priority
1,Medicine A,100,50.5,São Paulo,Hospital X,0
2,Medicine B,50,25.2,Campinas,Clinic Y,1
...
Priority Levels:

0 = High Priority (Urgent)

1 = Medium Priority

2 = Low Priority

3. distances.csv
Pre-calculated distances between cities (in kilometers):

csv
city1,city2,distance_km
São Paulo,Campinas,99.2
São Paulo,Santos,72.5
...
4. vehicles.csv
Vehicle specifications:

csv
vehicle_id,max_load,max_distance,type,max_weight,cost_per_km,name
V001,5000,1000,Small,1000,1.5,"Van Pequena"
V002,10000,1500,Medium,2000,2.0,"Van Média"
...
🚀 Usage
Starting the Application
bash
cd src
python main.py
Initial Setup
Select Mode when prompted:

TSP: Single vehicle optimization

VRP: Multiple vehicles with depot

Configure Genetic Algorithm:

Choose crossover type (OX, PMX, CX)

Choose mutation type (Swap, Inversion, Scramble)

Choose selection type (Tournament, Roulette, Rank)

For VRP Mode:

Select depot city from the list

System will calculate optimal routes

Keyboard Controls
TSP Mode Controls
Key	Action
Q	Quit program
G	Toggle evolution plots
L	Toggle route list
T	Toggle attempt visualization
C	Toggle coordinates display
P	Pause/Resume evolution
R	Restart population
E	Export current solution
VRP Mode Controls
Key	Action
Q	Quit program
L	Toggle route list
C	Toggle coordinates display
G	Toggle evolution plots
P	Pause/Resume
D	Toggle details panel
V	Toggle city visualization
I	Toggle initial search view
R	Recalculate solution
E	Export current solution
🔬 Algorithms
Genetic Algorithm Implementation
1. Population Generation
Random initialization with diverse strategies

Priority-based grouping for initial solutions

Proximity-based clustering

2. Fitness Function
python
fitness = distance_cost + priority_penalty + constraint_violations + vehicle_cost
Components:

Distance Cost: Actual travel distance × cost per km

Priority Penalty: Higher for low-priority deliveries at route start

Constraint Violations: Exponential penalties for weight/distance limits

Vehicle Cost: Fixed cost per vehicle used

3. Crossover Operators
OX (Order Crossover): Preserves order from parents

PMX (Partially Matched Crossover): Preserves absolute positions

CX (Cycle Crossover): Preserves cycles between parents

4. Mutation Operators
Swap Mutation: Randomly swap two cities

Inversion Mutation: Reverse a route segment

Scramble Mutation: Shuffle a route segment

VRP-Specific: Route splitting, city moving between routes

5. Selection Methods
Tournament Selection: Best of random subset

Roulette Wheel: Probability proportional to fitness

Rank Selection: Based on fitness ranking

VRP-Specific Algorithms
1. Initial Solution Strategies
Priority Grouping: Group cities by delivery priority

Proximity Clustering: Group nearby cities together

Capacity-Based: Distribute based on vehicle capacity

2. Constraint Handling
Vehicle Uniqueness: Each vehicle used at most once

Capacity Limits: Weight and distance constraints per vehicle

Feasibility Repair: Automatic correction of violations

3. Local Search
2-opt Optimization: Improve individual routes

Priority Reordering: Place high-priority deliveries first

Inter-route Optimization: Balance loads between vehicles

⚙️ Configuration
Genetic Algorithm Parameters
python
# config.py
POPULATION_SIZE = 100       # Number of solutions in population
MUTATION_RATE = 0.4        # Base mutation probability
PRIORITY_WEIGHT = 20       # Weight for priority optimization
VRP_GENERATIONS_PER_ROUTE = 100  # Generations for VRP optimization
VRP Parameters
python
ROUTE_FIXED_COST = 800     # Fixed cost per vehicle used
BIG_PENALTY = 1_000_000    # Penalty for constraint violations
MAX_REPAIR_ATTEMPTS = 40   # Maximum repair attempts
DIVERSITY_RATE = 0.15      # Rate of random solution injection
UI Configuration
python
INFO_WIDTH = 400           # Info panel width
MAP_WIDTH = 1080           # Map display width
HEIGHT = 900               # Window height
ROUTE_COLORS = [...]       # Color palette for different routes
📤 Export Features
JSON Export Structure
The system exports solutions in a structured JSON format perfect for LLM analysis:

json
{
  "metadata": {
    "export_timestamp": "2024-01-15T10:30:00",
    "mode": "VRP",
    "description": "Best solution found for VRP",
    "algorithm": "Genetic Algorithm with VRP enhancements",
    "depot": "São Paulo"
  },
  "constraints": {
    "depot_city": "São Paulo",
    "vehicle_unique_constraint": true
  },
  "solution": {
    "routes": [...],
    "aggregate_stats": {...}
  },
  "analysis": {
    "feasibility_summary": {...},
    "priority_distribution": {...},
    "vehicle_utilization": [...]
  },
  "llm_instructions": {
    "task": "Analyze the VRP solution and generate an executive report",
    "sections_to_include": [...],
    "key_points_to_highlight": [...],
    "output_format": "Detailed markdown report"
  }
}
Export Usage
During execution: Press E to export current solution

Automatic export: Solution exported when program exits

File naming: [mode]_solution_YYYYMMDD_HHMMSS.json

LLM Integration Example
Use with ChatGPT/Claude/Gemini:

text
You are a logistics analyst. Analyze this VRP solution JSON and provide:
1. Executive summary
2. Feasibility assessment
3. Priority distribution analysis
4. Cost efficiency evaluation
5. Recommendations for improvement
🐛 Troubleshooting
Common Issues
1. PyGame Installation Issues
bash
# If pip install fails, try:
pip install pygame --pre
# or
python -m pip install pygame==2.5.0
2. Missing Data Files
text
Error: File not found: data/cidades_sp.csv
Solution: Ensure all CSV files are in the data/ directory

3. Memory Issues with Large Populations
text
Error: Memory allocation failed
Solution: Reduce POPULATION_SIZE in config.py

4. Slow Performance
Solutions:

Reduce POPULATION_SIZE

Reduce VRP_GENERATIONS_PER_ROUTE

Disable visualization features

Debug Mode
Add debug prints by setting:

python
# In config.py
DEBUG = True
🤝 Contributing
We welcome contributions! Here's how:

Development Setup
Fork the repository

Create a feature branch

Install development dependencies:

bash
pip install -r requirements-dev.txt
Guidelines
Follow PEP 8 style guide

Add tests for new features

Update documentation

Create descriptive pull requests

Areas for Contribution
New crossover/mutation operators

Additional optimization algorithms

Enhanced visualization features

More constraint types

Performance optimizations

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📞 Support
For issues, questions, or suggestions:

Check the Troubleshooting section

Open an issue on GitHub

Contact the maintainers

🙏 Acknowledgments
Inspired by real-world pharmaceutical logistics challenges

Built with educational and research purposes in mind

Special thanks to contributors and testers