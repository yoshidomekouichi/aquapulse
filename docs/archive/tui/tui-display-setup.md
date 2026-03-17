# AquaPulse TUI ディスプレイセットアップ

Pi Touch Display 1 (800x480) に TUI ダッシュボードを表示するための手順と、トラブルシュートで判明した技術的なポイント。

---

## 1. うまくいった理由（まとめ）

| 課題 | 試したこと | 結果 | 採用した解決策 |
|------|------------|------|----------------|
| 出力がディスプレイに表示されない | `</dev/tty1 >/dev/tty1` でリダイレクト | 単純な echo は表示されるが、Textual TUI は真っ黒 | **`script` で PTY を作成** |
| openvt が使えない | SSH から `openvt` 実行 | `Couldn't get a file descriptor referring to the console` | SSH からは `script` + リダイレクト |
| ログイン画面が表示される | - | getty が tty1 で動作 | `systemctl disable getty@tty1` |
| ブートログで画面が埋まる | sleep で待機 | 15秒 + cloud-init 待機で改善 | `After=cloud-init.target`、`sleep 15` |

### 重要: Textual は PTY が必要

**`script -q -c "python3 dashboard.py" /dev/null`** で疑似端末（PTY）を作成することで、Textual がターミナルとして認識し、正しく描画される。単純なリダイレクト `>/dev/tty1` だけでは Textual は動作しない。

---

## 2. セットアップ手順（初回）

### 2.1 依存関係（SSD にインストール、ルート容量不足時）

**pip が無い場合**（`No module named pip` が出る場合）は、まず get-pip で pip を導入する：

```bash
cd /mnt/ssd/projects/aquapulse/tui
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --target ./pip-packages --no-cache-dir
```

その後、依存関係をインストール：

```bash
PYTHONPATH=$(pwd)/pip-packages python3 -m pip install --target ./packages textual psycopg2-binary plotext --no-cache-dir
```

**pip が既にある場合**は上記の `get-pip.py` の 2 行を飛ばし、最後の `pip install` だけ実行する。

**plotext だけ追加する場合**（既に textual 等は入っている）：

```bash
cd /mnt/ssd/projects/aquapulse/tui
# pip が無い場合、先に get-pip を実行
# curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# python3 get-pip.py --target ./pip-packages --no-cache-dir
PYTHONPATH=$(pwd)/pip-packages python3 -m pip install --target ./packages plotext --no-deps
```

### 2.2 手動でディスプレイに表示（動作確認）

```bash
sudo ./run_on_display.sh
```

ディスプレイに TUI が表示されれば OK。Ctrl+C で停止（SSH セッションはブロックされる）。

### 2.3 キオスクモード（ログイン画面を出さない）

```bash
sudo systemctl disable getty@tty1
```

### 2.4 フォント（高精細グラフ・時刻表示のため重要）

**滑らかな点字折れ線**と**X軸の時刻ラベル**を表示するには、フォントを小さくしてマス目を増やす必要がある。

```bash
sudo dpkg-reconfigure console-setup
# Terminus を選択、6x12 または 8x14 を選択（極小でマス目最大化）
```

詳細は `docs/tui-terminal-font-setup.md` を参照。

### 2.5 自動起動の有効化

```bash
sudo cp aquapulse-tui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aquapulse-tui
sudo reboot
```

---

## 3. ファイル構成

| ファイル | 役割 |
|----------|------|
| `dashboard.py` | Textual アプリ本体（Pip-Boy 風 UI） |
| `db.py` | TimescaleDB から sensor_readings 取得 |
| `run_on_display.sh` | 手動実行用（script + tty1 リダイレクト） |
| `aquapulse-tui.service` | systemd ユニット（起動時自動表示） |
| `test_display.sh` | tty1 出力の簡易テスト |
| `diagnose_display.sh` | 真っ暗時の診断（config/dmesg/DRM 等を確認） |

---

## 4. トラブルシュート

| 症状 | 確認・対処 |
|------|------------|
| **真っ暗（何も表示されない）** | 下記「4.1 真っ暗の診断」を参照 |
| 真っ黒・アンダースコア点滅のみ | `cat /tmp/aquapulse-tui.log` で Python エラー確認 |
| ログイン画面が表示される | `systemctl disable getty@tty1` を実行したか確認 |
| ブートログで埋まる | 15秒待機後クリア。`/boot/firmware/cmdline.txt` に `quiet loglevel=3` 追加で軽減。`console=tty3` で tty1 を TUI 専用にすることも可。詳細は `docs/tui-display-troubleshooting-2026-03-17.md` |
| 手動では表示されるが自動では表示されない | `sudo systemctl status aquapulse-tui`、journal 確認 |
| 再起動後に表示されない | 手動で `sudo ./run_on_display.sh` を試す。DB が未起動だと接続失敗で落ちる場合あり。`docker compose ps` で db が healthy か確認 |

### 4.1 真っ暗の診断

ディスプレイがずっと真っ暗な場合、以下を順に確認する。

1. **診断スクリプト実行**
   ```bash
   cd /mnt/ssd/projects/aquapulse/tui
   ./diagnose_display.sh
   ```
   結果は `/tmp/display_diagnostic.txt` に保存される。

2. **簡単な出力テスト**
   ```bash
   sudo ./test_display.sh
   ```
   5秒間「AquaPulse Display Test」が表示されるはず。**何も出ない**場合は tty1 とディスプレイの対応に問題がある。

3. **想定される原因と対処**

   | 原因 | 対処 |
   |------|------|
   | **tty1 が別ディスプレイに割り当て** | Pi 5 で HDMI と DSI 両方接続時、コンソールが HDMI 側に出ることがある。`/boot/firmware/config.txt` に `display_default_lcd=1` を追加して DSI を優先 |
   | **バックライトがオフ** | 公式 7" は I2C 制御。サードパーティは GPIO 制御の可能性。`dmesg \| grep -i backlight` で確認 |
   | **DSI ドライバ未ロード** | `dmesg \| grep -i dsi` でエラー確認。`dtoverlay=vc4-kms-dsi-generic` 等が必要な場合あり |
   | **ディスプレイ未検出** | リボンケーブルの接続（Pi 5 は**裏側** DSI コネクタ）、電源（Pin 4=5V, Pin 14=GND）を確認 |

### 4.2 Pi 5 固有の注意点（原因調査）

| 項目 | 内容 |
|------|------|
| **端子の種類** | Pi 5 の MIPI ポート（CAM0/CAM1）は**カメラ・ディスプレイ両対応**。どちらのポートにもディスプレイを接続可能。 |
| **アダプタケーブルは別物** | Pi 5 は 22pin 0.5mm の小型コネクタのため、**アダプタケーブル**（22pin→15pin）が必要。**カメラ用とディスプレイ用のアダプタは配線が異なり、互換性なし**。ディスプレイ用アダプタを使わないと I2C タイムアウトで検出されない。 |
| **dmesg で確認** | `i2c_designware.*controller timed out` や `rpi_touchscreen_attiny.*probe failed` が出たら、**カメラ用ケーブル誤用**の可能性が高い。 |
| **DSI がログに無い** | `dmesg \| grep -i dsi` で rp1-dsi や mipi-dsi が出ない場合、**DSI が検出されていない**。オーバーレイ（`dtoverlay=vc4-kms-dsi-7inch,dsi0`）の指定が効いていないか、`dsi0`/`dsi1` のポートが逆の可能性。 |
| **vc4-drm: Cannot find any crtc** | DSI が検出されないと、表示パイプラインが構築されずこのエラーが出る。上記のケーブル・オーバーレイを確認。 |
| **dsi0 vs dsi1** | Pi 5 の 2 つの MIPI ポートに対応。`dtoverlay=vc4-kms-dsi-7inch,dsi0` でダメなら `dsi1` に変更して再起動を試す。 |

### 4.3 バックライトは点くが画面が真っ黒

**症状**: バックライトは点灯するが、画像が一切表示されない。

**意味**: 電源と I2C（バックライト制御）は通っている。**DSI の映像信号**がパネルに届いていない。

| 原因 | 対処 |
|------|------|
| **DSI 映像パイプライン未接続** | `vc4-drm: Cannot find any crtc` が出ている場合、DRM が DSI を出力先に認識していない。`dtoverlay=vc4-kms-dsi-7inch,dsi0` または `dsi1` を**追加**して再起動 |
| **dsi0 と dsi1 が逆** | オーバーレイで `dsi0` を指定しているなら `dsi1` に、`dsi1` なら `dsi0` に変更して試す |
| **apt upgrade 後のファームウェア** | 以前動いていた場合、`apt upgrade` でファームウェアが変わり壊れた可能性。`vcgencmd version` でバージョン確認。ロールバックは `rpi-eeprom-update -f` で特定バージョンを指定可能（要調査） |
| **DSI データレーンの接触不良** | I2C と DSI は同じケーブル内の別線。リボンケーブルを抜き差しし、ロックをしっかり締める |

---

## 5. 参考: Pi Touch Display 1 接続

- DSI リボンケーブルを Pi 5 の**裏側** DSI コネクタに接続
- 電源: Pin 4 (5V), Pin 14 (GND)
- 解像度: 800x480

---

## 6. 関連ドキュメント

| ファイル | 内容 |
|----------|------|
| `docs/tui-terminal-font-setup.md` | ターミナルフォントの最小化（高精細グラフ・時刻表示のための文字サイズ設定） |
| `docs/tui-display-troubleshooting-2026-03-17.md` | 2026-03-17 のトラブルシュートログ。真っ暗→復旧の経緯、dsi1 が有効だったこと、残課題（ブートログ・レイアウト） |
