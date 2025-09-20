from __future__ import annotations

from typing import List, Tuple

from strategy_base import DIRS4, StrategyBase, bfs_shortest_path, run


Coord = Tuple[int, int]


class SnakeStrategy(StrategyBase):
    def generate_static_candidates(self) -> List[Coord]:
        path = bfs_shortest_path(self.original_grid, self.s, self.t)
        path_set = set(path)
        buffer: set[Coord] = set(path_set)
        for i, j in path_set:
            for di, dj in DIRS4:
                ni, nj = i + di, j + dj
                if 0 <= ni < self.N and 0 <= nj < self.N:
                    buffer.add((ni, nj))
        result: List[Coord] = []
        for i in range(self.N):
            cols = range(self.N) if i % 2 == 0 else range(self.N - 1, -1, -1)
            for j in cols:
                if self.original_grid[i][j] != ".":
                    continue
                if (i, j) == self.s or (i, j) == self.t:
                    continue
                if (i, j) in buffer:
                    continue
                result.append((i, j))
        return result

    def dynamic_candidates(self, pos: Coord, newly) -> List[Coord]:
        cand = super().dynamic_candidates(pos, newly)
        pi, pj = pos
        # Add side pins perpendicular to movement to discourage shortcuts
        for di, dj in DIRS4:
            ni, nj = pi + di, pj + dj
            if not (0 <= ni < self.N and 0 <= nj < self.N):
                continue
            oi, oj = ni + dj, nj - di  # rotate 90 degrees
            if 0 <= oi < self.N and 0 <= oj < self.N:
                cand.append((oi, oj))
            oi, oj = ni - dj, nj + di
            if 0 <= oi < self.N and 0 <= oj < self.N:
                cand.append((oi, oj))
        return cand


if __name__ == "__main__":
    run(SnakeStrategy)

