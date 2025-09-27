# AHC054 詳細実装仕様書

## 概要
本仕様書は、AHC054の解法実装のための詳細な仕様を記載する。
冒険者を効率的に迷わせるため、迷路のような一本道を構築し、分岐路を追加することで移動回数を最大化する。

## 座標系の定義
- 座標は `[i,j]` で表記する（0-indexed）
- `i`：行（縦方向、下向きが正）
- `j`：列（横方向、右向きが正）
- スタート地点：`[0, N//2]`
- 花の位置：`[ti, tj]`

## 記号の定義
- `.`：空きマス（何も置かれていない道）
- `T`：初期配置の木
- `#`：新規配置する木（トレント）
- `*`：パスとして使用する予定の道
- `S`：スタート地点
- `X`：花（ゴール）の位置

## データ構造

### Board クラス
```python
class Board:
    def __init__(self, N, ti, tj, initial_board):
        self.N = N
        self.flower = (ti, tj)
        self.start = (0, N // 2)
        self.grid = [[cell for cell in row] for row in initial_board]
        # grid[i][j] は 'T', '.', '*', '#' のいずれか

    def copy(self):
        # 盤面の深いコピーを作成

    def is_valid_pos(self, i, j):
        # 座標が盤面内かチェック
        return 0 <= i < self.N and 0 <= j < self.N

    def debug_print(self):
        # デバッグ用の盤面出力（S,Xも表示）
```

### ForestMazeGenerator クラス
```python
class ForestMazeGenerator:
    def __init__(self):
        pass

    def generate_maze(self, board):
        # 各ステップを実行して迷路を生成
        board = self.step1_surround_flower(board)
        board = self.step2_create_vertical_paths(board)
        board = self.step3_create_main_path(board)
        board = self.step4_connect_start_and_goal(board)
        board = self.step5_create_branches(board)
        board = self.step6_post_process(board)
        return board
```

## 実装詳細

### Step 1: 花の周りに木を配置

#### 処理概要
花の周囲に木を配置して、冒険者が花に直接アクセスできないようにする。
ただし、1箇所だけ開口部を残す。

#### アルゴリズム

1. **上下チェック**
   - `: [ti-1, tj-1]を通路` のいずれかが空きマス(`.`)の場合
     - 左右 `[ti, tj-1]` と `[ti, tj+1]` に木を配置（既存の木や外壁は無視）
     - 上下のうち片方を通路(`.`)、もう片方を木(`#`)にする
     - 通路側の2マス先に木を配置
     - 斜め位置に木を配置（詳細は後述）

2. **上下が両方塞がっている場合**
   - 左右に移動して空きマスを探す
   - 見つかった位置を新しい花の位置として扱い、同様の処理を実行

3. **斜め木の配置ルール**
   ```python
   # 盤面の左側にある時 or 右の端側にある場合、通路が左に来るようにする
   if 3 < tj < N/2 or N-3 <= tj 
       if [ti-1, tj] が通路: [ti-1, tj+1] に木: [ti-1, tj-1]を通路
       if [ti+1, tj] が通路: [ti+1, tj+1] に木: [ti-1, tj-1]を通路
   # 盤面の右側にある時 or 左の端側にある場合、通路が右に来るようにする
   else:
       if [ti-1, tj] が通路: [ti-1, tj-1] に木: [ti-1, tj+1]を通路
       if [ti+1, tj] が通路: [ti+1, tj-1] に木: [ti-1, tj+1]を通路
   ```

上の通路が作れない場合（すでに木が配置されているなど）は、
- 1. の上下の通路の選択を入れ替える
- それでもダメな場合は2. のようにXを左右に移動して処理をする

### Step 2: 左右端に縦の道を作成

#### 処理概要
盤面の左端と右端に縦の道を作成し、後の一本道の基盤とする。各行ごとに到達可能な列を動的計画法（DP）で管理し、効率的に経路を構築する。

#### DPベースのアルゴリズム設計

##### 状態の定義
- `dp[i][j]`: i行目のj列に到達可能かどうか（bool値）
- `parent[i][j]`: i行目のj列に到達するための親ノード（i-1行目の列番号）

##### 左端の縦道構築アルゴリズム

1. **初期化フェーズ**
   ```
   開始候補列: j ∈ [2, min(5, N-1)]
   dp[0][j] = true if grid[0][j] == '.' else false
   選択: 最も左側の利用可能な列を開始点とする
   ```

2. **動的計画法による経路計算**
   ```
   for i from 1 to N-1:
       for j from 2 to min(7, N-1):  // 左端付近の制限範囲
           if grid[i][j] != '.':
               continue

           // 前の行から到達可能かチェック
           for prev_j in [j-1, j, j+1]:  // 斜め左、真下、斜め右から
               if prev_j < 2 or prev_j >= N:
                   continue
               if dp[i-1][prev_j]:
                   // 閉路チェック（簡易版）
                   if not has_adjacent_path_except(i, j, i-1, prev_j):
                       dp[i][j] = true
                       parent[i][j] = prev_j
                       break
   ```

3. **経路の復元**
   ```
   // 最下段（N-1行目）で到達可能な列を探す
   end_j = -1
   for j from 2 to min(7, N-1):
       if dp[N-1][j]:
           end_j = j
           break

   if end_j == -1:
       return FAILURE  // 経路構築失敗

   // 経路を逆順に復元
   path = []
   current_i = N-1
   current_j = end_j

   while current_i >= 0:
       path.append((current_i, current_j))
       grid[current_i][current_j] = '*'
       if current_i > 0:
           current_j = parent[current_i][current_j]
       current_i -= 1
   ```

##### 右端の縦道構築アルゴリズム

1. **初期化フェーズ**
   ```
   開始候補列: j ∈ [max(N-6, 0), N-3]
   dp[0][j] = true if grid[0][j] == '.' else false
   選択: 最も右側の利用可能な列を開始点とする
   ```

2. **動的計画法による経路計算**
   ```
   for i from 1 to N-1:
       for j from max(N-8, 0) to N-3:  // 右端付近の制限範囲
           if grid[i][j] != '.':
               continue

           // 前の行から到達可能かチェック
           for prev_j in [j+1, j, j-1]:  // 斜め右、真下、斜め左から（優先順位）
               if prev_j < 0 or prev_j > N-3:
                   continue
               if dp[i-1][prev_j]:
                   // 閉路チェック
                   if not has_adjacent_path_except(i, j, i-1, prev_j):
                       dp[i][j] = true
                       parent[i][j] = prev_j
                       break
   ```

##### 最適化のポイント

1. **列の範囲制限**
   - 左端: j ∈ [2, 7] の範囲に制限
   - 右端: j ∈ [N-8, N-3] の範囲に制限
   - これにより探索空間をO(N)からO(1)に削減

2. **閉路チェックの簡略化**
   ```python
   def has_adjacent_path_except(i, j, from_i, from_j):
       # 4方向の隣接セルをチェック
       for di, dj in [(0,1), (0,-1), (1,0), (-1,0)]:
           ni, nj = i + di, j + dj
           if (ni, nj) == (from_i, from_j):
               continue  # 接続元は除外
           if 0 <= ni < N and 0 <= nj < N:
               if grid[ni][nj] == '*':
                   return True
       return False
   ```

3. **経路の一意性保証**
   - 各行で最初に到達可能になった列のみを選択
   - これにより分岐を防ぎ、単一の縦道を構築

##### 計算量分析
- 時間計算量: O(N × W^2) where W = 列の探索幅（定数）
- 実質的に: O(N)
- 空間計算量: O(N × W) = O(N)

##### フォールバック処理
DPによる構築が失敗した場合（障害物が多すぎる等）：
1. 探索範囲を徐々に拡大（W を 5 → 10 → 15 と増やす）
2. それでも失敗したら、簡易的な貪欲法で部分的な縦道を構築

#### 実装例（Python）

```python
def create_vertical_paths(board):
    """左端と右端に縦の道を作成"""
    N = board.N

    # 左端の道を作成
    if not create_left_path_dp(board):
        print("Warning: Failed to create left path with DP", file=sys.stderr)
        return False

    # 右端の道を作成
    if not create_right_path_dp(board):
        print("Warning: Failed to create right path with DP", file=sys.stderr)
        return False

    return True

def create_left_path_dp(board):
    """DPを使用して左端の縦道を構築"""
    N = board.N
    W = min(6, N//2)  # 探索幅

    # DPテーブル初期化
    dp = [[False] * N for _ in range(N)]
    parent = [[-1] * N for _ in range(N)]

    # 初期状態設定
    start_j = -1
    for j in range(2, min(W, N)):
        if board.grid[0][j] == '.':
            dp[0][j] = True
            start_j = j
            break

    if start_j == -1:
        return False

    # DP遷移
    for i in range(1, N):
        for j in range(2, min(W, N)):
            if board.grid[i][j] != '.':
                continue

            # 前の行から到達可能かチェック
            for prev_j in [j-1, j, j+1]:  # 優先順位
                if prev_j < 2 or prev_j >= W:
                    continue
                if dp[i-1][prev_j]:
                    # 閉路チェック
                    if not has_adjacent_path(board, i, j, i-1, prev_j):
                        dp[i][j] = True
                        parent[i][j] = prev_j
                        break

    # 経路復元
    end_j = -1
    for j in range(2, min(W, N)):
        if dp[N-1][j]:
            end_j = j
            break

    if end_j == -1:
        return False

    # パスをマーク
    i = N - 1
    j = end_j
    while i >= 0:
        board.grid[i][j] = '*'
        if i > 0:
            j = parent[i][j]
        i -= 1

    return True

def create_right_path_dp(board):
    """DPを使用して右端の縦道を構築"""
    N = board.N
    W = min(6, N//2)  # 探索幅

    # DPテーブル初期化
    dp = [[False] * N for _ in range(N)]
    parent = [[-1] * N for _ in range(N)]

    # 初期状態設定
    start_j = -1
    for j in range(N-3, max(N-W, -1), -1):
        if board.grid[0][j] == '.':
            dp[0][j] = True
            start_j = j
            break

    if start_j == -1:
        return False

    # DP遷移
    for i in range(1, N):
        for j in range(max(N-W, 0), N-2):
            if board.grid[i][j] != '.':
                continue

            # 前の行から到達可能かチェック
            for prev_j in [j+1, j, j-1]:  # 優先順位（右優先）
                if prev_j < N-W or prev_j > N-3:
                    continue
                if dp[i-1][prev_j]:
                    # 閉路チェック
                    if not has_adjacent_path(board, i, j, i-1, prev_j):
                        dp[i][j] = True
                        parent[i][j] = prev_j
                        break

    # 経路復元
    end_j = -1
    for j in range(max(N-W, 0), N-2):
        if dp[N-1][j]:
            end_j = j
            break

    if end_j == -1:
        return False

    # パスをマーク
    i = N - 1
    j = end_j
    while i >= 0:
        board.grid[i][j] = '*'
        if i > 0:
            j = parent[i][j]
        i -= 1

    return True

def has_adjacent_path(board, i, j, from_i, from_j):
    """隣接パスチェック（閉路防止）"""
    for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        ni, nj = i + di, j + dj
        if (ni, nj) == (from_i, from_j):
            continue
        if 0 <= ni < board.N and 0 <= nj < board.N:
            if board.grid[ni][nj] == '*':
                return True
    return False
```
       # 優先順位：右 → 下 → 左（左端とは逆）

       visited = set()
       path = []

       def dfs(i, j):
           if i == N-1:
               return True

           for di, dj in [(0, 1), (1, 0), (0, -1)]:  # 右、下、左
               ni, nj = i + di, j + dj
               if not board.is_valid_pos(ni, nj) or nj > N-3:
                   continue
               if board.grid[ni][nj] != '.':
                   continue
               if (ni, nj) in visited:
                   continue
               # 隣接チェック（閉路防止）
               if has_adjacent_star(board, ni, nj, excluding=(i, j)):
                   continue

               visited.add((ni, nj))
               board.grid[ni][nj] = '*'
               path.append((ni, nj))

               if dfs(ni, nj):
                   return True

               # バックトラック
               visited.remove((ni, nj))
               board.grid[ni][nj] = '.'
               path.pop()

           return False
   ```

### Step 3: DFSで一本道を作成

#### 処理概要
左端の縦道から右端の縦道まで、蛇行する一本道を作成する。

#### アルゴリズム

1. **開始点と初期方向の決定**
   - Step2で作成した左端の道から1点を選択（任意の`*`マス）
   - `i < N/2` なら下向き、`i >= N/2` なら上向きでスタート

2. **右端の道の判定**
   ```python
   def is_right_vertical_path(board, i, j):
       # Step2で作成した右端の縦道の一部であるかチェック
       # j >= N-3 の範囲で、かつ既に'*'である
       return j >= N-3 and board.grid[i][j] == '*'
   ```

3. **DFSによる経路探索**
   ```python
   def create_main_path(board, start_i, start_j, initial_direction):
       direction = initial_direction  # 'up' or 'down'

       def dfs(i, j, direction):
           # 右端の縦道に到達したら成功
           if is_right_vertical_path(board, i, j):
               return True

           # 方向転換の判定
           if direction == 'up' and i == 0:
               direction = 'down'
           elif direction == 'down' and i == N-1:
               direction = 'up'
           elif direction == 'up' and i == 1:
               # 右に2歩以上移動してもi=0に到達できない場合
               if cannot_reach_top_in_2_moves(board, i, j):
                   direction = 'down'

           # 移動優先順位（進行方向により異なる）
           if direction == 'up':
               moves = [(0, -1), (-1, 0), (0, 1)]  # 左、上、右
           else:
               moves = [(0, -1), (1, 0), (0, 1)]   # 左、下、右

           for di, dj in moves:
               ni, nj = i + di, j + dj

               # 移動可能性チェック
               if not board.is_valid_pos(ni, nj):
                   continue
               if nj < 2:  # 左端制限
                   continue
               if board.grid[ni][nj] == '.':
                   # 隣接チェック（閉路防止）- ただし右端の道は除外
                   if has_adjacent_star_excluding_right_path(board, ni, nj, from_pos=(i, j)):
                       continue

                   board.grid[ni][nj] = '*'
                   if dfs(ni, nj, direction):
                       return True
                   board.grid[ni][nj] = '.'  # バックトラック
               elif is_right_vertical_path(board, ni, nj):
                   # 右端の道に接続
                   return True

           return False
   ```

4. **補助関数**
   ```python
   def cannot_reach_top_in_2_moves(board, i, j):
       # 現在位置から右に2歩移動してもi=0に到達できないかチェック
       # j+2 < N かつ [0, j+1], [0, j+2] が空きマスでない
       if j + 2 >= board.N:
           return True
       for jj in range(j+1, min(j+3, board.N)):
           if board.grid[0][jj] == '.':
               return False
       return True

   def has_adjacent_star_excluding_right_path(board, i, j, from_pos):
       # 右端の縦道との接続は許可する
       for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
           ni, nj = i + di, j + dj
           if (ni, nj) == from_pos:
               continue
           if board.is_valid_pos(ni, nj) and board.grid[ni][nj] == '*':
               # 右端の道なら許可
               if nj >= board.N - 3:
                   continue
               return True
       return False
   ```

### Step 4: パスとスタート・ゴールを接続

#### 処理概要
スタート地点と花の位置から、Step3で作成した一本道への最短経路を作成する。

#### アルゴリズム

1. **スタート地点の接続**
   ```python
   def connect_start_to_path(board):
       # スタート地点 [0, N//2] から最も近い '*' マスへの経路を探索
       from collections import deque

       start_pos = (0, board.N // 2)
       queue = deque([(start_pos, [])])
       visited = {start_pos}

       while queue:
           (i, j), path = queue.popleft()

           for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
               ni, nj = i + di, j + dj

               if not board.is_valid_pos(ni, nj):
                   continue
               if (ni, nj) in visited:
                   continue

               if board.grid[ni][nj] == '*':
                   # パスに到達 - 経路上のマスを'*'に変換
                   for pi, pj in path:
                       board.grid[pi][pj] = '*'
                   return True

               if board.grid[ni][nj] == '.':
                   visited.add((ni, nj))
                   queue.append(((ni, nj), path + [(ni, nj)]))

       return False  # 接続失敗
   ```

2. **花（ゴール）の接続**
   ```python
   def connect_flower_to_path(board):
       # 花の位置から最も近い '*' マスへの経路を探索
       # ただし、花の周りの木（Step1で配置）を考慮する必要がある
       from collections import deque

       flower_pos = board.flower
       queue = deque([(flower_pos, [])])
       visited = {flower_pos}

       while queue:
           (i, j), path = queue.popleft()

           for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
               ni, nj = i + di, j + dj

               if not board.is_valid_pos(ni, nj):
                   continue
               if (ni, nj) in visited:
                   continue

               # 花の周りの木('#')は通れるように一時的に扱う
               if board.grid[ni][nj] == '#' and is_adjacent_to_flower(board, ni, nj):
                   # 花に隣接する'#'は通路として扱う（後で戻す）
                   visited.add((ni, nj))
                   queue.append(((ni, nj), path + [(ni, nj)]))
               elif board.grid[ni][nj] == '*':
                   # パスに到達
                   for pi, pj in path:
                       if board.grid[pi][pj] == '#':
                           # 花の周りの木は残す（通路にしない）
                           continue
                       board.grid[pi][pj] = '*'
                   return True
               elif board.grid[ni][nj] == '.':
                   visited.add((ni, nj))
                   queue.append(((ni, nj), path + [(ni, nj)]))

       return False
   ```

3. **補助関数**
   ```python
   def is_adjacent_to_flower(board, i, j):
       # (i, j)が花に隣接しているかチェック
       fi, fj = board.flower
       return abs(i - fi) + abs(j - fj) == 1
   ```

4. **接続の統合処理**
   ```python
   def connect_start_and_goal(board):
       # スタートとゴールを順番に接続
       if not connect_start_to_path(board):
           print("Warning: Failed to connect start to path", file=sys.stderr)
           return False

       if not connect_flower_to_path(board):
           print("Warning: Failed to connect flower to path", file=sys.stderr)
           return False

       return True
   ```

### Step 5: 分岐路を生成

#### 処理概要
一本道から分岐を生成して、冒険者が迷いやすくする。
スタートからの距離が遠い地点から順に分岐を作成する。

#### アルゴリズム

1. **スタートからの距離計算（BFS）**
   ```python
   def calculate_distances_from_start(board):
       distances = {}
       queue = deque([(board.start, 0)])
       visited = {board.start}

       while queue:
           (i, j), dist = queue.popleft()
           if board.grid[i][j] == '*':
               distances[(i, j)] = dist

           for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
               ni, nj = i + di, j + dj
               if board.is_valid_pos(ni, nj) and (ni, nj) not in visited:
                   if board.grid[ni][nj] in ['.', '*']:
                       visited.add((ni, nj))
                       queue.append(((ni, nj), dist + 1))

       return distances
   ```

2. **分岐の生成**
   ```python
   def create_branch(board, i, j):
       # (i, j) から分岐を作成
       for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
           ni1, nj1 = i + di, j + dj
           ni2, nj2 = i + 2*di, j + 2*dj

           if not (board.is_valid_pos(ni1, nj1) and board.is_valid_pos(ni2, nj2)):
               continue

           # 両方が空きマスで、他の'*'に隣接していない
           if board.grid[ni1][nj1] == '.' and board.grid[ni2][nj2] == '.':
               if not has_adjacent_star(board, ni1, nj1, excluding=(i, j)):
                   if not has_adjacent_star(board, ni2, nj2, excluding=(ni1, nj1)):
                       # 分岐を作成
                       board.grid[ni1][nj1] = '*'
                       board.grid[ni2][nj2] = '*'
                       # 周囲を木で囲む
                       block_around_branch(board, ni1, nj1, ni2, nj2)
                       return True

       return False
   ```

3. **スコア計算**
   ```python
   def evaluate_board_score(board, distances):
       score = 0
       for (i, j), dist in distances.items():
           if board.grid[i][j] == '*':
               # 分岐があればボーナス
               if has_branch_at(board, i, j):
                   score += dist
       return score
   ```

### Step 6: 後処理

#### 処理概要
パスに隣接する空きマスに追加の `*` を配置して、迷路を複雑化する。

#### アルゴリズム
```python
def post_process(board):
    changes = True
    while changes:
        changes = False
        for i in range(board.N):
            for j in range(board.N):
                if board.grid[i][j] == '.':
                    # 隣接する'*'が1つだけの場合
                    adjacent_stars = count_adjacent_stars(board, i, j)
                    if adjacent_stars == 1:
                        board.grid[i][j] = '*'
                        changes = True
```

## メイン処理フロー

```python
def solve():
    # 入力読み込み
    N, ti, tj = map(int, input().split())
    initial_board = [input() for _ in range(N)]

    # 初期盤面作成
    board = Board(N, ti, tj, initial_board)

    # 最良の盤面を探索（時間制限まで繰り返し）
    best_board = None
    best_score = -1

    start_time = time.time()
    iteration = 0

    while time.time() - start_time < 1.5:  # 1.5秒まで探索
        # 盤面生成
        generator = ForestMazeGenerator()
        candidate_board = board.copy()

        try:
            # ランダム要素を加えながら生成
            candidate_board = generator.generate_maze(candidate_board)

            # スコア評価
            score = generator.evaluate_score(candidate_board)

            if score > best_score:
                best_score = score
                best_board = candidate_board
        except:
            # 生成失敗時は次の試行へ
            pass

        iteration += 1

    # 結果を初回配置用に変換
    trees_to_place = []
    for i in range(N):
        for j in range(N):
            if best_board.grid[i][j] == '*':
                # パスは残す（木を配置しない）
                pass
            elif best_board.grid[i][j] == '#':
                # 新規の木を配置
                trees_to_place.append((i, j))

    # インタラクティブ処理
    revealed = set()
    while True:
        pi, pj = map(int, input().split())
        parts = input().split()
        n = int(parts[0])
        xy = list(map(int, parts[1:]))

        for k in range(n):
            x = xy[2 * k]
            y = xy[2 * k + 1]
            revealed.add((x, y))

        if pi == ti and pj == tj:
            break

        # 初回のみ木を配置
        if len(revealed) == 1:  # 初回ターン
            output = []
            for i, j in trees_to_place:
                if (i, j) not in revealed:
                    output.append(f"{i} {j}")
            print(f"{len(output)} {' '.join(output)}", flush=True)
        else:
            print(0, flush=True)
```

## エラー処理とデバッグ

1. **経路の接続性チェック**
   - Step4の後、スタートから花への経路が存在することを確認
   - 存在しない場合はエラーメッセージを出力

2. **デバッグ出力**
   ```python
   def debug_board(board, message=""):
       print(f"=== {message} ===", file=sys.stderr)
       for i in range(board.N):
           row = []
           for j in range(board.N):
               if (i, j) == board.start:
                   row.append('S')
               elif (i, j) == board.flower:
                   row.append('X')
               else:
                   row.append(board.grid[i][j])
           print(''.join(row), file=sys.stderr)
   ```

## 計算量分析

### 各ステップの計算量

| ステップ | 従来手法 | 改善手法 | 備考 |
|---------|---------|---------|------|
| Step 1（花の周り） | O(1) | O(1) | 定数個の配置 |
| Step 2（縦の道） | O(2^N) 最悪 | O(N) | 段階的構築により改善 |
| Step 3（一本道） | O(N^3) 最悪 | O(N^2) | 経路長がO(N^2)、各ステップO(1) |
| Step 4（接続） | O(N^2) | O(N^2) | BFSによる最短経路探索 |
| Step 5（分岐） | O(N^2) | O(N^2) | 全パスポイントをチェック |
| Step 6（後処理） | O(N^2) | O(N^2) | 全マスをチェック |

### 全体の計算量
- **従来手法**: O(2^N) 最悪ケース（Step 2がボトルネック）
- **改善手法**: O(N^2) （全ステップがO(N^2)以内）

### 実行時間の見積もり
- N=20の場合：
  - 改善手法で1回の盤面生成: 約10ms
  - 1.5秒で約150回の試行が可能
- N=50の場合：
  - 改善手法で1回の盤面生成: 約50ms
  - 1.5秒で約30回の試行が可能

## 性能目標
- 1つの盤面生成：O(N^2) 以内
- 1.5秒で30回以上の試行を実施（N=50の場合）
- 1.5秒で150回以上の試行を実施（N=20の場合）
- スコア：初期実装で絶対スコア1000以上を目標