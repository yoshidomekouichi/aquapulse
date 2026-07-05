# Git ワークフロー提案書

**作成日**: 2026年7月5日  
**対象**: AquaPulse プロジェクト  
**目的**: プロフェッショナルな開発フローの確立

---

## 📊 エグゼクティブサマリー

本提案は、業界のベストプラクティス調査に基づき、**GitHub Flow + ブランチ保護 + AI支援レビュー**を推奨します。

**推奨理由**：
- ✅ 品質とスピードのバランスが最適
- ✅ 個人プロジェクトでもスケール可能
- ✅ Cloud Agentの自律作業と相性が良い
- ✅ 業界標準で将来のチーム拡大に対応

---

## 🔍 調査結果サマリー

### 1. ブランチ戦略の比較（2026年業界標準）

| 戦略 | 適用領域 | ブランチ寿命 | 複雑度 | CI/CD適合性 |
|------|---------|------------|--------|-----------|
| **Git Flow** | バージョン管理製品（モバイルアプリ等） | 数週間 | 高 | 低 |
| **GitHub Flow** | SaaS/Web継続デリバリー | 1-3日 | 低 | 高 |
| **Trunk-Based** | 超高頻度デプロイ（Google/Netflix） | 数時間 | 最低 | 最高 |

**業界コンセンサス**：
> "Start with GitHub Flow when you are unsure because it is easy to explain and easy to enforce with branch protection."
> — Bytepane Git Workflow Best Practices 2026

### 2. コードレビュー（PR）の効果

**Google/Microsoftの研究結果**：
- PRベースの開発は**最も効果的な品質保証手法**（テスト・静的解析より効果的）
- レビュー済みコードは**20-30%少ない欠陥**で本番到達
- PRサイズ400行以下：75%の欠陥検出率
- PRサイズ1000行超：検出率が70%低下

**2026年のベストプラクティス**：
- AIレビュー（CodeRabbit等）を第一パス（15-30秒）
- 人間は高レベルレビューに集中（ビジネスロジック、アーキテクチャ、セキュリティ）

### 3. mainへの直接コミットのリスク

**リスク分類**：

| リスク | 影響 | 発生確率 |
|--------|------|---------|
| **品質ゲートのバイパス** | CI/テスト未実行で本番障害 | 高 |
| **トレーサビリティ喪失** | バグ追跡・監査困難 | 中 |
| **レビュー機会の喪失** | 自己レビューの欠如 | 高 |
| **悪習慣の定着** | チーム拡大時に問題化 | 中 |

**業界の見解**：
> "Direct commits to the main branch are a silent quality risk. Even one unchecked commit can introduce regressions or erode trust."
> — Minware 2026

### 4. 個人プロジェクトでのブランチ保護

**個人開発者向けの推奨設定**：

```yaml
ブランチ保護ルール（main）:
  ✅ Force push禁止（履歴保護）
  ✅ ブランチ削除禁止
  ✅ ステータスチェック必須（CI pass）
  ⚠️ PR必須（オプション：自己レビューの機会）
  ⚠️ 承認数：0または1（個人の場合）
  
バイパスアクター:
  - Repository Admin（緊急時のみ）
```

**2つの学派**：

| アプローチ | メリット | デメリット | 適用ケース |
|-----------|---------|-----------|-----------|
| **PR必須** | 自己レビュー機会、履歴の明確化 | 若干の手間 | 品質重視、学習目的 |
| **Direct Push + CI** | 最速イテレーション | レビュー機会なし | 超高速開発、成熟した開発者 |

**推奨**：個人プロジェクトでも**PR必須**を推奨（将来のチーム拡大を見据えて）

---

## 🎯 AquaPulse プロジェクトへの推奨事項

### 推奨戦略：**GitHub Flow + ブランチ保護**

**理由**：

1. **現状との整合性**
   - 既にPR #34が存在（GitHub Flow実績あり）
   - Cloud Agentがfeatureブランチ作成可能

2. **プロジェクト特性**
   - 個人プロジェクト（現在）
   - 将来のチーム拡大可能性あり
   - SaaS/クラウド移行計画中（継続デリバリー向き）

3. **Cloud Agentとの相性**
   - 自律的に作業完了まで実行
   - PRレビューは人間（ユーザー）が実施
   - ブランチ命名規則に準拠可能（`cursor/<name>-cabf`）

4. **学習価値**
   - プロフェッショナルな習慣の確立
   - ポートフォリオとしての価値向上

### ワークフロー詳細

```
1. タスク開始
   ↓
2. Feature branch作成（cursor/xxx-cabf）
   ↓
3. 実装・テスト・コミット
   ↓
4. Push to remote branch
   ↓
5. PR作成（draft: true）
   ↓
6. CI自動実行（lint, test, build）
   ↓
7. AI自動レビュー（オプション：CodeRabbit）
   ↓
8. 人間レビュー（ユーザー）
   ↓
9. 承認・マージ
   ↓
10. Featureブランチ削除
```

---

## 📋 実装計画

### Phase 1: ブランチ保護設定（即時実施）

**GitHub設定**：

```bash
# Settings → Branches → Branch protection rules
# Rule: main

✅ Require a pull request before merging
   - Required approvals: 1
   - Dismiss stale reviews: No（個人のため）
   - Require review from Code Owners: No（現時点では不要）

✅ Require status checks to pass before merging
   - Require branches to be up to date: Yes
   - Status checks: 未定義（Phase 2で追加予定）

✅ Require conversation resolution before merging: No

✅ Do not allow bypassing the above settings
   - バイパス許可: Repository Administrators（緊急時のみ）

✅ Restrict who can push to matching branches: No
   （PRベースなので不要）

✅ Require signed commits: No（現時点では不要）

✅ Require linear history: No

✅ Block force pushes: Yes ← 重要

✅ Allow deletions: No ← 重要
```

### Phase 2: CI/CD整備（ESP32移行と並行）

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install black isort ruff
      - run: black --check .
      - run: isort --check .
      - run: ruff check .
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r collector/requirements.txt
      - run: pytest tests/
  
  # 将来追加
  # - docker-build
  # - security-scan
```

**ステータスチェック追加**：
- ブランチ保護ルールに`lint`, `test`を追加
- これらがpassしないとマージ不可

### Phase 3: AI自動レビュー導入（オプション）

**候補ツール**：
- [CodeRabbit](https://coderabbit.ai/) - PRに自動コメント
- [Cursor BugBot](https://docs.cursor.com/) - Cursor統合
- [Greptile](https://greptile.com/) - コードベース理解型

**メリット**：
- 15-30秒で第一パスレビュー完了
- 構文エラー、スタイル違反、明らかなバグを自動検出
- 人間はビジネスロジックに集中

### Phase 4: PRテンプレート整備

```markdown
# .github/pull_request_template.md

## 変更内容

<!-- 何をしたか、なぜしたかを簡潔に -->

## 変更種別

- [ ] 新機能
- [ ] バグ修正
- [ ] リファクタリング
- [ ] ドキュメント
- [ ] インフラ

## テスト

- [ ] ローカルテスト済み
- [ ] CI通過確認

## チェックリスト

- [ ] コードは `.cursorrules` に準拠している
- [ ] コミットメッセージは Conventional Commits 形式
- [ ] 関連ドキュメントを更新した

## 関連Issue

<!-- #123 などでリンク -->
```

---

## 🛡️ 緊急時の対応プロトコル

**原則**：緊急時でもプロセスを守る

### 定義：「緊急」とは

- 本番システムの完全停止
- データ喪失の危機
- セキュリティ侵害

### 緊急時フロー

```bash
# 1. Feature branchで修正（省略しない）
git checkout -b cursor/hotfix-production-down-cabf

# 2. 最小限の修正を実施
# ...

# 3. コミット
git commit -m "fix(critical): resolve production outage"

# 4. Push
git push -u origin cursor/hotfix-production-down-cabf

# 5. PR作成（緊急であることを明記）
gh pr create --title "🚨 HOTFIX: Production down" \
  --body "Critical fix. Post-merge review required." \
  --label "hotfix" \
  --assignee @me

# 6. 管理者権限でCI待たずにマージ（最終手段）
# または
# 6. CI passを待ってマージ（可能な限りこちら）

# 7. 事後レビュー必須
# - 翌営業日にretrospective
# - 再発防止策の文書化
```

**重要**：緊急時の直接mainへのpushは**禁止**。必ずPRを経由。

---

## 📐 成功指標（KPI）

| 指標 | 目標値 | 測定方法 |
|------|--------|---------|
| **PR作成率** | 100% | 全変更がPR経由 |
| **平均PR寿命** | < 2日 | マージまでの時間 |
| **CI pass率** | > 95% | 初回pass率 |
| **緊急直接push** | 0回/月 | GitHub監査ログ |
| **PRサイズ** | < 400行 | GitHub Insights |

---

## 🔄 今回のインシデント対応

### 選択肢A：このまま受け入れる（推奨）

**理由**：
- 変更内容は適切（ルールファイル移行）
- 実害なし（mainは動作する）
- 学習機会として記録済み

**アクション**：
- このドキュメントで再発防止を確立
- 次回から正しいフローを徹底

### 選択肢B：取り消してPR経由でやり直す

**理由**：
- プロセスの重要性を示す
- 正しい履歴を残す

**リスク**：
- Force push必要（リスク高）
- 時間的コスト

**判断**：選択肢Aを推奨（実用主義）

---

## 📝 ルール整備案

### .cursor/rules/git-workflow.mdc

```markdown
---
description: Git ワークフローとブランチ戦略ルール
alwaysApply: true
---

# Git Workflow Rules

## ブランチ戦略

- **GitHub Flow** を採用
- `main` ブランチは常にデプロイ可能な状態を維持
- すべての変更は feature branch 経由で実施

## ブランチ命名規則（Cloud Agent）

```
cursor/<descriptive-name>-cabf
```

例：
- `cursor/esp32-sensor-integration-cabf`
- `cursor/fix-grafana-query-cabf`
- `cursor/update-docs-cabf`

## 作業フロー

1. **ブランチ作成**: `git checkout -b cursor/<name>-cabf`
2. **実装・コミット**: Conventional Commits形式
3. **Push**: `git push -u origin cursor/<name>-cabf`
4. **PR作成**: draft: true でまず作成
5. **CI確認**: すべてのチェックがpass
6. **レビュー依頼**: draftを解除
7. **マージ**: Squash merge推奨
8. **クリーンアップ**: ブランチ削除

## 禁止事項

- ❌ `main` への直接push
- ❌ Force push to `main`
- ❌ PRをスキップ
- ❌ CI失敗のままマージ

## PR作成時の必須事項

- [ ] タイトルは Conventional Commits 形式
- [ ] 変更内容の説明（なぜ、何を）
- [ ] テスト実施状況
- [ ] 関連ドキュメントの更新

## コミットメッセージ規約

Conventional Commits形式を使用：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `test`: テスト追加
- `chore`: ビルド・設定

**例**:
```
feat(collector): ESP32センサー読み取り機能を追加

DS18B20とMCP3424からのデータ取得を実装。
MQTTでPub/Subに送信する機能を含む。

Closes #123
```

## 緊急時の対応

緊急時でも必ずPRを経由。ただし以下を許可：

- CI待機のスキップ（管理者権限）
- 承認数の一時的な削減
- **事後レビュー必須**
```

### README.mdへの追記

```markdown
## 🔀 開発フロー

このプロジェクトは **GitHub Flow** を採用しています。

### 貢献方法

1. Feature branchを作成
   ```bash
   git checkout -b cursor/your-feature-cabf
   ```

2. 変更を実装・コミット
   ```bash
   git commit -m "feat: add new sensor support"
   ```

3. Pushしてプルリクエストを作成
   ```bash
   git push -u origin cursor/your-feature-cabf
   gh pr create
   ```

4. CIが通過し、レビューが承認されたらマージ

詳細: [docs/operations/git-workflow-proposal.md](docs/operations/git-workflow-proposal.md)
```

---

## 🎓 教育的価値

このワークフローは以下のスキルを向上させます：

1. **プロフェッショナルな習慣**
   - 業界標準のワークフロー体得
   - コードレビュー文化の理解

2. **品質意識**
   - 自己レビューの習慣化
   - CI/CDの重要性の体感

3. **コラボレーション準備**
   - チーム開発への即応力
   - オープンソース貢献の基礎

4. **ポートフォリオ価値**
   - 整った履歴
   - プロセス重視の姿勢

---

## 📚 参考資料

### 業界標準ガイド

- [Git Workflow Best Practices 2026](https://bytepane.com/blog/git-workflow-best-practices/)
- [GitHub Code Review Best Practices 2026](https://gitautoreview.com/blog/github-code-review-best-practices-2026)
- [Code Review Best Practices - DEV Community](https://dev.to/rahulxsingh/code-review-best-practices-the-complete-guide-for-engineering-teams-2026-52a4)

### 研究データ

- Google Engineering Practices: Code Review
- Microsoft Empirical Studies: 20-30% fewer defects with review
- SmartBear Analysis: 60-90% defect detection before production

### ツール

- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [CodeRabbit](https://coderabbit.ai/) - AI Code Review

---

## ✅ 承認後のアクション

### 即時実施（Phase 1）

- [ ] GitHubブランチ保護設定
- [ ] `.cursor/rules/git-workflow.mdc` 作成
- [ ] README.md 更新
- [ ] このドキュメントをコミット（**PRで！**）

### 短期実施（Phase 2 - 1週間以内）

- [ ] CI/CDワークフロー作成
- [ ] PRテンプレート作成
- [ ] ステータスチェック有効化

### 中期実施（Phase 3 - 1ヶ月以内）

- [ ] AI自動レビュー導入検討
- [ ] CODEOWNERSファイル作成（将来の協力者用）

---

## 🤝 承認プロセス

このドキュメントを読んで以下を判断してください：

1. **推奨戦略に同意しますか？**
   - [ ] はい（GitHub Flow + ブランチ保護）
   - [ ] 代替案を提案

2. **今回のインシデント対応**
   - [ ] 選択肢A（このまま受け入れる）
   - [ ] 選択肢B（取り消してやり直す）

3. **実装フェーズ**
   - [ ] Phase 1のみ即時実施
   - [ ] Phase 1-2を実施
   - [ ] 全Phase実施

承認後、このドキュメント自体を **PR経由で** コミットし、新しいワークフローの最初の実践とします。

---

**作成者**: Cloud Agent  
**レビュー待ち**: @yoshidomekouichi  
**関連Issue**: なし（ワークフロー確立）
