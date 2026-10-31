#!/usr/bin/env python3
"""
CloudGuard: Cloud Microservice Dependency and Hierarchy Mapper
A Graph-Theoretic Approach to Microservice Dependency Mapping and
Deployment Order Verification.

Subject : Discrete Mathematics and Graph Theory (DMGT)
Requires: Python 3.10+, networkx, matplotlib   (pip install networkx matplotlib)

ARROW CONVENTION (used everywhere in this program and in the report):
    A -> B   means   "A depends on B"   =>   B must be available before A starts.

Run:
    python cloudguard.py            # prints results, saves PNG images
    python cloudguard.py --show     # also opens the Matplotlib windows
"""

import argparse
import itertools

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# ----------------------------------------------------------------------
# 1. CORE SETS AND ILLUSTRATIVE DATA
# ----------------------------------------------------------------------
# Row/column order used by EVERY matrix in this program:
MICROSERVICES = ["Auth", "Prod", "Ord", "Pay", "Inv", "Notif"]          # set M

FULL_NAMES = {
    "Auth": "Authentication", "Prod": "Product", "Ord": "Order",
    "Pay": "Payment", "Inv": "Inventory", "Notif": "Notification",
}

ENDPOINTS = ["/login", "/products", "/orders", "/payment",
             "/inventory", "/notify"]                                    # set E

DATABASES = ["UserDB", "ProductDB", "OrderDB", "PaymentDB",
             "InventoryDB"]                                              # set D

# Direct dependency relation R_dep: (A, B) means "A depends on B".
DEPENDENCIES = [
    ("Prod", "Auth"),
    ("Ord", "Auth"),
    ("Ord", "Prod"),
    ("Pay", "Ord"),
    ("Inv", "Ord"),
    ("Notif", "Ord"),
]

# API permission relation R_perm (illustrative scheme, NOT a security standard).
PERMISSION_LEVELS = ["Public", "User", "Admin"]          # Public < User < Admin
ENDPOINT_PERMISSION = {
    "/login": "Public",
    "/products": "Public",
    "/orders": "User",
    "/payment": "User",
    "/inventory": "Admin",
    "/notify": "Admin",
}

# Illustrative links between the three sets.
ENDPOINT_SERVICE = {
    "/login": "Auth", "/products": "Prod", "/orders": "Ord",
    "/payment": "Pay", "/inventory": "Inv", "/notify": "Notif",
}
SERVICE_DATABASE = {
    "Auth": "UserDB", "Prod": "ProductDB", "Ord": "OrderDB",
    "Pay": "PaymentDB", "Inv": "InventoryDB", "Notif": "OrderDB",
}

# Deployment environments for the equivalence relation R_env (illustrative).
ENVIRONMENT = {
    "Auth": "Application Cluster A", "Prod": "Application Cluster A",
    "Ord": "Application Cluster B", "Notif": "Application Cluster B",
    "Pay": "Application Cluster C", "Inv": "Application Cluster C",
}

NAVY, MID, LIGHT = "#1F3864", "#2E75B6", "#9DC3E6"


# ----------------------------------------------------------------------
# ALGORITHM 1 - Construct the direct dependency graph
# ----------------------------------------------------------------------
def build_dependency_graph(services, dependencies):
    """Return a DiGraph in which edge A -> B means 'A depends on B'."""
    graph = nx.DiGraph()
    graph.add_nodes_from(services)
    graph.add_edges_from(dependencies)
    return graph


# ----------------------------------------------------------------------
# ALGORITHM 2 - Generate the relation matrix
# ----------------------------------------------------------------------
def relation_matrix(graph, order):
    """D[i][j] = 1  <=>  order[i] directly depends on order[j]."""
    n = len(order)
    index = {name: i for i, name in enumerate(order)}
    matrix = [[0] * n for _ in range(n)]
    for a, b in graph.edges():
        matrix[index[a]][index[b]] = 1
    return matrix


def print_matrix(matrix, order, title):
    print(f"\n{title}")
    print("Row/column order:", ", ".join(order))
    width = 7
    print(" " * width + "".join(f"{name:>{width}}" for name in order))
    for name, row in zip(order, matrix):
        print(f"{name:<{width}}" + "".join(f"{v:>{width}}" for v in row))


# ----------------------------------------------------------------------
# ALGORITHM 3 - Reflexive-transitive prerequisite relation (Warshall)
# ----------------------------------------------------------------------
def prerequisite_closure(direct):
    """P[i][j] = 1 <=> i == j, or j is a direct/indirect prerequisite of i."""
    n = len(direct)
    p = [row[:] for row in direct]
    for i in range(n):                      # reflexive pairs
        p[i][i] = 1
    for k in range(n):                      # transitive pairs (Warshall)
        for i in range(n):
            if p[i][k]:
                for j in range(n):
                    if p[k][j]:
                        p[i][j] = 1
    return p


def relation_pairs(matrix, order):
    return [(order[i], order[j]) for i in range(len(order))
            for j in range(len(order)) if matrix[i][j]]


# ----------------------------------------------------------------------
# ALGORITHM 4 - Verify reflexivity, antisymmetry, transitivity
# ----------------------------------------------------------------------
def check_reflexive(m, order):
    return [(order[i], order[i]) for i in range(len(order)) if not m[i][i]]


def check_antisymmetric(m, order):
    n = len(order)
    return [(order[i], order[j]) for i in range(n) for j in range(i + 1, n)
            if m[i][j] and m[j][i]]


def check_transitive(m, order):
    n = len(order)
    return [(order[i], order[k], order[j])
            for i in range(n) for k in range(n) for j in range(n)
            if m[i][k] and m[k][j] and not m[i][j]]


def verify_partial_order(m, order, label):
    refl = check_reflexive(m, order)
    anti = check_antisymmetric(m, order)
    trans = check_transitive(m, order)
    print(f"\nPartial-order verification for {label}")
    print(f"  Reflexive     : {'PASS' if not refl else 'FAIL'}"
          + (f"  missing: {refl}" if refl else ""))
    print(f"  Antisymmetric : {'PASS' if not anti else 'FAIL'}"
          + (f"  two-way pairs: {anti}" if anti else ""))
    print(f"  Transitive    : {'PASS' if not trans else 'FAIL'}"
          + (f"  missing (A,B,C): {trans}" if trans else ""))
    ok = not (refl or anti or trans)
    print(f"  Result        : {'PARTIAL ORDER' if ok else 'NOT A PARTIAL ORDER'}")
    return ok


# ----------------------------------------------------------------------
# ALGORITHM 5 - Hasse diagram edges (remove self-loops, transitive edges)
# ----------------------------------------------------------------------
def hasse_edges(p, order):
    n = len(order)
    edges = []
    for i in range(n):
        for j in range(n):
            if i == j or not p[i][j]:
                continue                                  # no self-loops
            transitive = any(k not in (i, j) and p[i][k] and p[k][j]
                             for k in range(n))
            if not transitive:
                edges.append((order[i], order[j]))
    return edges


# ----------------------------------------------------------------------
# ALGORITHM 8 - Cycle detection (used before topological sorting)
# ----------------------------------------------------------------------
def format_cycle(cycle):
    """Turn the edge list from nx.find_cycle into 'A -> B -> C -> A'."""
    nodes = [edge[0] for edge in cycle] + [cycle[0][0]]
    return " -> ".join(nodes)


def find_dependency_cycle(graph):
    """Return a list of edges forming a cycle, or None if the graph is a DAG."""
    try:
        return nx.find_cycle(graph, orientation="original")
    except nx.NetworkXNoCycle:
        return None


# ----------------------------------------------------------------------
# ALGORITHM 6 - Topological deployment order
# ----------------------------------------------------------------------
def deployment_order(graph, order):
    """Return a valid boot sequence (prerequisites first) or None if cyclic."""
    if find_dependency_cycle(graph) is not None:
        return None
    # Reverse every edge: B -> A now means "B must start before A".
    boot_graph = graph.reverse(copy=True)
    return list(nx.lexicographical_topological_sort(boot_graph, key=order.index))


def count_valid_orders(graph, order):
    """Brute force (6! = 720 permutations): count all valid boot sequences."""
    count = 0
    for perm in itertools.permutations(order):
        pos = {name: i for i, name in enumerate(perm)}
        if all(pos[b] < pos[a] for a, b in graph.edges()):
            count += 1
    return count


def boot_layers(graph):
    """Group services into layers that can start together."""
    boot_graph = graph.reverse(copy=True)
    return [sorted(layer, key=MICROSERVICES.index)
            for layer in nx.topological_generations(boot_graph)]


# ----------------------------------------------------------------------
# ALGORITHM 7 - Equivalence classes by deployment environment
# ----------------------------------------------------------------------
def group_by_environment(env_map, order):
    classes = {}
    for service in order:
        classes.setdefault(env_map[service], []).append(service)
    return classes


def verify_equivalence_partition(classes, order):
    members = [s for group in classes.values() for s in group]
    non_empty = all(len(g) > 0 for g in classes.values())
    disjoint = len(members) == len(set(members))
    covers = set(members) == set(order)
    return non_empty, disjoint, covers


def environment_relation_pairs(env_map, order):
    return [(a, b) for a in order for b in order if env_map[a] == env_map[b]]


# ----------------------------------------------------------------------
# VISUALISATION (Matplotlib + NetworkX)
# ----------------------------------------------------------------------
def _draw_digraph(edges, nodes, pos, title, note, filename, show):
    g = nx.DiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    fig, ax = plt.subplots(figsize=(8, 5.2))
    nx.draw_networkx_nodes(g, pos, node_color=NAVY, node_size=2600, ax=ax)
    nx.draw_networkx_labels(g, pos, font_color="white", font_size=11,
                            font_weight="bold", ax=ax)
    nx.draw_networkx_edges(g, pos, edge_color=MID, width=2.2, arrows=True,
                           arrowstyle="-|>", arrowsize=24, node_size=2600, ax=ax)
    ax.set_title(title, fontsize=13, fontweight="bold", color=NAVY)
    ax.text(0.5, -0.04, note, transform=ax.transAxes, ha="center",
            fontsize=10, color=NAVY)
    ax.margins(0.18)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(filename, dpi=200, bbox_inches="tight")
    print(f"Saved image: {filename}")
    if show:
        plt.show()
    plt.close(fig)


def draw_dependency_graph(graph, filename, show):
    pos = {"Auth": (0, 3), "Prod": (-1.6, 2), "Ord": (0, 1),
           "Pay": (-2.4, 0), "Inv": (0, 0), "Notif": (2.4, 0)}
    _draw_digraph(list(graph.edges()), list(graph.nodes()), pos,
                  "CloudGuard - Direct Dependency Graph",
                  "Arrow A -> B means: A depends on B (B must start first)",
                  filename, show)


def draw_hasse(edges, order, filename, show):
    g = nx.DiGraph()
    g.add_nodes_from(order)
    g.add_edges_from(edges)
    # level 0 (top) = services with no prerequisites; deeper = more prerequisites
    depth = {}
    for node in reversed(list(nx.topological_sort(g))):
        succ = list(g.successors(node))
        depth[node] = 0 if not succ else 1 + max(depth[s] for s in succ)
    levels = {}
    for node in order:
        levels.setdefault(depth[node], []).append(node)
    pos = {}
    for d, nodes in levels.items():
        for i, node in enumerate(nodes):
            pos[node] = ((i - (len(nodes) - 1) / 2) * 2.4, -d * 1.6)
    _draw_digraph(edges, order, pos,
                  "CloudGuard - Hasse Diagram of the Prerequisite Relation",
                  "Arrow A -> B: A depends on B.  Prerequisites are drawn higher "
                  "(Auth boots first).",
                  filename, show)


def draw_matrices(d, p, order, filename, show):
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.4))
    cmap = ListedColormap(["#FFFFFF", LIGHT])
    for ax, mat, title in (
        (axes[0], d, "Direct dependency matrix D\n(1 = row directly depends on column)"),
        (axes[1], p, "Prerequisite matrix P\n(1 = column is row itself or a prerequisite)"),
    ):
        ax.imshow(mat, cmap=cmap, vmin=0, vmax=1)
        ax.set_xticks(range(len(order)), order)
        ax.set_yticks(range(len(order)), order)
        ax.xaxis.tick_top()
        ax.set_xticks([x - 0.5 for x in range(len(order) + 1)], minor=True)
        ax.set_yticks([y - 0.5 for y in range(len(order) + 1)], minor=True)
        ax.grid(which="minor", color=NAVY, linewidth=1)
        ax.tick_params(which="both", length=0)
        for i in range(len(order)):
            for j in range(len(order)):
                ax.text(j, i, mat[i][j], ha="center", va="center",
                        fontsize=12, fontweight="bold", color=NAVY)
        ax.set_title(title, fontsize=11, color=NAVY, pad=28)
    fig.tight_layout()
    fig.savefig(filename, dpi=200, bbox_inches="tight")
    print(f"Saved image: {filename}")
    if show:
        plt.show()
    plt.close(fig)


# ----------------------------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------------------------
def banner(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="CloudGuard DMGT project")
    parser.add_argument("--show", action="store_true",
                        help="open Matplotlib windows as well as saving PNGs")
    args = parser.parse_args()
    order = MICROSERVICES

    banner("CLOUDGUARD - Convention:  A -> B  means  A depends on B")

    # --- Sets ---------------------------------------------------------
    banner("1. CORE SETS")
    print("M (microservices):", MICROSERVICES, " |M| =", len(MICROSERVICES))
    print("E (API endpoints):", ENDPOINTS, " |E| =", len(ENDPOINTS))
    print("D (databases)    :", DATABASES, " |D| =", len(DATABASES))

    # --- Algorithm 1 --------------------------------------------------
    banner("2. DIRECT DEPENDENCY GRAPH (Algorithm 1)")
    graph = build_dependency_graph(MICROSERVICES, DEPENDENCIES)
    print(f"Nodes: {graph.number_of_nodes()}   Edges: {graph.number_of_edges()}")
    for a, b in graph.edges():
        print(f"  {a} -> {b}    ({FULL_NAMES[a]} depends on {FULL_NAMES[b]})")

    # --- Algorithm 2 --------------------------------------------------
    banner("3. RELATION MATRICES (Algorithms 2 and 3)")
    d = relation_matrix(graph, order)
    print_matrix(d, order, "Matrix D: D[X][Y] = 1 means X DIRECTLY depends on Y")

    p = prerequisite_closure(d)
    print_matrix(p, order,
                 "Matrix P: P[X][Y] = 1 means Y = X or Y is a (direct/indirect) "
                 "PREREQUISITE of X")
    pairs = relation_pairs(p, order)
    print(f"\n|R_pre| = {len(pairs)} ordered pairs "
          f"(6 reflexive + {d_ones(d)} direct + "
          f"{len(pairs) - len(order) - d_ones(d)} indirect)")

    # --- Algorithm 4 --------------------------------------------------
    banner("4. PARTIAL-ORDER VERIFICATION (Algorithm 4)")
    verify_partial_order(p, order, "R_pre (prerequisite relation)")
    print("\nFor comparison, the DIRECT dependency matrix D alone:")
    verify_partial_order(d, order, "R_dep (direct dependency relation)")

    # --- Algorithm 5 --------------------------------------------------
    banner("5. HASSE DIAGRAM EDGES (Algorithm 5)")
    edges = hasse_edges(p, order)
    reduction = sorted(nx.transitive_reduction(graph).edges())
    print(f"Covering edges kept ({len(edges)}):")
    for a, b in edges:
        print(f"  {a} -> {b}")
    removed = [e for e in DEPENDENCIES if e not in edges]
    print("Direct dependencies removed as transitive:", removed)
    print("Cross-check with nx.transitive_reduction:",
          "MATCH" if sorted(edges) == reduction else "MISMATCH")

    # --- Algorithms 8 and 6 ------------------------------------------
    banner("6. CYCLE CHECK AND DEPLOYMENT ORDER (Algorithms 8 and 6)")
    cycle = find_dependency_cycle(graph)
    print("Cycle detected:", ("YES: " + format_cycle(cycle)) if cycle
          else "NO (graph is acyclic)")
    seq = deployment_order(graph, order)
    if seq:
        print("Valid deployment order:", " -> ".join(seq))
        print("Boot layers (services in a layer can start together):")
        for i, layer in enumerate(boot_layers(graph)):
            print(f"  Layer {i}: {', '.join(layer)}")
        print("Total number of valid deployment orders:",
              count_valid_orders(graph, order))
    else:
        print("No valid deployment order exists.")

    # --- Cycle demonstration -----------------------------------------
    banner("7. CYCLE DEMONSTRATION (test edge Auth -> Notif added)")
    bad = graph.copy()
    bad.add_edge("Auth", "Notif")          # Auth would depend on Notif
    bad_cycle = find_dependency_cycle(bad)
    print("Cycle detected:", ("YES: " + format_cycle(bad_cycle)) if bad_cycle
          else "NO")
    print("Deployment order:", deployment_order(bad, order)
          or "IMPOSSIBLE - circular dependency")
    bad_p = prerequisite_closure(relation_matrix(bad, order))
    verify_partial_order(bad_p, order, "closure of the cyclic graph")

    # --- Algorithm 7 --------------------------------------------------
    banner("8. EQUIVALENCE CLASSES BY DEPLOYMENT ENVIRONMENT (Algorithm 7)")
    classes = group_by_environment(ENVIRONMENT, order)
    for env, members in classes.items():
        print(f"  {env}: {{{', '.join(members)}}}")
    non_empty, disjoint, covers = verify_equivalence_partition(classes, order)
    print("Classes non-empty:", non_empty, "| pairwise disjoint:", disjoint,
          "| union equals M:", covers)
    print("Number of ordered pairs in R_env:",
          len(environment_relation_pairs(ENVIRONMENT, order)))

    # --- API permissions ---------------------------------------------
    banner("9. API PERMISSION RELATION (illustrative levels, not a standard)")
    print("Levels (low -> high):", " < ".join(PERMISSION_LEVELS))
    for ep in ENDPOINTS:
        print(f"  {ep:<11} requires {ENDPOINT_PERMISSION[ep]:<7} "
              f"(served by {ENDPOINT_SERVICE[ep]}, data in {SERVICE_DATABASE[ENDPOINT_SERVICE[ep]]})")

    # --- Images -------------------------------------------------------
    banner("10. SAVING IMAGES")
    draw_dependency_graph(graph, "dependency_graph.png", args.show)
    draw_hasse(edges, order, "hasse_diagram.png", args.show)
    draw_matrices(d, p, order, "relation_matrices.png", args.show)
    print("\nDone. Insert the PNG files and terminal screenshots into the report.")


def d_ones(matrix):
    return sum(sum(row) for row in matrix)


if __name__ == "__main__":
    main()
