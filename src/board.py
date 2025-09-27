from src.constants import GOAL, MAPPING, MAPPING_INV, NEW_TREE, PATH, START


class Board:
    def __init__(
        self,
        n: int,
        start_i: int,
        start_j: int,
        ti: int,
        tj: int,
        initial_board: list[list[str]],
    ) -> None:
        self.n = n
        self.start_pos = self._to_1d(start_i, start_j)
        self.goal_pos = self._to_1d(ti, tj)
        self.state = []
        for row in initial_board:
            self.state.extend([MAPPING_INV[cell] for cell in row])
        self.state[self.start_pos] = START
        self.state[self.goal_pos] = GOAL
        self.is_up_down_reversed = False
        self.is_left_right_reversed = False

    def _to_1d(self, i: int, j: int) -> int:
        return i * self.n + j

    def to_2d(self, v: int) -> tuple[int, int]:
        return v // self.n, v % self.n

    def get_state(self, x: int, y: int) -> int:
        return self.state[self._to_1d(x, y)]

    def set_state(self, x: int, y: int, state: int) -> None:
        self.state[self._to_1d(x, y)] = state

    def reverse_up_down(self) -> None:
        self.is_up_down_reversed = not self.is_up_down_reversed
        for i1 in range(self.n):
            i2 = self.n - 1 - i1
            if i1 >= i2:
                break
            for j in range(self.n):
                self.state[self._to_1d(i1, j)], self.state[self._to_1d(i2, j)] = (
                    self.state[self._to_1d(i2, j)],
                    self.state[self._to_1d(i1, j)],
                )
        start_x, start_y = self.to_2d(self.start_pos)
        self.start_pos = self._to_1d(self.n - 1 - start_x, start_y)
        goal_x, goal_y = self.to_2d(self.goal_pos)
        self.goal_pos = self._to_1d(self.n - 1 - goal_x, goal_y)

    def reverse_left_right(self) -> None:
        self.is_left_right_reversed = not self.is_left_right_reversed
        for i in range(self.n):
            for j1 in range(self.n):
                j2 = self.n - 1 - j1
                if j1 >= j2:
                    break
                self.state[self._to_1d(i, j1)], self.state[self._to_1d(i, j2)] = (
                    self.state[self._to_1d(i, j2)],
                    self.state[self._to_1d(i, j1)],
                )
        start_x, start_y = self.to_2d(self.start_pos)
        self.start_pos = self._to_1d(start_x, self.n - 1 - start_y)
        goal_x, goal_y = self.to_2d(self.goal_pos)
        self.goal_pos = self._to_1d(goal_x, self.n - 1 - goal_y)

    def __repr__(self) -> str:
        return "\n".join(
            [
                "".join([MAPPING[self.state[self._to_1d(i, j)]] for j in range(self.n)])
                for i in range(self.n)
            ]
        )

    def output(self) -> None:
        new_trees = []
        for i in range(self.n):
            for j in range(self.n):
                if self.get_state(i, j) == NEW_TREE:
                    new_trees.append((i, j))
        print(len(new_trees), " ".join([f"{i} {j}" for i, j in new_trees]))


if __name__ == "__main__":
    board = Board(
        5,
        2,
        2,
        [
            [".", ".", ".", ".", "."],
            ["#", ".", ".", ".", "."],
            [".", "T", "T", "T", "#"],
            [".", ".", ".", ".", "."],
            ["#", ".", ".", ".", "."],
        ],
    )
    print(board)
    print("reverse_up_down")
    board.reverse_up_down()
    print(board)
    print("reverse_left_right")
    board.reverse_left_right()
    print(board)
    print("set_state")
    board.set_state(2, 2, PATH)
    print(board)
