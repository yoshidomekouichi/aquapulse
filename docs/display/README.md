# ディスプレイ

Pi Touch Display 1 (800x480) への表示に関するドキュメント。

## ドキュメント

| ファイル | 内容 |
|----------|------|
| [grafana-kiosk.md](grafana-kiosk.md) | Grafana キオスクモードのセットアップ・運用 |

## 現在の構成

| 項目 | 設定 |
|------|------|
| 表示方式 | Grafana キオスク（Wayland/cage + Chromium） |
| 解像度 | 800x480 |
| 自動起動 | systemd (grafana-kiosk.service) |
| 輝度制御 | 時間帯で自動調整（cron） |

## クイック操作

```bash
# サービス再起動
sudo systemctl restart grafana-kiosk

# 輝度変更
/projects/aquapulse/kiosk/brightness.sh night

# ログ確認
journalctl -u grafana-kiosk -f
```

## 関連フォルダ

- `/projects/aquapulse/kiosk/` - スクリプト・設定ファイル
- `/etc/systemd/system/grafana-kiosk.service` - systemd サービス
