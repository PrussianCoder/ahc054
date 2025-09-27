EMPTY = 0
TREE = 1
PATH = 2
PATH_2 = 3
NEW_TREE = 4
START = 5
GOAL = 6
HIDDEN_TREE = 7

MAPPING = {
    EMPTY: ".",
    TREE: "T",
    PATH: "*",
    PATH_2: "@",
    NEW_TREE: "#",
    START: "S",
    HIDDEN_TREE: "H",
    GOAL: "X",
}
MAPPING_INV = {v: k for k, v in MAPPING.items()}
