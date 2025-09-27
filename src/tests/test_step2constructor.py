"""
Test for Step1Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from board import Board
from constants import PATH, PATH_2
from step2constructor import Step2Constructor


def create_test_board():
    """テスト用の盤面を作成"""
    # 初期盤面（doc/step2_implementation.mdの例を使用）
    input_data = [
        "..............T............T.....T",
        "...........................T..T.T.",
        "..T.......T.....T....T.......T.T..",
        "...T..T...T.......................",
        "......TT.....T.....T...T.T.T......",
        "........TT...............TT......T",
        "................T..T......T.T..T..",
        "........T.....T.T..T..T.T........T",
        ".........T.........T........T.....",
        "......TT....T....T..............T.",
        "................T.....T.......T...",
        "....T.....T....T...TTT............",
        "...................TT....T..T.....",
        "...........TT..................T..",
        "......................T.T.........",
        "T........T..T.T......TT.......T.TT",
        "..T.T.....T....T......T.....T.....",
        "...T....T......T.............T....",
        "....TT......TT..........T.TT...T..",
        "T.................T.T..T........T.",
        "T....T.................TT...T...T.",
        "T........T..T................T..T.",
        ".............T................TT..",
        "................T.........T..T..T.",
        "......T.....................T...T.",
        ".....T.T...T.......T...........T..",
        ".T................T............T..",
        "...........T........TT.T..........",
        ".......T.T..........T.......T....T",
        ".T.T..T.T..T................T.....",
        "T.....T.TT.T....TT.....T..T.......",
        "............T......T......T.T...T.",
        ".....T.T...T..TT......T...T.......",
        "......T.....T.................TT..",
    ]
    N = len(input_data)
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, ti, tj, [list(row) for row in initial_board])
    return board


board = create_test_board()

# put left path
board = Step2Constructor().construct(board, PATH)
print(board)


# put right path
board.reverse_left_right()
board = Step2Constructor().construct(board, PATH_2)
board.reverse_left_right()
print(board)
