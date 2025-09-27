"""
Debug Step6 board specifically
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from boardsimulator import BoardSimulator


class DebugBoardSimulator(BoardSimulator):
    """デバッグ用のBoardSimulator"""

    def _step(self, new_trees):
        """デバッグ情報付きのstep"""
        if self.turn < 5 or self.turn % 50 == 0:  # 最初の5ターンと50ターンごとに表示
            print(f"\n--- Turn {self.turn + 1} ---")
            print(f"Current position: {self.p}")
            print(f"Goal position: {self.t}")
            print(f"Current target: {self.target}")
            print(f"Queue length: {len(self.q)}")

        # ステップ実行前の状態を記録
        before_target = self.target
        before_pos = self.p
        before_q_len = len(self.q)

        result = super()._step(new_trees)

        if not result:
            print(f"\nFAILED at turn {self.turn}")
            print(f"Position before: {before_pos} -> after: {self.p}")
            print(f"Target before: {before_target} -> after: {self.target}")
            print(f"Queue length before: {before_q_len} -> after: {len(self.q)}")

            if self.p == self.t:
                print("  Reason: Already at goal (but this should not cause failure)")
            elif not self.q and self.target == (-1, -1):
                print("  Reason: No reachable targets")
            elif self.target != (-1, -1) and self.dist[self.p[0]][self.p[1]] == float('inf'):
                print(f"  Reason: Current position unreachable from target {self.target}")
            else:
                print("  Reason: Unknown failure")
                print(f"  Goal revealed: {self.revealed[self.t[0]][self.t[1]]}")
                print(f"  Current distance to target: {self.dist[self.p[0]][self.p[1]] if self.target != (-1, -1) else 'N/A'}")

        return result


def create_step6_board():
    """Step6完了後の盤面"""
    input_data = [
        "##***#*#T#*T##**#***",
        "***#*#***#***.T*#*##",
        "T#*#*#*#**#*#***.***",
        "***#*#*#T*#*#*###*##",
        "##*T*#*##*#*#*#*****",
        "***#*T*##*#*#*###*##",
        "##*#*#**#*T*#*#*****",
        "***#*##*#*#*#*###*##",
        "##*#**T*T*#*#*#***T#",
        "***#T*#*#*#*#**T#*T#",
        "#T*#T*#*#*#*#T**#*#T",
        "***#**#*T*#***#*#***",
        "##*#*##*#*###*#*#*##",
        "***#*TT*#***#*#*****",
        "##*#*#**#**#*##*T*##",
        "***#*#***#**#*#*****",
        "##*#*#*#.#T*#*###*##",  # ゴール位置
        "***#*#*#*#**T*###*T#",
        "##*#*#*####***#*****",
        "***#*****##T*TTT#*##",
    ]
    N = len(input_data)
    start_i, start_j = 0, 10  # START位置
    ti, tj = 16, 8  # GOAL位置
    initial_board = [list(row) for row in input_data]

    board = Board(N, start_i, start_j, ti, tj, initial_board)
    return board


def analyze_step6_path():
    """Step6盤面のパス構造を分析"""
    print("=== Step6 Board Path Analysis ===")
    board = create_step6_board()

    print("Board:")
    print(board)

    # START周辺の探索
    print(f"\nSTART position: (0, 10)")
    print("Area around START:")
    for i in range(5):
        row = ""
        for j in range(5, 16):
            char = board._board_to_char(board, i, j) if hasattr(board, '_board_to_char') else str(board)[i*21 + j]
            row += char
        print(f"  {i}: {row}")

    # GOAL周辺の探索
    print(f"\nGOAL position: (16, 8)")
    print("Area around GOAL:")
    for i in range(12, 20):
        row = ""
        for j in range(3, 14):
            char = str(board).split('\n')[i][j]
            row += char
        print(f"  {i}: {row}")

    # パス('*')の接続性をチェック
    board_str = str(board).split('\n')
    paths = []
    for i in range(len(board_str)):
        for j in range(len(board_str[i])):
            if board_str[i][j] == '*':
                paths.append((i, j))

    print(f"\nTotal number of path cells ('*'): {len(paths)}")

    # STARTから最初のパスまでの距離をチェック
    start_neighbors = [
        (0-1, 10), (0+1, 10), (0, 10-1), (0, 10+1)  # up, down, left, right
    ]

    print("Neighbors of START:")
    for ni, nj in start_neighbors:
        if 0 <= ni < len(board_str) and 0 <= nj < len(board_str[0]):
            char = board_str[ni][nj]
            print(f"  ({ni}, {nj}): '{char}'")


def test_step6_limited():
    """Step6盤面を制限付きでテスト"""
    print("\n=== Step6 Limited Debug Test ===")
    board = create_step6_board()
    simulator = DebugBoardSimulator(20, 0, 10, 16, 8)

    score = simulator.simulate(board)
    print(f"\nFinal Score: {score}")


if __name__ == "__main__":
    analyze_step6_path()
    test_step6_limited()