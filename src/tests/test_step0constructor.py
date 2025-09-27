"""
Test for Step0Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from constants import NEW_TREE, PATH
from step0constructor import Step0Constructor


def create_test_board():
    """テスト用の盤面を作成"""
    # 初期盤面（step0_implementation.mdの例を使用）
    input_data = [
        "........T.ST........",
        "..............T.....",
        "T...................",
        "........T...........",
        "...T................",
        ".....T..............",
        "..........T.........",
        "....................",
        "......T.T.........T.",
        "....T..........T..T.",
        ".T..T........T.....T",
        "........T...........",
        "....................",
        ".....TT.............",
        ".................T..",
        "....................",
        "........X.T.........",
        "............T.....T.",
        "....................",
        "...........T.TTT....",
    ]
    N = len(input_data)
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, [list(row) for row in initial_board])
    return board


def test_step0_constructor():
    """Step0Constructorのテスト"""
    board = create_test_board()
    constructor = Step0Constructor(seed=2)  # 再現可能性のためにシード固定

    print("Before Step0:")
    print(board)

    # Step0を実行
    board = constructor.construct(board)

    print("\nAfter Step0:")
    print(board)

    # 結果をチェック
    path_count = 0
    tree_count = 0

    for i in range(board.n):
        for j in range(board.n):
            state = board.get_state(i, j)
            if state == PATH:
                path_count += 1
            elif state == NEW_TREE:
                tree_count += 1

    print(f"\nPath cells created: {path_count}")
    print(f"New tree cells created: {tree_count}")

    # 基本的な検証
    assert path_count > 0, "パスが作成されていません"
    print("✓ パスが正常に作成されました")


if __name__ == "__main__":
    test_step0_constructor()
