from collections import deque
from typing import List, Tuple, Optional

from board import Board
from constants import EMPTY, TREE, PATH, PATH_2, NEW_TREE, START, GOAL


class BoardChecker:
    """constructor for board_checker.
    Calculate the penalty of the board around X.
    please read board_checker.md for more details"""

    def __init__(self):
        """
        Initialize the board checker.
        """
        self.directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 右、左、下、上

    def check(self, board: Board) -> int:
        """
        Calculate the penalty of the board around X.
        please read board_checker.md for more details

        Returns:
            int: ペナルティ値（0以上の整数）
        """
        # 1. SからXに向かう最短パスの経路を求める
        shortest_path = self._find_shortest_path(board)
        if not shortest_path:
            # パスが見つからない場合は大きなペナルティを返す
            return 999

        # 2. Xの周囲の#のセルについて、@と接しているかどうかをカウントする
        penalty = self._calculate_penalty(board, shortest_path)

        return penalty

    def _find_shortest_path(self, board: Board) -> Optional[List[Tuple[int, int]]]:
        """
        SからXに向かう最短パスをBFSで求める

        Args:
            board: 盤面

        Returns:
            Optional[List[Tuple[int, int]]]: 最短パス（見つからない場合はNone）
        """
        start_x, start_y = board.to_2d(board.start_pos)
        goal_x, goal_y = board.to_2d(board.goal_pos)

        # BFS用のキューと訪問管理
        queue = deque([(start_x, start_y, [(start_x, start_y)])])
        visited = set()
        visited.add((start_x, start_y))

        while queue:
            x, y, path = queue.popleft()

            # ゴールに到達した場合
            if x == goal_x and y == goal_y:
                return path

            # 4方向への移動を試す（上下左右の優先順位）
            for dx, dy in self.directions:
                nx, ny = x + dx, y + dy

                # 境界チェック
                if not (0 <= nx < board.n and 0 <= ny < board.n):
                    continue

                # 既に訪問済みかチェック
                if (nx, ny) in visited:
                    continue

                # 通行可能セルかチェック
                cell_state = board.get_state(nx, ny)
                if self._is_passable(cell_state):
                    visited.add((nx, ny))
                    new_path = path + [(nx, ny)]
                    queue.append((nx, ny, new_path))

        return None

    def _is_passable(self, cell_state: int) -> bool:
        """
        セルが通行可能かチェック

        Args:
            cell_state: セルの状態

        Returns:
            bool: 通行可能ならTrue
        """
        return cell_state in [EMPTY, PATH, PATH_2, START, GOAL]

    def _calculate_penalty(self, board: Board, shortest_path: List[Tuple[int, int]]) -> int:
        """
        Xの周囲の#のセルについて、最短パスと接しているかチェックしペナルティを計算

        Args:
            board: 盤面
            shortest_path: S→Xの最短パス

        Returns:
            int: ペナルティ値
        """
        goal_x, goal_y = board.to_2d(board.goal_pos)

        # 最短パスをセットに変換（高速な検索のため）
        path_set = set(shortest_path)

        # Xに隣接する@は除外（仕様：Xに隣接している@は.に戻す）
        path_cells = set()
        for px, py in shortest_path:
            # ゴールに隣接していない@のみを対象とする
            if abs(px - goal_x) + abs(py - goal_y) > 1:
                path_cells.add((px, py))

        penalty = 0

        # Xの4方向について、最初の#セルを見つける
        for dx, dy in self.directions:
            # Xから方向に進んで最初の#を探す
            nx, ny = goal_x + dx, goal_y + dy

            while 0 <= nx < board.n and 0 <= ny < board.n:
                cell_state = board.get_state(nx, ny)

                # #（TREE または NEW_TREE）を見つけた場合
                if cell_state in [TREE, NEW_TREE]:
                    # この#が@と隣接しているかチェック
                    if not self._is_adjacent_to_path(nx, ny, path_cells, board.n):
                        penalty += 1
                    break  # 最初の#を見つけたので終了

                # 次のセルへ進む
                nx, ny = nx + dx, ny + dy

        return penalty

    def _is_adjacent_to_path(self, tree_x: int, tree_y: int, path_cells: set, board_size: int) -> bool:
        """
        指定された#セルが@セル（最短パス）と隣接しているかチェック

        Args:
            tree_x, tree_y: #セルの座標
            path_cells: @セル（最短パス）のセット
            board_size: 盤面サイズ

        Returns:
            bool: 隣接していればTrue
        """
        for dx, dy in self.directions:
            adj_x, adj_y = tree_x + dx, tree_y + dy

            # 境界チェック
            if not (0 <= adj_x < board_size and 0 <= adj_y < board_size):
                continue

            # 隣接セルが@（最短パス）に含まれているかチェック
            if (adj_x, adj_y) in path_cells:
                return True

        return False
