from __future__ import annotations

from typing import List, Sequence, Tuple

from strategy_base import DIRS4, StrategyBase, run


Coord = Tuple[int, int]


class OnionStrategy(StrategyBase):
    def generate_static_candidates(self) -> List[Coord]:
        ti, tj = self.t
        max_r = 0
        for i in range(self.N):
            for j in range(self.N):
                if self.original_grid[i][j] == ".":
                    max_r = max(max_r, abs(i - ti), abs(j - tj))
        orientations: Sequence[Coord] = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        result: List[Coord] = []
        for r in range(1, max_r + 1):
            ring: List[Coord] = []
            for i in range(ti - r, ti + r + 1):
                for j in range(tj - r, tj + r + 1):
                    if not (0 <= i < self.N and 0 <= j < self.N):
                        continue
                    if max(abs(i - ti), abs(j - tj)) != r:
                        continue
                    if self.original_grid[i][j] != ".":
                        continue
                    if (i, j) == self.s or (i, j) == self.t:
                        continue
                    ring.append((i, j))
            if not ring:
                continue
            preferred = (ti + orientations[(r - 1) % len(orientations)][0] * r,
                         tj + orientations[(r - 1) % len(orientations)][1] * r)
            door = self._choose_door(ring, preferred)
            for cell in ring:
                if cell == door:
                    continue
                result.append(cell)
        return result

    def dynamic_candidates(self, pos: Coord, newly) -> List[Coord]:
        cand = super().dynamic_candidates(pos, newly)
        # Reinforce the next ring entrance by pre-placing diagonal blockers
        ti, tj = self.t
        pi, pj = pos
        ring_level = max(abs(pi - ti), abs(pj - tj))
        for di, dj in DIRS4:
            target = (pi + di + dj, pj + dj + di)
            if 0 <= target[0] < self.N and 0 <= target[1] < self.N:
                if max(abs(target[0] - ti), abs(target[1] - tj)) >= ring_level:
                    cand.append(target)
        return cand

    def _choose_door(self, ring: Sequence[Coord], preferred: Coord) -> Coord:
        if preferred in ring:
            return preferred
        pi, pj = preferred
        best = ring[0]
        best_score = 10**9
        for i, j in ring:
            d = abs(i - pi) + abs(j - pj)
            if d < best_score:
                best = (i, j)
                best_score = d
        return best


if __name__ == "__main__":
    run(OnionStrategy)

