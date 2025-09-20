from __future__ import annotations

from typing import List, Tuple

from strategy_base import StrategyBase, run


Coord = Tuple[int, int]


class FenceStrategy(StrategyBase):
    def generate_static_candidates(self) -> List[Coord]:
        result: List[Coord] = []
        gap = max(3, self.N // 6)
        rows = list(range(2, self.N, gap))
        shift = max(1, self.N // 5)
        for idx, r in enumerate(rows):
            if r == self.s[0] or r == self.t[0]:
                continue
            gate_col = (idx * shift + self.t[1]) % self.N
            for c in range(self.N):
                if self.original_grid[r][c] != ".":
                    continue
                if (r, c) == self.s or (r, c) == self.t:
                    continue
                if abs(c - gate_col) <= 1:
                    continue
                result.append((r, c))
        return result

    def dynamic_candidates(self, pos: Coord, newly) -> List[Coord]:
        cand = super().dynamic_candidates(pos, newly)
        pi, pj = pos
        gap = max(3, self.N // 6)
        row_mod = (pi - 2) % gap if gap else 0
        if row_mod == 0:
            # Seal the far side of the gate to force oscillation
            for dj in (-2, -1, 1, 2):
                target = (pi + 1, pj + dj)
                if 0 <= target[0] < self.N and 0 <= target[1] < self.N:
                    cand.append(target)
        return cand


if __name__ == "__main__":
    run(FenceStrategy)

