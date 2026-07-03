# 🌊 AquaPulse クラウド移行ガイド

**ラズパイ → ESP32 + GCP への完全移行手順**

---

## 📋 **このドキュメント群について**

### **目的**

ラズパイの**IPアドレス問題**と**物理アクセス問題**を解決するため、ESP32 + GCP構成に移行する。

### **移行後の構成**

```
【現在】
ラズパイ（水槽の裏、アクセス不可）
  - センサー読み取り
  - DB・Grafana
  - SSH接続（切れる）

【移行後】
ESP32（水槽の裏）
  - センサー読み取りのみ
  ↓ WiFi
GCP（クラウド）
  - BigQuery（データ保存）
  - Grafana Cloud（可視化）
  - 完全リモート管理
```

---

## 🎯 **メリット**

| 項目 | 現在（ラズパイ） | 移行後（ESP32+GCP） |
|------|----------------|-------------------|
| **物理アクセス** | 必要（SSH切れたら詰む） | 不要（完全クラウド） |
| **IPアドレス** | 固定必須 | 気にしなくてOK |
| **デバイスコスト** | ラズパイ: 1万円 | ESP32: 2千円 |
| **月額コスト** | 電気代: $2 | GCP無料枠: $0 |
| **スケーラビリティ** | 限界あり | ほぼ無限 |
| **Phase 3準備** | ローカルML | BigQuery+Databricks |

---

## 📚 **ドキュメント構成**

### **1. [00_OVERVIEW.md](00_OVERVIEW.md)** - 全体概要
- システム構成図
- 技術スタック
- コスト試算
- 移行スケジュール

### **2. [01_HARDWARE_SETUP.md](01_HARDWARE_SETUP.md)** - ハードウェア準備
- ESP32購入ガイド（Amazonリンク）
- 部品リスト
- 配線図
- センサー接続

### **3. [02_GCP_SETUP.md](02_GCP_SETUP.md)** - GCP環境構築
- プロジェクト作成
- 認証設定
- 必要なAPI有効化
- gcloud CLI セットアップ

### **4. [03_PHASE1_MANUAL.md](03_PHASE1_MANUAL.md)** - Phase 1: 手動デプロイ
- gcloud CLI での手動デプロイ
- 動作確認
- トラブルシューティング
- 学習ポイント

### **5. [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md)** - Phase 2: 自動化
- GitHub Actions設定
- Dev/Prod環境分離
- CI/CDパイプライン
- ロールバック方法

### **6. [05_TESTING.md](05_TESTING.md)** - テスト・検証
- ローカルテスト（Functions Framework）
- Dev環境テスト
- 本番デプロイ前チェックリスト
- パフォーマンステスト

### **7. [06_OPERATIONS.md](06_OPERATIONS.md)** - 運用ガイド
- 日常の運用フロー
- モニタリング
- アラート設定
- バックアップ・リストア

### **8. [07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md)** - トラブルシューティング
- よくある問題と解決策
- エラーメッセージ集
- デバッグ方法
- サポート連絡先

### **9. [APPENDIX.md](APPENDIX.md)** - 付録
- 用語集
- GCPサービス詳細解説
- 参考リンク
- FAQ

---

## 🚀 **クイックスタート（3ステップ）**

### **ステップ1: ハードウェア準備（1-2日）**
```bash
# ESP32購入 → 到着待ち → 配線
```
詳細: [01_HARDWARE_SETUP.md](01_HARDWARE_SETUP.md)

### **ステップ2: GCP環境構築（1日）**
```bash
# プロジェクト作成 → 認証 → 手動デプロイ
```
詳細: [02_GCP_SETUP.md](02_GCP_SETUP.md) + [03_PHASE1_MANUAL.md](03_PHASE1_MANUAL.md)

### **ステップ3: 自動化（1日）**
```bash
# GitHub Actions設定 → git push だけでデプロイ
```
詳細: [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md)

---

## 📊 **進捗チェックリスト**

### **Phase 0: 準備**
- [ ] このドキュメントを読む
- [ ] ESP32を購入
- [ ] GCPアカウント作成
- [ ] Grafana Cloudアカウント作成

### **Phase 1: 開発環境（手動）**
- [ ] ESP32セットアップ
- [ ] GCPプロジェクト作成
- [ ] 手動デプロイ成功
- [ ] Dev環境でテスト

### **Phase 2: 自動化**
- [ ] GitHub Actions設定
- [ ] Dev環境自動デプロイ
- [ ] Prod環境自動デプロイ
- [ ] 動作確認

### **Phase 3: 本番切り替え**
- [ ] ラズパイと並行稼働（1週間）
- [ ] データ比較・検証
- [ ] ラズパイ停止
- [ ] ESP32本番運用開始

---

## 🎓 **学習の進め方**

### **推奨順序**

```
1. 全体像を理解
   └ 00_OVERVIEW.md を読む
   
2. ハードウェア準備
   └ 01_HARDWARE_SETUP.md
   
3. GCP基礎
   └ 02_GCP_SETUP.md
   
4. 手を動かす（Phase 1）
   └ 03_PHASE1_MANUAL.md
   └ ここで仕組みを理解！
   
5. 自動化（Phase 2）
   └ 04_PHASE2_AUTOMATION.md
   
6. テスト
   └ 05_TESTING.md
   
7. 本番運用
   └ 06_OPERATIONS.md
```

### **時間配分の目安**

| Phase | 時間 | 内容 |
|-------|------|------|
| 準備 | 1-2日 | ESP32購入・到着待ち |
| Phase 1 | 1日 | 手動デプロイで学習 |
| Phase 2 | 1日 | GitHub Actions設定 |
| テスト | 2-3日 | 並行稼働・検証 |
| **合計** | **5-7日** | - |

---

## 💡 **重要なコンセプト**

### **1. Pub/Sub の役割**

```
ESP32 → Pub/Sub → Cloud Functions → BigQuery
        ↑ ここでバッファリング
        
メリット:
  - データ保証（7日間保持）
  - 自動リトライ
  - 高可用性（SLA 99.95%）
```

詳細: [00_OVERVIEW.md](00_OVERVIEW.md#pubsub)

### **2. Dev/Prod 分離**

```
開発: aquapulse-dev
  ↓ テスト成功
本番: aquapulse
```

詳細: [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md#devprod)

### **3. IaC (Infrastructure as Code)**

```
terraform/ でインフラ管理
  - バージョン管理
  - 環境複製
  - 変更履歴
```

詳細: [04_PHASE2_AUTOMATION.md](04_PHASE2_AUTOMATION.md#terraform)

---

## 🆘 **困ったら**

### **トラブルシューティング**
[07_TROUBLESHOOTING.md](07_TROUBLESHOOTING.md) を参照

### **用語が分からない**
[APPENDIX.md](APPENDIX.md#glossary) の用語集を参照

### **GCPサービスの詳細**
[APPENDIX.md](APPENDIX.md#gcp-services) を参照

---

## 🔗 **外部リンク**

- [GCP公式ドキュメント](https://cloud.google.com/docs)
- [ESP32公式](https://www.espressif.com/en/products/socs/esp32)
- [MicroPython](https://micropython.org/)
- [GitHub Actions](https://docs.github.com/actions)

---

## 📝 **変更履歴**

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-03 | 1.0.0 | 初版作成 |

---

**次のステップ:** [00_OVERVIEW.md](00_OVERVIEW.md) を読んで全体像を理解しよう！
