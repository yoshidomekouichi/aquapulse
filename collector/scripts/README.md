# collector/scripts

ハードウェア検証・テスト用スクリプト。ホスト上で実行する（`/dev/i2c-1` 等にアクセスするため）。

**本番の TDS 収集**は `sources/gpio_tds.py` が担当。本フォルダは配線確認・デバッグ用。

| スクリプト | 用途 |
|------------|------|
| `read_mcp3424_ch1.py` | MCP3424 CH1（TDS）の生電圧を読む（配線確認用） |
| `measure_tds_bottle.py` | TDS 瓶測定。ppm 表示。`--save` で DB に保存（暫定運用用） |
| `read_mcp3424_ch2.py` | （将来）CH2（pH）の生電圧を読む |

## 実行前

```bash
sudo modprobe i2c-dev
```

## 瓶測定（measure_tds_bottle.py）

プロジェクトルートから実行する：

```bash
# プローブを瓶に浸してから
python3 collector/scripts/measure_tds_bottle.py

# DB に保存（db コンテナ起動中）
python3 collector/scripts/measure_tds_bottle.py --save
```
