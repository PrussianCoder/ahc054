from board import Board
from constants import EMPTY, PATH, PATH_2


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
        print(f"ranges={ranges}")

        # Step2: 開始点を設定
        start_i, start_j = self._find_starting_point(board, ranges, start_i)
        if start_i == -1:
            return board, True  # 開始点が見つからない場合
        ranges[start_i] = (ranges[start_i][0] - 1, ranges[start_i][1])
        print(f"start_i={start_i}, start_j={start_j}")

        # Step3: DPを実行
        self._initialize_dp(board, ranges, start_i, start_j)
        self._process_dp(board, ranges, start_i)

        # Step4: 経路復元
        path_ranges = self._reconstruct_path(ranges, start_i)
        if not path_ranges:
            print(f"No path found at start_i={start_i}, trying next start_i")
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
