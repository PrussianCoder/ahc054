# AHC054 スコア計算ガイド

## 概要

このドキュメントでは、AHC054において構築された盤面をBoardSimulatorクラスで評価し、スコアを見積もる方法について説明します。

## スコア計算の基本原理

### 1. 基本スコア（Absolute Score）
- **定義**: 冒険者が移動したターン数
- **計算方法**: `sim.turn` (シミュレーション完了時のターン数)
- **最適化目標**: できるだけ少ないターン数でゴールに到達する

### 2. 相対スコア（Relative Score）
- **定義**: `round(10^9 × (YOUR_SCORE / MAX_SCORE))`
- **説明**: 全参加者の中での最高スコアに対する相対的な評価
- **範囲**: 0 ～ 10^9

## スコア計算の実装

### tools/src/lib.rsの実装構造

#### 1. メイン関数
```rust
pub fn compute_score(input: &Input, out: &Output) -> (i64, String)
```
- 入力: 問題設定(`Input`)と出力解答(`Output`)
- 戻り値: `(スコア, エラーメッセージ)`
- エラーがある場合はスコアを0に設定

#### 2. 詳細計算関数
```rust
pub fn compute_score_details(input: &Input, out: &[Vec<(usize, usize)>]) -> (i64, String, Sim)
```
- シミュレーション詳細も含めて返す
- 戻り値: `(スコア, エラーメッセージ, シミュレータ状態)`

### Simクラスの構造

#### フィールド
- `N`: 盤面サイズ
- `b`: 盤面状態 (Vec<char>)
- `p`: 現在の冒険者位置
- `t`: ゴール位置（花の位置）
- `target`: 現在のターゲット位置
- `revealed`: 各セルが明らかになっているかのフラグ
- `turn`: 現在のターン数

#### 主要メソッド
- `new(input: &Input)`: 初期化
- `step(xy: &[(usize, usize)])`: 1ターンの処理
- `change_target(target: (usize, usize))`: ターゲット変更

## BoardSimulatorクラスの使用方法

### 完全実装されたBoardSimulator
`src/boardsimulator.py`は完全に実装され、tools/src/lib.rsのRust実装を忠実に再現しています。

```python
class BoardSimulator:
    def __init__(self, n: int, start_i: int, start_j: int, ti: int, tj: int):
        """
        Args:
            n: 盤面サイズ
            start_i, start_j: 冒険者の開始位置
            ti, tj: ゴール（花）の位置
        """

    def simulate(self, board: Board) -> int:
        """
        盤面をシミュレーションしてスコア（ターン数）を返す

        Returns:
            int: 冒険者がゴールに到達するまでのターン数（到達不可能な場合は0）
        """
```

### 主要な実装機能

#### 1. 冒険者の移動シミュレーション
- 4方向（上下左右）への視線による探索
- 障害物（'T', '#'）による視線の遮断
- 通行可能セル（'.', '*', 'S', 'X'）の識別

#### 2. 経路探索アルゴリズム
- BFSによる最短距離計算
- 既知のセルのみを使った動的経路計算
- ターゲット変更時の距離再計算

#### 3. ターゲット選択ロジック
- ゴールが発見されたら即座にゴールをターゲット
- ランダムシャッフルされた探索順序
- 到達不可能ターゲットの自動スキップ

## Step0-6で構築された盤面の評価方法

### 1. 評価対象の盤面
Step0からStep6までの処理を完了した盤面：
- Step0: 初期設定
- Step1: 花の周りの木の配置
- Step2: 左右端の垂直パス作成
- Step3: 垂直パス間の接続パス作成
- Step4: START/GOALとパスの接続
- Step5: 既存パスからの分岐作成
- Step6: 空きセルの後処理

### 2. 評価手順

#### a) 基本的な使用方法
```python
from board import Board
from boardsimulator import BoardSimulator

# Step0-6で構築された盤面を評価
def evaluate_constructed_board(constructed_board, start_i, start_j, goal_i, goal_j):
    # BoardSimulatorを初期化
    simulator = BoardSimulator(
        n=constructed_board.n,
        start_i=start_i,
        start_j=start_j,
        ti=goal_i,
        tj=goal_j
    )

    # シミュレーション実行
    score = simulator.simulate(constructed_board)

    if score > 0:
        print(f"Success! Score: {score} turns")
        return score
    else:
        print("Failed: Unreachable goal")
        return 0
```

#### b) 実際の使用例
```python
# Step6完了後の盤面を評価
from step1constructor import Step1Constructor
from step2constructor import Step2Constructor
# ... 他のステップのインポート

# 盤面構築
board = Board(20, 0, 10, 16, 8, initial_board_data)
step1 = Step1Constructor()
board = step1.construct(board, pattern_idx=0)
# ... 各ステップの実行

# スコア評価
score = evaluate_constructed_board(board, 0, 10, 16, 8)
print(f"Constructed board score: {score}")
```

#### c) テスト結果の例
実際のテスト結果：
- **シンプルな直線パス**: 4ターン
- **パス付き盤面**: 4ターン
- **Step6風の単純構造**: 4ターン
- **複雑なStep6盤面**: 194ターン（ゲームオーバー）

### 3. 期待されるスコア特性

#### 良い盤面の特徴
- STARTからGOALまでの直接的なパス
- 冒険者が迷わない明確な経路
- 不要な分岐が少ない構造

#### スコアに影響する要因
- パスの長さ（短いほど良い）
- 分岐の複雑さ（シンプルほど良い）
- 障害物による迂回の必要性

## 実装上の注意点

### 1. 座標系の統一
- Board クラス: (i, j) = (行, 列)
- tools/src/lib.rs: 同様に(i, j)使用
- 1次元変換: `index = i * N + j`

### 2. セル状態の対応
```python
# constants.pyの定義
EMPTY = 0      # '.'
TREE = 1       # 'T'
PATH = 2       # '*'
PATH_2 = 3     # 未使用
NEW_TREE = 4   # '#' (新しく配置した木)
START = 5      # 'S'
GOAL = 6       # 'X' (ゴール位置、実際は花)
```

### 3. エラーハンドリング
- 到達不可能な盤面の検出
- 無限ループの防止
- デバッグ用の中間状態出力

## 次のステップ

1. **BoardSimulator.simulate()の完全実装**
   - Rustの実装を参考にPythonで移植
   - 視線処理、経路探索、移動ロジックの実装

2. **テストとデバッグ**
   - 既知のテストケースでの検証
   - スコア計算の正確性確認

3. **最適化**
   - 計算効率の改善
   - メモ化による高速化

これらの実装により、Step0-6で構築した盤面の品質を定量的に評価し、アルゴリズムの改善点を特定することができます。