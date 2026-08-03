# 【送信元Agent】引き継ぎ: 【タスク概要】

## 1. メタ情報

- **送信元**: Cloud Agent / Local Agent
- **送信先**: Cloud Agent / Local Agent
- **作成日時**: YYYY-MM-DD HH:MM
- **優先度**: 🔴 High / 🟡 Medium / 🟢 Low
- **期限**: YYYY-MM-DD（理由: お盆前の1週間不在など）
- **関連PR/Issue**: #番号

## 2. 前提知識・参照ドキュメント

受信側エージェントが最初に読むべき情報を明示：

- **必須のADR**: `docs/decisions/xxxx.md`
- **関連ガイド**: `docs/guides/xxxx.md`
- **参照コード**: `path/to/existing/code.py`
- **関連PR**: #番号

## 3. 現在の状況サマリー

- **達成済み**:
  - 項目1
  - 項目2
  
- **未着手**:
  - 項目1
  - 項目2
  
- **ブロッカー**:
  - 項目1（理由）

## 4. 技術スタック

- **言語/フレームワーク**: Python 3.11, MicroPython, etc.
- **主要ライブラリ**: `python-kasa`, `google-cloud-bigquery`, etc.
- **インフラ/サービス**: GCP (Cloud Functions, BigQuery), Grafana Cloud, etc.

## 5. 実装要件

### 5.1 必須要件
- [ ] 要件1
- [ ] 要件2

### 5.2 推奨要件
- [ ] 要件1
- [ ] 要件2

### 5.3 オプション要件
- [ ] 要件1
- [ ] 要件2

## 6. 環境情報

- **実行環境**: Mac / Linux / Cloud VM
- **必要な認証情報**:
  - GCP Service Account（取得方法: GCP Console > IAM > Service Accounts）
  - API Keys（取得方法: ...）
- **必要なツール**: `gcloud`, `bq`, `python3`, etc.
- **環境変数**:
  ```bash
  export GCP_PROJECT_ID="aquapulse-dev"
  export BIGQUERY_DATASET="aquarium_data"
  ```

## 7. 依存関係

- **事前に完了すべきタスク**:
  - PRマージ: #番号
  - GCPリソースのデプロイ
  
- **並行作業可能なタスク**:
  - タスク1
  
- **後続タスク**:
  - このタスク完了後に可能になること

## 8. 詳細タスクリスト

- [ ] **タスク1**: 説明
  - **成功基準**: 何ができたらOKか
  - **確認コマンド**: `command to verify`
  
- [ ] **タスク2**: 説明
  - **成功基準**: 何ができたらOKか
  - **確認コマンド**: `command to verify`

## 9. 成功基準

### 最低限の成功
これができれば最低限OK：
- [ ] 基準1
- [ ] 基準2

### 完全な成功
理想的な完了状態：
- [ ] 基準1
- [ ] 基準2

### 確認方法
具体的な検証コマンド/手順：
```bash
# 例: データが取得できているか確認
bq query --use_legacy_sql=false 'SELECT * FROM dataset.table LIMIT 10'
```

## 10. テスト・検証手順

### 単体テスト
```bash
# テストコマンド例
python -m pytest tests/
```

### 統合テスト
```bash
# 統合テストコマンド例
./scripts/integration_test.sh
```

### 本番想定テスト
```bash
# 本番環境でのテスト手順
```

## 11. トラブルシューティング・エラーハンドリング

### よくあるエラー

| エラー内容 | 原因 | 解決方法 |
|---------|------|---------|
| `Connection timeout` | ネットワーク接続の問題 | デバイスのIPアドレスを確認 |
| `Permission denied` | 認証情報の問題 | Service Accountの権限を確認 |

### デバッグ手順

1. **ログ確認**:
   ```bash
   tail -f /path/to/logfile
   ```

2. **接続確認**:
   ```bash
   ping 192.168.10.xxx
   ```

3. **権限確認**:
   ```bash
   gcloud auth list
   ```

## 12. ロールバック手順

### 緊急停止方法
```bash
# プロセス停止
pkill -f script_name.py

# Cloud Functionの無効化
gcloud functions delete function-name
```

### データ復旧
```bash
# バックアップからの復元手順
```

### 影響範囲
- ロールバックによる影響: ...

## 13. 制約事項・トレードオフ

- **技術的制約**:
  - 制約1（理由）
  
- **コスト制約**:
  - 制約1（理由）
  
- **時間制約**:
  - 制約1（理由）

## 14. セキュリティ・機密情報の扱い

- **使用する認証情報**:
  - GCP Service Account JSON Key
  - Tapo デバイスの認証情報
  
- **保存場所**:
  - Cursor Secrets（Cloud Agent用）
  - 環境変数（Local Agent用）
  
- **注意事項**:
  - ⚠️ Service Account JSONをコミットしない
  - ⚠️ `.env` ファイルを `.gitignore` に追加

## 15. 完了報告フォーマット

引き継ぎ完了時、以下を送信元エージェントに報告：

- [ ] **実装したファイル・変更内容**:
  - ファイル1: 変更内容
  - ファイル2: 変更内容
  
- [ ] **テスト結果**:
  - ✅ 単体テスト: 成功
  - ✅ 統合テスト: 成功
  
- [ ] **遭遇した問題と解決方法**:
  - 問題1: 解決方法
  
- [ ] **未解決の問題・次の課題**:
  - 課題1
  
- [ ] **作成したPR番号**: #番号

## 16. 次のアクション

- **報告先**: Cloud Agent / Local Agent / ユーザー
- **次の引き継ぎ先**: どこに戻すか（Cloud Agent / Local Agent）
- **後続タスク**: 次に誰が何をするか

---

## 補足メモ

その他、受信側エージェントに伝えたい情報があればここに記載。
