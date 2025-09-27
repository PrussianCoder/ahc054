"""
Test for BoardSimulator
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import Board
from boardsimulator import BoardSimulator


def create_simple_test_board():
    """シンプルなテスト用の盤面を作成"""
    input_data = [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ]
    N = len(input_data)
    start_i, start_j = 0, 2  # START位置
    ti, tj = 4, 2  # GOAL位置
    initial_board = [list(row) for row in input_data]

    board = Board(N, start_i, start_j, ti, tj, initial_board)
    return board


def create_test_board_with_obstacles():
    """障害物がある複雑なテスト用の盤面を作成"""
    input_data = [
        "....T",
        ".T...",
        ".....",
        "...T.",
        ".....",
    ]
    N = len(input_data)
    start_i, start_j = 0, 2  # START位置
    ti, tj = 4, 2  # GOAL位置
    initial_board = [list(row) for row in input_data]

    board = Board(N, start_i, start_j, ti, tj, initial_board)
    return board


def create_step6_completed_board():
    """Step6完了後のような実際の盤面"""
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


def test_simple_board():
    """シンプルな盤面でのテスト"""
    print("=== Simple Board Test ===")
    board = create_simple_test_board()
    simulator = BoardSimulator(5, 0, 2, 4, 2)  # START(0,2) -> GOAL(4,2)

    print("Board:")
    print(board)

    score = simulator.simulate(board)
    print(f"Score: {score}")
    print(f"Expected score: approximately 4 (straight path down)")
    assert score > 0, "Score should be positive"
    print("✓ Simple board test passed")


def test_board_with_obstacles():
    """障害物がある盤面でのテスト"""
    print("\n=== Board with Obstacles Test ===")
    board = create_test_board_with_obstacles()
    simulator = BoardSimulator(5, 0, 2, 4, 2)  # START(0,2) -> GOAL(4,2)

    print("Board:")
    print(board)

    score = simulator.simulate(board)
    print(f"Score: {score}")
    print(f"Expected score: > 4 (need to explore around obstacles)")
    assert score > 0, "Score should be positive"
    print("✓ Board with obstacles test passed")


def test_step6_completed_board():
    """Step6完了後の実際の盤面でのテスト"""
    print("\n=== Step6 Completed Board Test ===")
    board = create_step6_completed_board()
    simulator = BoardSimulator(20, 0, 10, 16, 8)  # START(0,10) -> GOAL(16,8)

    print("Board (first 10 rows):")
    board_str = str(board)
    lines = board_str.split('\n')
    for line in lines[:10]:
        print(line)
    print("...")

    score = simulator.simulate(board)
    print(f"Score: {score}")
    print(f"Expected score: varies based on path complexity")

    if score > 0:
        print("✓ Step6 completed board test passed")
        print(f"  Estimated performance: {score} turns to reach goal")
    else:
        print("✗ Step6 completed board test failed - unreachable")


def test_board_states():
    """Board状態の変換テスト"""
    print("\n=== Board State Conversion Test ===")
    board = create_simple_test_board()
    simulator = BoardSimulator(5, 0, 2, 4, 2)

    # 状態変換のテスト
    char_s = simulator._board_to_char(board, 0, 2)  # START position (0, n//2)
    char_x = simulator._board_to_char(board, 4, 2)  # GOAL position
    char_empty = simulator._board_to_char(board, 1, 1)  # Empty position

    print(f"START character: '{char_s}' (expected: 'S')")
    print(f"GOAL character: '{char_x}' (expected: 'X')")
    print(f"EMPTY character: '{char_empty}' (expected: '.')")

    assert char_s == 'S', f"Expected 'S', got '{char_s}'"
    assert char_x == 'X', f"Expected 'X', got '{char_x}'"
    assert char_empty == '.', f"Expected '.', got '{char_empty}'"

    # 通行可能性のテスト
    assert simulator._is_passable('.')  # Empty
    assert simulator._is_passable('*')  # Path
    assert simulator._is_passable('S')  # Start
    assert simulator._is_passable('X')  # Goal
    assert not simulator._is_passable('T')  # Tree
    assert not simulator._is_passable('#')  # New tree

    print("✓ Board state conversion test passed")


if __name__ == "__main__":
    test_board_states()
    test_simple_board()
    test_board_with_obstacles()
    test_step6_completed_board()

    print("\n=== All BoardSimulator Tests Completed ===")