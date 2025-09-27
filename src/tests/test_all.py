import os
import sys
import time

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

    board = Board(N, start_i, start_j, ti, tj, [list(row) for row in initial_board])
    return board


start_time = time.time()

# Step0
print("Initial Board:")
board = create_test_board()
constructor_0 = Step0Constructor()
board = constructor_0.construct(board)
print("After Step0:")
print(board)


# Step1
constructor_1 = Step1Constructor()
board = constructor_1.random_construct(board)
print("After Step1:")
print(board)


# Step2
constructor_2 = Step2Constructor()
board = constructor_2.construct(board, PATH)
board.reverse_left_right()
board = constructor_2.construct(board, PATH_2)
board.reverse_left_right()
print("After Step2:")
print(board)


# Step3
constructor_3 = Step3Constructor()
cycle = 0
while True:
    if cycle % 2 == 1:
        board.reverse_up_down()
    board, is_reached = constructor_3.construct(board, PATH)
    if cycle % 2 == 1:
        board.reverse_up_down()
    print(f"After Step3 {cycle}-cycle")
    print(board)
    cycle += 1
    if is_reached:
        break


# Step4
constructor_4 = Step4Constructor()
board = constructor_4.construct(board)
print("After Step4:")
print(board)


# Step5
constructor_5 = Step5Constructor()
board = constructor_5.construct(board)
print("After Step5:")
print(board)


# Step6
constructor_6 = Step6Constructor()
board = constructor_6.construct(board)
print("After Step6:")
print(board)

if board.is_up_down_reversed:
    board.reverse_up_down()
if board.is_left_right_reversed:
    board.reverse_left_right()

start_i, start_j = board.to_2d(board.start_pos)
ti, tj = board.to_2d(board.goal_pos)

evaluator = BoardSimulator(board.n, start_i, start_j, ti, tj)
score = evaluator.simulate(board)
print(f"Score: {score}")
board.output()

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
