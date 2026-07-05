# ADR-0003: ShellツールでのGit操作におけるworking_directory明示

## ステータス

承認済み（2026-07-05）

## コンテキスト

PR #40-42の作成中、`git branch --show-current` が正しいブランチを返さず、意図しないブランチで作業してしまう問題が発生しました。

具体的な問題:
- `git checkout -b cursor/add-adr-v3-0d1c` を実行
- しかし `git branch --show-current` が `main` や別のブランチ名を返す
- 結果、mainブランチに直接コミットしてしまう（禁止事項違反）

原因:
- Shellツールの `working_directory` パラメータを指定していなかった
- 前回のコマンドの状態に依存してしまった

## 検討した選択肢

### 1. 毎回 `cd /workspace &&` を使用

```bash
Shell(command="cd /workspace && git checkout -b ...")
```

- pros: 動作する、以前成功していた
- cons: 冗長、エラーが起きやすい（&&の連結）

### 2. working_directory パラメータを明示（採用）

```python
Shell(
  command="git checkout -b ...",
  working_directory="/workspace"
)
```

- pros: 明確、Shellツールの正しい使い方、状態依存を回避
- cons: 毎回パラメータ指定が必要

### 3. 何もしない

- cons: 問題が再発する

## 決定

**すべてのGit操作で `working_directory="/workspace"` を明示**

理由:
- Shellツールの状態依存を構造的に回避
- より明示的で理解しやすい
- ツールの正しい使用法

## 影響

### ポジティブ
- Git操作の誤りを構造的に防止
- コードレビューで確認しやすい
- 他のShellコマンドにも適用可能

### ネガティブ
- 毎回パラメータ指定が必要（冗長）
- コード量が若干増加

### リスク
- ルールを忘れた場合、問題が再発
- → 20-version-control.mdcでルール化

## 関連資料

- [20-version-control.mdc](../../.cursor/rules/20-version-control.mdc)（Git操作の必須パラメータ）
- PR #40-42（問題が発生したPR）
