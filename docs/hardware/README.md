# ハードウェア

AquaPulse の物理構成・配線に関するドキュメント。

---

## 配線記録

| バージョン | 内容 |
|------------|------|
| [v1.0](wiring/v1.0.md) | DS18B20 水温のみ |
| [**v2.0**](wiring/v2.0.md) | DS18B20 + MCP3424 ADC + TDS + pH（**最新**） |

→ [wiring/](wiring/) を参照

---

## 改善計画・試行ログ

トライアンドエラーを伴う改善は、計画と実施を分けて記録する。

| ドキュメント | 役割 |
|--------------|------|
| [improvement-plan.md](improvement-plan.md) | 改善計画・ピン変更の予定・rationale |
| [experiment-log.md](experiment-log.md) | 試したこと・結果・学び・次のステップ |

**運用**: 計画を立てる → 実施して experiment-log に記録 → 成功したら wiring を更新
