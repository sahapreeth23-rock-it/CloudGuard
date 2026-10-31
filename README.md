# CloudGuard – Cloud Microservice Dependency and Hierarchy Mapper

## Project Overview
CloudGuard is a Python-based project developed for **Discrete Mathematics and Graph Theory (DMGT)**. It uses graph theory and mathematical relations to model dependencies between microservices and determine a valid deployment sequence.

The project demonstrates how discrete mathematical concepts can be applied to real-world cloud application architecture.

## Objectives
- Represent microservices using mathematical sets.
- Model dependencies between microservices using relations.
- Generate direct dependency and prerequisite relation matrices.
- Verify reflexivity, antisymmetry, and transitivity.
- Generate a Hasse diagram to represent the dependency hierarchy.
- Determine a valid microservice deployment order using topological sorting.
- Identify equivalence classes based on deployment environments.
- Detect circular dependencies.

## Technologies Used
- **Programming Language:** Python
- **Libraries:** NetworkX, Matplotlib
- **IDE:** Visual Studio Code

## Microservices Used
The project simulates an e-commerce application containing six microservices:

1. Auth – Authentication
2. Prod – Product
3. Ord – Order
4. Pay – Payment
5. Inv – Inventory
6. Notif – Notification

**Arrow convention:** A → B means A depends on B. Therefore, B must be available before A starts.

## Key Features
- Microservice dependency graph visualization.
- Direct dependency and prerequisite relation matrices.
- Partial-order property verification.
- Hasse diagram generation.
- Topological deployment sequence generation.
- Circular dependency detection.
- Equivalence class identification.

## Project Files
| File | Description |
|---|---|
| `cloudguard.py` | Main Python source code |
| `dependency_graph.png` | Microservice dependency graph |
| `hasse_diagram.png` | Dependency hierarchy |
| `relation_matrices.png` | Relation matrices visualization |
| `README.md` | Project documentation |
| `requirements.txt` | Required Python libraries |

## Installation and Execution

### 1. Install Python
Install Python 3.10 or above.

### 2. Clone the Repository
```bash
git clone https://github.com/sahapreeth23-rock-it/CloudGuard.git
```

### 3. Open the Project Folder
```bash
cd CloudGuard
```

### 4. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 5. Run the Program
```bash
python cloudguard.py
```

The program displays the graph-theoretic results and generates PNG visualizations.

To also open the Matplotlib windows, run:

```bash
python cloudguard.py --show
```

## Expected Outcomes
CloudGuard demonstrates how graph theory and partial orders can help identify microservice dependencies, verify deployment prerequisites, generate a valid startup sequence, and detect circular dependencies.

## Author
Developed as a case-based PBL project for **Discrete Mathematics and Graph Theory (DMGT)**.