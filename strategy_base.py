from __future__ import annotations

from collections import deque
from typing import Iterable, List, Sequence, Tuple


Coord = Tuple[int, int]


DIRS4: Tuple[Coord, ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))


def bfs_shortest_path(grid: Sequence[Sequence[str]], s: Coord, t: Coord) -> List[Coord]:
    """Return one shortest path from s to t (inclusive). Empty if unreachable."""

    n = len(grid)
    si, sj = s
    ti, tj = t
    if grid[si][sj] == "T" or grid[ti][tj] == "T":
        return []
    parent = [[(-1, -1) for _ in range(n)] for _ in range(n)]
    dist = [[-1] * n for _ in range(n)]
    q: deque[Coord] = deque([s])
    dist[si][sj] = 0
    while q:
        i, j = q.popleft()
        if (i, j) == t:
            break
        for di, dj in DIRS4:
            ni, nj = i + di, j + dj
            if not (0 <= ni < n and 0 <= nj < n):
                continue
            if grid[ni][nj] == "T" or dist[ni][nj] != -1:
                continue
            dist[ni][nj] = dist[i][j] + 1
            parent[ni][nj] = (i, j)
            q.append((ni, nj))
    if dist[ti][tj] == -1:
        return []
    path: List[Coord] = []
    cur = t
    while cur != (-1, -1):
        path.append(cur)
        cur = parent[cur[0]][cur[1]]
    path.reverse()
    return path


def is_reachable(grid: Sequence[Sequence[str]], s: Coord, t: Coord) -> bool:
    n = len(grid)
    si, sj = s
    ti, tj = t
    if grid[si][sj] == "T" or grid[ti][tj] == "T":
        return False
    seen = [[False] * n for _ in range(n)]
    q: deque[Coord] = deque([s])
    seen[si][sj] = True
    while q:
        i, j = q.popleft()
        if (i, j) == t:
            return True
        for di, dj in DIRS4:
            ni, nj = i + di, j + dj
            if not (0 <= ni < n and 0 <= nj < n):
                continue
            if seen[ni][nj] or grid[ni][nj] == "T":
                continue
            seen[ni][nj] = True
            q.append((ni, nj))
    return False


def dedup_preserve_order(cells: Iterable[Coord]) -> List[Coord]:
    seen = set()
    result: List[Coord] = []
    for cell in cells:
        if cell in seen:
            continue
        seen.add(cell)
        result.append(cell)
    return result


class StrategyBase:
    def __init__(self, n: int, s: Coord, t: Coord, grid: Sequence[Sequence[str]]):
        self.N = n
        self.s = s
        self.t = t
        self.original_grid = [list(row) for row in grid]
        self.grid = [list(row) for row in grid]
        self.revealed = [[False] * n for _ in range(n)]
        self.revealed[s[0]][s[1]] = True
        self.turn = 0
        self.static_candidates = self.generate_static_candidates()
        self.static_used = False
        self.turn_budget = 60

    # --- hooks ---
    def generate_static_candidates(self) -> List[Coord]:
        return []

    def dynamic_candidates(self, pos: Coord, newly: Sequence[Coord]) -> List[Coord]:
        return self._ray_curtains(pos)

    # --- API ---
    def update_revealed(self, newly: Sequence[Coord]) -> None:
        for x, y in newly:
            if 0 <= x < self.N and 0 <= y < self.N:
                self.revealed[x][y] = True

    def plan_turn(self, pos: Coord, newly: Sequence[Coord]) -> List[Coord]:
        self.turn += 1
        candidates: List[Coord] = []
        if not self.static_used:
            candidates.extend(self.static_candidates)
            self.static_used = True
        candidates.extend(self.dynamic_candidates(pos, newly))
        filtered = dedup_preserve_order(candidates)
        moves = self._select_safe(filtered)
        return moves

    # --- helpers ---
    def _in_bounds(self, i: int, j: int) -> bool:
        return 0 <= i < self.N and 0 <= j < self.N

    def _is_placeable(self, i: int, j: int) -> bool:
        if not self._in_bounds(i, j):
            return False
        if self.revealed[i][j]:
            return False
        return self.grid[i][j] == "."

    def _select_safe(self, candidates: Sequence[Coord]) -> List[Coord]:
        moves: List[Coord] = []
        for i, j in candidates:
            if len(moves) >= self.turn_budget:
                break
            if not self._is_placeable(i, j):
                continue
            self.grid[i][j] = "T"
            if is_reachable(self.grid, self.s, self.t):
                moves.append((i, j))
            else:
                self.grid[i][j] = "."
        return moves

    def _ray_curtains(self, pos: Coord) -> List[Coord]:
        res: List[Coord] = []
        pi, pj = pos
        for di, dj in DIRS4:
            i, j = pi, pj
            while True:
                i += di
                j += dj
                if not self._in_bounds(i, j):
                    break
                if self.grid[i][j] == "T":
                    break
                if not self.revealed[i][j] and self.grid[i][j] == ".":
                    res.append((i, j))
                    break
        return res


def run(strategy_cls: type[StrategyBase]) -> None:
    import sys

    input = sys.stdin.readline
    n, ti, tj = map(int, input().split())
    board = [list(input().strip()) for _ in range(n)]
    s = (0, n // 2)
    t = (ti, tj)
    strategy = strategy_cls(n, s, t, board)

    while True:
        line = input().strip()
        if not line:
            return
        pi, pj = map(int, line.split())
        parts = input().split()
        if not parts:
            return
        m = int(parts[0])
        coords = list(map(int, parts[1:]))
        newly = [(coords[2 * k], coords[2 * k + 1]) for k in range(m)]
        strategy.update_revealed(newly)
        if (pi, pj) == t:
            break
        moves = strategy.plan_turn((pi, pj), newly)
        flat: List[int] = []
        for x, y in moves:
            flat.extend([x, y])
        print(len(moves), *flat)
        sys.stdout.flush()

