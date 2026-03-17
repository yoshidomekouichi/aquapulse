# TUI ダッシュボード デザイン仕様（総合依頼書準拠）

**参照**: Cursor への総合依頼書（Pip-boy 特化型完全版）

---

## デザイン目標

- **粗いブロック文字（■□）は使用しない**
- **Dolphie**（https://github.com/charles-001/dolphie）: 滑らかなグラフ、Grafana ライクなレイアウト
- **Pip-boy**（Fallout）: レトロフューチャー、モノクローム計器盤の雰囲気

---

## 技術スタック

| 項目 | 採用 |
|------|------|
| UI フレームワーク | Textual |
| グラフ描画 | plotext（Textual 上でレンダリングするラッパー実装） |

---

## 配色（Pip-boy グリーンモノクローム）

| 用途 | 色 |
|------|-----|
| 背景 | 完全な黒 `#0a0e0a` |
| テキスト・軸・グラフ線・グリッド | 明るいグリーン（蛍光グリーン）`#00ff41` |
| 薄いグリッド | `#1a4d1a` |
| アクセント | `#00ff88` |

---

## グラフ要件

- **点字マーカー（braille）** による滑らかな折れ線
- 薄いグリーンの背景グリッド（X/Y 軸）
- 短いグリーン目盛り線（Ticks）
- 24 時間の時系列データ

---

## レイアウト（800x480 最適化）

2x2 グリッド、薄いグリーンボーダー、左上にタイトル。

| 位置 | パネル | 内容 |
|------|--------|------|
| 左上 | Water Temp | 過去 24h 水温推移（折れ線） |
| 右上 | Tapo_Temp | 過去 24h 室温推移（折れ線） |
| 左下 | Tapo_Humidity | 過去 24h 湿度推移（折れ線） |
| 右下 | Tapo_Tank_Light | 現在のステータスを「ON」または「OFF」で中央に大きく表示 |

---

## 最終仕上げ（2026-03 追加）

| 項目 | 内容 |
|------|------|
| **スクロールバー** | `overflow: hidden`、`scrollbar-size: 0 0` で完全非表示 |
| **パネルボーダー** | `border: solid` で最も細い1ピクセル線 |
| **グリッド** | `PIPBOY_GRID = "#005500"` で暗いグリーン、目立たせない |
| **グラフ線** | `marker="braille"`、`fillx=False`。フォントを小さく（6x12 等）してマス目を確保 |
| **X軸** | `plt.xticks()` で時刻ラベル（14:00 等）。`xaxes(True,False)` で下軸のみ表示 |
| **ステータスヘッダー** | 画面上部に Water / Room / Hum / Light の現在値を1行表示 |

## フォント（高精細グラフの要）

**滑らかな braille 折れ線**と**X軸時刻ラベル**には、フォントを小さくしてマス目を増やす必要がある。詳細は `docs/tui-terminal-font-setup.md` を参照。

```bash
# 推奨: 6x12 または 8x14（極小でマス目最大化）
sudo dpkg-reconfigure console-setup
# → Terminus を選択、6x12 を選択

# または /etc/default/console-setup を直接編集
# FONTFACE="Terminus"
# FONTSIZE="6x12"
```

## 実装ファイル

| ファイル | 役割 |
|----------|------|
| `dashboard.py` | Textual アプリ本体、2x2 グリッドレイアウト |
| `plotext_wrapper.py` | plotext を Pip-boy 風にレンダリングするラッパー（fill 対応） |
| `db.py` | データ取得 |
