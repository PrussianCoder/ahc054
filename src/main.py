from __future__ import annotations

import random
import sys
import time
from collections import deque
from typing import Optional

start_time = time.time()

EMPTY = 0
TREE = 1
PATH = 2
PATH_2 = 3
NEW_TREE = 4
START = 5
GOAL = 6


MAPPING = {
    EMPTY: ".",
    TREE: "T",
    PATH: "*",
    PATH_2: "@",
    NEW_TREE: "#",
    START: "S",
    GOAL: "X",
}
MAPPING_INV = {v: k for k, v in MAPPING.items()}

NUM_EVALUATIONS = 10


class Board:
    def __init__(
        self,
        n: int,
        start_i: int,
        start_j: int,
        ti: int,
        tj: int,
        initial_board: list[list[str]],
    ) -> None:
        self.n = n
        self.start_pos = self._to_1d(start_i, start_j)
        self.goal_pos = self._to_1d(ti, tj)
        self.state = []
        for row in initial_board:
            self.state.extend([MAPPING_INV[cell] for cell in row])
        self.state[self.start_pos] = START
        self.state[self.goal_pos] = GOAL
        self.is_up_down_reversed = False
        self.is_left_right_reversed = False

    def _to_1d(self, i: int, j: int) -> int:
        return i * self.n + j

    def to_2d(self, v: int) -> tuple[int, int]:
        return v // self.n, v % self.n

    def get_state(self, x: int, y: int) -> int:
        return self.state[self._to_1d(x, y)]

    def set_state(self, x: int, y: int, state: int) -> None:
        self.state[self._to_1d(x, y)] = state

    def reverse_up_down(self) -> None:
        self.is_up_down_reversed = not self.is_up_down_reversed
        for i1 in range(self.n):
            i2 = self.n - 1 - i1
            if i1 >= i2:
                break
            for j in range(self.n):
                self.state[self._to_1d(i1, j)], self.state[self._to_1d(i2, j)] = (
                    self.state[self._to_1d(i2, j)],
                    self.state[self._to_1d(i1, j)],
                )
        start_x, start_y = self.to_2d(self.start_pos)
        self.start_pos = self._to_1d(self.n - 1 - start_x, start_y)
        goal_x, goal_y = self.to_2d(self.goal_pos)
        self.goal_pos = self._to_1d(self.n - 1 - goal_x, goal_y)

    def reverse_left_right(self) -> None:
        self.is_left_right_reversed = not self.is_left_right_reversed
        for i in range(self.n):
            for j1 in range(self.n):
                j2 = self.n - 1 - j1
                if j1 >= j2:
                    break
                self.state[self._to_1d(i, j1)], self.state[self._to_1d(i, j2)] = (
                    self.state[self._to_1d(i, j2)],
                    self.state[self._to_1d(i, j1)],
                )
        start_x, start_y = self.to_2d(self.start_pos)
        self.start_pos = self._to_1d(start_x, self.n - 1 - start_y)
        goal_x, goal_y = self.to_2d(self.goal_pos)
        self.goal_pos = self._to_1d(goal_x, self.n - 1 - goal_y)

    def __repr__(self) -> str:
        return "\n".join(
            [
                "".join([MAPPING[self.state[self._to_1d(i, j)]] for j in range(self.n)])
                for i in range(self.n)
            ]
        )

    def output(self) -> None:
        new_trees = []
        for i in range(self.n):
            for j in range(self.n):
                if self.get_state(i, j) == NEW_TREE:
                    new_trees.append((i, j))
        print(len(new_trees), " ".join([f"{i} {j}" for i, j in new_trees]))


class Step0Constructor:
    """constructor for step0.
    Create initial start path from START position.
    please read step0_implementation.md for more details"""

    def __init__(self, max_distance=5, seed=None):
        """
        初期化

        Args:
            max_distance (int): スタートからの最大マンハッタン距離
            seed (int): ランダムシードの設定
        """
        self.max_distance = max_distance
        if seed is not None:
            random.seed(seed)

    def construct(self, board: Board) -> Board:
        """construct the board for step0
        Create initial start path from START position.
        please read step0_implementation.md for more details"""

        # スタート位置を取得
        start_i, start_j = self._find_start_position(board)
        if start_i == -1:
            return board  # スタート位置が見つからない場合

        # スタートからマンハッタン距離が3以下かつ空きマスである点Aを選ぶ
        target_i, target_j = self._find_random_target(board, start_i, start_j)
        if target_i == -1:
            return board  # 適切なターゲットが見つからない場合

        # スタートから点Aまでのパスを作成
        path = self._find_path_bfs(board, start_i, start_j, target_i, target_j)
        if len(path) > self.max_distance:
            return board  # パスが最大距離を超える場合
        if not path:
            return board  # パスが見つからない場合

        # パスを盤面に適用
        self._apply_path_to_board(board, path)

        # パス周辺の空きマスを木にする
        self._surround_path_with_trees(board, path)

        # パスをもとに戻す
        self._recover_path_to_board(board, path)

        return board

    def _find_start_position(self, board: Board) -> tuple:
        """スタート位置を見つける"""
        start_x, start_y = board.to_2d(board.start_pos)
        return start_x, start_y

    def _find_random_target(self, board: Board, start_i: int, start_j: int) -> tuple:
        """スタートからマンハッタン距離が3以下かつ空きマスである点をランダムに選ぶ"""
        candidates = []

        for i in range(2):
            for j in range(max(0, start_j - 3), min(board.n, start_j + 4)):
                if board.get_state(i, j) == EMPTY:
                    candidates.append((i, j))

        if not candidates:
            return -1, -1

        # ランダムに選択
        return random.choice(candidates)

    def _find_path_bfs(
        self, board: Board, start_i: int, start_j: int, target_i: int, target_j: int
    ) -> list:
        """BFSを使ってスタートからターゲットまでのパスを見つける"""
        queue = deque([(start_i, start_j, [(start_i, start_j)])])
        visited = set()
        visited.add((start_i, start_j))

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            curr_i, curr_j, path = queue.popleft()

            # ターゲットに到達した場合
            if curr_i == target_i and curr_j == target_j:
                return path

            # 隣接セルを探索
            for di, dj in directions:
                next_i, next_j = curr_i + di, curr_j + dj

                # 境界チェック
                if not (0 <= next_i < board.n and 0 <= next_j < board.n):
                    continue

                # 訪問済みチェック
                if (next_i, next_j) in visited:
                    continue

                # 通行可能かチェック（空きマスまたはターゲット位置）
                state = board.get_state(next_i, next_j)
                if state == EMPTY or (next_i == target_i and next_j == target_j):
                    visited.add((next_i, next_j))
                    new_path = path + [(next_i, next_j)]
                    queue.append((next_i, next_j, new_path))

        return []  # パスが見つからない

    def _apply_path_to_board(self, board: Board, path: list):
        """パスを盤面に適用（ターゲット位置は除く）"""
        for i, (pos_i, pos_j) in enumerate(path):
            # スタート位置とターゲット位置（最後の位置）は除く
            if i == 0:
                continue

            # 空きマスの場合のみパスを設定
            if board.get_state(pos_i, pos_j) == EMPTY:
                board.set_state(pos_i, pos_j, PATH)

    def _recover_path_to_board(self, board: Board, path: list):
        """パスを盤面に適用（ターゲット位置は除く）"""
        for i, (pos_i, pos_j) in enumerate(path):
            # スタート位置とターゲット位置（最後の位置）は除く
            if i == 0:
                continue
            board.set_state(pos_i, pos_j, EMPTY)

    def _surround_path_with_trees(self, board: Board, path: list):
        """パス（ターゲット位置を除く）の周囲の空きマスを木にする"""
        directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]

        for i, (pos_i, pos_j) in enumerate(path):
            # ターゲット位置（最後の位置）は除く
            if i == len(path) - 1:
                continue

            # 周囲8方向をチェック
            for di, dj in directions:
                surround_i, surround_j = pos_i + di, pos_j + dj

                # 境界チェック
                if not (0 <= surround_i < board.n and 0 <= surround_j < board.n):
                    continue

                # 空きマスの場合のみ木を設置
                if board.get_state(surround_i, surround_j) == EMPTY:
                    board.set_state(surround_i, surround_j, NEW_TREE)


class Step1Constructor:
    """constructor for step1.
    Put Trees and Paths around the flower with several patterns.
    please read step1_implementation.md for more details"""

    # 8つのパターンを定義（仕様書通り）
    # 各パターンは花(X)を中心とした相対座標
    # 'trees': 木を配置する位置
    # 'paths': パス（通路）として確保する位置
    PATTERNS = [
        # パターン1
        # .#.
        # **#
        # #X#
        # .#.
        {
            "trees": [(-2, 0), (-1, 1), (0, -1), (0, 1), (1, 0)],
            "paths": [(-1, -1), (-1, 0)],
        },
        # パターン2
        # .#.
        # #**
        # #X#
        # .#.
        {
            "trees": [(-2, 0), (-1, -1), (0, -1), (0, 1), (1, 0)],
            "paths": [(-1, 0), (-1, 1)],
        },
        # パターン3
        # .#.
        # #X#
        # **#
        # .#.
        {
            "trees": [(-1, 0), (0, -1), (0, 1), (1, 1), (2, 0)],
            "paths": [(1, -1), (1, 0)],
        },
        # パターン4
        # .#.
        # #X#
        # #**
        # .#.
        {
            "trees": [(-1, 0), (0, -1), (0, 1), (1, -1), (2, 0)],
            "paths": [(1, 0), (1, 1)],
        },
        # パターン5（4x3の範囲）
        # .*#.
        # #*X#
        # .##.
        {
            "trees": [(-1, 0), (0, -2), (0, 1), (1, -1), (1, 0)],
            "paths": [(-1, -1), (0, -1)],
        },
        # パターン6（4x3の範囲）
        # .##.
        # #*X#
        # .*#.
        {
            "trees": [(-1, -1), (-1, 0), (0, -2), (0, 1), (1, 0)],
            "paths": [(0, -1), (1, -1)],
        },
        # パターン7（4x3の範囲）
        # .#*.
        # #X*#
        # .##.
        {
            "trees": [(-1, 0), (0, -1), (0, 2), (1, 0), (1, 1)],
            "paths": [(-1, 1), (0, 1)],
        },
        # パターン8（4x3の範囲）
        # .##.
        # #X*#
        # .#*.
        {
            "trees": [(-1, 0), (-1, 1), (0, -1), (0, 2), (1, 0)],
            "paths": [(0, 1), (1, 0)],
        },
    ]

    def random_construct(self, board: Board) -> Optional[Board]:
        """randomly construct the board for step1"""
        pattern_idx = random.randint(0, len(self.PATTERNS) - 1)
        if not self.can_apply_pattern(board, pattern_idx):
            return self.random_construct(board)
        return self.construct(board, pattern_idx)

    def can_apply_pattern(self, board: Board, pattern_idx: int) -> bool:
        """
        Check if the pattern can be applied to the board
        """
        pattern = self.PATTERNS[pattern_idx]
        return self._can_apply_pattern(board, pattern)

    def construct(self, board: Board, pattern_idx: int) -> Optional[Board]:
        """construct the board for step1
        if you cannot put path in the specified relative position, return None
        please read step1_implementation.md for more details"""

        # 花の位置を取得
        goal_i, goal_j = board.to_2d(board.goal_pos)
        pattern = self.PATTERNS[pattern_idx]

        # パターンを適用
        return self._apply_pattern(board, goal_i, goal_j, pattern)

    def _can_apply_pattern(self, board: Board, pattern: dict) -> bool:
        """
        パターンが適用可能かチェック
        """
        ti, tj = board.to_2d(board.goal_pos)
        # 通路として必要な箇所をチェック
        for di, dj in pattern["paths"]:
            ni, nj = ti + di, tj + dj

            # 盤面外チェック
            if not (0 <= ni < board.n and 0 <= nj < board.n):
                return False

            # 通路として必要な箇所に既に木がある場合は適用不可
            current_state = board.get_state(ni, nj)
            if current_state == TREE:
                return False

        return True

    def _apply_pattern(self, board: Board, ti: int, tj: int, pattern: dict) -> Board:
        """
        パターンを盤面に適用
        """
        # 木を配置
        for di, dj in pattern["trees"]:
            ni, nj = ti + di, tj + dj

            if not (0 <= ni < board.n and 0 <= nj < board.n):
                continue

            # 既に木がある場合はスキップ
            current_state = board.get_state(ni, nj)
            if current_state == TREE:
                continue

            # 新しい木を配置
            board.set_state(ni, nj, NEW_TREE)

        return board


class Step2Constructor:
    """constructor for step2.
    Create vertical paths on the left edges of the board.
    please read step2_implementation.md for more details"""

    def __init__(self, penalty=6, max_width=8):
        """
        初期化

        Args:
            penalty (int): l<2以下の侵入に対するペナルティ
            max_width (int): 最大幅
        """
        self.penalty = penalty
        self.max_width = max_width
        self.L = 0  # 0から開始（l<2以下の侵入を許可）
        self.dp = None
        self.parent = None
        self.N = 0
        self.R = 0

    def construct(self, board: Board, path_type: int) -> Board:
        """construct the board for step2
        Create vertical paths on the left edges of the board.
        please read step2_implementation.md for more details"""

        # DPを使用して左端の縦道を構築
        path_ranges, min_cost = self._solve(board)

        if path_ranges is None:
            # 経路が見つからない場合はそのまま返す
            return board

        # 経路をboardに反映
        return self._apply_path_to_board(board, path_ranges, path_type)

    def _is_passable(self, board: Board, i: int, j: int) -> bool:
        """セルが通行可能かチェック"""
        if not (0 <= i < board.n and 0 <= j < board.n):
            return False

        state = board.get_state(i, j)
        return state in [EMPTY, PATH]  # 空きマスまたは既存のパスは通行可能

    def _solve(self, board: Board):
        """
        DPを使用して左端の縦道を構築

        Args:
            board (Board): Boardオブジェクト

        Returns:
            tuple: (path_ranges, min_cost) または (None, None) で経路が見つからない場合
        """
        self.N = board.n
        self.R = min(self.max_width, board.n)  # 盤面の幅に合わせる

        # dp[i][l][r] := i行目のl列からr列までの範囲がパスとなるような最小コスト
        self.dp = [
            [[float("inf")] * self.R for _ in range(self.R)] for _ in range(self.N)
        ]

        # parent[i][l][r] := i行目のl列からr列までの範囲に遷移した親ノード (prev_l, prev_r)
        self.parent = [[[None] * self.R for _ in range(self.R)] for _ in range(self.N)]

        # 初期化
        self._initialize(board)

        # 遷移
        self._transition(board)

        # 経路復元
        return self._reconstruct_path()

    def _initialize(self, board: Board):
        """初期化"""
        for l in range(self.L, self.R):
            for r in range(l, self.R):
                # 0行目のl列からr列までが全て通行可能かチェック
                valid = True
                for j in range(l, r + 1):
                    if not self._is_passable(board, 0, j):
                        valid = False
                        break
                if valid:
                    # l<2以下の場合はペナルティを加算
                    penalty = self.penalty if l < 2 else 0
                    self.dp[0][l][r] = r + penalty
                    # 初期状態では親ノードなし
                    self.parent[0][l][r] = None

    def _transition(self, board: Board):
        """遷移"""
        for i in range(1, self.N):
            # パターン1: (l,r)から(r,r2)に遷移する場合
            for r in range(self.L, self.R):
                min_r = float("inf")
                for l in reversed(range(self.L, r + 1)):
                    min_r = min(min_r, self.dp[i - 1][l][r])

                if min_r != float("inf"):
                    for r2 in range(r, self.R):
                        if not self._is_passable(board, i, r2):
                            break
                        # l<2以下の場合はペナルティを加算
                        penalty = self.penalty if r < 2 else 0
                        new_cost = min_r + r2 + penalty
                        if new_cost < self.dp[i][r][r2]:
                            self.dp[i][r][r2] = new_cost
                            # 親ノードを記録（パターン1: (l,r)から(r,r2)への遷移）
                            for l in reversed(range(self.L, r + 1)):
                                if self.dp[i - 1][l][r] == min_r:
                                    self.parent[i][r][r2] = (l, r)
                                    break

            # パターン2: (l,r)から(l2,r)に遷移する場合
            for l in range(self.L, self.R):
                min_l = float("inf")
                for r in range(l, self.R):
                    min_l = min(min_l, self.dp[i - 1][l][r])

                if min_l != float("inf"):
                    for l2 in reversed(range(self.L, l + 1)):
                        if not self._is_passable(board, i, l2):
                            break
                        # l<2以下の場合はペナルティを加算
                        penalty = self.penalty if l2 < 2 else 0
                        new_cost = min_l + l + penalty
                        if new_cost < self.dp[i][l2][l]:
                            self.dp[i][l2][l] = new_cost
                            # 親ノードを記録（パターン2: (l,r)から(l2,r)への遷移）
                            for r in range(l, self.R):
                                if self.dp[i - 1][l][r] == min_l:
                                    self.parent[i][l2][l] = (l, r)
                                    break

    def _reconstruct_path(self):
        """経路復元"""
        # 1. 最適解の探索
        min_cost = float("inf")
        best_l, best_r = -1, -1

        # 最終行から順番に有効な経路を探す
        for i in range(self.N - 1, -1, -1):
            for l in range(self.L, self.R):
                for r in range(l, self.R):
                    if self.dp[i][l][r] < min_cost:
                        min_cost = self.dp[i][l][r]
                        best_l, best_r = l, r
            if min_cost != float("inf"):
                break

        if min_cost == float("inf"):
            return None, None  # 経路が見つからない

        # 2. 経路の逆算（親ノード情報を使用）
        path_ranges = []
        current_l, current_r = best_l, best_r

        for i in range(self.N - 1, -1, -1):
            path_ranges.append((i, current_l, current_r))

            # 親ノード情報を使用して前の行の範囲を取得
            if i > 0 and self.parent[i][current_l][current_r] is not None:
                current_l, current_r = self.parent[i][current_l][current_r]
            else:
                # 親ノード情報がない場合は従来の方法で探索
                found = False
                for l2 in range(self.L, self.R):
                    for r2 in range(l2, self.R):
                        if (
                            self.dp[i - 1][l2][r2] + current_r
                            == self.dp[i][current_l][current_r]
                        ):
                            current_l, current_r = l2, r2
                            found = True
                            break
                    if found:
                        break

        return list(reversed(path_ranges)), min_cost  # 0行目から順番に並び替え

    def _apply_path_to_board(
        self, board: Board, path_ranges: list, tree_type: int
    ) -> Board:
        """経路をboardに適用"""
        for i, l, r in path_ranges:
            for j in range(l, r + 1):
                # 空きマスの場合のみパスを設定
                if board.get_state(i, j) == EMPTY:
                    board.set_state(i, j, tree_type)

        return board


class Step3Constructor:
    """constructor for step3.
    Create paths on the board from left.
    please read step3_implementation.md for more details"""

    def __init__(self):
        """初期化"""
        self.N = 0
        self.dp = None
        self.parent = None
        self.ranges = None

    def construct(
        self, board: Board, path_type: int, start_i: int = 0
    ) -> tuple[Board, bool]:
        """construct the board for step3
        Create paths on the board from left.
        Args:
            board: Board
            path_type: int
            start_i: int

        Returns:
            Board
        please read step3_implementation.md for more details"""

        self.N = board.n

        # Step1: 範囲を計算
        ranges = self._calculate_ranges(board)

        # Step2: 開始点を設定
        start_i, start_j = self._find_starting_point(board, ranges, start_i)
        if start_i == -1:
            return board, True  # 開始点が見つからない場合
        ranges[start_i] = (ranges[start_i][0] - 1, ranges[start_i][1])

        # Step3: DPを実行
        self._initialize_dp(board, ranges, start_i, start_j)
        self._process_dp(board, ranges, start_i)

        # Step4: 経路復元
        path_ranges = self._reconstruct_path(ranges, start_i)
        if not path_ranges:
            return self.construct(board, path_type, start_i + 1)

        # Step5: 経路をboardに適用
        board, is_reached = self._apply_path_to_board(board, path_ranges, path_type)
        return board, is_reached

    def _calculate_ranges(self, board: Board) -> list:
        """各行の有効な範囲を計算"""
        ranges = []

        for i in range(self.N):
            # i行目で最も右側にある`*`を見つける
            left = 2
            for j in range(self.N - 1, -1, -1):
                if board.get_state(i, j) == PATH:
                    break
                up_state = board.get_state(i - 1, j) if i - 1 >= 0 else None
                left_state = board.get_state(i, j - 1) if j - 1 >= 0 else None
                bottom_state = board.get_state(i + 1, j) if i + 1 < self.N else None

                if up_state == PATH or left_state == PATH or bottom_state == PATH:
                    continue
                left = j
            right = min(self.N - 1, left + 10)
            ranges.append((left, right))

        return ranges

    def _find_starting_point(self, board: Board, ranges: list, start_i: int) -> tuple:
        """開始点を見つける"""
        for i in range(start_i, self.N - 1):
            left = ranges[i][0]
            left2_state = board.get_state(i, left - 2) if left - 2 >= 0 else None
            if left2_state == PATH:
                return i, left - 1
        return -1, -1  # 開始点が見つからない

    def _initialize_dp(self, board: Board, ranges: list, start_i: int, start_j: int):
        """DPテーブルを初期化"""
        # dp[i][l][r] := i行目のl列からr列までの範囲がパスとなるような最小コスト
        self.dp = [
            [[float("inf")] * self.N for _ in range(self.N)] for _ in range(self.N)
        ]

        # parent[i][l][r] := 親ノード情報 (prev_l, prev_r)
        self.parent = [[[None] * self.N for _ in range(self.N)] for _ in range(self.N)]

        # 開始行の初期化（開始点から右に延ばす）
        l = start_j
        for r in range(start_j, ranges[start_i][1]):
            if not self._is_passable(board, start_i, r):
                break
            self.dp[start_i][l][r] = r
            self.parent[start_i][l][r] = None  # 開始点なので親なし

    def _is_passable(self, board: Board, i: int, j: int) -> bool:
        """セルが通行可能かチェック"""
        if not (0 <= i < board.n and 0 <= j < board.n):
            return False

        state = board.get_state(i, j)
        return state == EMPTY

    def _process_dp(self, board: Board, ranges: list, start_i: int):
        """DPの遷移処理"""
        for i in range(start_i + 1, self.N):
            # パターン1: (l,r)から(r,r2)に遷移する場合
            for r in range(ranges[i - 1][0], ranges[i - 1][1]):
                if not (ranges[i][0] <= r < ranges[i][1]):
                    continue

                min_r = float("inf")
                for l in range(r + 1):
                    if l < ranges[i - 1][0] or l > ranges[i - 1][1]:
                        continue
                    min_r = min(min_r, self.dp[i - 1][l][r])

                if min_r != float("inf"):
                    for r2 in range(r, ranges[i][1]):
                        if not self._is_passable(board, i, r2):
                            break
                        new_cost = min_r + r2
                        if new_cost < self.dp[i][r][r2]:
                            self.dp[i][r][r2] = new_cost
                            # 親ノードを記録
                            for l in range(r + 1):
                                if (
                                    l >= ranges[i - 1][0]
                                    and l <= ranges[i - 1][1]
                                    and self.dp[i - 1][l][r] == min_r
                                ):
                                    self.parent[i][r][r2] = (l, r)
                                    break

            # パターン2: (l,r)から(l2,l)に遷移する場合
            for l in range(ranges[i - 1][0], ranges[i - 1][1]):
                if not (ranges[i][0] <= l < ranges[i][1]):
                    continue

                min_l = float("inf")
                for r in range(l, ranges[i - 1][1]):
                    min_l = min(min_l, self.dp[i - 1][l][r])

                if min_l != float("inf"):
                    for l2 in reversed(range(ranges[i][0], l + 1)):
                        if not self._is_passable(board, i, l2):
                            break
                        new_cost = min_l + l2
                        if new_cost < self.dp[i][l2][l]:
                            self.dp[i][l2][l] = new_cost
                            # 親ノードを記録
                            for r_prev in range(l, ranges[i - 1][1]):
                                if self.dp[i - 1][l][r_prev] == min_l:
                                    self.parent[i][l2][l] = (l, r_prev)
                                    break
                        if i >= self.N - 2:
                            break

    def _reconstruct_path(self, ranges: list, start_i: int) -> list:
        """経路復元"""
        # 最適解を探索
        min_cost = float("inf")
        best_l, best_r, best_i = -1, -1, -1

        # 最終行から順番に有効な経路を探す
        for i in range(self.N - 1, self.N // 2, -1):
            for l in range(ranges[i][0], ranges[i][1]):
                for r in range(l, ranges[i][1]):
                    if self.dp[i][l][r] < min_cost:
                        min_cost = self.dp[i][l][r]
                        best_l, best_r, best_i = l, r, i
            if min_cost != float("inf"):
                break

        if min_cost == float("inf"):
            return []  # 経路が見つからない

        # 経路の逆算
        path_ranges = []
        current_l, current_r, current_i = best_l, best_r, best_i

        while current_i >= start_i:
            path_ranges.append((current_i, current_l, current_r))

            # 親ノード情報を使用して前の行の範囲を取得
            if (
                current_i > start_i
                and self.parent[current_i][current_l][current_r] is not None
            ):
                prev_l, prev_r = self.parent[current_i][current_l][current_r]
                current_l, current_r = prev_l, prev_r
                current_i -= 1
            else:
                break

        path_ranges.reverse()  # 逆順なので反転
        return path_ranges

    def _apply_path_to_board(
        self, board: Board, path_ranges: list, path_type: int
    ) -> tuple[Board, bool]:
        """経路をboardに適用"""
        for i, l, r in path_ranges:
            for j in range(l, r + 1):
                # 空きマスの場合のみパスを設定
                if board.get_state(i, j) == EMPTY:
                    board.set_state(i, j, path_type)
                    if board.get_state(i, j + 1) == PATH_2:
                        return board, True
        return board, False


class Step4Constructor:
    """constructor for step4.
    Connect paths to START and GOAL positions.
    please read step4_implementation.md for more details"""

    def __init__(self):
        """初期化"""
        pass

    def construct(self, board: Board) -> Board:
        """construct the board for step4
        Connect paths to START and GOAL positions.
        please read step4_implementation.md for more details"""

        # Step1: PATH_2をPATHに変換
        self._convert_path2_to_path(board)

        # Step2: STARTを既存のパスに接続
        self._connect_start_to_path(board)

        # Step3: GOALを既存のパスに接続
        self._connect_goal_to_path(board)

        return board

    def _convert_path2_to_path(self, board: Board):
        """PATH_2(@)をPATH(*)に変換"""
        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) == PATH_2:
                    board.set_state(i, j, PATH)

    def _connect_start_to_path(self, board: Board):
        """STARTを既存のパスに接続"""
        start_i, start_j = board.to_2d(board.start_pos)

        # 既存のパスの位置を見つける
        path_positions = self._find_path_positions(board)
        if not path_positions:
            return

        # STARTから最も近いパス位置を見つける
        target_i, target_j = self._find_nearest_path(
            board, start_i, start_j, path_positions
        )
        if target_i == -1:
            return

        # BFSでパスを見つけて接続
        connection_path = self._find_connection_path_bfs(
            board, start_i, start_j, target_i, target_j
        )
        if connection_path:
            self._apply_connection_path(board, connection_path)

    def _connect_goal_to_path(self, board: Board):
        """GOALを既存のパスに接続"""
        goal_i, goal_j = board.to_2d(board.goal_pos)

        # 既存のパスの位置を見つける
        path_positions = self._find_path_positions(board)
        if not path_positions:
            return

        # GOALから最も近いパス位置を見つける
        target_i, target_j = self._find_nearest_path(
            board, goal_i, goal_j, path_positions
        )
        if target_i == -1:
            return

        # BFSでパスを見つけて接続
        connection_path = self._find_connection_path_bfs(
            board, goal_i, goal_j, target_i, target_j
        )
        if connection_path:
            self._apply_connection_path(board, connection_path)

    def _find_path_positions(self, board: Board) -> list:
        """既存のパス位置を全て取得"""
        path_positions = []
        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) == PATH:
                    path_positions.append((i, j))
        return path_positions

    def _find_nearest_path(
        self, board: Board, from_i: int, from_j: int, path_positions: list
    ) -> tuple:
        """BFSを使って指定位置から最も近いパス位置を見つける（通行可能な経路で）"""
        if not path_positions:
            return -1, -1

        queue = deque([(from_i, from_j, 0)])  # (i, j, distance)
        visited = set()
        visited.add((from_i, from_j))

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        # パス位置を集合に変換して高速検索
        path_set = set(path_positions)

        while queue:
            curr_i, curr_j, distance = queue.popleft()

            # 現在位置がパス位置の場合
            if (curr_i, curr_j) in path_set:
                return curr_i, curr_j

            # 隣接セルを探索
            for di, dj in directions:
                next_i, next_j = curr_i + di, curr_j + dj

                # 境界チェック
                if not (0 <= next_i < board.n and 0 <= next_j < board.n):
                    continue

                # 訪問済みチェック
                if (next_i, next_j) in visited:
                    continue

                # 通行可能かチェック（接続パス用の判定を使用）
                state = board.get_state(next_i, next_j)
                is_target = (next_i, next_j) in path_set
                if self._is_passable_for_connection(state, is_target):
                    visited.add((next_i, next_j))
                    queue.append((next_i, next_j, distance + 1))

        return -1, -1  # パスが見つからない

    def _find_connection_path_bfs(
        self, board: Board, start_i: int, start_j: int, target_i: int, target_j: int
    ) -> list:
        """BFSを使って接続パスを見つける"""
        queue = deque([(start_i, start_j, [(start_i, start_j)])])
        visited = set()
        visited.add((start_i, start_j))

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            curr_i, curr_j, path = queue.popleft()

            # ターゲットに到達した場合
            if curr_i == target_i and curr_j == target_j:
                return path

            # 隣接セルを探索
            for di, dj in directions:
                next_i, next_j = curr_i + di, curr_j + dj

                # 境界チェック
                if not (0 <= next_i < board.n and 0 <= next_j < board.n):
                    continue

                # 訪問済みチェック
                if (next_i, next_j) in visited:
                    continue

                # 通行可能かチェック
                state = board.get_state(next_i, next_j)
                if self._is_passable_for_connection(
                    state, next_i == target_i and next_j == target_j
                ):
                    visited.add((next_i, next_j))
                    new_path = path + [(next_i, next_j)]
                    queue.append((next_i, next_j, new_path))

        return []  # パスが見つからない

    def _is_passable_for_connection(self, state: int, is_target: bool) -> bool:
        """接続用のパス探索で通行可能かチェック"""
        if is_target:
            # ターゲット位置の場合はPATHも通行可能
            return state in [EMPTY, PATH]
        else:
            # それ以外は空きマス、START、GOALのみ通行可能
            # 木（TREE、NEW_TREE）は通行不可
            return state in [EMPTY, START, GOAL]

    def _apply_connection_path(self, board: Board, path: list):
        """接続パスを盤面に適用"""
        for i, (pos_i, pos_j) in enumerate(path):
            # スタート位置とターゲット位置（最後の位置）は除く
            if i == 0 or i == len(path) - 1:
                continue

            # 空きマスの場合のみパスを設定
            if board.get_state(pos_i, pos_j) == EMPTY:
                board.set_state(pos_i, pos_j, PATH)


class Step5Constructor:
    """constructor for step5.
    Create branches from existing paths.
    please read step5_implementation.md for more details"""

    def __init__(self):
        """初期化"""
        pass

    def construct(self, board: Board) -> Board:
        """construct the board for step5
        Create branches from existing paths.
        please read step5_implementation.md for more details"""

        # STARTからの距離を計算
        start_distances = self._calculate_distances_from_start(board)

        # パス位置を距離の遠い順にソート
        path_positions = self._get_path_positions_sorted_by_distance(
            board, start_distances
        )

        # 各パス位置について分岐を試行
        for path_i, path_j in path_positions:
            self._try_create_branch(board, path_i, path_j)

        return board

    def _calculate_distances_from_start(self, board: Board) -> dict:
        """STARTからの距離をBFSで計算"""
        start_i, start_j = board.to_2d(board.start_pos)

        queue = deque([(start_i, start_j, 0)])
        distances = {(start_i, start_j): 0}
        visited = set()
        visited.add((start_i, start_j))

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            curr_i, curr_j, dist = queue.popleft()

            for di, dj in directions:
                next_i, next_j = curr_i + di, curr_j + dj

                # 境界チェック
                if not (0 <= next_i < board.n and 0 <= next_j < board.n):
                    continue

                # 訪問済みチェック
                if (next_i, next_j) in visited:
                    continue

                # パスまたはGOALの場合のみ探索を続ける
                state = board.get_state(next_i, next_j)
                if state in [PATH, GOAL]:
                    visited.add((next_i, next_j))
                    distances[(next_i, next_j)] = dist + 1
                    queue.append((next_i, next_j, dist + 1))

        return distances

    def _get_path_positions_sorted_by_distance(
        self, board: Board, distances: dict
    ) -> list:
        """パス位置を距離の遠い順にソート"""
        path_positions = []

        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) == PATH:
                    distance = distances.get((i, j), float("inf"))
                    path_positions.append(((i, j), distance))

        # 距離の遠い順にソート
        path_positions.sort(key=lambda x: x[1], reverse=True)

        # 位置のみを返す
        return [pos for pos, dist in path_positions]

    def _try_create_branch(self, board: Board, path_i: int, path_j: int):
        """指定されたパス位置から分岐を作成を試行"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for di, dj in directions:
            # 点A（隣接する点）
            a_i, a_j = path_i + di, path_j + dj
            # 点B（その先の点）
            b_i, b_j = path_i + 2 * di, path_j + 2 * dj

            # 境界チェック
            if not (
                0 <= a_i < board.n
                and 0 <= a_j < board.n
                and 0 <= b_i < board.n
                and 0 <= b_j < board.n
            ):
                continue

            # 条件1: AとBが両方とも空きマスか
            if not (
                board.get_state(a_i, a_j) == EMPTY
                and board.get_state(b_i, b_j) == EMPTY
            ):
                continue

            # 条件2: AとBに隣接する点のうち、C（現在のパス）以外で`*`であるものがないか
            if not self._check_no_adjacent_paths(board, a_i, a_j, path_i, path_j):
                continue
            if not self._check_no_adjacent_paths(board, b_i, b_j, path_i, path_j):
                continue

            # 条件を満たすので分岐を作成
            self._create_branch(board, a_i, a_j, b_i, b_j)
            return  # 1つの分岐を作成したら終了

    def _check_no_adjacent_paths(
        self, board: Board, check_i: int, check_j: int, exclude_i: int, exclude_j: int
    ) -> bool:
        """指定位置に隣接するパス（除外位置以外）がないかチェック"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for di, dj in directions:
            adj_i, adj_j = check_i + di, check_j + dj

            # 境界チェック
            if not (0 <= adj_i < board.n and 0 <= adj_j < board.n):
                continue

            # 除外位置の場合はスキップ
            if adj_i == exclude_i and adj_j == exclude_j:
                continue

            # パスが隣接している場合はNG
            if board.get_state(adj_i, adj_j) == PATH:
                return False

        return True

    def _create_branch(self, board: Board, a_i: int, a_j: int, b_i: int, b_j: int):
        """分岐を作成し、周辺を木で囲む"""
        # AとBをパスに変更
        board.set_state(a_i, a_j, PATH)
        board.set_state(b_i, b_j, PATH)

        # AとBに隣接する空きマスを木に変更
        self._surround_with_trees(board, a_i, a_j)
        self._surround_with_trees(board, b_i, b_j)

    def _surround_with_trees(self, board: Board, center_i: int, center_j: int):
        """指定位置の周辺4方向の空きマスを木に変更"""
        directions = [
            (-1, 0),
            (0, -1),
            (0, 1),
            (1, 0),
        ]

        for di, dj in directions:
            surr_i, surr_j = center_i + di, center_j + dj

            # 境界チェック
            if not (0 <= surr_i < board.n and 0 <= surr_j < board.n):
                continue

            # 空きマスの場合のみ木を設置
            if board.get_state(surr_i, surr_j) == EMPTY:
                board.set_state(surr_i, surr_j, NEW_TREE)


class Step6Constructor:
    """constructor for step6.
    Post-processing to fill empty cells adjacent to paths.
    please read step6_implementation.md for more details"""

    def __init__(self, seed=None):
        """
        初期化

        Args:
            seed (int): ランダムシードの設定
        """
        if seed is not None:
            random.seed(seed)

    def construct(self, board: Board) -> Board:
        """construct the board for step6
        Post-processing to fill empty cells adjacent to paths.
        please read step6_implementation.md for more details"""

        # Step1: PATHに隣接するEMPTYセルを見つけてキューに追加
        empty_queue = self._find_empty_cells_adjacent_to_paths(board)

        # Step2: キューをシャッフル
        random.shuffle(empty_queue)
        queue = deque(empty_queue)

        # Step3: キューから1つずつ処理
        while queue:
            empty_i, empty_j = queue.popleft()

            # 現在の状態を確認（既に処理されている可能性）
            if board.get_state(empty_i, empty_j) != EMPTY:
                continue

            # 条件をチェック：隣接するPATHが1つだけか
            if self._should_convert_to_path(board, empty_i, empty_j):
                # EMPTYをPATHに変更
                board.set_state(empty_i, empty_j, PATH)

                # 新しくPATHになったセルに隣接するEMPTYセルをキューに追加
                new_empty_cells = self._find_adjacent_empty_cells(
                    board, empty_i, empty_j
                )
                for new_empty_i, new_empty_j in new_empty_cells:
                    queue.append((new_empty_i, new_empty_j))

        # Step4: 残りのすべてのEMPTYセルをNEW_TREEに変更
        self._convert_remaining_empty_to_trees(board)

        return board

    def _find_empty_cells_adjacent_to_paths(self, board: Board) -> list:
        """PATHに隣接するEMPTYセルを全て見つける"""
        empty_cells = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) == EMPTY:
                    # 隣接セルにPATHがあるかチェック
                    has_adjacent_path = False
                    for di, dj in directions:
                        adj_i, adj_j = i + di, j + dj
                        if (
                            0 <= adj_i < board.n
                            and 0 <= adj_j < board.n
                            and board.get_state(adj_i, adj_j) == PATH
                        ):
                            has_adjacent_path = True
                            break

                    if has_adjacent_path:
                        empty_cells.append((i, j))

        return empty_cells

    def _should_convert_to_path(self, board: Board, empty_i: int, empty_j: int) -> bool:
        """EMPTYセルをPATHに変換すべきかチェック"""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        adjacent_paths = 0

        for di, dj in directions:
            adj_i, adj_j = empty_i + di, empty_j + dj

            # 境界チェック
            if not (0 <= adj_i < board.n and 0 <= adj_j < board.n):
                continue

            # 隣接セルがPATHかチェック
            if board.get_state(adj_i, adj_j) == PATH:
                adjacent_paths += 1

        # 隣接するPATHが1つだけの場合に変換
        return adjacent_paths == 1

    def _find_adjacent_empty_cells(
        self, board: Board, center_i: int, center_j: int
    ) -> list:
        """指定位置に隣接するEMPTYセルを見つける"""
        empty_cells = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for di, dj in directions:
            adj_i, adj_j = center_i + di, center_j + dj

            # 境界チェック
            if not (0 <= adj_i < board.n and 0 <= adj_j < board.n):
                continue

            # EMPTYセルの場合に追加
            if board.get_state(adj_i, adj_j) == EMPTY:
                empty_cells.append((adj_i, adj_j))

        return empty_cells

    def _convert_remaining_empty_to_trees(self, board: Board):
        """残りのすべてのEMPTYセルをNEW_TREEに変更"""
        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) == EMPTY:
                    board.set_state(i, j, NEW_TREE)


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


N, ti, tj = map(int, input().split())
board_input = [input() for _ in range(N)]
start_i, start_j = map(int, input().split())
input()
constructor_0 = Step0Constructor()
constructor_1 = Step1Constructor()
constructor_2 = Step2Constructor()
constructor_3 = Step3Constructor()
constructor_4 = Step4Constructor()
constructor_5 = Step5Constructor()
constructor_6 = Step6Constructor()
score_evaluators = [
    BoardSimulator(N, start_i, start_j, ti, tj) for _ in range(NUM_EVALUATIONS)
]

best_score = -1
best_board = None
all_cycle = 0

while time.time() - start_time < 2.0:
    print("start", time.time() - start_time, file=sys.stderr)
    board = Board(N, start_i, start_j, ti, tj, board_input)
    board = constructor_0.construct(board)
    board = constructor_1.random_construct(board)
    board = constructor_2.construct(board, PATH)
    board.reverse_left_right()
    board = constructor_2.construct(board, PATH_2)
    board.reverse_left_right()
    cycle = 0
    print("step3 start", time.time() - start_time, file=sys.stderr)
    while True:
        if cycle % 2 == 1:
            board.reverse_up_down()
        board, is_reached = constructor_3.construct(board, PATH)
        if cycle % 2 == 1:
            board.reverse_up_down()
        cycle += 1
        if is_reached:
            break
    print("step3 end", time.time() - start_time, file=sys.stderr)
    board = constructor_4.construct(board)
    print("step4 end", time.time() - start_time, file=sys.stderr)
    board = constructor_5.construct(board)
    board = constructor_6.construct(board)
    print("step6 end", time.time() - start_time, file=sys.stderr)
    if board.is_up_down_reversed:
        board.reverse_up_down()
    if board.is_left_right_reversed:
        board.reverse_left_right()
    score_min = float("inf")
    for score_evaluator in score_evaluators:
        score = score_evaluator.simulate(board)
        score_min = min(score_min, score)
        if score_min < best_score:
            break
    print("score end", time.time() - start_time, file=sys.stderr)
    if score_min > best_score:
        best_score = score_min
        best_board = board
    all_cycle += 1

best_board.output()
print(-1)
print(f"Cycle: {all_cycle}", file=sys.stderr)
print(f"Best score: {best_score}", file=sys.stderr)
