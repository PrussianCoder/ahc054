"""
Test for Step4Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from constants import PATH, PATH_2
from step4constructor import Step4Constructor


def create_test_board():
    """テスト用の盤面を作成（step3完了後のような状態）"""
    input_data = [
        "..***.*.T.ST****.@..",
        "..*.*.***.#**.T*.@..",
        "T.*.*.*.**.*.***.@..",
        "..*.*.*.T*.*.*...@..",
        "..*T*.*.**.*.*...@..",
        "..*.*T*.*.**.*...@..",
        "..*.*.*.**T*.*...@..",
        "..*.*.**.*.*.*...@..",
        "..*.**T*T*.*.*...@T.",
        "..*.T*.*.*.*.**T.@T.",
        ".T*.T*.*.*.*.T*..@.T",
        "..*.**.*T*.*..*..@..",
        "..*.*.**.*.*.**..@..",
        "..*.*TT*.*.**.**@@..",
        "..*.*.**.**.**..@T..",
        "..*.*.*.##**.*..@@..",
        "..*.*.*#X.T***...@..",
        "..*.*.*.#***T....@T.",
        "..*.*.*..*.......@..",
        "..*.***..*.T.TTT.@..",
    ]
    N = len(input_data)
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, [list(row) for row in initial_board])
    return board


def test_step4_constructor():
    """Step4Constructorのテスト"""
    board = create_test_board()
    constructor = Step4Constructor()

    print("Before Step4:")
    print(board)

    # PATH_2の数をカウント（変換前）
    path2_count_before = 0
    path_count_before = 0
    for i in range(board.n):
        for j in range(board.n):
            state = board.get_state(i, j)
            if state == PATH_2:
                path2_count_before += 1
            elif state == PATH:
                path_count_before += 1

    print(f"\nBefore: PATH(*) = {path_count_before}, PATH_2(@) = {path2_count_before}")

    # Step4を実行
    board = constructor.construct(board)

    print("\nAfter Step4:")
    print(board)

    # PATH_2の数をカウント（変換後）
    path2_count_after = 0
    path_count_after = 0
    for i in range(board.n):
        for j in range(board.n):
            state = board.get_state(i, j)
            if state == PATH_2:
                path2_count_after += 1
            elif state == PATH:
                path_count_after += 1

    print(f"\nAfter: PATH(*) = {path_count_after}, PATH_2(@) = {path2_count_after}")

    # 基本的な検証
    assert path2_count_after == 0, "PATH_2が残っています"
    assert path_count_after > path_count_before, "パスが増加していません"
    print("✓ PATH_2がPATHに正常に変換されました")
    print("✓ 新しい接続パスが作成されました")


if __name__ == "__main__":
    test_step4_constructor()
