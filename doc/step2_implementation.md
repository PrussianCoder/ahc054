## Step2. 左端と右端に縦の道を作る

下のように、左側と右側に対して道を作る

```
..*.....T.ST.....*..
..*...........T..*..
T.*..............*..
..*.....T........*..
..*T.............*..
..*..T...........*..
..*.......T......*..
..*..............*..
..*...T.T........*T.
..*.T..........T.*T.
.T*.T........T...*.T
..*.....T........*..
..*..............*..
..*..TT.........**..
..*.....#.......*T..
..*......#......**..
..*....#X#T......*..
..*.....#...T....*T.
..*..............*..
..*........T.TTT.*..
```

左側の構築方法を示す。右側も左右対称として同様である

- 下記のパスが満たすべき条件を満たす必要がある
- Y<=1の領域には入っていけない（Y>=2の範囲を動くこと）
- なるべく左側に寄せた1本道を作る

上の条件を満たすために、下記のDP+経路復元アルゴリズムで実装する
dp[i][l][r] := i行目のセルのうち、l<=j<=rの領域がパスとなる最小コスト
l,rは0<=l,r<=8程度を考えれば良い（全範囲とってもO(N^3)なので計算は間に合う）

- 初期状態
    - [0,l]から[0,r]の範囲が全て`.`ならば
        - dp[0][l][r] = r + penalty (l<2の場合はpenalty=6を加算)
    - それ以外
        - dp[0][l][r] = inf

- 遷移（2つのパターン）
    - パターン1: (l,r)から(r,r2)への遷移
        - 前の行の最小コストを事前計算: min_r = min(dp[i-1][l][r] for l <= r)
        - dp[i][r][r2] = min(dp[i][r][r2], min_r + r2 + penalty)
    - パターン2: (l,r)から(l2,r)への遷移
        - 前の行の最小コストを事前計算: min_l = min(dp[i-1][l][r] for l <= r)
        - dp[i][l2][r] = min(dp[i][l2][r], min_l + l2 + penalty)

- 復元方法
    - 親ノード情報を記録して正確な経路復元を実行
    - 最終行から逆算して経路を構築


- 参考となる実装

```
class DPPathConstructor:
    """
    DPを使用して左端の縦道を構築するクラス
    l<2以下の侵入を許しつつ、ペナルティ6をかける
    """

    def __init__(self, penalty=6, max_width=8):
        """
        初期化

        Args:
            penalty (int): l<2以下の侵入に対するペナルティ
            max_width (int): 最大幅
        """
        self.penalty = penalty
        self.max_width = max_width
        self.L = 0  # 0から開始（l<2以下の侵入を許可）
        self.dp = None
        self.parent = None
        self.N = 0
        self.R = 0

    def solve(self, grid):
        """
        DPを使用して左端の縦道を構築

        Args:
            grid (list): グリッド（2次元リスト）

        Returns:
            tuple: (path_ranges, min_cost) または (None, None) で経路が見つからない場合
        """
        self.N = len(grid)
        self.R = min(self.max_width, len(grid[0]))  # グリッドの幅に合わせる

        # dp[i][l][r] := i行目のl列からr列までの範囲がパスとなるような最小コスト
        self.dp = [
            [[float("inf")] * self.R for _ in range(self.R)] for _ in range(self.N)
        ]

        # parent[i][l][r] := i行目のl列からr列までの範囲に遷移した親ノード (prev_l, prev_r)
        self.parent = [[[None] * self.R for _ in range(self.R)] for _ in range(self.N)]

        # 初期化
        self._initialize(grid)

        # 遷移
        self._transition(grid)

        # 経路復元
        return self._reconstruct_path()

    def _initialize(self, grid):
        """初期化"""
        for l in range(self.L, self.R):
            for r in range(l, self.R):
                # 0行目のl列からr列までが全て'.'かチェック
                valid = True
                for j in range(l, r + 1):
                    if grid[0][j] != ".":
                        valid = False
                        break
                if valid:
                    # l<2以下の場合はペナルティを加算
                    penalty = self.penalty if l < 2 else 0
                    self.dp[0][l][r] = r + penalty
                    # 初期状態では親ノードなし
                    self.parent[0][l][r] = None

    def _transition(self, grid):
        """遷移"""
        for i in range(1, self.N):
            # パターン1: (l,r)から(r,r2)に遷移する場合
            for r in range(self.L, self.R):
                min_r = float("inf")
                for l in reversed(range(self.L, r + 1)):
                    min_r = min(min_r, self.dp[i - 1][l][r])

                if min_r != float("inf"):
                    for r2 in range(r, self.R):
                        if grid[i][r2] != ".":
                            break
                        # l<2以下の場合はペナルティを加算
                        penalty = self.penalty if r < 2 else 0
                        new_cost = min_r + r2 + penalty
                        if new_cost < self.dp[i][r][r2]:
                            self.dp[i][r][r2] = new_cost
                            # 親ノードを記録（パターン1: (l,r)から(r,r2)への遷移）
                            for l in reversed(range(self.L, r + 1)):
                                if self.dp[i - 1][l][r] == min_r:
                                    self.parent[i][r][r2] = (l, r)
                                    break

            # パターン2: (l,r)から(l2,r)に遷移する場合
            for l in range(self.L, self.R):
                min_l = float("inf")
                for r in range(l, self.R):
                    min_l = min(min_l, self.dp[i - 1][l][r])

                if min_l != float("inf"):
                    for l2 in reversed(range(self.L, l + 1)):
                        if grid[i][l2] != ".":
                            break
                        # l<2以下の場合はペナルティを加算
                        penalty = self.penalty if l2 < 2 else 0
                        new_cost = min_l + l + penalty
                        if new_cost < self.dp[i][l2][l]:
                            self.dp[i][l2][l] = new_cost
                            # 親ノードを記録（パターン2: (l,r)から(l2,r)への遷移）
                            for r in range(l, self.R):
                                if self.dp[i - 1][l][r] == min_l:
                                    self.parent[i][l2][l] = (l, r)
                                    break

    def _reconstruct_path(self):
        """経路復元"""
        # 1. 最適解の探索
        min_cost = float("inf")
        best_l, best_r = -1, -1

        # 最終行から順番に有効な経路を探す
        for i in range(self.N - 1, -1, -1):
            for l in range(self.L, self.R):
                for r in range(l, self.R):
                    if self.dp[i][l][r] < min_cost:
                        min_cost = self.dp[i][l][r]
                        best_l, best_r = l, r
            if min_cost != float("inf"):
                break

        if min_cost == float("inf"):
            return None, None  # 経路が見つからない

        # 2. 経路の逆算（親ノード情報を使用）
        path_ranges = []
        current_l, current_r = best_l, best_r

        for i in range(self.N - 1, -1, -1):
            path_ranges.append((i, current_l, current_r))

            # 親ノード情報を使用して前の行の範囲を取得
            if i > 0 and self.parent[i][current_l][current_r] is not None:
                current_l, current_r = self.parent[i][current_l][current_r]
            else:
                # 親ノード情報がない場合は従来の方法で探索
                found = False
                for l2 in range(self.L, self.R):
                    for r2 in range(l2, self.R):
                        if (
                            self.dp[i - 1][l2][r2] + current_r
                            == self.dp[i][current_l][current_r]
                        ):
                            current_l, current_r = l2, r2
                            found = True
                            break
                    if found:
                        break

        return path_ranges, min_cost

```
