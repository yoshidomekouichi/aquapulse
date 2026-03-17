# ラズパイ配線記録

Raspberry Pi（40ピンヘッダー）のピン配置およびブレッドボードの配線を記録する。配線を追加・変更したら都度更新すること。

---

## Fritzing 配線図

- **ファイル名**: `AquaPulse_Wiring_v2.0_Temp_TDS_pH.fzz`（Fritzing 形式）
- **保存場所**: PC 上（ラズパイでは閲覧不可。Fritzing は PC アプリのため）
- **対応**: v2.0 の全配線を図示。v1.0 は Fritzing ファイルなしだが、v2.0 の **DS18B20 水温センサー部分のみ** が v1.0 に該当する

---

## バージョン一覧

| バージョン | 内容 |
|------------|------|
| [v1.0](v1.0.md) | DS18B20 水温のみ |
| [**v2.0**](v2.0.md) | DS18B20 + MCP3424 ADC + TDS + pH（**最新**） |
| v2.1（予定） | TDS に DFR0504 アイソレータ導入 → [improvement-plan](../improvement-plan.md) 参照 |
