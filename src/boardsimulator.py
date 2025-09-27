import random
from collections import deque

from board import Board
from constants import MAPPING


class BoardSimulator:
    def __init__(
        self,
        n: int,
        start_i: int,
        start_j: int,
        ti: int,
        tj: int,
        point_order: list[tuple[int, int]] = None,
    ):
        self.n = n
        self.start_i = start_i
        self.start_j = start_j
        self.ti = ti
        self.tj = tj
        if point_order is None:
            self.point_order = [(i, j) for i in range(n) for j in range(n)]
            self.point_order.remove((ti, tj))
            self.point_order.remove((start_i, start_j))
            random.shuffle(self.point_order)
            self.point_order.append((ti, tj))
        else:
            self.point_order = point_order

        self.point_order.append((ti, tj))

        # Direction vectors: up, down, left, right
        self.dij = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def _board_to_char(self, board: Board, i: int, j: int) -> str:
        """Board状態をRust実装の文字表現に変換"""
        state = board.get_state(i, j)
        return MAPPING[state]

    def _is_passable(self, char: str) -> bool:
        """通行可能なセルかどうか判定"""
        return char in [".", "*", "S", "X"]

    def _change_target(self, target: tuple[int, int]) -> None:
        """ターゲットを変更し、BFSで距離を計算"""
        if self.target == target:
            return

        self.target = target
        if target == (-1, -1):  # None target
            return

        # BFS for distance calculation
        self.dist = [[float("inf")] * self.n for _ in range(self.n)]
        queue = deque([target])
        ti, tj = target
        self.dist[ti][tj] = 0

        while queue:
            i, j = queue.popleft()
            for di, dj in self.dij:
                i2, j2 = i + di, j + dj
                if (
                    0 <= i2 < self.n
                    and 0 <= j2 < self.n
                    and self.dist[i2][j2] == float("inf")
                    and (
                        not self.revealed[i2][j2]
                        or self._is_passable(self.board_chars[i2][j2])
                    )
                ):
                    self.dist[i2][j2] = self.dist[i][j] + 1
                    queue.append((i2, j2))

    def _reveal_from_position(self, pos: tuple[int, int]) -> bool:
        """指定位置からの視線で新しいセルを明らかにし、障害物が見つかったかを返す"""
        changed = False
        i, j = pos

        for di, dj in self.dij:
            i2, j2 = i, j
            while True:
                i2 += di
                j2 += dj
                if not (0 <= i2 < self.n and 0 <= j2 < self.n):
                    break

                if not self.revealed[i2][j2]:
                    self.revealed[i2][j2] = True
                    self.new_revealed.append((i2, j2))
                    changed = True

                # 障害物で視線が遮られる
                if not self._is_passable(self.board_chars[i2][j2]):
                    break

        return changed

    def simulate(self, board: Board) -> int:
        """problem.mdやローカルテスターの実装に従って、盤面をシミュレーションしてスコアを見積もる"""
        # 初期化
        self.board = board
        self.board_chars = [
            [self._board_to_char(board, i, j) for j in range(self.n)]
            for i in range(self.n)
        ]
        self.p = (self.start_i, self.start_j)  # 現在位置
        self.t = (self.ti, self.tj)  # ゴール位置
        self.target = (-1, -1)  # 現在のターゲット
        self.revealed = [[False] * self.n for _ in range(self.n)]
        self.revealed[self.start_i][self.start_j] = True
        self.new_revealed = [(self.start_i, self.start_j)]
        self.dist = [[float("inf")] * self.n for _ in range(self.n)]
        self.q = list(reversed(self.point_order))  # Rust実装に合わせて逆順
        self.turn = 0

        # 初期視線探索
        self._reveal_from_position(self.p)

        # メインシミュレーションループ
        while self.p != self.t:
            if not self._step():
                return 0  # エラー: 到達不可能

        return self.turn

    def _step(
        self,
    ) -> bool:
        """1ターンの処理を実行。成功時True、失敗時Falseを返す"""
        self.new_revealed = []
        self.turn += 1

        if self.p == self.t:
            return False  # Too many outputs

        # 視線による探索
        changed = self._reveal_from_position(self.p)

        # ターゲットの再計算が必要な場合
        if changed:
            target = self.target
            self.target = (-1, -1)
            self._change_target(target)

        # ゴールが見つかった場合はゴールをターゲットに
        if self.revealed[self.t[0]][self.t[1]]:
            self._change_target(self.t)

        # 現在のターゲットに到達不可能な場合
        if self.target != (-1, -1) and self.dist[self.p[0]][self.p[1]] == float("inf"):
            self.target = (-1, -1)

        # 新しいターゲットを選択
        if self.target == (-1, -1) or (
            self.target != self.t and self.revealed[self.target[0]][self.target[1]]
        ):
            self._change_target(self.p)

            while True:
                if self.q:
                    target = self.q.pop()
                    if not self.revealed[target[0]][target[1]] and self.dist[target[0]][
                        target[1]
                    ] != float("inf"):
                        self._change_target(target)
                        break
                else:
                    return False  # Not reachable

        # 最短経路に基づいて次の移動を決定
        min_dist = float("inf")
        next_dir = -1

        for dir_idx in range(4):
            di, dj = self.dij[dir_idx]
            i2, j2 = self.p[0] + di, self.p[1] + dj

            if 0 <= i2 < self.n and 0 <= j2 < self.n and self.dist[i2][j2] < min_dist:
                min_dist = self.dist[i2][j2]
                next_dir = dir_idx

        if next_dir == -1:
            # デバッグ情報を追加
            for dir_idx in range(4):
                di, dj = self.dij[dir_idx]
                i2, j2 = self.p[0] + di, self.p[1] + dj
            return False  # No valid move

        # 移動実行
        di, dj = self.dij[next_dir]
        self.p = (self.p[0] + di, self.p[1] + dj)
        return True
