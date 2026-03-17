# Tapo 互換性ステータスレポート

**作成日**: 2026-03-16  
**最終更新**: 2026-03-16  
**対象**: tapo_sensors (H100), tapo_lighting (P300)

---

## 数日前にデータが取れなくなった原因（まとめ）

| 要因 | 内容 |
|------|------|
| **tapo ライブラリのエラー** | tapo_sensors: H100 が `InvalidRequest` (error_code -1002) を返す。tapo_lighting: P300 の `get_child_device_list` で `Serde(missing field auto_off_remain_time)`。tapo ライブラリが両方で失敗 |
| **TAPO_HUB_IP の誤り** | 当初 192.168.3.4 が P110M 等の別デバイスを指していた。H100 の正しい IP は 192.168.3.6 |
| **TAPO_LIGHTING_IP と TAPO_HUB_IP の混同** | 両方 192.168.3.6 (H100) にすると、tapo_lighting が H100 の子デバイス（T310）を取得してしまう。P300 マルチタップは別 IP であり、`TAPO_LIGHTING_IP` は P300 を指す必要がある |
| **python-kasa の temperature_unit バグ** | features の `"temperature" in fid` が `temperature_unit` にもマッチし、`float("celsius")` でクラッシュ |

**結論**: tapo ライブラリの互換性問題が直接原因。python-kasa への切り替え後も、IP 設定の見直しと temperature_unit の修正が必要だった。

---

## トラブルシュートログ

| 日付 | 実施内容 | 結果 |
|------|----------|------|
| 2026-03-16 | tapo 0.8.12 → 0.8.11 へダウングレード | **効果なし**。tapo_sensors は InvalidRequest のまま、tapo_lighting は Serde エラーのまま |
| 2026-03-16 | **python-kasa へ切り替え** | **tapo_lighting: 成功**。P300 の power_state 取得 OK。**tapo_sensors: 要確認**。TAPO_HUB_IP のデバイスが P110M として検出（H100 でない可能性）。H100 の IP を確認すること |
| 2026-03-16 | **TAPO_HUB_IP=192.168.3.6 に修正** | H100 の正しい IP。python-kasa で tapo_sensors の温湿度取得に **temperature_unit バグ** を発見 |
| 2026-03-16 | **python-kasa の temperature_unit 修正** | features の `"temperature" in fid` が `temperature_unit` にもマッチし `float("celsius")` でエラー。完全一致 `fid == "temperature"` に修正して解決 |
| 2026-03-16 | **tapo ライブラリでの再現テスト** | H100 は tapo で動作確認。P300 の `get_child_device_list` は Serde(`auto_off_remain_time` 欠如) で失敗。**TAPO_BACKEND=tapo** で tapo_sensors を tapo に切り替え可能 |
| 2026-03-16 | **tapo_lighting が Grafana に表示されない** | TAPO_LIGHTING_IP=192.168.3.6 (H100) のため、tapo_lighting が H100 の T310 を取得。sensor_id が P300 の `80227057...` と異なり `802E31BF...` に。**TAPO_LIGHTING_IP は P300 の IP を指定すること** |

---

## 1. バージョンチェック

| 項目 | 状態 |
|------|------|
| **PyPI 最新版** | 0.8.12 |
| **requirements.txt** | `python-kasa>=0.10.0`（tapo から切り替え済み） |
| **コンテナ内実装** | python-kasa 0.10.2 ✓ |

→ **結論**: python-kasa で tapo_lighting は動作。tapo_sensors は T310 の feature 取得要調査。

---

## 2. GitHub リポジトリ状況

- **main 最新コミット**: 2026-03-15 (protocol layer refactor)
- **リリース**: 0.8.12 が最新（2026-03-11）
- **auto_off_remain_time 関連**: 未修正（main でも必須フィールドのまま）

---

## 3. スキーマチェック（tapo_lighting / P300）

**問題**: `PowerStripPlugResult` の `auto_off_remain_time` が必須 (`u64`)

```rust
// tapo ライブラリ (power_strip_plug_result.rs)
pub auto_off_remain_time: u64,  // 必須 → レスポンスに無いと Serde エラー
```

**P300 の実際のレスポンス**: オートオフ無効時などで `auto_off_remain_time` が含まれない場合あり

**対応**: tapo ライブラリ側で `Option<u64>` にする修正が必要。現時点で該当 PR/issue は未確認。

---

## 4. エラー別サマリー

| ソース | エラー | 原因 | 現状 |
|-------|--------|------|------|
| tapo_sensors | `Tapo(InvalidRequest)` | H100 が error_code -1002 を返す（メソッド未サポート等） | ライブラリ・ファームウェア互換性の可能性 |
| tapo_lighting | `Serde(missing field auto_off_remain_time)` | P300 レスポンスにフィールドが無い | ライブラリのスキーマ修正待ち |

---

## 5. Agent として実施したこと

1. **PyPI バージョン確認** - 最新 0.8.12
2. **コンテナ内 tapo バージョン確認** - 0.8.12 → 0.8.11 へ変更
3. **GitHub main の power_strip_plug_result.rs 確認** - auto_off_remain_time は未だ必須
4. **tapo issues 検索** - auto_off 関連の修正 PR は未発見
5. **CHANGELOG 確認** - 0.8.12 に該当修正なし
6. **tapo 0.8.11 ダウングレード試行** - 両エラーとも変化なし
7. **python-kasa へ切り替え** - tapo_lighting.py, tapo_sensors.py を python-kasa で書き換え。tapo_lighting は成功、tapo_sensors は T310 データ未取得（要調査）

---

## 6. 推奨アクション・運用

1. **tapo_sensors**: `TAPO_BACKEND=tapo` で tapo ライブラリ使用。**TAPO_HUB_IP** は H100 の IP（Tapo アプリの端末情報で確認）
2. **tapo_lighting**: python-kasa を継続使用（tapo は P300 の `get_child_device_list` で Serde エラー）。**TAPO_LIGHTING_IP** は P300 マルチタップの IP（H100 とは別）
3. **H100 と P300 は別デバイス**: 同じ IP にすると sensor_id が変わり、Grafana の既存クエリと合わなくなる

---

## 7. tapo_lighting が Grafana に反映されない場合

**症状**: DB には power_state が入っているが、Grafana のパネルに表示されない。

**原因**: `TAPO_LIGHTING_IP` が H100 を指していると、tapo_lighting は H100 の子デバイス（T310）を取得する。sensor_id が `tapo_lighting_802E31BF...`（T310）になり、P300 の `tapo_lighting_80227057...` とは異なる。

**対応**: `TAPO_LIGHTING_IP` を P300 マルチタップの IP に設定する。Tapo アプリで P300 の端末情報から IP を確認。電源抜きで IP が変わる可能性は低いが、ルーターの DHCP 設定次第。

---

## 8. 将来の改善（TODO）

- **過去ログとの照合** - ライブラリ切り替え後、過去の tapo データと比較し、同じデータ挙動かチェックする仕組みを追加する
