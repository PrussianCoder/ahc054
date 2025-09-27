"""
Test for Step1Constructor
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.board import Board
from src.step1constructor import Step1Constructor


def create_test_board():
    """テスト用の盤面を作成"""
    N = 20
    ti = 16  # 花の位置(行)
    tj = 8  # 花の位置(列)

    # 初期盤面（doc/step1_implementation.mdの例を使用）
    initial_board = [
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

    board = Board(N, ti, tj, [list(row) for row in initial_board])
    return board


def get_from_file():
    N, ti, tj = map(int, input().split())
    initial_board = []
    for _ in range(N):
        initial_board.append(input())
    start_i = 0
    start_j = N // 2
    return N, start_i, start_j, ti, tj, initial_board


n, start_i, start_j, ti, tj, initial_board = get_from_file()

for pattern_idx in range(len(Step1Constructor.PATTERNS)):
    board = Board(n, start_i, start_j, ti, tj, initial_board)
    if not Step1Constructor().can_apply_pattern(board, pattern_idx):
        continue
    print(f"pattern_idx: {pattern_idx}")
    board = Step1Constructor().construct(board, pattern_idx)
    print(board)
