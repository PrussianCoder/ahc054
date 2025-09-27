import random
from typing import Optional

from src.board import Board
from src.constants import NEW_TREE, TREE


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
            "paths": [(0, 1), (1, 1)],
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

        # 木を配置する箇所をチェック
        for di, dj in pattern["trees"]:
            ni, nj = ti + di, tj + dj

            # 盤面外の場合はスキップ（配置しないだけ）
            if not (0 <= ni < board.n and 0 <= nj < board.n):
                continue

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
