# Backlog

保留中のタスク・将来やりたいこと。

**ステータス:**
- 🔵 Backlog - 未着手
- 🟡 In Progress - 作業中
- 🟢 Done - 完了
- 🔴 Cancelled - 中止

---

## 🔵 High Priority

### 水温監視 + ファン自動制御（サーモスタット）

**Status:** 🔵 Backlog  
**Estimated:** 3-5 hours  
**Added:** 2026-07-09  
**Deadline:** ⚠️ **2026-08 お盆前（1週間不在）**  
**Context:** 2026-07-09にファン付け忘れで水温30℃到達。魚は無事だったが危険な状態。お盆で1週間不在のため、自動化が必須  

**Incident Record:**
- **日時:** 2026-07-09
- **事象:** ファン起動忘れ → 帰宅時に水温30℃
- **影響:** 魚は無事だったが、あと数度高ければ危険だった
- **原因:** 手動でのファンON/OFF管理
- **再発防止:** 自動制御の実装（本タスク）

**What to do (Phase 1 - 必須):**

1. **Cloud Function実装**
   - Pub/Sub trigger（水温データ受信）
   - 閾値ロジック（ヒステリシス付き）:
     - 水温 ≥ 28℃ → ファンON
     - 水温 ≤ 26℃ → ファンOFF
   - Tapo P300制御（python-kasa使用）
   - エラーハンドリング（Tapo接続失敗時）

2. **通知機能**
   - ファンON/OFF時にLINE/Email通知
   - 30℃超過時に緊急アラート
   - 制御失敗時に通知

3. **動作テスト**
   - 手動で水温を上げてテスト
   - ファンON/OFF確認
   - 通知動作確認
   - 1週間の連続動作テスト

4. **Grafana監視**
   - ファン状態パネル追加（既存）
   - 水温アラート設定（30℃超過）
   - 制御ログの可視化

**What to do (Phase 2 - 保険/低優先度):**

5. **クーラー自動制御（オプション）**
   - Tapoリモコン機能の調査
   - python-kasaのIR対応確認
   - 代替製品検討（SwitchBot, Nature Remoなど）
   - 35℃超過時の緊急クーラー起動

**Why critical:**
- **魚の生命に直結**：30℃超過は致命的なリスク
- **お盆不在**：1週間自宅を空けるため、手動対応不可
- **実績あり**：既に1回インシデント発生済み

**Implementation priority:**
- Phase 1（ファン制御）: **お盆前に必須**
- Phase 2（クーラー）: 余裕があれば（手動対応も可）

**Technical notes:**
```python
# Cloud Function イメージ
# collector/cloud-functions/thermostat/main.py

import asyncio
from kasa import Discover

THRESHOLD_HIGH = 28.0  # ファンON
THRESHOLD_LOW = 26.0   # ファンOFF

async def control_fan(temperature: float):
    dev = await Discover.discover_single(
        TAPO_P300_IP,
        username=TAPO_USERNAME,
        password=TAPO_PASSWORD
    )
    await dev.update()
    fan = dev.children[0]  # ファン接続口
    
    if temperature >= THRESHOLD_HIGH and not fan.is_on:
        await fan.turn_on()
        send_notification(f"🔥 水温 {temperature}℃ → ファンON")
    elif temperature <= THRESHOLD_LOW and fan.is_on:
        await fan.turn_off()
        send_notification(f"❄️ 水温 {temperature}℃ → ファンOFF")
```

**Prerequisites:**
- ESP32基本実装完了（水温データ送信）
- Tapo P300設定済み（既存）
- Pub/Sub設定済み（既存）

**Related:**
- `collector/src/sources/tapo_lighting.py` (既存のTapo P300制御)
- `docs/operations/tapo-status-report.md` (python-kasa利用)
- インシデント記録（本エントリ）

---

### Legacy Docs整理

**Status:** 🔵 Backlog  
**Estimated:** 1-2 hours  
**Added:** 2026-07-06  
**Context:** PR #48-50でDiátaxis構造に移行したが、古いRaspberry Pi docsが残っている  

**What to do:**
1. Archive old directories:
   - `docs/design/` → `docs/archive/raspberry-pi-design/`
   - `docs/hardware/` → `docs/archive/raspberry-pi-hardware/`
   - `docs/operations/` → `docs/archive/raspberry-pi-operations/`
   - `docs/display/` → `docs/archive/raspberry-pi-display/`
2. Update `docs/archive/README.md` with new archived content
3. Update `README.md` to remove references to archived directories

**Why important:**
- Clean up documentation structure
- Follow Diátaxis framework completely
- Reduce confusion between old (Raspberry Pi) and new (ESP32) docs

**Related:**
- PR #50 (Diátaxis restructuring)
- `.cursor/rules/00-base.mdc` (Documentation Standards)

---

### CI/CD Basic Setup

**Status:** 🔵 Backlog  
**Estimated:** 1-2 hours  
**Added:** 2026-07-06  
**Context:** PR #51でconflict checkルールを追加したが、手動。自動化して構造的に強制すべき  

**What to do:**
1. Create `.github/workflows/pr-checks.yml`
2. Implement automated checks:
   - **Conflict check** (fail on conflict) - Prevent PR #50 scenario
   - **PR size check** (warning only) - Alert when PR >400 lines
3. Test on draft PR to verify functionality

**Why important:**
- Prevents PR #50 scenario (conflict detected after PR creation)
- Structural enforcement of `.cursor/rules/20-version-control.mdc` Section 6
- Reduces manual review burden
- Teaches rules automatically to new contributors

**Implementation notes:**
```yaml
# .github/workflows/pr-checks.yml
# - Use git merge-tree for conflict detection
# - Use git diff --stat for size check
# - Fail on conflict, warn on size
```

**Related:**
- PR #51 (conflict check rules)
- `.cursor/rules/20-version-control.mdc` (Section 6: Pre-PR Conflict Check)

---

## 🔵 Medium Priority

### CI/CD Advanced Features

**Status:** 🔵 Backlog  
**Estimated:** 2-3 hours  
**Added:** 2026-07-06  

**What to do:**
1. Commit message format check (Conventional Commits)
   - Warn if format doesn't match `type(scope): description`
2. Documentation update check
   - Fail if code changes but docs unchanged (heuristic)
3. Enhanced PR template with auto-checklist
   - Auto-check items verified by CI

**Prerequisites:**
- CI/CD Basic Setup completed

**Related:**
- PR #51 (conflict check rules)
- `.cursor/rules/00-base.mdc` (Commit Messages)

---

### Phase 2: ユニバーサル基板への移行

**Status:** 🔵 Backlog  
**Estimated:** 2-3 hours  
**Added:** 2026-07-06  
**Context:** Phase 1（ブレッドボード）で動作確認後、配線整理のためユニバーサル基板に移行  

**What to do:**
1. **アダプタ基板の統合:**
   - DS18B20プルアップ回路を基板に内蔵（4.7kΩ抵抗）
   - MCP3424を基板に実装
   - センサーから直接3線/2線接続（途中の基板なし）

2. **コネクタ化:**
   - JST-XH 3ピン（DS18B20用）
   - JST-XH 2ピン（TDS用）
   - 予備コネクタ3-5個（将来の拡張用）

3. **部品実装:**
   - ユニバーサル基板（7×9cm）
   - ピンソケット（ESP32取り付け）
   - ICソケット（MCP3424取り付け）
   - 半田付け（裏面配線）

**Why important:**
- 配線がすっきり（途中の基板なし）
- 故障点が減少（接続部減少）
- 見た目が改善（プロフェッショナル）
- 拡張性確保（予備コネクタ）

**Prerequisites:**
- Phase 1（ブレッドボード）で動作確認完了
- ESP32基本実装完了（センサー読み取り動作）
- 1-2ヶ月の安定稼働確認

**Parts list:**
- ユニバーサル基板（7×9cm）: ¥200
- ピンソケット（19ピン×2）: ¥100
- ICソケット（8ピン）: ¥50
- JST-XH コネクタ各種: ¥300
- 抵抗・配線材料: ¥150
- **合計:** ¥800

**Related:**
- 配線整理の議論（2026-07-06チャット）
- `docs/guides/hardware-setup.md` (Phase 2 section, future)

---

## 🔵 Low Priority

### Additional Documentation

**Status:** 🔵 Backlog  
**Estimated:** 3-5 hours  
**Added:** 2026-07-06  

**Missing docs from Diátaxis structure:**
- `guides/manual-deployment.md` - Manual GCP deployment steps
- `guides/operations.md` - Day-to-day operations guide
- `guides/troubleshooting.md` - Common issues and solutions
- `docs/contributing.md` - Detailed contribution guidelines (detailed version of `.cursor/rules/00-base.mdc`)

**Priority rationale:**
- Can wait until ESP32 implementation progresses
- Diátaxis structure is in place, easy to add incrementally

**Related:**
- `.cursor/rules/00-base.mdc` (Documentation Standards)

---

## 🔵 Future Features

### ESP32 OTA Updates

**Status:** 🔵 Backlog  
**Estimated:** 5-8 hours  
**Added:** 2026-07-06  

**Description:**
- Implement Over-The-Air (OTA) firmware updates for ESP32
- Avoid USB cable requirement for updates after initial setup
- Version management and rollback capability

**What to do:**
1. Research ESP32 OTA mechanisms (HTTP, MQTT-based)
2. Implement update server (Cloud Functions or Cloud Storage)
3. Add OTA update code to ESP32 firmware
4. Test with gradual rollout strategy

**Prerequisites:**
- ESP32 basic implementation complete
- WiFi connection stable (99%+ uptime)
- Monitoring in place to detect failed updates

**Why not now:**
- Need stable baseline first
- Initial USB-based development is acceptable
- Can add later without disrupting system

---

## 📝 Notes

### How to use this file

- **Add tasks:** Important but not urgent, require >1 hour
- **Small tasks (<30 min):** Just do them, no need to record
- **When starting:** Create branch and PR, link here
- **When completing:** Mark 🟢 Done, add PR number, move to bottom

### Task lifecycle

```
Idea → Add to Backlog (🔵)
       ↓
Start work → Mark In Progress (🟡)
       ↓
Complete → Mark Done (🟢), add PR link
       ↓
Archive (after 1 month) → Remove from file
```

### Review schedule

- **Weekly:** Review High Priority items
- **Monthly:** Re-prioritize all items
- **Quarterly:** Archive completed items (>1 month old)

---

## 🟢 Completed

*(Items completed in the last month)*

<!-- Example:
### Task Name
**Status:** 🟢 Done (PR #XX)
**Completed:** 2026-07-06
**Notes:** Brief summary
-->

---

Last updated: 2026-07-09
