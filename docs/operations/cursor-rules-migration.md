# Cursor ルールファイル移行記録

## 概要

2026年7月5日、`.cursorrules`（レガシー形式）から`.cursor/rules/*.mdc`（推奨形式）への移行を実施。

## 背景

### 発見された問題

1. **親Cloud Agentは`.cursorrules`を読み込んでいた**
   - 検証コード: `CR-TEST-2026`が出力された
   - レガシー形式が機能していた

2. **サブエージェント（cursor-guide）は`.mdc`を読み込んでいた**
   - 検証コード: `MDC-TEST-2026`が出力された
   - 新形式が正しく機能していた

3. **`.mdc`ファイルに非標準フィールドが含まれていた**
   ```yaml
   metadata:           # ← 公式仕様にない
     environments: cloud  # ← 公式仕様にない
   ```

## 公式仕様（調査結果）

### `.cursorrules`（レガシー形式）
- ❌ **Agent Modeでは完全に無視される**（2026年現在）
- ✅ Chat Modeでのみサポート（後方互換性）
- 配置場所: プロジェクトルート

### `.cursor/rules/*.mdc`（推奨形式）
- ✅ Agent Modeで動作
- ✅ 条件付き適用が可能
- 配置場所: `.cursor/rules/`ディレクトリ

### 正しいフロントマター形式

公式で定義されているフィールドは**3つのみ**：

```yaml
---
description: ルールの説明（AIが判断に使用）
alwaysApply: true または false
globs: ["src/**/*.ts", "app/**/*.tsx"]
---
```

### 適用モード

| `alwaysApply` | `description` | `globs` | 動作 |
|---------------|---------------|---------|------|
| `true` | - | - | 常に適用 |
| `false` | なし | あり | globsマッチで自動適用 |
| `false` | あり | なし | AIが判断して適用 |
| `false` | なし | なし | `@`メンションで手動適用のみ |

## 実施した変更

### 1. `.mdc`ファイルのフロントマター修正

**変更前：**
```yaml
---
description: AquaPulseプロジェクトの開発ルールとスタンス
alwaysApply: true
metadata:
  environments: cloud
---
```

**変更後：**
```yaml
---
description: AquaPulseプロジェクトの開発ルールとスタンス（Cloud Agent用）
alwaysApply: true
---
```

**対象ファイル：**
- `.cursor/rules/aquapulse-rules.mdc`
- `.cursor/rules/test-verification.mdc`

### 2. レガシーファイルのバックアップ

```bash
mv .cursorrules .cursorrules.bak
```

## 検証方法

次回のCloud Agentセッションで以下を確認：

1. **検証コードの確認**
   - `[検証コード: MDC-TEST-2026]`が出力されるか
   - `CR-TEST-2026`（レガシー）が出力されないか

2. **ルールの適用確認**
   - 日本語で回答されるか
   - 絵文字を使わないか
   - プロジェクト固有のルール（ESP32+GCP推奨等）が適用されるか

## 今後のメンテナンス

### ルールファイルの管理

```
.cursor/rules/
├── aquapulse-rules.mdc       # プロジェクト共通ルール（常時適用）
├── test-verification.mdc     # 検証用（検証完了後に削除予定）
└── （将来追加可能）
    ├── backend.mdc           # バックエンド専用ルール
    ├── frontend.mdc          # フロントエンド専用ルール
    └── testing.mdc           # テスト専用ルール
```

### ルール追加時の注意点

1. **ファイル拡張子は`.mdc`**（`.md`は無視される）
2. **YAMLフロントマターは必須**
3. **公式定義の3フィールドのみ使用**（`description`, `alwaysApply`, `globs`）
4. **非標準フィールドは追加しない**

## 参考リンク

- [Cursor公式ドキュメント - Rules](https://cursor.com/help/customization/rules)
- 調査担当サブエージェント: `cbef8501-8512-4aba-9f94-ed7a03e07fd8`

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-07-05 | 初版作成、`.cursorrules`から`.mdc`形式へ移行 |
