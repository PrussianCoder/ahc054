import random
from collections import deque
import heapq

from board import Board
from constants import MAPPING


class BoardSimulatorOptimizedV2:
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

        # 事前計算: ビットマスクとシフト量
        self.bit_masks = {}
        self.bit_shifts = {}
        for i in range(n):
            for j in range(n):
                pos = i * n + j
                self.bit_shifts[(i, j)] = pos
                self.bit_masks[(i, j)] = 1 << pos

    def _board_to_char(self, board: Board, i: int, j: int) -> str:
        """Board状態をRust実装の文字表現に変換"""
        state = board.get_state(i, j)
        return MAPPING[state]

    def _is_passable(self, char: str) -> bool:
        """通行可能なセルかどうか判定"""
        return char in [".", "*", "S", "X"]

    def _change_target(self, target: tuple[int, int]) -> None:
        """ターゲットを変更し、BFSで距離を計算（最適化版）"""
        if self.target == target:
            return

        self.target = target
        if target == (-1, -1):  # None target
            return

        # BFSキャッシュをチェック
        if target in self.dist_cache:
            # キャッシュされた距離情報が現在のrevealed状態と一致するかチェック
            cache_revealed, cached_dist = self.dist_cache[target]
            # revealed状態の変更部分だけ再計算が必要か判定
            if (cache_revealed & self.revealed_bits) == cache_revealed:
                # キャッシュが有効（新しく明らかになった部分だけ追加でBFS）
                self.dist = cached_dist
                self._update_distances_incremental(target)
                return

        # フルBFS実行
        self.dist = [[float("inf")] * self.n for _ in range(self.n)]
        queue = deque([target])
        ti, tj = target
        self.dist[ti][tj] = 0

        while queue:
            i, j = queue.popleft()
            current_dist = self.dist[i][j]

            for di, dj in self.dij:
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < self.n and 0 <= j2 < self.n):
                    continue

                if self.dist[i2][j2] != float("inf"):
                    continue

                # ビット演算で高速チェック
                bit_mask = self.bit_masks[(i2, j2)]
                if not (self.revealed_bits & bit_mask) or (self.passable_bits & bit_mask):
                    self.dist[i2][j2] = current_dist + 1
                    queue.append((i2, j2))

        # キャッシュに保存
        self.dist_cache[target] = (self.revealed_bits, [row[:] for row in self.dist])

    def _update_distances_incremental(self, target: tuple[int, int]):
        """差分BFS - 新しく明らかになった部分だけ距離を更新"""
        queue = deque()

        # 新しく明らかになったセルの隣接セルから探索開始
        for i, j in self.new_revealed:
            for di, dj in self.dij:
                ni, nj = i + di, j + dj
                if (0 <= ni < self.n and 0 <= nj < self.n and
                    self.dist[ni][nj] != float("inf")):
                    queue.append((ni, nj))

        while queue:
            i, j = queue.popleft()
            current_dist = self.dist[i][j]

            for di, dj in self.dij:
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < self.n and 0 <= j2 < self.n):
                    continue

                new_dist = current_dist + 1
                if self.dist[i2][j2] <= new_dist:
                    continue

                bit_mask = self.bit_masks[(i2, j2)]
                if not (self.revealed_bits & bit_mask) or (self.passable_bits & bit_mask):
                    self.dist[i2][j2] = new_dist
                    queue.append((i2, j2))

    def _reveal_from_position(self, pos: tuple[int, int]) -> bool:
        """指定位置からの視線で新しいセルを明らかにする（最適化版）"""
        changed = False
        i, j = pos

        # 4方向の視線を並列的に処理
        for di, dj in self.dij:
            i2, j2 = i + di, j + dj

            # 境界チェックを最適化
            if di != 0:  # 上下方向
                limit = self.n if di > 0 else -1
                step = di
            else:  # 左右方向
                limit = self.n if dj > 0 else -1
                step = dj

            while 0 <= i2 < self.n and 0 <= j2 < self.n:
                bit_mask = self.bit_masks[(i2, j2)]

                # 既に明らかになっているかチェック
                if not (self.revealed_bits & bit_mask):
                    self.revealed_bits |= bit_mask
                    self.new_revealed.append((i2, j2))
                    changed = True

                # 障害物で視線が遮られるかチェック
                if not (self.passable_bits & bit_mask):
                    break

                i2 += di
                j2 += dj

        return changed

    def simulate(self, board: Board) -> int:
        """problem.mdやローカルテスターの実装に従って、盤面をシミュレーションしてスコアを見積もる"""
        # 初期化
        self.board = board

        # ビットセット初期化: 通行可能性を事前計算（一度だけ実行）
        self.passable_bits = 0
        for i in range(self.n):
            for j in range(self.n):
                char = self._board_to_char(board, i, j)
                if self._is_passable(char):
                    self.passable_bits |= self.bit_masks[(i, j)]

        self.p = (self.start_i, self.start_j)  # 現在位置
        self.t = (self.ti, self.tj)  # ゴール位置
        self.target = (-1, -1)  # 現在のターゲット

        # ビットセットで明らかになったセルを管理
        self.revealed_bits = self.bit_masks[(self.start_i, self.start_j)]

        self.new_revealed = [(self.start_i, self.start_j)]
        self.dist = [[float("inf")] * self.n for _ in range(self.n)]
        self.dist_cache = {}  # BFSキャッシュ

        # ターゲット候補を優先度付きキューで管理
        self.unrevealed_targets = []
        for point in reversed(self.point_order):
            heapq.heappush(self.unrevealed_targets, (0, point))

        self.turn = 0

        # 初期視線探索
        self._reveal_from_position(self.p)

        # メインシミュレーションループ
        while self.p != self.t:
            if not self._step():
                return 0  # エラー: 到達不可能

        return self.turn

    def _step(self) -> bool:
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
        if self.revealed_bits & self.bit_masks[(self.t[0], self.t[1])]:
            self._change_target(self.t)

        # 現在のターゲットに到達不可能な場合
        if self.target != (-1, -1) and self.dist[self.p[0]][self.p[1]] == float("inf"):
            self.target = (-1, -1)

        # 新しいターゲットを選択（優先度付きキューから）
        if self.target == (-1, -1) or (
            self.target != self.t and (self.revealed_bits & self.bit_masks[(self.target[0], self.target[1])])
        ):
            self._change_target(self.p)

            while self.unrevealed_targets:
                _, target = heapq.heappop(self.unrevealed_targets)
                if not (self.revealed_bits & self.bit_masks[(target[0], target[1])]) and \
                   self.dist[target[0]][target[1]] != float("inf"):
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
            return False  # No valid move

        # 移動実行
        di, dj = self.dij[next_dir]
        self.p = (self.p[0] + di, self.p[1] + dj)
        return True