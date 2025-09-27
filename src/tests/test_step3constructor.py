"""
Test for Step1Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from constants import PATH
from step3constructor import Step3Constructor


def create_test_board():
    """テスト用の盤面を作成"""
    # 初期盤面（doc/step2_implementation.mdの例を使用）
    input_data = [
        "..*.....T.ST.....@..",
        "..*...........T..@..",
        "T.*..............@..",
        "..*.....T........@..",
        "..*T.............@..",
        "..*..T...........@..",
        "..*.......T......@..",
        "..*..............@..",
        "..*...T.T........@T.",
        "..*.T..........T.@T.",
        ".T*.T........T...@.T",
        "..*.....T........@..",
        "..*..............@..",
        "..*..TT.........@@..",
        "..*.....#.......@T..",
        "..*....#........@@..",
        "..*....#X#T......@..",
        "..*.....#...T....@T.",
        "..*..............@..",
        "..*........T.TTT.@..",
    ]
    N = len(input_data)
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, [list(row) for row in initial_board])
    return board


board = create_test_board()
constructor = Step3Constructor()
cycle = 0
while True:
    if cycle % 2 == 1:
        board.reverse_up_down()
    board, is_reached = constructor.construct(board, PATH)
    print(f"After Step3 {cycle}-cycle")
    print(board)
    if is_reached:
        break
    if cycle % 2 == 1:
        board.reverse_up_down()
    cycle += 1
