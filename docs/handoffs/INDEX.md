# Agent Handoff Index

このディレクトリは、Cloud AgentとLocal Agent間の引き継ぎドキュメントを管理します。

## ディレクトリ構造

```
handoffs/
├── INDEX.md              # このファイル - 全引き継ぎの一覧
├── templates/            # 引き継ぎドキュメントのテンプレート
├── active/               # 🟢 進行中の引き継ぎ
├── completed/            # ✅ 完了した引き継ぎ（直近3ヶ月）
│   └── YYYY-MM/
└── archive/              # 📦 アーカイブ（3ヶ月以上前）
    └── YYYY-MM/
```

## 命名規則

```
{送信元}-to-{送信先}-{タスク概要}-{YYYYMMDD}.md

例:
- cloud-to-local-tapo-poller-20260803.md
- local-to-cloud-esp32-integration-20260804.md
```

## ライフサイクル

1. **作成時** → `active/` に配置
2. **タスク完了後** → `completed/YYYY-MM/` に移動
3. **3ヶ月経過後** → `archive/YYYY-MM/` に移動（または削除）

---

## Active Handoffs 🟢

| 作成日 | 送信元→送信先 | タスク概要 | 優先度 | ステータス | ファイル |
|--------|-------------|----------|--------|----------|---------|
| 2026-08-04 | Local→Cloud | Grafana完了→アラート+ESP32 | 🔴 High | 🟢 In Progress | [local-to-cloud-grafana-alert-esp32-20260804.md](active/local-to-cloud-grafana-alert-esp32-20260804.md) |

## Recently Completed ✅ (Last 3 months)

| 完了日 | 送信元→送信先 | タスク概要 | 成功/失敗 | 学び | ファイル |
|--------|-------------|----------|----------|------|---------|
| 2026-08-04 | Cloud→Local | Tapo Poller 実装 | ✅ 成功 | Aterm `-2s` 分離OFF、P300 TPAP はサードパーティ連携必須 | [cloud-to-local-tapo-poller-20260803.md](completed/2026-08/cloud-to-local-tapo-poller-20260803.md) |

## Archive 📦

- なし

---

## 使い方

### Cloud Agent（送信側）
ユーザーが「引き継ぎドキュメント作成」「次のエージェントに引き継ぐ」などと指示したら：

1. `templates/handoff-template.md` をベースに引き継ぎドキュメントを作成
2. `active/` ディレクトリに配置
3. この `INDEX.md` の「Active Handoffs」セクションに追加
4. コミット＆プッシュ

### Local Agent（受信側）
ユーザーが「引き継ぎドキュメント読み込み」「前のエージェントから引き継ぐ」などと指示したら：

1. この `INDEX.md` の「Active Handoffs」から該当ドキュメントを特定
2. ドキュメントを読み込み、タスクを実行
3. 完了後、ドキュメントを `completed/YYYY-MM/` に移動
4. `INDEX.md` を更新（Active → Completed）
5. 送信元エージェントに完了報告（必要に応じて）

### ユーザー
- 定期的に `completed/` を確認し、3ヶ月経過したものを `archive/` に移動
- 不要になった引き継ぎドキュメントは削除可能

---

## 関連ルール

詳細なプロトコルは `.cursor/rules/40-agent-handoff.mdc` を参照してください。
