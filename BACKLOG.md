# Backlog

保留中のタスク・将来やりたいこと。

**ステータス:**
- 🔵 Backlog - 未着手
- 🟡 In Progress - 作業中
- 🟢 Done - 完了
- 🔴 Cancelled - 中止

---

## 🔵 High Priority

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

Last updated: 2026-07-06
