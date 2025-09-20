# A - Treant's Forest

実行時間制限: 2 sec / メモリ制限: 1024 MiB

### ストーリー
AtCoder王国の南には、通称「迷いの森」と呼ばれる、入るたびに道が変わる不思議な森が広がっている。この森には、見つけると幸せが訪れるという伝説の花 *Aura Amaryllis*（通称AA）が存在すると言われており、今日もその花を求めて冒険者がやってきた。

迷いの森の真相は、木の魔物「トレント」が木に化けて冒険者を惑わせているというものである。トレントは迷っている冒険者から魔力を吸い取ることで生命を維持しており、できる限り長い時間、冒険者を森に留まらせたいと考えている。ただし、冒険者がAAにたどり着けなかった場合、「あの花は存在しなかった」という噂が広まり、それ以降誰も森に来なくなってしまう。そうなると魔力を得られなくなったトレントたちは、やがて死に絶えてしまうのだ。

また、冒険者は道に迷わないよう、マッピングをしながら森を探索している。すでにマッピングされた場所にトレントを移動させてしまうと、それが本物の木ではなくトレントであることが冒険者に見破られ、切り倒されてしまう。このような事態は、何としても避けなければならない。

トレントのボスであるあなたには、冒険者がAAにたどり着くまでの時間ができるだけ長くなるよう、冒険者の動きに応じてトレントたちの配置を適切に調整していくことが求められる。

### 問題文
N × N マスの森がある。左上のマスの座標を (0, 0) とし、下方向に i、右方向に j マス進んだ位置の座標を (i, j) とする。各マスは「空きマス」もしくは「木」のいずれかである。N × N マスの範囲外は木で囲まれている。

マス (0, ⌊ N / 2 ⌋) は森の入口であり、空きマスである。マス (t_i, t_j) に伝説の花が咲いており、そこも空きマスである。

伝説の花を求めて、冒険者が森へやってきた。冒険者は、公開情報である **現在位置** と **確認済みマス**、非公開情報である **目的地** の3つの状態を持つ。未確認のマスをすべて空きマスであると仮定した森の地図を、**暫定地図** と呼ぶ。

初期状態では、**現在位置** は森の入口、**確認済みマス** はその1マスと N × N マスの外部すべて、**目的地** は未定である。冒険者の行動は毎ターン、以下の順に処理される。

1. **現在位置** に伝説の花がある場合、目的を達成し、行動を終了する。
2. 上下左右それぞれの方向に対し、**現在位置** からその方向に進んだ最初の「木」のマスまで（その木のマスを含む）のすべての未確認マスを **確認済みマス** に追加する。
3. 伝説の花が **確認済みマス** に含まれている場合、**目的地** をそのマスに設定する。
4. **目的地** が未定でなく、**暫定地図** において **目的地** が現在位置から空きマスのみを通って到達不能な場合、**目的地** を未定に戻す。
5. **目的地** が未定であるか、伝説の花以外の **確認済みマス** にある場合、**暫定地図** において、現在位置から空きマスのみを通って到達可能な未確認マスの中から一様ランダムに1つ選び、それを **目的地** に設定する（そのようなマスが存在しない場合、後述するように WA となる）。
6. **暫定地図** において、各マスから空きマスのみを通って **目的地** へ到達する最短距離を計算する。現在位置に隣接する空きマスのうち、**目的地** までの最短距離がより短くなるマスに移動する。そのようなマスが複数ある場合、上下左右の順に優先度をつけ、先に挙げられた方向を選択する。

木の魔物「トレント」のボスであるあなたの目的は、トレントたちに指示を出して冒険者を迷わせ、伝説の花にたどり着くまでのターン数をできるだけ長くすることである。あなたは毎ターンの開始前に、**確認済みマス** でない任意個の空きマスを選び、それぞれに1体ずつトレントを配置することができる。トレントを配置したマスは、それ以降「空きマス」ではなく「木」として扱われ、動かすことはできない。

ただし、森の入口から伝説の花まで、空きマスのみを通る経路が必ず1つ以上存在しなければならない。そのような経路が存在しない場合、解答は WA となる。

### 得点
冒険者が森の入口から入り、伝説の花にたどり着くまでにかかった移動回数が、そのテストケースにおける絶対スコアとなる。絶対スコアは大きいほど良い。

各テストケース毎に、round(10^9 × (自身の絶対スコア / 全参加者中の最大絶対スコア)) の**相対評価スコア**が得られ、その和が提出の得点となる。

最終順位はコンテスト終了後に実施されるより多くの入力に対するシステムテストにおける得点で決定される。暫定テスト、システムテストともに、一部のテストケースで不正な出力や制限時間超過をした場合、そのテストケースの相対評価スコアは0点となり、そのテストケースにおいては「全参加者中の最大絶対スコア」の計算から除外される。システムテストは**CE 以外の結果を得た一番最後の提出**に対してのみ行われるため、最終的に提出する解答を間違えないよう注意せよ。

#### テストケース数
- 暫定テスト: 100個
- システムテスト: 3000個、コンテスト終了後に [seeds.txt](https://img.atcoder.jp/ahc054/seeds.txt) (sha256=f46e04db0ec8f80d641bbc8e166b1d2f4050a340b356acea1adce1a41a0a7fc8) を公開

#### 相対評価システムについて
暫定テスト、システムテストともに、CE 以外の結果を得た一番最後の提出のみが順位表に反映される。相対評価スコアの計算に用いられる各テストケース毎の全参加者中の最大絶対スコアの算出においても、順位表に反映されている最終提出のみが用いられる。

順位表に表示されているスコアは相対評価スコアであり、新規提出があるたびに、相対評価スコアが再計算される。一方、提出一覧から確認出来る各提出のスコアは各テストケース毎の絶対スコアをそのまま足し合わせたものであり、相対評価スコアは表示されない。最新以外の提出の、現在の順位表における相対評価スコアを知るためには、再提出が必要である。不正な出力や制限時間超過をした場合、提出一覧から確認出来るスコアは0となるが、順位表には正解したテストケースに対する相対スコアの和が表示されている。

#### 実行時間について
実行時間には多少のブレが生じます。また、システムテストでは同時に大量の実行を行うため、暫定テストに比べて数%程度実行時間が伸びる現象が確認されています。そのため、実行時間制限ギリギリの提出がシステムテストでTLEとなる可能性があります。実行時間を計測してプロセスを終了させるようにするか、十分な余裕を持たせてください。

### 入出力
まずはじめに、以下の情報が標準入力から与えられる。

```
N t_i t_j
b_{0,0}…b_{0,N-1}
⋮
b_{N-1,0}…b_{N-1,N-1}
```

- 森の縦横の幅 N は 20 ≤ N ≤ 40 を満たす。
- 伝説の花の座標 (t_i, t_j) は 0 ≤ t_i, t_j ≤ N - 1 を満たし、森の入口 (0, ⌊ N / 2 ⌋) とのマンハッタン距離が 5 以上であることが保証されている。
- b_{i,0} … b_{i,N-1} は長さ N の文字列であり、その j 文字目 b_{i,j} は、マス (i, j) が空きマスであれば `.`、木であれば `T` を表す。
- すべての空きマスは、森の入口 (0, ⌊ N / 2 ⌋) から空きマスのみを通って到達可能であることが保証されている。

次に、以下の処理を繰り返す。まず、各ターンの開始時に、冒険者の現在位置と、前のターンに新たに確認済みとなったマスが、以下の形式で標準入力から与えられる。

```
p_i p_j
n x_0 y_0 … x_{n-1} y_{n-1}
```

- (p_i, p_j) は冒険者の現在位置を表す。
- n は前のターンに新たに確認済みとなったマスの個数であり、(x_k, y_k) はその k 番目のマスの座標である。
- 最初のターンにおいては、(p_i, p_j) = (0, ⌊ N / 2 ⌋)、n = 1、(x_0, y_0) = (0, ⌊ N / 2 ⌋) である。

(p_i, p_j) = (t_i, t_j) の場合、冒険者が伝説の花に到達したことを意味し、繰り返しを終了してプログラムも終了する。そうでない場合、このターンの開始前に新たにトレントを配置するマスの集合を (x_0', y_0'), …, (x_{m-1}', y_{m-1}') とし、以下の形式で標準出力に出力せよ。

```
m x_0' y_0' … x_{m-1}' y_{m-1}'
```

**出力の後には改行をし、更に標準出力を flush しなければならない。** そうしない場合、TLE となる可能性がある。

[例を見る](https://img.atcoder.jp/ahc054/YDAxDRZr.html?lang=ja&seed=0&output=sample)

### 入力生成方法
L 以上 U 以下の整数値を一様ランダムに生成する関数を rand(L, U) とする。

N = rand(20, 40) により、森のサイズ N を生成する。

すべて空きマスの状態から開始し、以下の手順で木の配置を生成する。まず、木の本数の上限 K を K = max(1, rand(0, ⌊ N^2 / 6 ⌋)) により生成する。森の入口を除いた N^2 - 1 個のマスをランダムな順序で (i_0, j_0), …, (i_{N^2 - 2}, j_{N^2 - 2}) に並べ、各 k に対して順に以下の処理を行う。

(i_k, j_k) に木を仮に置いたうえで、すべての空きマスが森の入口から到達可能かを判定する。到達不能な場合は、木を置くのを取りやめる。置いた木の本数が K に達した時点で、処理を中断する。

最後に、伝説の花の座標 (t_i, t_j) を、条件を満たす空きマスの中から一様ランダムに選択する。

### ツール(入力ジェネレータ・ローカルテスタ・ビジュアライザ)
- [Web版](https://img.atcoder.jp/ahc054/YDAxDRZr.html?lang=ja): ローカル版より高性能でアニメーション表示が可能です。
- [ローカル版](https://img.atcoder.jp/ahc054/YDAxDRZr.zip): 使用するには[Rust言語](https://www.rust-lang.org/ja)のコンパイル環境をご用意下さい。
  - [Windows用のコンパイル済みバイナリ](https://img.atcoder.jp/ahc054/YDAxDRZr_windows.zip): Rust言語の環境構築が面倒な方は代わりにこちらをご利用下さい。

コンテスト期間中に、ビジュアライズ結果の共有や、解法・考察に関する言及は禁止されています。ご注意下さい。

#### ツールで用いられる入出力ファイルの仕様
ローカルテスタに与える入力ファイルは以下の形式を用いている。

```
N t_i t_j
b_{0,0}…b_{0,N-1}
⋮
b_{N-1,0}…b_{N-1,N-1}
q_i^0 q_j^0
⋮
q_i^{N^2-2} q_j^{N^2-2}
```

末尾に追加されている (q_i^k, q_j^k) は、k 回目の目的地を表し、冒険者が目的地を選択する際にはこの順番で見ていき、条件を満たすものが順に選ばれる。q は森の入口を除いた N^2 - 1 個のマスをランダムな順序で並べることで生成されている。

### サンプルプログラム (Python)
Python による解答例を示す。このプログラムでは、確認済みとなったマスの管理を行いつつ、トレントは一切配置しない。

```
N, ti, tj = map(int, input().split())
b = [input() for _ in range(N)]
revealed = [[False] * N for _ in range(N)]
while True:
    pi, pj = map(int, input().split())
    parts = input().split()
    n = int(parts[0])
    xy = list(map(int, parts[1:]))
    for k in range(n):
        x = xy[2 * k]
        y = xy[2 * k + 1]
        revealed[x][y] = True
    if pi == ti and pj == tj:
        break
    print(0, flush=True)
```

### 入力例 1
```
20 16 8
........T..T........
..............T.....
T...................
........T...........
...T................
.....T..............
..........T.........
....................
......T.T.........T.
....T..........T..T.
.T..T........T.....T
........T...........
....................
.....TT.............
.................T..
....................
..........T.........
............T.....T.
....................
...........T.TTT....
16 3
1 7
8 6
8 13
3 1
13 2
16 6
2 5
18 10
10 9
19 2
7 10
6 12
4 7
10 4
10 7
18 8
12 2
14 2
3 7
4 19
14 7
18 5
5 4
4 2
14 16
11 4
0 3
0 0
8 18
19 17
11 5
18 17
18 12
10 1
8 7
17 3
16 18
16 15
0 5
13 13
14 1
8 9
19 10
17 4
15 9
9 11
1 16
4 1
10 5
1 14
17 7
17 10
11 10
8 5
6 9
4 5
4 3
12 9
6 2
4 17
8 2
19 19
12 1
2 4
8 10
13 7
5 16
2 17
5 0
16 0
14 10
6 13
18 13
12 7
0 12
11 9
8 15
10 18
11 11
16 11
5 12
9 15
7 13
15 1
16 9
7 9
15 10
1 13
7 16
7 18
3 10
1 2
18 1
15 11
5 8
6 16
8 12
2 3
18 14
5 14
13 10
2 9
17 12
0 4
11 3
13 6
17 16
14 4
16 5
14 15
17 1
16 8
3 11
12 11
8 19
1 5
5 7
12 16
0 2
17 0
19 8
7 11
10 2
3 6
0 16
5 1
4 16
19 9
7 6
3 9
6 11
16 2
13 3
19 15
12 13
6 10
6 7
16 12
15 7
13 18
8 14
19 7
4 18
15 14
11 13
4 12
11 16
17 8
2 14
12 19
15 5
9 19
12 5
13 19
3 13
9 16
10 17
7 14
3 0
6 5
17 19
9 17
15 2
1 17
17 6
2 13
9 8
5 19
9 2
8 8
15 16
15 12
15 4
10 6
4 8
7 19
10 19
18 9
9 0
10 12
16 4
15 17
1 12
18 0
13 16
14 5
9 5
13 9
1 11
2 0
14 12
14 14
2 12
7 8
1 18
5 13
9 9
10 13
16 16
3 4
17 5
0 7
5 3
17 2
11 12
13 17
18 3
1 19
1 1
6 17
12 6
15 0
8 3
11 17
8 1
14 0
15 8
7 3
14 19
2 15
15 18
17 14
2 6
3 3
12 3
10 16
6 8
3 8
14 9
10 14
18 18
3 15
0 15
11 15
18 16
5 15
3 17
16 19
11 6
5 2
13 8
12 15
5 10
6 0
7 0
5 5
4 10
7 17
11 8
6 1
4 6
19 11
7 5
10 15
18 2
18 11
2 1
12 0
0 9
5 18
13 14
15 6
9 18
9 3
15 15
4 11
2 2
13 0
8 0
9 6
9 12
9 13
9 7
5 6
4 14
12 17
2 19
2 18
14 17
8 11
6 18
3 14
5 17
11 19
1 3
15 3
10 11
18 6
19 4
17 9
14 11
19 18
17 15
0 13
11 14
3 19
7 7
4 15
9 1
12 10
2 11
19 16
9 14
4 0
6 14
10 0
17 17
12 4
17 13
16 10
13 1
2 7
19 6
12 12
0 11
7 12
19 13
0 6
12 8
19 1
14 13
1 6
11 1
0 1
0 18
7 1
14 8
6 19
4 4
1 15
8 17
5 11
5 9
16 14
10 3
13 15
0 14
1 10
7 4
3 2
3 5
6 6
6 4
3 16
12 14
15 13
18 4
19 12
17 11
15 19
6 15
13 4
16 7
4 13
7 2
19 3
12 18
1 0
16 17
10 8
11 18
8 4
18 7
6 3
19 0
19 14
16 1
16 13
1 4
1 8
0 19
18 15
2 10
0 17
14 18
7 15
1 9
9 4
14 3
11 0
14 6
13 11
3 12
11 2
2 8
4 9
3 18
8 16
19 5
2 16
11 7
13 5
17 18
13 12
10 10
0 8
9 10
18 19
```

### 出力例 1
```
1 1 10
0 
1 1 8
2 2 8 2 10
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
```

### Story
To the south of the Kingdom of AtCoder lies a mysterious forest commonly known as the "Lost Forest," where the paths change every time one enters. It is said that within this forest blooms a legendary flower called *Aura Amaryllis* (commonly abbreviated as AA), which brings happiness to those who find it. Even today, adventurers arrive in search of this flower.

The true nature of the Lost Forest is that tree monsters known as "Treants" disguise themselves as trees to confuse adventurers. Treants sustain their lives by absorbing magical energy from lost adventurers, so they aim to keep the adventurers in the forest for as long as possible. However, if an adventurer fails to reach the AA, rumors will spread that "the flower never existed," and no one will enter the forest again. If that happens, the Treants will no longer be able to obtain magical energy and will eventually perish.

Furthermore, adventurers explore the forest while mapping it to avoid getting lost. If a Treant moves to a location that has already been mapped, the adventurer will realize that it is not a real tree but a Treant in disguise and will cut it down. This situation must be avoided at all costs.

As the boss of the Treants, your role is to adjust the placement of the Treants in response to the adventurer's movements to ensure that it takes longer for the adventurer to reach the AA.

### Problem Statement
There is a forest consisting of an N × N grid of cells. The coordinates of the top-left cell are (0, 0). The cell located i cells down and j cells to the right has coordinates (i, j). Each cell is either an "empty cell" or a "tree". The area outside the N × N grid is surrounded by trees.

The cell (0, ⌊ N / 2 ⌋) is the entrance to the forest and is an empty cell. The legendary flower blooms at cell (t_i, t_j), which is also an empty cell.

An adventurer has entered the forest in search of the legendary flower. The adventurer has three states: the **current position** and the **revealed cells**, which are public information, and the **destination**, which is hidden. A map of the forest assuming all unrevealed cells are empty is called the **tentative map**.

Initially, the **current position** is the forest entrance, the **revealed cells** include only that one cell and all cells outside the N × N grid, and the **destination** is unset. Each turn, the adventurer's actions are processed in the following order:

1. If the legendary flower is at the **current position**, the goal is achieved and the adventurer stops moving.
2. For each of the four directions (up, down, left, right), add to the **revealed cells** all unrevealed cells from the **current position** up to and including the first "tree" cell encountered in that direction.
3. If the legendary flower is included in the **revealed cells**, set the **destination** to that cell.
4. If the **destination** is set but is unreachable from the current position in the **tentative map** using only empty cells, unset the **destination**.
5. If the **destination** is unset or is a cell in the **revealed cells** other than the legendary flower, choose one cell uniformly at random from the unrevealed cells that are reachable from the current position via empty cells in the **tentative map**, and set it as the **destination** (if no such cell exists, this will result in a WA, as described below).
6. In the **tentative map**, compute the shortest distance to the **destination** using only empty cells. Move to an adjacent empty cell that shortens the distance to the **destination**. If multiple such cells exist, choose the one in the order of preference: up, down, left, right.

As the boss of the tree monsters known as "Treants," your goal is to direct the Treants to confuse the adventurer and maximize the number of turns it takes to reach the legendary flower.

At the beginning of each turn, you may choose any number of empty cells that are not part of the **revealed cells** and place one Treant in each. Cells where Treants are placed are no longer considered "empty" and are treated as "trees" from that point onward. Treants cannot be moved once placed.

You must ensure that there is always at least one path from the forest entrance to the legendary flower consisting only of empty cells. If no such path exists, your solution will result in a WA.

### Scoring
The number of moves the adventurer takes to reach the legendary flower from the forest entrance is the absolute score for that test case. The higher the absolute score, the better.

For each test case, we compute the **relative score** round(10^9 × (YOUR / MAX)), where YOUR is your absolute score and MAX is the highest absolute score among all competitors obtained on that test case. The score of the submission is the sum of the relative scores.

The final ranking will be determined by the system test with more inputs which will be run after the contest is over. In both the provisional/system test, if your submission produces illegal output or exceeds the time limit for some test cases, only the score for those test cases will be zero, and your submission will be excluded from the MAX calculation for those test cases.

The system test will be performed only for **the last submission which received a result other than CE**. Be careful not to make a mistake in the final submission.

#### Number of test cases
- Provisional test: 100
- System test: 3000. We will publish [seeds.txt](https://img.atcoder.jp/ahc054/seeds.txt) (sha256=f46e04db0ec8f80d641bbc8e166b1d2f4050a340b356acea1adce1a41a0a7fc8) after the contest is over.

#### About relative evaluation system
In both the provisional/system test, the standings will be calculated using only the last submission which received a result other than CE. Only the last submissions are used to calculate the MAX for each test case when calculating the relative scores.

The scores shown in the standings are relative, and whenever a new submission arrives, all relative scores are recalculated. On the other hand, the score for each submission shown on the submissions page is the sum of the absolute score for each test case, and the relative scores are not shown. In order to know the relative score of submission other than the latest one in the current standings, you need to resubmit it. If your submission produces illegal output or exceeds the time limit for some test cases, the score shown on the submissions page will be 0, but the standings show the sum of the relative scores for the test cases that were answered correctly.

#### About execution time
Execution time may vary slightly from run to run. In addition, since system tests simultaneously perform a large number of executions, it has been observed that execution time increases by several percent compared to provisional tests. For these reasons, submissions that are very close to the time limit may result in TLE in the system test. Please measure the execution time in your program to terminate the process, or have enough margin in the execution time.

### Input and Output
At the beginning, the following information is given via Standard Input:

```
N t_i t_j
b_{0,0}…b_{0,N-1}
⋮
b_{N-1,0}…b_{N-1,N-1}
```

- N, the height/width of the forest, satisfies 20 ≤ N ≤ 40.
- The coordinates (t_i, t_j) of the legendary flower satisfy 0 ≤ t_i, t_j ≤ N - 1, and it is guaranteed that the Manhattan distance from the forest entrance (0, ⌊ N / 2 ⌋) is at least 5.
- b_{i,0} … b_{i,N-1} is a string of length N. Its j-th character b_{i,j} is `.` if cell (i, j) is empty, and `T` if it is a tree.
- It is guaranteed that every empty cell is reachable from the forest entrance (0, ⌊ N / 2 ⌋) via empty cells only.

Next, repeat the following process. At the beginning of each turn, the adventurer's current position and the cells that became revealed during the previous turn are given via Standard Input in the following format:

```
p_i p_j
n x_0 y_0 … x_{n-1} y_{n-1}
```

- (p_i, p_j) represents the adventurer's current position.
- n is the number of cells that became revealed during the previous turn. (x_k, y_k) represents the coordinates of the k-th such cell.
- In the first turn, (p_i, p_j) = (0, ⌊ N / 2 ⌋), n = 1, and (x_0, y_0) = (0, ⌊ N / 2 ⌋).

If (p_i, p_j) = (t_i, t_j), the adventurer has reached the legendary flower, so you should terminate the loop and the program. Otherwise, let (x_0', y_0'), …, (x_{m-1}', y_{m-1}') be the set of cells where you newly place Treants before the start of this turn, and output the following to Standard Output:

```
m x_0' y_0' … x_{m-1}' y_{m-1}'
```

**You must print a newline after the output and flush Standard Output.** Otherwise, you may get TLE.

[View example](https://img.atcoder.jp/ahc054/YDAxDRZr.html?lang=en&seed=0&output=sample)

### Input Generation
Let rand(L, U) be a function that generates a uniformly random integer between L and U, inclusive.

Generate the forest size N using N = rand(20, 40).

Starting from the state where all cells are empty, generate the tree placement using the following procedure. First, generate the upper bound K on the number of trees using K = max(1, rand(0, ⌊ N^2 / 6 ⌋)). Arrange the N^2 - 1 cells other than the forest entrance in a random order (i_0, j_0), …, (i_{N^2 - 2}, j_{N^2 - 2}). For each k, perform the following process in this order.

Temporarily place a tree at (i_k, j_k) and check whether every empty cell remains reachable from the forest entrance. If not, cancel the placement. Stop the process once the number of placed trees reaches K.

Finally, choose the coordinates (t_i, t_j) of the legendary flower uniformly at random from the empty cells that satisfy the conditions.

### Tools (Input generator, local tester, and visualizer)
- [Web version](https://img.atcoder.jp/ahc054/YDAxDRZr.html?lang=en): Higher performance than the local version and can display animations.
- [Local version](https://img.atcoder.jp/ahc054/YDAxDRZr.zip): Requires a [Rust](https://www.rust-lang.org) compiler toolchain.
  - [Compiled binary for Windows](https://img.atcoder.jp/ahc054/YDAxDRZr_windows.zip): Use this if setting up Rust is troublesome.

Sharing visualization results or discussing solutions/strategies is prohibited during the contest. Please be careful.

#### Input/output file format used in the tools
The input files for the local tester follow the format below:

```
N t_i t_j
b_{0,0}…b_{0,N-1}
⋮
b_{N-1,0}…b_{N-1,N-1}
q_i^0 q_j^0
⋮
q_i^{N^2-2} q_j^{N^2-2}
```

The appended (q_i^k, q_j^k) at the end represents the destination chosen on the k-th attempt. When the adventurer selects destinations, they are checked in this order, and the first one satisfying the conditions is chosen. q is generated by arranging the N^2 - 1 cells other than the forest entrance in a random order.

### Sample Solution (Python)
Below is a sample solution in Python. This program keeps track of the revealed cells and never places any Treants.

```
N, ti, tj = map(int, input().split())
b = [input() for _ in range(N)]
revealed = [[False] * N for _ in range(N)]
while True:
    pi, pj = map(int, input().split())
    parts = input().split()
    n = int(parts[0])
    xy = list(map(int, parts[1:]))
    for k in range(n):
        x = xy[2 * k]
        y = xy[2 * k + 1]
        revealed[x][y] = True
    if pi == ti and pj == tj:
        break
    print(0, flush=True)
```

### Sample Input 1
```
20 16 8
........T..T........
..............T.....
T...................
........T...........
...T................
.....T..............
..........T.........
....................
......T.T.........T.
....T..........T..T.
.T..T........T.....T
........T...........
....................
.....TT.............
.................T..
....................
..........T.........
............T.....T.
....................
...........T.TTT....
16 3
1 7
8 6
8 13
3 1
13 2
16 6
2 5
18 10
10 9
19 2
7 10
6 12
4 7
10 4
10 7
18 8
12 2
14 2
3 7
4 19
14 7
18 5
5 4
4 2
14 16
11 4
0 3
0 0
8 18
19 17
11 5
18 17
18 12
10 1
8 7
17 3
16 18
16 15
0 5
13 13
14 1
8 9
19 10
17 4
15 9
9 11
1 16
4 1
10 5
1 14
17 7
17 10
11 10
8 5
6 9
4 5
4 3
12 9
6 2
4 17
8 2
19 19
12 1
2 4
8 10
13 7
5 16
2 17
5 0
16 0
14 10
6 13
18 13
12 7
0 12
11 9
8 15
10 18
11 11
16 11
5 12
9 15
7 13
15 1
16 9
7 9
15 10
1 13
7 16
7 18
3 10
1 2
18 1
15 11
5 8
6 16
8 12
2 3
18 14
5 14
13 10
2 9
17 12
0 4
11 3
13 6
17 16
14 4
16 5
14 15
17 1
16 8
3 11
12 11
8 19
1 5
5 7
12 16
0 2
17 0
19 8
7 11
10 2
3 6
0 16
5 1
4 16
19 9
7 6
3 9
6 11
16 2
13 3
19 15
12 13
6 10
6 7
16 12
15 7
13 18
8 14
19 7
4 18
15 14
11 13
4 12
11 16
17 8
2 14
12 19
15 5
9 19
12 5
13 19
3 13
9 16
10 17
7 14
3 0
6 5
17 19
9 17
15 2
1 17
17 6
2 13
9 8
5 19
9 2
8 8
15 16
15 12
15 4
10 6
4 8
7 19
10 19
18 9
9 0
10 12
16 4
15 17
1 12
18 0
13 16
14 5
9 5
13 9
1 11
2 0
14 12
14 14
2 12
7 8
1 18
5 13
9 9
10 13
16 16
3 4
17 5
0 7
5 3
17 2
11 12
13 17
18 3
1 19
1 1
6 17
12 6
15 0
8 3
11 17
8 1
14 0
15 8
7 3
14 19
2 15
15 18
17 14
2 6
3 3
12 3
10 16
6 8
3 8
14 9
10 14
18 18
3 15
0 15
11 15
18 16
5 15
3 17
16 19
11 6
5 2
13 8
12 15
5 10
6 0
7 0
5 5
4 10
7 17
11 8
6 1
4 6
19 11
7 5
10 15
18 2
18 11
2 1
12 0
0 9
5 18
13 14
15 6
9 18
9 3
15 15
4 11
2 2
13 0
8 0
9 6
9 12
9 13
9 7
5 6
4 14
12 17
2 19
2 18
14 17
8 11
6 18
3 14
5 17
11 19
1 3
15 3
10 11
18 6
19 4
17 9
14 11
19 18
17 15
0 13
11 14
3 19
7 7
4 15
9 1
12 10
2 11
19 16
9 14
4 0
6 14
10 0
17 17
12 4
17 13
16 10
13 1
2 7
19 6
12 12
0 11
7 12
19 13
0 6
12 8
19 1
14 13
1 6
11 1
0 1
0 18
7 1
14 8
6 19
4 4
1 15
8 17
5 11
5 9
16 14
10 3
13 15
0 14
1 10
7 4
3 2
3 5
6 6
6 4
3 16
12 14
15 13
18 4
19 12
17 11
15 19
6 15
13 4
16 7
4 13
7 2
19 3
12 18
1 0
16 17
10 8
11 18
8 4
18 7
6 3
19 0
19 14
16 1
16 13
1 4
1 8
0 19
18 15
2 10
0 17
14 18
7 15
1 9
9 4
14 3
11 0
14 6
13 11
3 12
11 2
2 8
4 9
3 18
8 16
19 5
2 16
11 7
13 5
17 18
13 12
10 10
0 8
9 10
18 19
```

### Sample Output 1
```
1 1 10
0 
1 1 8
2 2 8 2 10
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
0 
```
