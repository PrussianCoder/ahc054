import random
from collections import deque

from board import Board
from constants import EMPTY, NEW_TREE, PATH


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
