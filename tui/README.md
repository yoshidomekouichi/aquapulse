# AquaPulse TUI ダッシュボード

Pi Touch Display 1 (800x480) 用の Pip-Boy 風 TUI。水温・気温・湿度・照明の 24 時間時系列グラフを表示。

詳細なセットアップ手順・トラブルシュートは [docs/tui-display-setup.md](../docs/tui-display-setup.md) を参照。

---

## セットアップ

```bash
cd tui
# pip が無い場合: get-pip.py で SSD にインストール（docs 参照）
PYTHONPATH=pip-packages python3 -m pip install --target ./packages textual psycopg2-binary --no-cache-dir
```

## 実行

**SSH ターミナルに表示**（開発・内容修正用）:
```bash
./run_local.sh
```
現在のターミナルに TUI が表示される。内容修正後はここで確認できる。

**Pi Touch Display に表示**（SSH から手動実行）:
```bash
chmod +x run_on_display.sh
sudo ./run_on_display.sh
```
`script` で PTY を作成し、tty1 に出力。SSH セッションはブロックされる。

## 自動起動（systemd）

```bash
sudo systemctl disable getty@tty1   # ログイン画面を出さない
sudo cp aquapulse-tui.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aquapulse-tui
sudo reboot
```

## 技術メモ

- **Textual は PTY が必要**: 単純な `>/dev/tty1` では描画されない。`script -q -c "python3 ..."` で PTY を作成すること。
- **getty 無効化**: キオスクモードでは `getty@tty1` を無効化する。

## トラブルシュート

- エラーログ: `cat /tmp/aquapulse-tui.log`
- 出力テスト: `sudo ./test_display.sh`
- 詳細: [docs/tui-display-setup.md](../docs/tui-display-setup.md)
