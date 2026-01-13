import networkx as nx
from typing import List, Dict, Any, Generator, Optional


def find_isomorphisms_networkx(
        matrix: List[List[Any]],
        node_names: List[str],
        target_adj_dict: Dict[str, set],
        pins: Optional[Dict[str, str]] = None
) -> Generator[Dict[str, str], None, None] | List[Dict[str, str]]:
    """
    Создает графы из матрицы смежности и словаря смежности,
    затем ищет изоморфизмы с помощью алгоритма VF2++.
    """
    G_matrix = nx.Graph()
    G_target = nx.Graph()

    n = len(node_names)
    for i in range(n):
        G_matrix.add_node(node_names[i])
        for j in range(i + 1, n):
            val = matrix[i][j]
            if val not in (0, None, ''):
                G_matrix.add_edge(node_names[i], node_names[j])

    for node, neighbors in target_adj_dict.items():
        G_target.add_node(node)
        for neighbor in neighbors:
            G_target.add_edge(node, neighbor)

    matcher = nx.vf2pp_isomorphism(G_matrix, G_target)

    if pins:
        valid_mappings = []
        for mapping in matcher:
            if all(mapping.get(src) == dst for src, dst in pins.items()):
                valid_mappings.append(mapping)
        return valid_mappings

    return matcher


if __name__ == "__main__":
    P = ['П1', 'П2', 'П3']
    M = [[0, 10, 0], [10, 0, 20], [0, 20, 0]]
    adj = {'A': {'B'}, 'B': {'A', 'C'}, 'C': {'B'}}

    res = list(find_isomorphisms_networkx(M, P, adj))
    print(f"Найдено изоморфизмов: {len(res)}")