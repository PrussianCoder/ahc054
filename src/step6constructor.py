import random
from collections import deque

from board import Board
from constants import EMPTY, NEW_TREE, PATH


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
        【変更点】ゴール周辺の特別な処理を追加
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

        # Step4: 【新規追加】Xからマンハッタン距離がちょうど2のEMPTYセルに対する特別な処理
        self._process_goal_adjacent_empty_cells(board)

        # Step5: 残りのすべてのEMPTYセルをNEW_TREEに変更
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

    def _process_goal_adjacent_empty_cells(self, board: Board):
        """【新規追加】Xからマンハッタン距離がちょうど2のEMPTYセルに対する特別な処理"""
        # ゴール位置を取得
        goal_x, goal_y = board.to_2d(board.goal_pos)

        # マンハッタン距離がちょうど2のEMPTYセルを探す
        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) != EMPTY:
                    continue

                # マンハッタン距離をチェック（【修正】ちょうど2のもののみ対象）
                manhattan_distance = abs(i - goal_x) + abs(j - goal_y)
                if manhattan_distance != 2:
                    continue

                # 4つの方向パターンをチェック
                if self._check_corner_path_pattern(board, i, j):
                    board.set_state(i, j, PATH)

    def _check_corner_path_pattern(self, board: Board, x: int, y: int) -> bool:
        """指定位置で3点の組が全てPATHかチェック"""
        # 仕様書に記載された4パターン
        patterns = [
            [(x + 1, y), (x + 1, y + 1), (x, y + 1)],  # ([x+1,y], [x+1,y+1],[x,y+1])
            [(x + 1, y), (x + 1, y - 1), (x, y - 1)],  # ([x+1,y], [x+1,y-1],[x,y-1])
            [(x - 1, y), (x - 1, y + 1), (x, y + 1)],  # ([x-1,y], [x-1,y+1],[x,y+1])
            [(x - 1, y), (x - 1, y - 1), (x, y - 1)],  # ([x-1,y], [x-1,y-1],[x,y-1])
        ]

        for pattern in patterns:
            # パターン内の全ての点がPATHかチェック
            all_path = True
            for px, py in pattern:
                # 境界チェック
                if not (0 <= px < board.n and 0 <= py < board.n):
                    all_path = False
                    break
                # PATH状態チェック
                if board.get_state(px, py) != PATH:
                    all_path = False
                    break

            # いずれかのパターンが全てPATHなら True を返す
            if all_path:
                return True

        return False

    def _convert_remaining_empty_to_trees(self, board: Board):
        """残りのすべてのEMPTYセルをNEW_TREEに変更"""
        for i in range(board.n):
            for j in range(board.n):
                if board.get_state(i, j) == EMPTY:
                    board.set_state(i, j, NEW_TREE)
