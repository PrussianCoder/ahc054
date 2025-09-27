from collections import deque

from board import Board
from constants import EMPTY, GOAL, HIDDEN_TREE, NEW_TREE, PATH


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
            if (
                board.get_state(adj_i, adj_j) == PATH
                or board.get_state(adj_i, adj_j) == HIDDEN_TREE
            ):
                return False

        return True

    def _create_branch(self, board: Board, a_i: int, a_j: int, b_i: int, b_j: int):
        """分岐を作成し、周辺を木で囲む"""
        # AとBをパスに変更
        board.set_state(a_i, a_j, PATH)
        board.set_state(b_i, b_j, PATH)

        # AとBに隣接する空きマスを木に変更
        self._surround_with_trees(board, a_i, a_j)
        self._surround_with_trees(board, b_i, b_j, hidden_tree=True)

    def _surround_with_trees(
        self, board: Board, center_i: int, center_j: int, hidden_tree: bool = False
    ):
        """指定位置の周辺8方向の空きマスを木に変更"""
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
                board.set_state(
                    surr_i, surr_j, NEW_TREE if not hidden_tree else HIDDEN_TREE
                )
