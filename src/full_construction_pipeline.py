"""
Complete construction pipeline from Step0 to Step6 with score evaluation
"""

import os
import sys
import time

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from board import Board
from boardsimulator import BoardSimulator
from constants import PATH, PATH_2
from step0constructor import Step0Constructor
from step1constructor import Step1Constructor
from step2constructor import Step2Constructor
from step3constructor import Step3Constructor
from step4constructor import Step4Constructor
from step5constructor import Step5Constructor
from step6constructor import Step6Constructor


def create_test_board():
    """テスト用の盤面を作成"""
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
        "..........T.........",
        "............T.....T.",
        "....................",
        "...........T.TTT....",
    ]
    N = len(input_data)
    start_i = 0
    start_j = 10
    ti = 16
    tj = 8
    initial_board = [list(row) for row in input_data]

    board = Board(N, start_i, start_j, ti, tj, initial_board)
    return board


def run_full_construction_pipeline(verbose=True):
    """Step0からStep6までの完全な構築パイプラインを実行"""

    start_time = time.time()

    # 初期盤面の作成
    if verbose:
        print("=" * 50)
        print("FULL CONSTRUCTION PIPELINE")
        print("=" * 50)

    board = create_test_board()
    if verbose:
        print("Initial Board:")
        print(board)
        print()

    # Step0: 初期設定
    if verbose:
        print("Step0: Initial setup...")
    constructor_0 = Step0Constructor()
    board = constructor_0.construct(board)
    if verbose:
        print("✓ Step0 completed")
        print()

    # Step1: 花の周りに木を配置
    if verbose:
        print("Step1: Placing trees around flowers...")
    constructor_1 = Step1Constructor()
    board = constructor_1.random_construct(board)
    if verbose:
        print("✓ Step1 completed")
        print("After Step1:")
        print(board)
        print()

    # Step2: 左右端の垂直パス作成
    if verbose:
        print("Step2: Creating vertical paths on edges...")
    constructor_2 = Step2Constructor()
    board = constructor_2.construct(board, PATH)
    board.reverse_left_right()
    board = constructor_2.construct(board, PATH_2)
    board.reverse_left_right()
    if verbose:
        print("✓ Step2 completed")
        print("After Step2:")
        print(board)
        print()

    # Step3: 垂直パス間の接続パス作成
    if verbose:
        print("Step3: Creating connecting paths between vertical edges...")
    constructor_3 = Step3Constructor()
    cycle = 0
    max_cycles = 10  # 無限ループ防止
    while cycle < max_cycles:
        if cycle % 2 == 1:
            board.reverse_up_down()

        board, is_reached = constructor_3.construct(board, PATH)

        if cycle % 2 == 1:
            board.reverse_up_down()

        if verbose:
            print(f"  Step3 cycle {cycle} completed")

        cycle += 1
        if is_reached:
            if verbose:
                print("  ✓ Connection established!")
            break

    if verbose:
        print("✓ Step3 completed")
        print("After Step3:")
        print(board)
        print()

    # Step4: START/GOALとパスの接続
    if verbose:
        print("Step4: Connecting START and GOAL to paths...")
    constructor_4 = Step4Constructor()
    board = constructor_4.construct(board)
    if verbose:
        print("✓ Step4 completed")
        print("After Step4:")
        print(board)
        print()

    # Step5: 既存パスからの分岐作成
    if verbose:
        print("Step5: Creating branches from existing paths...")
    constructor_5 = Step5Constructor()
    board = constructor_5.construct(board)
    if verbose:
        print("✓ Step5 completed")
        print("After Step5:")
        print(board)
        print()

    # Step6: 空きセルの後処理
    if verbose:
        print("Step6: Post-processing empty cells...")
    constructor_6 = Step6Constructor()
    board = constructor_6.construct(board)
    if verbose:
        print("✓ Step6 completed")
        print("After Step6:")
        print(board)
        print()

    # 盤面の向きを正規化
    if board.is_up_down_reversed:
        board.reverse_up_down()
    if board.is_left_right_reversed:
        board.reverse_left_right()

    # スコア評価
    if verbose:
        print("Score Evaluation:")
        print("-" * 30)

    start_i, start_j = board.to_2d(board.start_pos)
    ti, tj = board.to_2d(board.goal_pos)

    evaluator = BoardSimulator(board.n, start_i, start_j, ti, tj)
    score = evaluator.simulate(board)

    end_time = time.time()
    elapsed_time = end_time - start_time

    if verbose:
        print(f"Final Score: {score} turns")
        if score > 0:
            print("✓ SUCCESS: Goal is reachable!")
        else:
            print("✗ FAILED: Goal is unreachable")

        print(f"Construction time: {elapsed_time:.2f} seconds")
        print()

        print("Final board configuration:")
        board.output()  # 新しい木の配置を出力
        print()

        print("=" * 50)
        print("PIPELINE COMPLETED")
        print("=" * 50)

    return {
        'board': board,
        'score': score,
        'start_pos': (start_i, start_j),
        'goal_pos': (ti, tj),
        'construction_time': elapsed_time,
        'success': score > 0
    }


def analyze_construction_quality(result):
    """構築結果の品質を分析"""
    print("Construction Quality Analysis:")
    print("-" * 40)

    board = result['board']
    score = result['score']

    # パスの数をカウント
    path_count = 0
    new_tree_count = 0
    for i in range(board.n):
        for j in range(board.n):
            state = board.get_state(i, j)
            if state == PATH or state == PATH_2:
                path_count += 1
            elif state == 4:  # NEW_TREE
                new_tree_count += 1

    total_cells = board.n * board.n
    path_ratio = path_count / total_cells
    tree_ratio = new_tree_count / total_cells

    print(f"Board size: {board.n}x{board.n} ({total_cells} cells)")
    print(f"Path cells: {path_count} ({path_ratio:.1%})")
    print(f"New trees: {new_tree_count} ({tree_ratio:.1%})")
    print(f"Score: {score} turns")
    print(f"Construction time: {result['construction_time']:.2f}s")

    # 品質評価
    if score == 0:
        quality = "Poor (Unreachable)"
    elif score < 50:
        quality = "Excellent"
    elif score < 100:
        quality = "Good"
    elif score < 200:
        quality = "Fair"
    else:
        quality = "Poor (Too many turns)"

    print(f"Quality assessment: {quality}")

    return {
        'path_count': path_count,
        'new_tree_count': new_tree_count,
        'path_ratio': path_ratio,
        'tree_ratio': tree_ratio,
        'quality': quality
    }


if __name__ == "__main__":
    # 完全な構築パイプラインを実行
    result = run_full_construction_pipeline(verbose=True)

    # 結果を分析
    print()
    analysis = analyze_construction_quality(result)

    # 簡潔なサマリー
    print()
    print("SUMMARY:")
    print(f"  Result: {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"  Score: {result['score']} turns")
    print(f"  Quality: {analysis['quality']}")
    print(f"  Time: {result['construction_time']:.2f}s")