import sys
from collections import deque


class Board:
    def __init__(self, N, ti, tj, initial_board):
        self.N = N
        self.flower = (ti, tj)
        self.start = (0, N // 2)
        self.grid = [[cell for cell in row] for row in initial_board]

    def copy(self):
        new_board = Board(self.N, self.flower[0], self.flower[1], [])
        new_board.grid = [row[:] for row in self.grid]
        return new_board

    def is_valid_pos(self, i, j):
        return 0 <= i < self.N and 0 <= j < self.N

    def debug_print(self, message=""):
        print(f"=== {message} ===", file=sys.stderr)
        for i in range(self.N):
            row = []
            for j in range(self.N):
                if (i, j) == self.start:
                    row.append("S")
                elif (i, j) == self.flower:
                    row.append("X")
                else:
                    row.append(self.grid[i][j])
            print("".join(row), file=sys.stderr)
        print(file=sys.stderr)


class ForestMazeGenerator:
    def __init__(self):
        pass

    def step1_surround_flower(self, board):
        """花の周りに木を配置"""
        ti, tj = board.flower
        N = board.N

        board.debug_print("Before Step1")

        # 上下チェック
        up_free = board.is_valid_pos(ti - 1, tj) and board.grid[ti - 1][tj] == "."
        down_free = board.is_valid_pos(ti + 1, tj) and board.grid[ti + 1][tj] == "."

        if up_free or down_free:
            # 左右に木を配置
            if board.is_valid_pos(ti, tj - 1) and board.grid[ti][tj - 1] == ".":
                board.grid[ti][tj - 1] = "#"
            if board.is_valid_pos(ti, tj + 1) and board.grid[ti][tj + 1] == ".":
                board.grid[ti][tj + 1] = "#"

            # 上下のうち片方を通路、もう片方を木にする
            if up_free and down_free:
                # 両方空いている場合は下を優先的に通路にする
                board.grid[ti + 1][tj] = "."
                board.grid[ti - 1][tj] = "#"
                passage_dir = "down"
            elif up_free:
                board.grid[ti - 1][tj] = "."
                if down_free:
                    board.grid[ti + 1][tj] = "#"
                passage_dir = "up"
            else:  # down_free
                board.grid[ti + 1][tj] = "."
                passage_dir = "down"

            # 通路側の2マス先に木を配置
            if (
                passage_dir == "up"
                and board.is_valid_pos(ti - 2, tj)
                and board.grid[ti - 2][tj] == "."
            ):
                board.grid[ti - 2][tj] = "#"
            elif (
                passage_dir == "down"
                and board.is_valid_pos(ti + 2, tj)
                and board.grid[ti + 2][tj] == "."
            ):
                board.grid[ti + 2][tj] = "#"

            # 斜め木の配置
            if tj <= 3 or (N / 2 <= tj < N - 4):
                # 端に近い場合：逆方向に配置
                if (
                    board.is_valid_pos(ti - 1, tj)
                    and board.grid[ti - 1][tj] == "."
                    and board.is_valid_pos(ti - 1, tj - 1)
                    and board.grid[ti - 1][tj - 1] == "."
                ):
                    board.grid[ti - 1][tj - 1] = "#"
                if (
                    board.is_valid_pos(ti + 1, tj)
                    and board.grid[ti + 1][tj] == "."
                    and board.is_valid_pos(ti + 1, tj - 1)
                    and board.grid[ti + 1][tj - 1] == "."
                ):
                    board.grid[ti + 1][tj - 1] = "#"
            else:
                # 上半分：外側に配置
                if (
                    board.is_valid_pos(ti - 1, tj)
                    and board.grid[ti - 1][tj] == "."
                    and board.is_valid_pos(ti - 1, tj + 1)
                    and board.grid[ti - 1][tj + 1] == "."
                ):
                    board.grid[ti - 1][tj + 1] = "#"
                if (
                    board.is_valid_pos(ti + 1, tj)
                    and board.grid[ti + 1][tj] == "."
                    and board.is_valid_pos(ti + 1, tj + 1)
                    and board.grid[ti + 1][tj + 1] == "."
                ):
                    board.grid[ti + 1][tj + 1] = "#"

        else:
            # 上下が両方塞がっている場合
            # 左右に移動して空きマスを探す
            new_ti, new_tj = ti, tj

            # 左を優先的に探す
            if board.is_valid_pos(ti, tj - 1) and board.grid[ti][tj - 1] == ".":
                new_tj = tj - 1
            elif board.is_valid_pos(ti, tj + 1) and board.grid[ti][tj + 1] == ".":
                new_tj = tj + 1

            if new_tj != tj:
                # 移動した位置で処理
                # 元の花の位置の左右を塞ぐ
                if (
                    board.is_valid_pos(ti, tj - 1)
                    and board.grid[ti][tj - 1] == "."
                    and new_tj != tj - 1
                ):
                    board.grid[ti][tj - 1] = "#"
                if (
                    board.is_valid_pos(ti, tj + 1)
                    and board.grid[ti][tj + 1] == "."
                    and new_tj != tj + 1
                ):
                    board.grid[ti][tj + 1] = "#"

                # 新しい位置で上下処理
                if (
                    board.is_valid_pos(new_ti - 1, new_tj)
                    and board.grid[new_ti - 1][new_tj] == "."
                ):
                    board.grid[new_ti - 1][new_tj] = "#"
                if (
                    board.is_valid_pos(new_ti + 1, new_tj)
                    and board.grid[new_ti + 1][new_tj] == "."
                ):
                    board.grid[new_ti + 1][new_tj] = "#"

                # 新しい位置の更に外側を塞ぐ
                if (
                    new_tj < tj
                    and board.is_valid_pos(new_ti, new_tj - 1)
                    and board.grid[new_ti][new_tj - 1] == "."
                ):
                    board.grid[new_ti][new_tj - 1] = "#"
                elif (
                    new_tj > tj
                    and board.is_valid_pos(new_ti, new_tj + 1)
                    and board.grid[new_ti][new_tj + 1] == "."
                ):
                    board.grid[new_ti][new_tj + 1] = "#"

        board.debug_print("After Step1")
        return board

    def has_adjacent_star(self, board, i, j, excluding=None):
        """指定位置に隣接する'*'があるかチェック（excluding位置は除外）"""
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ni, nj = i + di, j + dj
            if excluding and (ni, nj) == excluding:
                continue
            if board.is_valid_pos(ni, nj) and board.grid[ni][nj] == "*":
                return True
        return False

    def step2_create_vertical_paths(self, board):
        """左右端に縦の道を作成"""
        N = board.N

        # 左端の道を作成
        self.create_vertical_path_left(board)
        board.debug_print("After Step2 Left")

        # 右端の道を作成
        self.create_vertical_path_right(board)
        board.debug_print("After Step2 Right")

        return board

    def create_vertical_path_left(self, board):
        """左端に縦の道を作成"""
        N = board.N

        # 開始点を探す
        start_i, start_j = 0, 2
        while start_j < N and board.grid[start_i][start_j] != ".":
            start_j += 1

        if start_j >= N:
            print("Warning: Cannot find start point for left path", file=sys.stderr)
            return False

        board.grid[start_i][start_j] = "*"

        def dfs(i, j):
            if i == N - 1:
                return True

            for di, dj in [(0, -1), (1, 0), (0, 1)]:  # 左、下、右
                ni, nj = i + di, j + dj
                if not board.is_valid_pos(ni, nj) or nj < 2:
                    continue
                if board.grid[ni][nj] != ".":
                    continue
                # 隣接チェック（閉路防止）
                if self.has_adjacent_star(board, ni, nj, excluding=(i, j)):
                    continue

                board.grid[ni][nj] = "*"
                if dfs(ni, nj):
                    return True
                # バックトラック
                board.grid[ni][nj] = "."

            return False

        success = dfs(start_i, start_j)
        if not success:
            print("Warning: Failed to create left vertical path", file=sys.stderr)
        return success

    def create_vertical_path_right(self, board):
        """右端に縦の道を作成"""
        N = board.N

        # 開始点を探す
        start_i, start_j = 0, N - 3
        while start_j >= 0 and board.grid[start_i][start_j] != ".":
            start_j -= 1

        if start_j < 0:
            print("Warning: Cannot find start point for right path", file=sys.stderr)
            return False

        board.grid[start_i][start_j] = "*"

        def dfs(i, j):
            if i == N - 1:
                return True

            for di, dj in [(0, 1), (1, 0), (0, -1)]:  # 右、下、左
                ni, nj = i + di, j + dj
                if not board.is_valid_pos(ni, nj) or nj > N - 3:
                    continue
                if board.grid[ni][nj] != ".":
                    continue
                # 隣接チェック（閉路防止）
                if self.has_adjacent_star(board, ni, nj, excluding=(i, j)):
                    continue

                board.grid[ni][nj] = "*"
                if dfs(ni, nj):
                    return True
                # バックトラック
                board.grid[ni][nj] = "."

            return False

        success = dfs(start_i, start_j)
        if not success:
            print("Warning: Failed to create right vertical path", file=sys.stderr)
        return success

    def is_right_vertical_path(self, board, i, j):
        """右端の縦道の一部であるかチェック"""
        return j >= board.N - 3 and board.grid[i][j] == "*"

    def cannot_reach_top_in_2_moves(self, board, i, j):
        """現在位置から右に2歩移動してもi=0に到達できないかチェック"""
        if j + 2 >= board.N:
            return True
        for jj in range(j + 1, min(j + 3, board.N)):
            if board.grid[0][jj] == ".":
                return False
        return True

    def has_adjacent_star_excluding_right_path(self, board, i, j, from_pos):
        """右端の縦道との接続は許可する隣接チェック"""
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ni, nj = i + di, j + dj
            if (ni, nj) == from_pos:
                continue
            if board.is_valid_pos(ni, nj) and board.grid[ni][nj] == "*":
                # 右端の道なら許可
                if nj >= board.N - 3:
                    continue
                return True
        return False

    def step3_create_main_path(self, board):
        """DFSで一本道を作成"""
        N = board.N

        # 左端の道から開始点を選択
        start_i, start_j = None, None
        for i in range(N):
            for j in range(2, N):
                if board.grid[i][j] == "*" and j <= 4:  # 左端の道から選択
                    start_i, start_j = i, j
                    break
            if start_i is not None:
                break

        if start_i is None:
            print("Warning: Cannot find start point in left path", file=sys.stderr)
            return board

        # 初期方向を決定
        initial_direction = "down" if start_i < N / 2 else "up"

        def dfs(i, j, direction, move_history=None):
            if move_history is None:
                move_history = []

            # 右端の縦道に到達したら成功
            if self.is_right_vertical_path(board, i, j):
                return True

            # 方向転換の判定
            if direction == "up" and i == 0:
                direction = "down"
            elif direction == "down" and i == N - 1:
                direction = "up"
            elif direction == "up" and i <= 2:
                # 上端近くで直近2回の移動が右の場合は下向きに反転
                if len(move_history) >= 2 and all(move == 'right' for move in move_history[-2:]):
                    direction = "down"
            elif direction == "down" and i >= N - 3:
                # 下端近くで直近2回の移動が右の場合は上向きに反転
                if len(move_history) >= 2 and all(move == 'right' for move in move_history[-2:]):
                    direction = "up"

            # 移動優先順位（進行方向により異なる）
            if direction == "up":
                moves = [(0, -1), (-1, 0), (0, 1)]  # 左、上、右
                move_names = ['left', 'up', 'right']
            else:
                moves = [(0, -1), (1, 0), (0, 1)]  # 左、下、右
                move_names = ['left', 'down', 'right']

            for (di, dj), move_name in zip(moves, move_names):
                ni, nj = i + di, j + dj

                # 移動可能性チェック
                if not board.is_valid_pos(ni, nj):
                    continue
                if nj < 2:  # 左端制限
                    continue
                if board.grid[ni][nj] == ".":
                    # 隣接チェック（閉路防止）- ただし右端の道は除外
                    if self.has_adjacent_star_excluding_right_path(
                        board, ni, nj, from_pos=(i, j)
                    ):
                        continue

                    board.grid[ni][nj] = "*"
                    new_history = move_history + [move_name]
                    # 履歴は最大5個まで保持
                    if len(new_history) > 5:
                        new_history = new_history[-5:]

                    if dfs(ni, nj, direction, new_history):
                        return True
                    board.grid[ni][nj] = "."  # バックトラック
                elif self.is_right_vertical_path(board, ni, nj):
                    # 右端の道に接続
                    return True

            return False

        success = dfs(start_i, start_j, initial_direction)
        if not success:
            print("Warning: Failed to create main path", file=sys.stderr)

        board.debug_print("After Step3")
        return board

    def is_adjacent_to_flower(self, board, i, j):
        """(i, j)が花に隣接しているかチェック"""
        fi, fj = board.flower
        return abs(i - fi) + abs(j - fj) == 1

    def connect_start_to_path(self, board):
        """スタート地点から最も近い '*' マスへの経路を探索"""
        start_pos = board.start
        queue = deque([(start_pos, [])])
        visited = {start_pos}

        while queue:
            (i, j), path = queue.popleft()

            for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ni, nj = i + di, j + dj

                if not board.is_valid_pos(ni, nj):
                    continue
                if (ni, nj) in visited:
                    continue

                if board.grid[ni][nj] == "*":
                    # パスに到達 - 経路上のマスを'*'に変換
                    for pi, pj in path:
                        if board.grid[pi][pj] == ".":
                            board.grid[pi][pj] = "*"
                    # スタート地点も'*'にする
                    board.grid[start_pos[0]][start_pos[1]] = "*"
                    return True

                if board.grid[ni][nj] == ".":
                    visited.add((ni, nj))
                    queue.append(((ni, nj), path + [(ni, nj)]))

        return False  # 接続失敗

    def connect_flower_to_path(self, board):
        """花の位置から最も近い '*' マスへの経路を探索"""
        flower_pos = board.flower
        queue = deque([(flower_pos, [])])
        visited = {flower_pos}

        while queue:
            (i, j), path = queue.popleft()

            for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ni, nj = i + di, j + dj

                if not board.is_valid_pos(ni, nj):
                    continue
                if (ni, nj) in visited:
                    continue

                if board.grid[ni][nj] == "*":
                    # パスに到達 - 経路を'*'に変換
                    for pi, pj in path:
                        # '.'のみ'*'に変換
                        if board.grid[pi][pj] == ".":
                            board.grid[pi][pj] = "*"
                    # 花の位置も'*'にする
                    board.grid[flower_pos[0]][flower_pos[1]] = "*"
                    return True
                elif board.grid[ni][nj] == ".":
                    # '.'のみ通行可能
                    visited.add((ni, nj))
                    queue.append(((ni, nj), path + [(ni, nj)]))

        return False

    def step4_connect_start_and_goal(self, board):
        """スタートとゴールをパスに接続"""
        # スタートとゴールを順番に接続
        if not self.connect_start_to_path(board):
            print("Warning: Failed to connect start to path", file=sys.stderr)

        if not self.connect_flower_to_path(board):
            print("Warning: Failed to connect flower to path", file=sys.stderr)

        board.debug_print("After Step4")
        return board

    def step5_create_branches(self, board):
        """簡易版の分岐路を生成"""
        # 今回は簡易版として、パスに隣接する空きマスを一部パスに変換
        changes_made = 0
        for i in range(board.N):
            for j in range(board.N):
                if board.grid[i][j] == "." and changes_made < 10:  # 最大10個まで
                    # 隣接する'*'が1つだけの場合にパスに変換
                    adjacent_stars = 0
                    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ni, nj = i + di, j + dj
                        if board.is_valid_pos(ni, nj) and board.grid[ni][nj] == "*":
                            adjacent_stars += 1

                    if adjacent_stars == 1:
                        board.grid[i][j] = "*"
                        changes_made += 1

        board.debug_print("After Step5")
        return board

    def step6_post_process(self, board):
        """後処理で追加の*を配置"""
        # 今回は簡易版として木の配置はしない（経路確保のため）
        board.debug_print("After Step6")
        return board

    def generate_maze(self, board):
        """各ステップを実行して迷路を生成"""
        board = self.step1_surround_flower(board)
        board = self.step2_create_vertical_paths(board)
        board = self.step3_create_main_path(board)
        board = self.step4_connect_start_and_goal(board)
        board = self.step5_create_branches(board)
        board = self.step6_post_process(board)
        return board


def main():
    # 入力読み込み
    N, ti, tj = map(int, input().split())
    initial_board = [input() for _ in range(N)]

    # 初期盤面作成
    board = Board(N, ti, tj, initial_board)

    # 迷路生成
    generator = ForestMazeGenerator()
    best_board = generator.generate_maze(board.copy())

    # 配置する木のリスト作成
    trees_to_place = []
    for i in range(N):
        for j in range(N):
            if best_board.grid[i][j] == "#":
                trees_to_place.append((i, j))

    # インタラクティブ処理
    revealed = set()
    turn = 0

    while True:
        pi, pj = map(int, input().split())
        parts = input().split()
        n = int(parts[0])
        xy = list(map(int, parts[1:]))

        for k in range(n):
            x = xy[2 * k]
            y = xy[2 * k + 1]
            revealed.add((x, y))

        if pi == ti and pj == tj:
            break

        # 初回のみ木を配置
        if turn == 0:
            output = []
            for i, j in trees_to_place:
                if (i, j) not in revealed:
                    output.append(f"{i} {j}")

            if output:
                print(f"{len(output)} {' '.join(output)}", flush=True)
            else:
                print("0", flush=True)
        else:
            print("0", flush=True)

        turn += 1


if __name__ == "__main__":
    main()
