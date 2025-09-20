import sys
from collections import deque
from typing import Dict, List, Set, Tuple

import pulp


def dprint(*args, **kwargs) -> None:
    print(*args, **kwargs, file=sys.stderr)


N, X, Y = map(int, input().split())
S = [[a for a in input()] for _ in range(N)]
p1, p2 = map(int, input().split())
parts = input().split()
n = int(parts[0])
xy = list(map(int, parts[1:]))
prob = pulp.LpProblem("prob", pulp.LpMinimize)
x = [
    [pulp.LpVariable(f"x_{i}_{j}", cat=pulp.LpBinary) for j in range(N)]
    for i in range(N)
]
prob += pulp.lpSum(x)

for i in range(N):
    for j in range(N):
        if S[i][j] == "T":
            prob += x[i][j] == 1
prob += x[0][N // 2] == 0
prob += x[X][Y] == 0
for k in range(n):
    prob += x[xy[k * 2]][xy[k * 2 + 1]] == 0

for i in range(N):
    for j in range(N - 4):
        prob += pulp.lpSum(x[i][j : j + 4]) >= 1

for i in range(N - 4):
    for j in range(N):
        prob += pulp.lpSum(x[i + k][j] for k in range(4)) >= 1

for i in range(N - 1):
    for j in range(N - 1):
        prob += pulp.lpSum(x[i][j] + x[i + 1][j + 1] + x[i + 1][j] + x[i][j + 1]) >= 1


prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=1.0))
ans = [["."] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if S[i][j] == "T":
            ans[i][j] = "T"
        elif pulp.value(x[i][j]) == 1:
            ans[i][j] = "P"


Coord = Tuple[int, int]


def solve_min_breaks(grid_str: List[str]) -> Dict[str, object]:
    """
    与えられた盤面で、全ての'.'を連結にするために壊すべき'P'の最小集合を求める。

    盤面仕様:
      '.' = 何もない（通行可、コスト0）
      'P' = 壊せる壁（通行不可だが壊せば通行可、開通コスト1）
      'T' = 壊せない壁（通行不可、コスト∞）
    近傍: 4近傍

    戻り値:
      {
        "components": int,                # '.' の連結成分数
        "break_positions": Set[Coord],    # 壊すべき P の座標集合 {(r,c), ...}
        "visualization": List[str],       # 壊すPを'*'で表示した盤面
      }

    アルゴリズム概要:
      1) '.' の連結成分をBFSでラベリング
      2) 各成分から 0-1 BFS（.の遷移コスト0、Pの遷移コスト1、Tは不可）を実施し、
         他成分への最小コストと経路を取得
      3) 成分を頂点、最小コストを重みとする完全グラフ上でMSTを構築
      4) MSTで選ばれた経路上の P を集約 → 最小集合
    """
    if not grid_str:
        return {"components": 0, "break_positions": set(), "visualization": []}

    N = len(grid_str)
    assert all(len(row) == N for row in grid_str), "正方行列（N×N）を想定しています。"
    grid = [list(row) for row in grid_str]
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # ---- 1) '.'の連結成分ラベリング ----
    comp_id = [[-1] * N for _ in range(N)]
    components: List[List[Coord]] = []

    for r in range(N):
        for c in range(N):
            if grid[r][c] == "." and comp_id[r][c] == -1:
                q = deque([(r, c)])
                cid = len(components)
                comp_id[r][c] = cid
                cells = [(r, c)]
                while q:
                    x, y = q.popleft()
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < N
                            and 0 <= ny < N
                            and grid[nx][ny] == "."
                            and comp_id[nx][ny] == -1
                        ):
                            comp_id[nx][ny] = cid
                            q.append((nx, ny))
                            cells.append((nx, ny))
                components.append(cells)

    K = len(components)
    if K <= 1:
        return {
            "components": K,
            "break_positions": set(),
            "visualization": grid_str[:],
        }

    comp_sets = [set(cells) for cells in components]

    # ---- 2) 各成分から 0-1 BFS ----
    INF = 10**9

    def zero_one_bfs_from_sources(sources: List[Coord]):
        dist = [[INF] * N for _ in range(N)]
        parent: List[List[Coord | None]] = [[None] * N for _ in range(N)]
        dq = deque()
        for r, c in sources:
            dist[r][c] = 0
            dq.append((r, c))
        while dq:
            x, y = dq.popleft()
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < N and 0 <= ny < N):
                    continue
                if grid[nx][ny] == "T":
                    continue
                w = 1 if grid[nx][ny] == "P" else 0
                nd = dist[x][y] + w
                if nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    parent[nx][ny] = (x, y)
                    if w == 0:
                        dq.appendleft((nx, ny))
                    else:
                        dq.append((nx, ny))
        return dist, parent

    # 成分間の最小コスト＆経路
    pair_cost = [[INF] * K for _ in range(K)]
    pair_path: List[List[List[Coord] | None]] = [[None] * K for _ in range(K)]

    for i in range(K):
        dist, parent = zero_one_bfs_from_sources(components[i])
        for j in range(K):
            if i == j:
                pair_cost[i][j] = 0
                pair_path[i][j] = []
                continue
            best_cost = INF
            best_cell: Coord | None = None
            for r, c in components[j]:
                if dist[r][c] < best_cost:
                    best_cost = dist[r][c]
                    best_cell = (r, c)
            pair_cost[i][j] = best_cost
            if best_cell is None or best_cost >= INF:
                pair_path[i][j] = None
            else:
                # 経路復元（i成分のいずれかに到達するまで戻る）
                path: List[Coord] = []
                cur: Coord | None = best_cell
                while cur is not None and cur not in comp_sets[i]:
                    path.append(cur)
                    pr = parent[cur[0]][cur[1]]
                    cur = pr
                path.reverse()
                pair_path[i][j] = path

    # ---- 3) 成分グラフのMST（Prim） ----
    in_mst = [False] * K
    min_edge = [float("inf")] * K
    parent_comp = [-1] * K
    min_edge[0] = 0.0

    for _ in range(K):
        u = -1
        best = float("inf")
        for v in range(K):
            if not in_mst[v] and min_edge[v] < best:
                best = min_edge[v]
                u = v
        if u == -1:
            break
        in_mst[u] = True
        for v in range(K):
            if not in_mst[v] and pair_cost[u][v] < min_edge[v]:
                min_edge[v] = pair_cost[u][v]
                parent_comp[v] = u

    # ---- 4) MSTで選ばれた経路上のPを集約 ----
    break_positions: Set[Coord] = set()
    for v in range(1, K):
        u = parent_comp[v]
        if u == -1:
            continue
        path = pair_path[u][v]
        if path is None:
            continue
        for r, c in path:
            if grid[r][c] == "P":
                grid[r][c] = "."
    return grid


grid = solve_min_breaks(ans)
new_grid = []
for i in range(N):
    for j in range(N):
        if grid[i][j] == "P":
            new_grid.extend([i, j])
print(len(new_grid) // 2, " ".join(map(str, new_grid)))
while True:
    p1, p2 = map(int, input().split())
    if (p1, p2) == (X, Y):
        exit()
    input()
    print(0)
