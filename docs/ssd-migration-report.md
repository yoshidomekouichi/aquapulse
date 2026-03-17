# Raspberry Pi SSD起動移行レポート

作成日: 2026-03-17

## 概要

Raspberry PiのルートファイルシステムをSDカードからSSDに移行した際に発生した問題と、その解決方法についての包括的なドキュメント。

---

## 1. 背景・コンテキスト

### 移行前の状況
| 項目 | 状態 |
|------|------|
| SDカード (`/dev/mmcblk0p2`) | 2.3GB、100%使用、不良セクタあり |
| SSD (`/dev/sda1`) | 465GB、データ用として `/mnt/ssd` にマウント |
| 問題 | 容量不足でGrafana等をインストールできない |

### 移行後の構成
| デバイス | サイズ | マウント先 | 用途 |
|----------|--------|------------|------|
| `/dev/mmcblk0p1` | 512M | `/boot/firmware` | ブートローダー専用 |
| `/dev/sda1` | 458G | `/` | ルートファイルシステム |

### 重要なパスの変更
| 移行前 | 移行後 |
|--------|--------|
| `/mnt/ssd/projects/aquapulse` | `/projects/aquapulse` |
| `/mnt/ssd/vscode-server` | `/vscode-server` |
| `/mnt/ssd/cursor-server` | `/cursor-server` |
| `/mnt/ssd/influxdb` | `/influxdb` |

---

## 2. 発生した問題

### 問題1: Remote SSH接続の失敗

**症状:**
- CursorのRemote SSH拡張機能で接続できない
- 「Workspace does not exist」エラー
- ターミナルからの通常SSHは成功する

**原因:**
シンボリックリンクが存在しない旧パスを指していた

```
~/.vscode-server -> /mnt/ssd/vscode-server  (存在しない)
~/.cursor-server -> /mnt/ssd/cursor-server  (存在しない)
```

**エラーログ:**
```
Creating the server install dir failed...
exitCode==34==
```

### 問題2: Dockerコンテナが起動していない

**症状:**
- Grafanaにアクセスできない
- データ収集が停止している

**原因:**
- Docker Composeが自動起動になっていなかった
- 再起動後に手動で `docker compose up -d` が必要だった

### 問題3: ワークスペースが見つからない

**症状:**
- 「Workspace does not exist」ダイアログが表示される

**原因:**
- 以前開いていたパス `/mnt/ssd/projects/aquapulse` が存在しない
- 新しいパス `/projects/aquapulse` を開く必要がある

---

## 3. 解決手順

### 3.1 シンボリックリンクの修正

```bash
# vscode-serverの修正
rm ~/.vscode-server
ln -s /vscode-server ~/.vscode-server

# cursor-serverの修正
rm ~/.cursor-server
ln -s /cursor-server ~/.cursor-server

# 確認
ls -la ~/.vscode-server ~/.cursor-server
```

### 3.2 Docker Composeの起動

```bash
cd /projects/aquapulse
docker compose up -d

# 確認
docker ps
```

### 3.3 ワークスペースの再設定

1. Remote SSH接続後、「Open Workspace...」をクリック
2. 新しいパス `/projects/aquapulse` を入力
3. または `File > Open Folder` で開く

---

## 4. トラブルシューティング

### SSH接続自体ができない場合

```bash
# Mac側で実行
# 1. known_hostsをクリア
ssh-keygen -R raspberrypi.local

# 2. SSH詳細デバッグ
ssh -vvv koichi@raspberrypi.local

# 3. 接続確認
ssh koichi@raspberrypi.local "echo OK"
```

### Remote SSHが失敗する場合

```bash
# Raspberry Pi側で確認
# 1. シンボリックリンクの確認
ls -la ~/.vscode-server ~/.cursor-server

# 2. リンク先の確認
ls -la /vscode-server /cursor-server

# 3. 権限の確認
touch /vscode-server/test && rm /vscode-server/test
touch /cursor-server/test && rm /cursor-server/test
```

**Cursorログの場所 (Mac):**
```
~/Library/Application Support/Cursor/logs/[最新日付]/window*/exthost/output_logging_*/1-Remote - SSH.log
```

### Dockerコンテナが動かない場合

```bash
# 状態確認
docker ps -a
docker compose logs

# 再起動
cd /projects/aquapulse
docker compose down
docker compose up -d

# Dockerサービス自体の確認
sudo systemctl status docker
```

### 起動しない（画面真っ黒）場合

1. SDカードをPCに接続
2. `bootfs` パーティションの `cmdline.txt` を編集
3. `root=` を元のSDカードに戻す:
   ```
   root=PARTUUID=184e3e8b-02
   ```
4. SDカードをPiに戻して起動

---

## 5. 確認コマンド集

### システム状態

```bash
# ルートファイルシステムの確認
df -h /

# マウント状態
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT

# ブート設定
cat /boot/firmware/cmdline.txt

# fstab
cat /etc/fstab
```

### サービス状態

```bash
# Docker
docker ps
docker compose ps

# 各サービス
curl -s -o /dev/null -w %{http_code} http://localhost:3000  # Grafana
curl -s -o /dev/null -w %{http_code} http://localhost:5432  # PostgreSQL
```

### ネットワーク

```bash
# IPアドレス
ip addr show

# ホスト名
hostname
```

---

## 6. 予防策・今後の対応

### 自動起動の設定

```bash
# Dockerサービスの自動起動を確認
sudo systemctl enable docker

# 確認
sudo systemctl is-enabled docker
```

### バックアップの作成

```bash
# cmdline.txtのバックアップ
sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.backup

# シンボリックリンク設定のメモ
ls -la ~/.vscode-server ~/.cursor-server > ~/symlink-backup.txt
```

### 移行前チェックリスト

SSD移行を行う前に確認すべき項目:

- [ ] シンボリックリンクの一覧を取得 (`find ~ -type l -ls`)
- [ ] `/mnt/ssd` を参照しているパスをすべて特定
- [ ] cmdline.txt のバックアップ
- [ ] fstab のバックアップ
- [ ] Docker Compose設定の確認

---

## 7. 関連情報

### 重要なファイル

| ファイル | 用途 |
|----------|------|
| `/boot/firmware/cmdline.txt` | カーネルブートパラメータ |
| `/etc/fstab` | マウント設定 |
| `/projects/aquapulse/docker-compose.yml` | サービス定義 |
| `/projects/aquapulse/.env` | 環境変数 |

### UUID vs PARTUUID

| 項目 | UUID | PARTUUID |
|------|------|----------|
| 定義 | ファイルシステムID | パーティションID |
| initramfsなし | 動作しない | 動作する |
| initramfsあり | 動作する | 動作しない場合あり |

Raspberry Pi OSはデフォルトでinitramfsを使わないため、`root=PARTUUID=` を使用すること。

### 現在の設定

```
cmdline.txt:
console=serial0,115200 console=tty1 root=PARTUUID=d6d1931d-725e-e14f-a8e7-71b296e33281 rootfstype=ext4 fsck.repair=yes rootwait cfg80211.ieee80211_regdom=JP
```

---

## 8. 連絡先・参考

- プロジェクト: `/projects/aquapulse`
- ホスト名: `raspberrypi` / `raspberrypi.local`
- ユーザー: `koichi`
- Grafana: http://raspberrypi.local:3000

---

*このドキュメントは2026年3月17日のSSD移行作業に基づいて作成されました。*
