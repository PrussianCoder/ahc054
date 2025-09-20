# AHC054 Tester Utilities

This repository contains helper scripts and binaries for running the AtCoder Heuristic Contest 054 tester locally.

## 環境準備

1. **Python 仮想環境の用意**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install optuna optunahub ray
   ```

   > 💡 `optunahub` は社内パッケージのため、社内 PyPI へのアクセス権が必要です。アクセスできない場合は、プロキシ設定を確認してください。

2. **Rust toolchain (1.80.0)** をインストールし、`cargo` コマンドを利用できるようにします。

3. **テスターのビルド**

   `run_eval.sh` から利用される可視化バイナリ (`tools/target/release/vis`) はホスト環境でビルドされている必要があります。事前に以下を実行してください。

   ```bash
   source .venv/bin/activate
   python setup.py
   ```

   - スクリプトは毎回 `cargo clean` → `cargo build --release` を行うため、ビルド済みバイナリが別アーキテクチャ向けだった場合も自動的に置き換えられます。
   - ネットワーク制限がある環境では、Rustup や補助ツールのダウンロードが失敗することがあります。`https_proxy` などのプロキシ設定を確認し、再実行してください。

## テストコードの実行方法

テストランナー `eval.py` にはラッパースクリプト `run_eval.sh` が用意されています。仮想環境を有効化し、必要なバイナリをビルド済みであることを確認した上で次を実行します。

```bash
source .venv/bin/activate
./run_eval.sh [ターゲットスクリプト] [オプション]
```

- ターゲットスクリプトを省略した場合は既定の `main.py` が評価されます。
- 実行ログやスコアは `tools/out` 以下に出力されます。

### 代表的な利用例

| 用途 | コマンド例 |
| --- | --- |
| 既定の `main.py` を 1 ケースだけ試す | `./run_eval.sh -s 0 -v` |
| 独自実装 `my.py` を複数シードで評価 | `./run_eval.sh my.py -s 0 9` |
| 可視化なしで全ケース評価 | `./run_eval.sh my.py` |

> ℹ️ `-s` オプションは `[開始シード 終了シード]` の形式で指定します。単一シードの場合は `-s 0` のように開始値のみを渡します。

## トラブルシューティング

- `ModuleNotFoundError: No module named 'optunahub'`
  - 依存パッケージがインストールされていません。社内リポジトリにアクセスできるネットワークかを確認してください。
- `/bin/sh: tools/target/release/vis: Exec format error`
  - 可視化バイナリがホスト環境向けにビルドされていません。`python setup.py` を再実行してネイティブバイナリを生成してください。
- `cargo` が見つからない
  - Rust ツールチェインをインストールし、`PATH` に `~/.cargo/bin` を追加してください。
- `curl: (56) CONNECT tunnel failed`
  - プロキシ設定や社内 VPN の接続状態を確認し、必要に応じて環境変数 `https_proxy` を設定して再実行します。

## 参考コマンド

- スコアの算出結果を静的に閲覧する: `python -m http.server --directory tools/out 8000`
- Optuna のダッシュボード: `optuna-dashboard sqlite:///tools/out/optuna.db`

