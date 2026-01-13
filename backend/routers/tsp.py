from typing import List

def tour_length(order: List[int], matrix: List[List[float]]) -> float:
    n = len(order)
    if n == 0:
        return 0.0
    total = 0.0
    for i in range(n - 1):
        total += matrix[order[i]][order[i + 1]]
    return total


def nearest_neighbor(matrix: List[List[float]], start: int = 0) -> List[int]:
    n = len(matrix)
    if n == 0:
        return []
    visited = [False] * n
    order = [start]
    visited[start] = True
    current = start
    for _ in range(n - 1):
        next_idx = None
        best = float('inf')
        for j in range(n):
            if not visited[j] and matrix[current][j] < best:
                best = matrix[current][j]
                next_idx = j
        if next_idx is None:
            break
        order.append(next_idx)
        visited[next_idx] = True
        current = next_idx
    return order


def two_opt(order: List[int], matrix: List[List[float]]) -> List[int]:
    n = len(order)
    if n < 4:
        return order
    improved = True
    best_order = order[:]
    best_len = tour_length(best_order, matrix)
    while improved:
        improved = False
        for i in range(1, n - 2):
            for k in range(i + 1, n - 1):
                new_order = best_order[:i] + best_order[i:k+1][::-1] + best_order[k+1:]
                new_len = tour_length(new_order, matrix)
                if new_len < best_len:
                    best_order = new_order
                    best_len = new_len
                    improved = True
                    break
            if improved:
                break
    return best_order


def solve_tsp_nearest_2opt(matrix: List[List[float]], start: int = 0) -> List[int]:
    """Return an ordered list of indices (a path visiting all nodes).
    This uses nearest-neighbor followed by 2-opt improvement.
    """
    if not matrix:
        return []
    nn = nearest_neighbor(matrix, start=start)
    improved = two_opt(nn, matrix)
    return improved
