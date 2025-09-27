"""
Debug test for BoardSimulator
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from boardsimulator import BoardSimulator


def create_debug_board():
    """デバッグ用のシンプルな盤面"""
    input_data = [
        ".......",
        "..*****..",
        "..S*X*..",
        "..*****..",
        ".......",
    ]
    N = len(input_data)
    ti = 2  # ゴール位置（X）
    tj = 4
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, initial_board)
    return board


class DebugBoardSimulator(BoardSimulator):
    """デバッグ用のBoardSimulator"""

    def _step(self, new_trees):
        """デバッグ情報付きのstep"""
        print(f"\n--- Turn {self.turn + 1} ---")
        print(f"Current position: {self.p}")
        print(f"Goal position: {self.t}")
        print(f"Current target: {self.target}")

        # 現在の視野を表示
        print("Current vision:")
        for i in range(self.n):
            row = ""
            for j in range(self.n):
                if self.revealed[i][j]:
                    row += self.board_chars[i][j]
                else:
                    row += "?"
            print(f"  {row}")

        result = super()._step(new_trees)
        print(f"Step result: {result}")

        if not result:
            print("FAILED - checking reason...")
            if self.p == self.t:
                print("  Reason: Already at goal")
            elif not self.q and self.target == (-1, -1):
                print("  Reason: No reachable targets")
            else:
                print("  Reason: Other error")

        return result


def test_debug_simple():
    """デバッグ用シンプルテスト"""
    print("=== Debug Simple Test ===")
    board = create_debug_board()
    simulator = DebugBoardSimulator(7, 2, 2, 2, 4)  # START(2,2) -> GOAL(2,4)

    print("Board:")
    print(board)
    print()

    score = simulator.simulate(board)
    print(f"\nFinal Score: {score}")


def test_debug_step6_mini():
    """Step6風の小さな盤面でテスト"""
    print("\n=== Debug Step6 Mini Test ===")
    input_data = [
        "#####",
        "#*S*#",
        "#***#",
        "#*X*#",
        "#####",
    ]
    N = len(input_data)
    ti = 3  # ゴール位置（X）
    tj = 2
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, initial_board)
    simulator = DebugBoardSimulator(N, 1, 2, ti, tj)

    print("Board:")
    print(board)
    print()

    score = simulator.simulate(board)
    print(f"\nFinal Score: {score}")


if __name__ == "__main__":
    test_debug_simple()
    test_debug_step6_mini()