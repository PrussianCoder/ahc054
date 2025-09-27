"""
Test for Step4Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from step5constructor import Step5Constructor


def create_test_board():
    """テスト用の盤面を作成（step3完了後のような状態）"""
    input_data = [
        "..***.*.T*ST****.*..",
        "..*.*.****#**.T*.*..",
        "T.*.*.*.**.*.***.*..",
        "..*.*.*.T*.*.*...*..",
        "..*T*.*.**.*.*...*..",
        "..*.*T*.*.**.*...*..",
        "..*.*.*.**T*.*...*..",
        "..*.*.**.*.*.*...*..",
        "..*.**T*T*.*.*...*T.",
        "..*.T*.*.*.*.**T.*T.",
        ".T*.T*.*.*.*.T*..*.T",
        "..*.**.*T*.*..*..*..",
        "..*.*.**.*.*.**..*..",
        "..*.*TT*.*.**.****..",
        "..*.*.**.**.**..*T..",
        "..*.*.*.##**.*..**..",
        "..*.*.*#X*T***...*..",
        "..*.*.*.#***T....*T.",
        "..*.*.*..*.......*..",
        "..*.***..*.T.TTT.*..",
    ]
    N = len(input_data)
    start_i = 0
    start_j = 10
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, start_i, start_j, ti, tj, [list(row) for row in initial_board])
    return board


board = create_test_board()
constructor = Step5Constructor()

print("Before Step5:")
print(board)

board = constructor.construct(board)

print("After Step5:")
print(board)
