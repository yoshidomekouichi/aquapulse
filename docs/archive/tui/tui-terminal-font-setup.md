# TUI ターミナルフォント設定（高精細グラフ・時刻表示のための文字サイズ最小化）

AquaPulse TUI で「滑らかな点字（braille）折れ線」と「X軸の時刻ラベル」を確実に表示するには、**ターミナルの文字サイズを小さくし、描画に使える文字グリッド（マス目）を増やす**ことが重要です。

**重要**: 文字サイズは Python/Textual のコードでは変更できません。**ターミナル（コンソール）側の設定**で行います。

---

## 1. 環境の確認

AquaPulse TUI は以下のいずれかで動作します：

| 環境 | フォント設定方法 |
|------|------------------|
| **Linux コンソール（tty1）** | `console-setup` / `/etc/default/console-setup` |
| **Wayland デスクトップ** | Alacritty / Foot の設定ファイル |
| **X11 デスクトップ** | 同上、または GNOME Terminal 等 |

`run_on_display.sh` で tty1 に表示している場合は **Linux コンソール**です。

---

## 2. Linux コンソール（tty1）のフォント設定

### 2.1 最小フォントサイズへの変更

```bash
# 現在の設定を確認
cat /etc/default/console-setup

# 設定を編集（sudo が必要）
sudo nano /etc/default/console-setup
```

以下のように設定します（**極小フォント**でマス目を最大化）：

```
# フォントの選択（Terminus は braille 対応）
FONTFACE="Terminus"
FONTSIZE="6x12"

# または 8x16（やや読みやすい）
# FONTSIZE="8x16"

# 文字セット（Unicode で braille 表示に必要）
CHARMAP="UTF-8"
```

**FONTSIZE の候補**（小さいほどマス目が増える）:

| サイズ | 800x480 での目安 | 備考 |
|--------|-------------------|------|
| `6x12` | 約 66 行 × 133 桁 | 極小、近づいて読む |
| `8x14` | 約 34 行 × 100 桁 | やや小さい |
| `8x16` | 約 30 行 × 100 桁 | バランス型 |
| `16x32` | 約 15 行 × 50 桁 | 現状（マス目不足の原因） |

### 2.2 Braille 対応フォント（点字折れ線用）

plotext の `marker="braille"` は Unicode U+2800–28FF の点字を使います。**Terminus 4.40 以降**は braille を含みます。

```bash
# Terminus の braille 対応を確認（br1 または br2 が含まれる）
ls /usr/share/consolefonts/ | grep -i term
# Terminus22x11.psf.gz 等が表示される。br1/br2 は別パッケージの可能性あり。

# console-setup で Terminus を選べば通常は braille も含まれる
sudo dpkg-reconfigure console-setup
# → Terminus を選択、6x12 または 8x14 を選択
```

### 2.3 設定の反映

```bash
# 即時反映（現在の tty に適用）
sudo setupcon

# または再起動
sudo reboot
```

---

## 3. Wayland デスクトップ（Alacritty / Foot）

デスクトップで TUI を起動する場合、ターミナルエミュレータの設定でフォントサイズを変更します。

### 3.1 Alacritty

```bash
# 設定ファイルを作成・編集
mkdir -p ~/.config/alacritty
nano ~/.config/alacritty/alacritty.toml
```

```toml
[font]
size = 8
# または 10（やや読みやすい）

[font.normal]
family = "DejaVu Sans Mono"
# または "Liberation Mono"（braille 対応）

[font.bold]
family = "DejaVu Sans Mono"

[font.italic]
family = "DejaVu Sans Mono"
```

### 3.2 Foot

```bash
mkdir -p ~/.config/foot
nano ~/.config/foot/foot.ini
```

```ini
[main]
font=DejaVu Sans Mono:size=8
# または font=Liberation Mono:size=10
```

### 3.3 起動方法

```bash
# Alacritty で起動
alacritty -e bash -c "cd /mnt/ssd/projects/aquapulse/tui && PYTHONPATH=./packages python3 dashboard.py"

# Foot で起動
foot -e bash -c "cd /mnt/ssd/projects/aquapulse/tui && PYTHONPATH=./packages python3 dashboard.py"
```

---

## 4. 800x480 での目安

| フォントサイズ | 行数 | 桁数 | グラフパネルあたり |
|----------------|------|------|--------------------|
| 6x12 | ~66 | ~133 | 高さ約 15 行、幅約 65 桁 |
| 8x16 | ~30 | ~100 | 高さ約 7 行、幅約 50 桁 |
| 16x32 | ~15 | ~50 | 高さ約 3 行、幅約 25 桁（不足） |

**推奨**: `6x12` または `8x14` で、グラフと X 軸ラベルに十分なスペースを確保。

---

## 5. 関連ドキュメント

- `docs/tui-display-setup.md` - ディスプレイ全体のセットアップ
- `docs/tui-design-spec.md` - TUI デザイン仕様
