# 🚨 緊急バックアップ - 今すぐメモしてください

**OS再インストール前に、以下の情報を必ず控えてください！**

---

## ✅ **控える必要がある情報チェックリスト**

### 1. データベース認証情報

現在のラズパイの `.env` ファイルから確認：

```bash
cat /projects/aquapulse/.env | grep POSTGRES
```

- [ ] `POSTGRES_USER`: _______________
- [ ] `POSTGRES_PASSWORD`: _______________
- [ ] `POSTGRES_DB`: _______________

### 2. Tapo 認証情報

```bash
cat /projects/aquapulse/.env | grep TAPO
```

- [ ] `TAPO_USERNAME`: _______________ （Tapoアプリのメールアドレス）
- [ ] `TAPO_PASSWORD`: _______________ （Tapoアプリのパスワード）
- [ ] `TAPO_HUB_IP`: _______________ （H100 ハブのIP）
- [ ] `TAPO_LIGHTING_IP`: _______________ （P300 マルチタップのIP）

### 3. 有効化しているデータソース

```bash
cat /projects/aquapulse/.env | grep SOURCES
```

- [ ] `SOURCES`: _______________

### 4. その他のオプション設定（あれば）

```bash
cat /projects/aquapulse/.env
```

- [ ] `TDS_SENSOR_ID`: _______________
- [ ] `GPIO_TEMP_INTERVAL`: _______________
- [ ] その他: _______________

---

## 💾 **データベースのバックアップ（推奨）**

時間があれば、データもバックアップしましょう：

```bash
# ラズパイ上で実行
cd /projects/aquapulse
docker compose exec db pg_dump -U postgres aquapulse > ~/aquapulse_backup_$(date +%Y%m%d).sql
```

バックアップファイルをMacにコピー：

```bash
# Mac上で実行（SSH接続できる場合）
scp pi@【ラズパイのIP】:~/aquapulse_backup_*.sql ~/Downloads/
```

---

## 📋 **Grafanaダッシュボードのバックアップ（推奨）**

Grafanaの設定も控えておくと安心です。

ブラウザで Grafana にアクセスして：

1. ダッシュボードを開く
2. 右上の「Share」→「Export」→「Save to file」
3. JSONファイルをダウンロード

---

## 🔗 **参考ドキュメント**

再セットアップ手順: [docs/operations/RECOVERY_SETUP.md](RECOVERY_SETUP.md)

---

## 📱 **このメモの保存場所**

- [ ] スマホのメモアプリ
- [ ] 紙にメモ
- [ ] 別のPC
- [ ] クラウドストレージ（Google Keep、Notionなど）

**重要**: GitHubには絶対にプッシュしないでください！
