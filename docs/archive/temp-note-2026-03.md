# 一時メモ（2026-03 アーカイブ）

> 2026-03-14 時点のメモ。有用な情報は daily-log や hardware/wiring に統合済み。

---

## 水温センサーのラズパイピンの引越しのための事前記録

- `dtoverlay=w1-gpio`

## w1 デバイス一覧

```
drwxr-xr-x 2 root root 0 Mar 14 19:39 .
drwxr-xr-x 4 root root  0 Mar  3 21:49 ..
lrwxrwxrwx 1 root root 0 Mar  3 22:00 28-00001117a4e0 -> ../../../devices/w1_bus_master1/28-00001117a4e0
lrwxrwxrwx 1 root root 0 Mar  3 22:00 w1_bus_master1 -> ../../../devices/w1_bus_master1
```

## DS18B20 読み取り例

```
ac 01 4b 46 7f ff 04 10 86 : crc=86 YES
ac 01 4b 46 7f ff 04 10 86 t=26750
```

## Tapo エラー（参考）

```
Handshake1 error: 403 Forbidden
[tapo_sensors] Failed: Tapo(InvalidResponse)
[tapo_lighting] Failed: Serde(Error("missing field `auto_off_remain_time`", line: 1, column: 914))
```

## Collector 出力例（JSON）

```json
{"time": "2026-03-14 10:38:24.402512+00:00", "sensor_id": "ds18b20_water_28_00001117a4e0", "metric": "temperature", "value": 26.75}
{"time": "2026-03-14 10:39:25.198562+00:00", "sensor_id": "ds18b20_water_28_00001117a4e0", "metric": "temperature", "value": 26.75}
```
