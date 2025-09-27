from collections import deque

from board import Board
from constants import EMPTY, PATH, PATH_2, START, GOAL


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
        target_i, target_j = self._find_nearest_path(board, start_i, start_j, path_positions)
        if target_i == -1:
            return

        # BFSでパスを見つけて接続
        connection_path = self._find_connection_path_bfs(
            board, start_i, start_j, target_i, target_j
        )
        print(f"START connection_path={connection_path}")
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
        target_i, target_j = self._find_nearest_path(board, goal_i, goal_j, path_positions)
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
