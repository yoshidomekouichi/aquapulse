# TUI ゴーストグラフ問題 デバッグログ

## 問題

- 初回描画：正しいフルサイズのグラフが表示される
- 定期更新時（30秒後）：小さいゴーストグラフが上に被さる

---

## 試行 1: 閾値を下げる + layout=False

**変更内容**:
- `_MIN_VALID_WIDTH = 60` → `20`
- `_MIN_VALID_HEIGHT = 15` → `5`
- 全ての `update()` に `layout=False` を適用
- 閾値未満でも `_redraw()` は呼ぶ（return しない）

**結果**: グラフが出なくなった

**原因**: 閾値が高すぎて実機でキャッシュが設定されなかった

---

## 試行 2: 閾値を大幅に下げる

**変更内容**:
- `_MIN_VALID_WIDTH = 20`
- `_MIN_VALID_HEIGHT = 5`

**結果**: まだグラフが小さい（52x8）

**ログ**:
```
on_resize: event.size=56x10, w=52, h=8, cache=0x0, series_len=0
```

**原因**: GraphWidget を Vertical に変更し、子 Static に height が指定されていなかった

---

## 試行 3: #graph-content に CSS 追加

**変更内容**:
```css
#graph-content {
    height: 1fr;
    width: 100%;
}
```

**結果**: 
- グラフの描画は戻った
- **ゴーストはまだ出る**

**ログ (03:11:48)**:
```
on_resize: event.size=56x10, w=52, h=8, cache=0x0, series_len=0
on_resize: cache UPDATED to 52x8
_redraw: SKIP (no data, series_len=0)

GraphPanel.update_data: title=Water Temp, series_len=80, latest=26.19
_redraw: DRAWING with size 52x8
build_pipboy_line_plot: input width=52, height=8 -> w=52, h=8
_redraw: DONE
```

**観察**:
- サイズはまだ 56x10 → 52x8 のまま（CSS が反映されていない？）
- 初回は正常に描画されている
- ゴーストが出るタイミングは未確認（30秒後の更新ログが必要）

---

---

## 試行 4: Static をクリアしてから更新

**変更内容**:
```python
static.update("", layout=False)  # まずクリア
static.update(plot_text, layout=False)  # 新しい内容をセット
```

**仮説**: Static の内容が正しく置き換えられていない可能性

**結果**: ゴースト消えず

---

## 試行 5: plotext を無効化して固定文字列で確認

**変更内容**:
```python
test_text = f"[TEST {self._valid_width}x{self._valid_height}]\nval={self.series[-1]:.1f}"
static.update(test_text, layout=False)
return  # plotext をスキップ
```

**仮説**: 
- ゴーストが出れば → Textual の問題
- ゴーストが出なければ → plotext の問題

**結果**: ゴースト出る → **Textual の問題確定**

---

## 試行 6: GraphWidget を Static に変更（Vertical のネスト回避）

**変更内容**:
```python
class GraphWidget(Static):  # Vertical → Static に変更
    def __init__(self, unit: str = "", **kwargs):
        super().__init__("", **kwargs)  # 空文字で初期化
        ...
    
    def _redraw(self) -> None:
        ...
        self.update(plot_text, layout=False)  # 自身を直接 update
```

**仮説**: Vertical コンテナのネストが Textual の描画で問題を起こしている

**結果**: ゴースト出る（30秒後に3秒間）

---

## 試行 7: layout=True に戻す

**変更内容**:
```python
self.update(plot_text, layout=True)  # False → True
```

**仮説**: `layout=False` が描画の遅延を引き起こしている

**結果**: 15秒ごとに切り替わる

---

## 試行 8: @work を削除（メインスレッドで直接処理）

**変更内容**:
- `@work(exclusive=True, thread=True)` を削除
- `call_from_thread` を削除し、直接呼び出し

**結果**: 
- 0-3秒: 正常
- 3-28秒: ゴースト
- 28秒以降: 正常

**結論**: **スレッドは原因ではない**

---

## 現時点での分析

### ゴーストのパターン
1. 初回描画は正常
2. 約3秒後にゴーストが出現
3. 約30秒後（次の更新時）に正常に戻る

### 原因の可能性
1. **Textual の遅延レイアウト計算**
   - 初回描画後に遅延してレイアウトが再計算される
   - その際に古い/異なる描画が表示される

2. **plotext のグローバル状態**（試行 5 で否定）
   - plotext を無効化してもゴーストが出た

3. **スレッドの問題**（試行 8 で否定）
   - @work を削除してもゴーストが出た

---

## 試行 9: 強制再描画タイマー

**変更内容**:
```python
# on_mount 内
self.set_interval(1, self._force_redraw_all)
```

**結果**:
| 間隔 | ゴースト |
|------|----------|
| 3秒後と5秒後のみ | 9秒〜27秒 |
| 2秒ごと | 18-19秒の1秒間 |
| 1秒ごと | 12秒に一瞬だけ |

**結論**: **強制再描画でゴーストを抑え込める**

---

## 現状（2026-03-17 深夜）

### 採用した解決策
- **1秒ごとに強制再描画** (`set_interval(1, self._force_redraw_all)`)
- ゴーストは「一瞬だけ」に抑制

### 根本原因（未特定）
- Textual の内部で約3秒後に何らかの遅延描画が発生
- plotext やスレッドは原因ではない（試行 5, 8 で確認済み）
- 強制再描画で上書きすることで回避

### 懸念点
- 1秒ごとの再描画は負荷が高い可能性
- 根本原因が未特定のため、将来問題が再発する可能性

---

## 次回のタスクリスト

### 優先度: 高
1. **負荷の確認**
   - CPU 使用率を監視（`htop` や `top`）
   - 1秒ごとの再描画が Pi に負担をかけていないか確認

2. **間隔の最適化**
   - 負荷が高い場合、2秒ごとに戻す（1秒だけゴーストを許容）
   - 0.5秒ごとでゴーストが完全に消えるか確認

### 優先度: 中
3. **根本原因の特定**
   - Textual の Show, Mount, Ready イベントをログに出す
   - 3秒後に何が起きているか特定
   - Textual のソースコードを調査

4. **Textual のバージョン確認**
   - 現在: textual-8.1.1
   - 最新バージョンで修正されている可能性

### 優先度: 低
5. **デバッグログの削除**
   - 問題が解決したら、`logging.debug` を削除
   - `/tmp/aquapulse-debug.log` への出力を停止

---

## 次のステップ

1. **30秒後の更新時のログを確認** - ゴーストが出るタイミングを特定
2. **CSS が反映されているか確認** - `#graph-content` のサイズを確認
3. **plotext の Lock が正しく動作しているか確認**

---

## 仮説

### ゴーストの原因候補

1. **plotext のグローバル状態の干渉**
   - 複数の GraphWidget が同時に描画されると、plotext の状態が混ざる
   - Lock は追加済みだが、十分でない可能性

2. **Static の重複描画**
   - `update(layout=False)` でも何らかの理由で古い描画が残る

3. **レイアウト再計算による Resize の発火**
   - どこかで `layout=True` の update が呼ばれている

4. **Textual の内部キャッシュ**
   - Static の描画キャッシュが正しく更新されていない
