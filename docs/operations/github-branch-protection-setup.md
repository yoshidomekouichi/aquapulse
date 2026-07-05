# GitHub ブランチ保護設定手順

**対象ブランチ**: `main`  
**目的**: mainへの直接push防止、PR必須化  
**実施タイミング**: Phase 1完了後（PR #35マージ後）

---

## 📋 設定手順

### 1. GitHubリポジトリ設定にアクセス

```
https://github.com/yoshidomekouichi/aquapulse/settings/branches
```

または：

```
Repository → Settings → Branches → Add branch protection rule
```

### 2. ブランチ名パターンを入力

```
Branch name pattern: main
```

### 3. 保護ルールを設定

以下の項目にチェックを入れます：

#### ✅ Require a pull request before merging

**必須設定**：
- [x] Require a pull request before merging

**サブ設定**：
- [x] **Required approvals: 1**
  - 最低1人の承認が必要
- [ ] Dismiss stale PR approvals when new commits are pushed
  - 個人開発のため不要
- [ ] Require review from Code Owners
  - CODEOWNERSファイル未作成のため現時点では不要
- [ ] Require approval of the most recent reviewable push
  - 個人開発のため不要
- [ ] Require conversation resolution before merging
  - 個人開発のため不要（将来検討）

#### ✅ Require status checks to pass before merging

**Phase 1では設定しない**（CI未整備のため）

**Phase 2で設定**：
- [x] Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- Status checks（以下を追加）:
  - `lint`
  - `test`

#### ✅ Require conversation resolution before merging

- [ ] **Phase 1では不要**
- 将来的に複数人でレビューする場合に検討

#### ✅ Require signed commits

- [ ] **Phase 1では不要**
- セキュリティ強化時に検討

#### ✅ Require linear history

- [ ] **Phase 1では不要**
- Squash mergeを使うため不要

#### ✅ Do not allow bypassing the above settings

**重要**：
- [x] **Do not allow bypassing the above settings**

**例外設定**（Bypass actors）：
- **Repository administrators**: ✅ 許可
  - 緊急時のみ使用
  - 使用後は必ずretrospective実施

#### ✅ Restrict who can push to matching branches

- [ ] **Phase 1では不要**
- PR経由なので誰も直接pushできないため不要

#### ✅ Allow force pushes

- [ ] **絶対に許可しない**
- 履歴の改ざん防止

#### ✅ Allow deletions

- [ ] **絶対に許可しない**
- mainブランチの誤削除防止

---

## ✅ 最終チェックリスト

設定完了後、以下を確認：

- [ ] Require a pull request before merging: ✅
- [ ] Required approvals: 1
- [ ] Do not allow bypassing: ✅（Repository admins除く）
- [ ] Block force pushes: ✅
- [ ] Do not allow deletions: ✅
- [ ] Status checks: ⚠️ Phase 2で追加予定

---

## 🧪 動作確認

設定後、以下のテストを実施：

### テスト1: 直接pushの禁止確認

```bash
# mainブランチに切り替え
git checkout main

# テストファイル作成
echo "test" > test.txt
git add test.txt
git commit -m "test: direct push test"

# Push試行（失敗するはず）
git push origin main
```

**期待結果**：
```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: Changes must be made through a pull request.
```

### テスト2: PR経由のマージ確認

```bash
# Featureブランチ作成
git checkout -b cursor/test-branch-protection-cabf

# テストファイル作成
echo "test via PR" > test-pr.txt
git add test-pr.txt
git commit -m "test: PR経由テスト"

# Push
git push -u origin cursor/test-branch-protection-cabf

# PR作成
gh pr create --title "test: ブランチ保護テスト" --body "動作確認用"

# マージ試行（承認後にのみ成功するはず）
```

**期待結果**：
- 承認なしではマージボタンが無効
- 1人の承認後にマージ可能
- マージ後にfeatureブランチ削除可能

---

## 📊 設定完了後の状態

```
main ブランチ
  ├─ ✅ 直接push禁止
  ├─ ✅ PR必須
  ├─ ✅ 承認1人必須
  ├─ ✅ Force push禁止
  ├─ ✅ ブランチ削除禁止
  └─ ⚠️ CI必須（Phase 2で追加）
```

---

## 🔄 Phase 2での追加設定

CI/CD整備後（1週間以内）、以下を追加：

```bash
# .github/workflows/ci.yml作成後

# GitHub Settings → Branches → main → Edit
# ↓
# Require status checks to pass before merging: ✅
#   - lint
#   - test
# Require branches to be up to date: ✅
```

---

## 📚 参考資料

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Git Workflow Proposal](git-workflow-proposal.md)
- [Incident Report](incident-2026-07-05-direct-push.md)

---

## 🚨 トラブルシューティング

### Q: 管理者なのにpushできない

**A**: `Do not allow bypassing`を有効にしている場合、管理者でもPR経由が必須です。これは意図的な設定です。

緊急時のみ、GitHub UIから一時的にルールを無効化 → push → ルール再有効化。

### Q: PRがマージできない（Status checksが表示されない）

**A**: Phase 1ではCI未整備のため、Status checksは設定していません。Phase 2で追加予定。

### Q: 承認者が自分しかいない

**A**: 個人プロジェクトでは問題ありません。自己承認（self-review）で進めます。

---

**設定実施日**: ＿＿＿＿年＿＿月＿＿日  
**実施者**: @yoshidomekouichi  
**確認者**: ＿＿＿＿＿＿＿＿＿＿＿＿
