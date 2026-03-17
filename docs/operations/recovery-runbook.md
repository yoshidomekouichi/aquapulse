# AquaPulse 復旧手順（OS 再インストール後）

Raspberry Pi 5 の OS をクリーンインストールした後、AquaPulse を再稼働させるための手順まとめ。  
2026年3月の復旧で実際に成功した方法を記録。

---

## 前提条件

- **コード**: `aquapulse` プロジェクトは SSD (`/mnt/ssd/projects/aquapulse`) に存在
- **SSD**: `/mnt/ssd` にマウント済み（起動時に自動マウントされるよう設定済みであること）
- **Remote SSH**: PC から Raspberry Pi に SSH 接続して作業（Cursor の Remote SSH 等）

---

## 成功のポイント（なぜうまくいったか）

### 1. ディスク構成の理解

| 場所 | 用途 | 容量 |
|------|------|------|
| **MicroSD** | OS ルート (`/`) | 2.3G 程度（拡張失敗時） |
| **SSD** | プロジェクト・Docker/containerd データ | 十分な空き |

**重要**: Docker の「バイナリ」は apt で `/usr` にインストールされるため、ルートに最低 100〜150MB 必要。一方、**イメージ・コンテナ・containerd のデータ**は SSD に逃がせる。

### 2. 3箇所を SSD に寄せる

| コンポーネント | 設定ファイル | 設定内容 |
|----------------|--------------|----------|
| **Docker** | `/etc/docker/daemon.json` | `"data-root": "/mnt/ssd/docker_data"` |
| **containerd** | `/etc/containerd/config.toml` | `root = "/mnt/ssd/containerd_data"` |
| **apt キャッシュ** | コマンドオプション | `-o Dir::Cache::archives="/mnt/ssd/apt_cache"` |

**containerd が盲点**: イメージの pull は containerd が担当。Docker の data-root だけ変えても、pull 中は `/var/lib/containerd` を使うため、SD が満杯になる。必ず containerd の root も SSD に変更すること。

### 3. containerd の root がコメントアウトされていた

デフォルトの `config.toml` では `#root = "/var/lib/containerd"` のようにコメントアウトされている。  
`sed` で置換すると `#root = "/mnt/ssd/containerd_data"` になり、**依然としてコメント**のまま。  
2段階で修正が必要:

```bash
# 1. パスを変更
sudo sed -i 's|root = "/var/lib/containerd"|root = "/mnt/ssd/containerd_data"|' /etc/containerd/config.toml

# 2. コメントを外す（# を削除）
sudo sed -i 's|#root = "/mnt/ssd/containerd_data"|root = "/mnt/ssd/containerd_data"|' /etc/containerd/config.toml
```

### 4. 容量逼迫時の Docker インストール

ルートの空きが少ない場合:

- `sudo apt-get clean` / `sudo rm -rf /usr/share/man/*` で空き確保
- `-o Dir::Cache::archives="/mnt/ssd/apt_cache"` でダウンロード先を SSD に
- `--no-install-recommends` で docker-buildx, rootless-extras, git 等を省き、必要容量を削減

---

## 手順一覧

### Step 1: Docker 環境の確認とインストール

```bash
# 確認
docker --version
docker compose version

# 未インストールの場合
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
# Docker 公式リポジトリ追加（公式手順に従う）
# 容量が少ない場合は下記の「容量逼迫時のインストール」を参照
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

**容量逼迫時のインストール**:

```bash
sudo mkdir -p /mnt/ssd/apt_cache
sudo apt-get -o Dir::Cache::archives="/mnt/ssd/apt_cache" install -y --no-install-recommends \
  docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Step 2: Docker / containerd を SSD に設定

```bash
# Docker
sudo mkdir -p /mnt/ssd/docker_data
echo '{"data-root": "/mnt/ssd/docker_data"}' | sudo tee /etc/docker/daemon.json

# containerd（イメージ pull の実体）
sudo mkdir -p /mnt/ssd/containerd_data
sudo mkdir -p /etc/containerd
[ ! -f /etc/containerd/config.toml ] && containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's|root = "/var/lib/containerd"|root = "/mnt/ssd/containerd_data"|' /etc/containerd/config.toml
sudo sed -i 's|#root = "/mnt/ssd/containerd_data"|root = "/mnt/ssd/containerd_data"|' /etc/containerd/config.toml

# 再起動
sudo systemctl stop docker
sudo systemctl restart containerd
sudo systemctl start docker
```

### Step 3: docker グループと権限

```bash
sudo usermod -aG docker $USER
newgrp docker   # またはログアウトして再ログイン
```

### Step 4: .env の確認

```bash
cd /mnt/ssd/projects/aquapulse
ls -la .env
# 必要な変数: POSTGRES_*, TAPO_*, SOURCES
```

### Step 5: コンテナ起動

```bash
cd /mnt/ssd/projects/aquapulse
docker compose up -d --build
docker ps
docker compose logs collector --tail 50
```

---

## Remote SSH について

- Cursor の Remote SSH で Raspberry Pi に接続し、ターミナル操作とファイル編集を行う
- ラズパイの IP が固定（または DHCP 予約）されていると接続しやすい
- `~/.ssh/config` で Host を設定しておくと便利
- **パスワードレス認証の推奨**: Mac 側で SSH 公開鍵を作成し、ラズパイの `~/.ssh/authorized_keys` に登録しておくと接続がスムーズ

---

## ネットワーク障害時の復旧（Wi-Fi ロスト等）

Wi-Fi 接続がロストし、SSH・ネットワーク経由のアクセスが一切できない場合の手順（2026-03-03 の実績に基づく）。

### Step 1: 有線 LAN への切り替え

1. 有線 LAN ケーブルを調達し、ラズパイとルーターを直接接続
2. OS を再起動（電源オフ→オン、または `sudo reboot` が可能な場合）
3. 有線 LAN 経由で DHCP により新しい IP が割り当てられる

### Step 2: 新しい IP の特定（PC から）

```bash
# ローカルネットワークをスキャン（例: 192.168.3.0/24）
nmap -sn 192.168.3.0/24
```

スキャン結果から Raspberry Pi の新しい IP を特定する（有線接続時は Wi-Fi 時と異なる IP になることがある）。

### Step 3: SSH 接続とシステム確認

```bash
ssh koichi@<特定したIP>
docker ps
docker compose logs collector --tail 20
```

主要コンテナ（collector, timescaledb, grafana, mosquitto 等）が正常に稼働していることを確認。

### Step 4: 今後の対策

- **IP 固定化**: 有線 IP をルーターで DHCP 予約するか、ラズパイ側で静的 IP を設定し、接続先のブレを防ぐ
- **Remote-SSH の事前設定**: 障害前に SSH 公開鍵認証と `~/.ssh/config` を設定しておくと、復旧後の作業が効率化される

---

## システム情報（SSH 追い出し時の復旧用）

raspi-config の再設定や SSH 設定変更で接続できなくなった場合、**モニター＋キーボード**で直接ログインして復旧する。以下は復旧時に参照する情報（記録日: 2026-03-02）。

### ネットワーク

| 項目 | 値 |
|------|-----|
| ホスト名 | `raspberrypi` |
| プライマリ IP (有線 LAN) | `192.168.3.17`（2026-03-03 時点、Wi-Fi 障害後の有線接続） |
| 旧 IP (Wi-Fi) | `192.168.3.14`（Wi-Fi 接続時） |
| デフォルトゲートウェイ | `192.168.3.1` |
| DNS | `192.168.3.1` |
| 有効インターフェース | `eth0`（有線）、`wlan0`（Wi-Fi 障害により未使用） |

### ユーザー・認証

| 項目 | 値 |
|------|-----|
| ユーザー名 | `koichi` |
| UID/GID | 1000 |
| 所属グループ | sudo, docker, adm, netdev 等 |
| ホーム | `/home/koichi` |
| シェル | `/bin/bash` |

### SSH 設定

| 項目 | 値 |
|------|-----|
| サービス | `ssh` (enabled) |
| パスワード認証 | 有効 (`/etc/ssh/sshd_config.d/50-cloud-init.conf`) |
| デフォルトポート | 22 |

**SSH を再有効化する場合**（raspi-config で無効にした後）:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
# または raspi-config → Interface Options → SSH → Enable
```

### ディスク・マウント

| デバイス | サイズ | マウント先 | UUID |
|----------|--------|------------|------|
| mmcblk0p1 | 512M | /boot/firmware | EACA-13DA (vfat) |
| mmcblk0p2 | 59G | / (ルート) | 21724cc6-e5a3-48a1-8643-7917dba3a9fb |
| sda1 | 465.8G | /mnt/ssd | 8be67772-748b-4f37-ab28-1163af600b8e |

**fstab の SSD 行**（起動時に自動マウント）:

```
UUID=8be67772-748b-4f37-ab28-1163af600b8e /mnt/ssd ext4 defaults 0 2
```

### OS

- Debian GNU/Linux 13 (trixie)
- Raspberry Pi 5 向けイメージ

### 接続確認コマンド（PC から）

```bash
# 疎通確認（有線接続時）
ping 192.168.3.17

# SSH 接続（パスワード認証 or 公開鍵認証）
ssh koichi@192.168.3.17

# ~/.ssh/config の例
# Host aquapulse
#   HostName 192.168.3.17
#   User koichi
```

### IP が変わった場合の確認（ラズパイで実行）

```bash
hostname -I
ip route show default
```

---

## トラブルシューティング

| 現象 | 原因 | 対処 |
|------|------|------|
| Wi-Fi 接続ロスト、SSH 不可 | Wi-Fi ドライバ・設定不具合 | 有線 LAN に切り替え、上記「ネットワーク障害時の復旧」参照 |
| SSH 接続できない | raspi-config で SSH 無効化、ファイアウォール | モニター接続で `sudo systemctl start ssh`、上記「システム情報」参照 |
| IP が分からない | DHCP で IP が変わった | PC から `nmap -sn 192.168.3.0/24`、ルーター管理画面、またはモニターで `hostname -I` |
| `No space left on device` (apt) | ルートが満杯 | apt キャッシュを SSD に、不要パッケージ削除 |
| `No space left on device` (docker pull) | containerd が SD を使用 | containerd の root を SSD に変更 |
| `permission denied` (docker.sock) | ユーザーが docker グループに未加入 | `sudo usermod -aG docker $USER` + 再ログイン |
| `resize2fs` I/O error | オンライン拡張がサポートされない | 別 PC で SD をオフライン拡張、または OS を SSD に移行 |
| Grafana でデータが表示されない | データソースの Host が古い固定 IP のまま | 下記「Grafana でデータが表示されない」参照 |

---

## Grafana でデータが表示されない

ログインはできるが、パネルに水温・TDS などのグラフが出ない場合の対処（2026-03-15 の実績に基づく）。

### 症状

- Grafana のログインは成功する
- ダッシュボードは開けるが、パネルにデータが表示されない（空 or エラー）
- `docker compose logs grafana --tail 20` で `path=/api/ds/query status=400` が連続する

### 原因

`docker-compose.yml` で db の固定 IP（172.28.0.2）をコメントアウトした後、Grafana の PostgreSQL データソースの Host を更新していない。ラズパイ再起動や `docker compose down && up` により Docker ネットワークが作り直されると、IP の割り当てが変わり、`172.28.0.2` が db を指さなくなる。

### 対処手順

1. Grafana にログイン（Tailscale 経由可）
2. 左メニュー **⚙️ Configuration** → **Data sources**
3. PostgreSQL データソース（例: aquapulse_mock）をクリック
4. **Host URL** を `172.28.0.2:5432` から **`db:5432`** に変更
5. **Save & test** をクリック → 「Database Connection OK」が出れば成功
6. ダッシュボードを開き直し、グラフが表示されることを確認

### 予防

固定 IP をやめたら、**Grafana の Host も同時にホスト名（`db`）に変更**すること。`db` は Docker の内部 DNS で解決されるため、再起動後も安定する。

---

## 参照

- [Docker 公式インストール手順（Debian）](https://docs.docker.com/engine/install/debian/)
- [containerd config](https://github.com/containerd/containerd/blob/main/docs/man/containerd-config.toml.5.md)
