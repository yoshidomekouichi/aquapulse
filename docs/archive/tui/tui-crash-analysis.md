# TUI クラッシュ原因の検証結果

## 推論：Traceback が発生して UI が崩壊した原因

### 1. plotext_wrapper.py: `canvas` 未定義の NameError

**問題**: `try/finally` 内で例外が発生した場合、`canvas` が設定される前に `finally` が実行され、その後の `plain = re.sub(..., canvas)` で `NameError: name 'canvas' is not defined` が発生する。

```python
try:
    ...
    canvas = plt.build()  # ここで例外 → canvas 未設定
finally:
    plt.clf()
# ここで canvas を参照 → NameError
plain = re.sub(..., canvas)
```

### 2. GraphWidget.render(): 例外が Textual の描画ループに伝播

**問題**: `render()` に try/except がなく、`build_pipboy_line_plot()` や `self.size` アクセスで例外が起きると、Textual の描画ループがクラッシュし、Traceback が画面に表示される。

### 3. self.size の初期状態

**問題**: レイアウト未完了時に `self.size` が (0,0) や未初期化の可能性。`self.size.width - 2` で負の値になることは `width > 2` チェックで防いでいるが、`self.size` 自体が None や不正な場合に AttributeError の可能性。

### 4. call_from_thread 内の未捕捉例外

**問題**: `update_header` や `lambda: self.query_one(...)` が例外を投げると、メインスレッドで未処理となりアプリがクラッシュする。

### 5. plotext plot_size の不正値

**問題**: plotext に 0 や負の値、極端に大きな値を渡すと内部でエラーになる可能性。現状はフォールバックで防いでいるが、型が float になる場合などは未検証。

## 対策

1. `canvas` を try の前に初期化
2. `build_pipboy_line_plot` 全体を try/except で囲み、エラー時は安全な Text を返す
3. `GraphWidget.render()` を try/except で囲む
4. すべての `call_from_thread` コールバックを try/except で保護
5. w, h に clamp を適用（最小 2、最大 200 等）
