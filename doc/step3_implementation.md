## Step3. 左端から開始して一本道を作る

完成系のイメージ

```
..***...T.ST****.*..
..*.*.***..**.T*.*..
T.*.*.*.**.*.***.*..
..*.*.*.T*.*.*...*..
..*T*.*..*.*.*...*..
..*.*T*..*.*.*...*..
..*.*.**.*T*.*...*..
..*.*..*.*.*.*...*..
..*.**T*T*.*.*...*T.
..*.T*.*.*.*.**T.*T.
.T*.T*.*.*.*.T**.*.T
..*.**.*T*.***.*.*..
..*.*..*.*...*.*.*..
..*.*TT*.***.*.***..
..*.*.**#..*.*..*T..
..*.*.*..#.*.*..**..
..*.*.*#X#T*.*...*..
..*.*.*.#..*T*...*T.
..*.*.*....***...*..
..*.***....T.TTT.*..
```

### 開始パスの選択
- iの昇順にみて、下記の条件を満たすPATHを開始パスとする
    - i行目の中で、[i,j]=PATHかつ[i,j+1]=`.`となる最小のjである
    - [i+1,j+1]!=PATHである（次の行で道を延ばせる）

### パス構築
- 開始パスから開始してi=N-1に到達するパスを下向きにStep2のDP+経路復元で求める
- Step2との相違点：
    - **動的範囲設定**: l,rの範囲は行ごとに変える
    - **範囲計算**: i行目にあるPATHのうち最も右側にあるセルのjの値をj_maxとした時
        - 通常: `j_max + 2 <= l, r <= min(N-1, j_max + 10)`
        - 開始パスがある行のみ: `j_max + 1 <= l, r <= min(N-1, j_max + 10)`
    - **制約**: Step2の右端のパス(PATH_2)は除外して考える
    - **ペナルティ**: PENALTYはかけない
- 仮に復元したパスがi=N//2にも到達できていないような場合は、開始点を下げて再度実行する

### 終了条件
- このアルゴリズムを繰り返した時、最終的にはStep2で構築した右側のパスと接触する
- そのような状態になったら終了する

grid = [
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
    "..*.....#.....,.@T..",
    "..*......#......@@..",
    "..*....#X#T......@..",
    "..*.....#...T....@T.",
    "..*..............@..",
    "..*........T.TTT.@..",
]

N = len(grid)
# dp[i][l][r] := i行目のl列からr列までの範囲がパスとなるような最小コスト
dp = [[[float("inf")] * N for _ in range(N)] for _ in range(N)]
# parent[i][l][r] := 親ノード情報 (prev_l, prev_r)
parent = [[[None] * N for _ in range(N)] for _ in range(N)]

# 範囲を求める
ranges = []
for i in range(N):
    for j in reversed(range(N)):
        if grid[i][j] == "*":
            left = j + 2
            right = min(N - 1, j + 10)
            ranges.append((left, right))
            break

# 初期点を決める
for i in range(N - 1):
    if ranges[i][0] >= ranges[i + 1][0]:
        si, sj = i, ranges[i][0]
        ranges[i] = (ranges[i][0] - 1, ranges[i][1])
        break

# DPの初期状態（ただし開始行はlから開始するようにする
l = ranges[si][0]
for r in range(ranges[si][0], ranges[si][1]):
    if grid[0][r] != ".":
        break
    dp[si][l][r] = r
    parent[si][l][r] = None  # 開始点なので親なし
print(ranges)

# 遷移
for i in range(1, N):
    # (l,r)から(r,r2)に遷移する場合
    # min(dp[i-1][l][r] for l <=r)
    for r in range(ranges[i - 1][0], ranges[i - 1][1]):
        if not ranges[i][0] <= r <= ranges[i][1]:
            continue
        min_r = float("inf")
        for l in range(r + 1):
            min_r = min(min_r, dp[i - 1][l][r])
        if min_r != float("inf"):
            for r2 in range(r, ranges[i][1]):
                if grid[i][r2] != ".":
                    break
                new_cost = min_r + r2
                if new_cost < dp[i][r][r2]:
                    dp[i][r][r2] = new_cost
                    # 親ノードを記録（パターン1: (l,r)から(r,r2)への遷移）
                    for l in range(r + 1):
                        if dp[i - 1][l][r] == min_r:
                            parent[i][r][r2] = (l, r)
                            break

    # (l,r)から(l2,r)に遷移する場合
    for l in range(ranges[i - 1][0], ranges[i - 1][1]):
        if not ranges[i][0] <= l <= ranges[i][1]:
            continue
        min_l = float("inf")  # min(dp[i-1][l][r] for l <=r)
        for r in range(l, ranges[i][1]):
            min_l = min(min_l, dp[i - 1][l][r])
        if min_l != float("inf"):
            for l2 in reversed(range(ranges[i][0], l + 1)):
                if grid[i][l2] != ".":
                    break
                new_cost = min_l + l2
                if new_cost < dp[i][l2][l]:
                    dp[i][l2][l] = new_cost
                    # 親ノードを記録（パターン2: (l,r)から(l2,r)への遷移）
                    for r_prev in range(l, ranges[i - 1][1]):
                        if dp[i - 1][l][r_prev] == min_l:
                            parent[i][l2][l] = (l, r_prev)
                            break
    for l in range(ranges[i][0], ranges[i][1]):
        for r in range(l, ranges[i][1]):
            if dp[i][l][r] != float("inf"):
                print(f"dp[{i}][{l}][{r}] = {dp[i][l][r]}")


# 経路復元
def reconstruct_path():
    """経路復元"""
    # 1. 最適解の探索
    min_cost = float("inf")
    best_l, best_r = -1, -1
    best_i = -1

    # 最終行から順番に有効な経路を探す
    for i in range(N - 1, -1, -1):
        for l in range(ranges[i][0], ranges[i][1]):
            for r in range(l, ranges[i][1]):
                if dp[i][l][r] < min_cost:
                    min_cost = dp[i][l][r]
                    best_l, best_r = l, r
                    best_i = i
        if min_cost != float("inf"):
            break

    if min_cost == float("inf"):
        print("経路が見つかりませんでした")
        return []

    print(f"最適解: 行{best_i}, 範囲[{best_l}, {best_r}], コスト{min_cost}")

    # 2. 経路の逆算（親ノード情報を使用）
    path_ranges = []
    current_l, current_r = best_l, best_r
    current_i = best_i

    while current_i >= 0:
        path_ranges.append((current_i, current_l, current_r))
        print(f"経路点: 行{current_i}, 範囲[{current_l}, {current_r}]")

        # 親ノード情報を使用して前の行の範囲を取得
        if current_i > 0 and parent[current_i][current_l][current_r] is not None:
            prev_l, prev_r = parent[current_i][current_l][current_r]
            current_l, current_r = prev_l, prev_r
            current_i -= 1
        else:
            break

    path_ranges.reverse()  # 逆順なので反転
    return path_ranges


# 経路復元を実行
path = reconstruct_path()
print(f"\n復元された経路: {path}")

# 経路をグリッドに適用して表示
result_grid = [list(row) for row in grid]
for i, l, r in path:
    for j in range(l, r + 1):
        if 0 <= j < len(result_grid[i]):
            result_grid[i][j] = "#"

print("\n=== 最終的なグリッド（#はStep3のパス） ===")
for row in result_grid:
    print("".join(row))
