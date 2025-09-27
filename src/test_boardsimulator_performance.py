import time
import sys
sys.path.append('.')

from board import Board
from constants import EMPTY, TREE, GOAL, NEW_TREE
from boardsimulator import BoardSimulator
from boardsimulator_optimized import BoardSimulatorOptimized
from boardsimulator_optimized_v2 import BoardSimulatorOptimizedV2


def create_test_board(n=20):
    """テスト用の盤面を作成"""
    # スタート位置
    start_i, start_j = 0, n // 2

    # ゴール位置（花）
    ti, tj = n - 1, n // 2

    # 初期盤面を作成
    initial_board = [['.' for _ in range(n)] for _ in range(n)]

    # いくつか障害物を配置
    for i in range(n):
        for j in range(n):
            if (i, j) != (start_i, start_j) and (i, j) != (ti, tj):
                if (i + j) % 7 == 0:
                    initial_board[i][j] = 'T'

    board = Board(n, start_i, start_j, ti, tj, initial_board)

    return board, start_i, start_j, ti, tj


def benchmark_simulators():
    """両方のシミュレータのパフォーマンスを比較"""

    # テストケースを準備
    test_cases = []
    for n in [10, 15, 20]:
        for _ in range(3):
            board, start_i, start_j, ti, tj = create_test_board(n)
            test_cases.append((n, board, start_i, start_j, ti, tj))

    print("=== BoardSimulator Performance Comparison ===\n")

    for n, board, start_i, start_j, ti, tj in test_cases:
        print(f"Board size: {n}x{n}")

        # オリジナル版のベンチマーク
        simulator_orig = BoardSimulator(n, start_i, start_j, ti, tj)
        start_time = time.perf_counter()
        result_orig = simulator_orig.simulate(board)
        time_orig = time.perf_counter() - start_time

        # 最適化版v1のベンチマーク
        simulator_opt = BoardSimulatorOptimized(n, start_i, start_j, ti, tj)
        start_time = time.perf_counter()
        result_opt = simulator_opt.simulate(board)
        time_opt = time.perf_counter() - start_time

        # 最適化版v2のベンチマーク
        simulator_opt_v2 = BoardSimulatorOptimizedV2(n, start_i, start_j, ti, tj)
        start_time = time.perf_counter()
        result_opt_v2 = simulator_opt_v2.simulate(board)
        time_opt_v2 = time.perf_counter() - start_time

        # 結果の検証（同じ結果になるはず）
        if result_orig != result_opt or result_orig != result_opt_v2:
            print(f"  WARNING: Results differ! Original: {result_orig}, OptV1: {result_opt}, OptV2: {result_opt_v2}")
        else:
            print(f"  Result (turns): {result_orig}")

        print(f"  Original time: {time_orig*1000:.2f} ms")
        print(f"  Optimized V1 time: {time_opt*1000:.2f} ms")
        print(f"  Optimized V2 time: {time_opt_v2*1000:.2f} ms")

        if time_opt_v2 > 0:
            speedup = time_orig / time_opt_v2
            print(f"  V2 Speedup: {speedup:.2f}x")

        print()

    # 大量実行テスト
    print("=== Bulk Execution Test (100 runs) ===")
    board, start_i, start_j, ti, tj = create_test_board(15)

    # オリジナル版
    start_time = time.perf_counter()
    for _ in range(100):
        simulator_orig = BoardSimulator(15, start_i, start_j, ti, tj)
        simulator_orig.simulate(board)
    time_orig_bulk = time.perf_counter() - start_time

    # 最適化版V1
    start_time = time.perf_counter()
    for _ in range(100):
        simulator_opt = BoardSimulatorOptimized(15, start_i, start_j, ti, tj)
        simulator_opt.simulate(board)
    time_opt_bulk = time.perf_counter() - start_time

    # 最適化版V2
    start_time = time.perf_counter()
    for _ in range(100):
        simulator_opt_v2 = BoardSimulatorOptimizedV2(15, start_i, start_j, ti, tj)
        simulator_opt_v2.simulate(board)
    time_opt_v2_bulk = time.perf_counter() - start_time

    print(f"Original (100 runs): {time_orig_bulk*1000:.2f} ms")
    print(f"Optimized V1 (100 runs): {time_opt_bulk*1000:.2f} ms")
    print(f"Optimized V2 (100 runs): {time_opt_v2_bulk*1000:.2f} ms")
    print(f"V1 Speedup: {time_orig_bulk/time_opt_bulk:.2f}x")
    print(f"V2 Speedup: {time_orig_bulk/time_opt_v2_bulk:.2f}x")


if __name__ == "__main__":
    benchmark_simulators()