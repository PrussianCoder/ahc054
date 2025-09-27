"""
Test for Step6Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from constants import PATH, EMPTY, NEW_TREE
from step6constructor import Step6Constructor


def create_test_board():
    """テスト用の盤面を作成（step5完了後のような状態）"""
    input_data = [
        "##***.*.T*ST****.***",
        "***.*.***.***.T*.*##",
        "T#*.*.*.**.*.***.***",
        "***.*.*.T*.*.*...*##",
        "##*T*.*..*.*.*.*****",
        "***.*T*..*.*.*...*##",
        "##*.*.**.*T*.*.*****",
        "***.*..*.*.*.*...*##",
        "##*.**T*T*.*.*.***T.",
        "***.T*.*.*.*.**T.*T.",
        "#T*.T*.*.*.*.T**.*.T",
        "***.**.*T*.***.*.***",
        "##*.*..*.*...*.*.*##",
        "***.*TT*.***.*.*****",
        "##*.*.**#..*.*..*T##",
        "***.*.***#.*.*.*****",
        "##*.*.*#X#T*.*...*##",
        "***.*.*.#***T*...*T#",
        "##*.*.*....***.*****",
        "***.*****..T.TTT.*##",
    ]
    N = len(input_data)
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, initial_board)
    return board


def test_step6_constructor():
    """Step6Constructorのテスト"""
    board = create_test_board()
    constructor = Step6Constructor(seed=42)  # 再現可能性のためにシード固定

    print("Before Step6:")
    print(board)

    # パス、空きマス、新しい木の数をカウント（変換前）
    path_count_before = 0
    empty_count_before = 0
    new_tree_count_before = 0
    for i in range(board.n):
        for j in range(board.n):
            state = board.get_state(i, j)
            if state == PATH:
                path_count_before += 1
            elif state == EMPTY:
                empty_count_before += 1
            elif state == NEW_TREE:
                new_tree_count_before += 1

    print(f"\nBefore: PATH(*) = {path_count_before}, EMPTY(.) = {empty_count_before}, NEW_TREE(#) = {new_tree_count_before}")

    # Step6を実行
    board = constructor.construct(board)

    print("\nAfter Step6:")
    print(board)

    # パス、空きマス、新しい木の数をカウント（変換後）
    path_count_after = 0
    empty_count_after = 0
    new_tree_count_after = 0
    for i in range(board.n):
        for j in range(board.n):
            state = board.get_state(i, j)
            if state == PATH:
                path_count_after += 1
            elif state == EMPTY:
                empty_count_after += 1
            elif state == NEW_TREE:
                new_tree_count_after += 1

    print(f"\nAfter: PATH(*) = {path_count_after}, EMPTY(.) = {empty_count_after}, NEW_TREE(#) = {new_tree_count_after}")

    # 基本的な検証
    assert empty_count_after == 0, "空きマスが残っています"
    print("✓ All empty cells have been processed")

    if path_count_after > path_count_before:
        print("✓ Some empty cells were converted to paths")
    else:
        print("- No empty cells were converted to paths")

    print("✓ Step6 post-processing completed successfully")


if __name__ == "__main__":
    test_step6_constructor()
