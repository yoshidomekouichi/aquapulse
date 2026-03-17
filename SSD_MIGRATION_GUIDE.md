# Raspberry Pi SSD起動への移行ガイド

作成日: 2026-03-17

## 現在の状況

### 問題
- SDカード (`/dev/mmcblk0p2`) に不良セクタがある
- ルートファイルシステムが 2.3GB で100%使用中、拡張できない
- エラー: `I/O error, dev mmcblk0, sector 6045800`
- Grafana + デスクトップ環境をインストールする容量がない

### 現在の構成
```
デバイス          サイズ   マウント先        用途
/dev/mmcblk0p1    512M    /boot/firmware    ブートローダー
/dev/mmcblk0p2    2.3G    /                 ルート（問題あり）
/dev/sda1         465G    /mnt/ssd          データ用SSD
```

### 目標
- ルートファイルシステムを SSD に移行
- SDカードはブートローダー専用にする

---

## 移行手順

### Step 1: バックアップ
```bash
# cmdline.txt のバックアップ（重要！）
sudo cp /boot/firmware/cmdline.txt /boot/firmware/cmdline.txt.backup
sudo cp /boot/firmware/cmdline.txt /mnt/ssd/cmdline.txt.backup

# 現在の設定を確認
cat /boot/firmware/cmdline.txt
```

現在の cmdline.txt:
```
console=serial0,115200 console=tty1 root=PARTUUID=184e3e8b-02 rootfstype=ext4 fsck.repair=yes fsck.mode=force rootwait cfg80211.ieee80211_regdom=JP
```

### Step 2: SSD の PARTUUID を確認
```bash
sudo blkid /dev/sda1
```
出力例: `/dev/sda1: UUID="8be67772-748b-4f37-ab28-1163af600b8e" ...`

**この UUID をメモしておく！**

### Step 3: ルートファイルシステムを SSD にコピー
```bash
# 除外リストを作成
cat << 'EOF' | sudo tee /tmp/rsync-exclude.txt
/boot/firmware/*
/dev/*
/proc/*
/sys/*
/tmp/*
/run/*
/mnt/*
/media/*
/lost+found
EOF

# rsync でコピー（約5-10分）
sudo rsync -axv --exclude-from=/tmp/rsync-exclude.txt / /mnt/ssd/
```

### Step 4: SSD の fstab を編集
```bash
# SSD 側の fstab を編集
sudo nano /mnt/ssd/etc/fstab
```

変更前:
```
PARTUUID=184e3e8b-02  /  ext4  defaults,noatime  0  1
```

変更後（SSD の UUID を使用）:
```
UUID=8be67772-748b-4f37-ab28-1163af600b8e  /  ext4  defaults,noatime  0  1
```

### Step 5: cmdline.txt を編集
```bash
sudo nano /boot/firmware/cmdline.txt
```

変更前:
```
... root=PARTUUID=184e3e8b-02 ...
```

変更後（SSD の UUID を使用）:
```
... root=UUID=8be67772-748b-4f37-ab28-1163af600b8e ...
```

また、`fsck.mode=force` を削除:
```
console=serial0,115200 console=tty1 root=UUID=8be67772-748b-4f37-ab28-1163af600b8e rootfstype=ext4 fsck.repair=yes rootwait cfg80211.ieee80211_regdom=JP
```

### Step 6: リブート
```bash
sudo reboot
```

### Step 7: 確認
```bash
# ルートが SSD になっているか確認
df -h /
# /dev/sda1 が / にマウントされていれば成功

# 旧データディレクトリの確認（移行後は /mnt/ssd は空になる）
ls /mnt/ssd
```

---

## 復旧方法（起動しない場合）

### 方法A: PCでSDカードを編集
1. SDカードをPCに差す
2. `bootfs` パーティションの `cmdline.txt` を開く
3. `root=` を元に戻す:
   ```
   root=PARTUUID=184e3e8b-02
   ```
4. SDカードをPiに戻して起動

### 方法B: バックアップファイルを使う
SDカード内のバックアップ:
- `/boot/firmware/cmdline.txt.backup`

SSD内のバックアップ:
- `/mnt/ssd/cmdline.txt.backup`

---

## 重要な情報

### ネットワーク設定
- IPアドレスは変わらない（同じ設定がコピーされる）
- ホスト名: `raspberrypi`

### データの場所
移行前:
- プロジェクト: `/mnt/ssd/projects/aquapulse`
- データベース: `/mnt/ssd/influxdb`

移行後:
- プロジェクト: `/projects/aquapulse` （SSDがルートになるため）
- または `/mnt/ssd` のマウントポイントは無くなる

**注意**: 移行後は SSD がルートになるので、パスが変わる可能性がある。
シンボリックリンクで対応可能:
```bash
sudo ln -s /projects /mnt/ssd/projects
```

### SSH 接続
- ユーザー: `koichi`
- ホスト: `raspberrypi` または IPアドレス

### サービス
- InfluxDB: `/mnt/ssd/influxdb`
- Grafana: インストール予定

---

## トラブルシューティング

### 症状: 起動しない（画面真っ黒）
→ cmdline.txt の `root=` が間違っている。復旧方法Aを実行。

### 症状: 起動するが `/mnt/ssd` が空
→ 正常。SSD がルートになったため。旧 `/mnt/ssd/*` は `/` 直下にある。

### 症状: rsync がエラーで止まる
→ SDカードの不良セクタが原因の可能性。`--ignore-errors` オプションを追加:
```bash
sudo rsync -axv --ignore-errors --exclude-from=/tmp/rsync-exclude.txt / /mnt/ssd/
```

### 症状: Permission denied エラー
→ `sudo` を忘れている。全コマンドで `sudo` を使う。

---

## 参考コマンド

```bash
# ディスク情報
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT,UUID

# パーティション UUID
sudo blkid

# マウント状態
mount | grep -E "sda|mmcblk"

# カーネルログ
dmesg | tail -50

# 起動ログ
journalctl -b | grep -i error
```

---

## このガイドの使い方

1. 別のチャット（Claude/ChatGPT等）でこのファイルの内容を共有
2. 「Raspberry Pi の SSD 移行で問題が発生しました。以下のガイドを参照してください」と伝える
3. 現在の状況（エラーメッセージ等）を伝える
