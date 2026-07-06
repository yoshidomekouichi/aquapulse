# Archived Documentation

This directory contains documentation that has been superseded by the restructured documentation under `docs/`.

---

## Why Archived

**Date:** 2026-07-06

**Reason:** Documentation restructuring using the [Diátaxis framework](https://diataxis.fr/)

The original cloud migration documentation was:
- Written in Japanese
- Mixed tutorials, guides, references, and explanations in single files
- Redundant content across multiple files
- Difficult to navigate for new users

The new documentation structure separates content by user intent:
- **Tutorials** (`docs/tutorials/`) - Learning-oriented
- **Guides** (`docs/guides/`) - Task-oriented
- **Reference** (`docs/reference/`) - Information-oriented
- **Explanation** (`docs/explanation/`) - Understanding-oriented

---

## What's Archived

### cloud-migration/

Original Japanese documentation for migrating from Raspberry Pi to ESP32 + GCP architecture.

**Files:**
- `README.md` - Overview and migration rationale (Japanese)
- `00_OVERVIEW.md` - System architecture and tech stack (Japanese)
- `01_HARDWARE_SETUP.md` - Hardware wiring guide (Japanese)
- `02_GCP_SETUP.md` - GCP account and project setup (Japanese)
- `03_PHASE1_MANUAL.md` - Manual deployment guide (Japanese)
- `04_PHASE2_AUTOMATION.md` - GitHub Actions CI/CD (Japanese)
- `07_TROUBLESHOOTING.md` - Common issues (Japanese)
- `08_REFERENCES.md` - External references (Japanese)

**Superseded by:**
- `docs/explanation/why-cloud-migration.md` - Migration rationale (English)
- `docs/reference/architecture.md` - System architecture (English)
- `docs/guides/hardware-setup.md` - Hardware guide (English)
- `docs/guides/gcp-setup.md` - GCP setup guide (English)
- `docs/tutorials/getting-started-esp32.md` - Getting started tutorial (English)

---

## Accessing Archived Content

If you need to reference the original Japanese documentation:

1. **Browse directly:** Files remain in this directory for reference

2. **Search in Git history:**
   ```bash
   # Find when file was moved
   git log --all --full-history -- "docs/cloud-migration/README.md"
   
   # View file at specific commit
   git show <commit-hash>:docs/cloud-migration/README.md
   ```

3. **Restore specific file (if needed):**
   ```bash
   # Restore from archive
   cp docs/archive/cloud-migration/README.md docs/cloud-migration/
   ```

---

## Note on Language

The project transitioned to English-first documentation to:
- Reach a global audience
- Follow open-source best practices
- Enable easier collaboration
- Improve discoverability

**User communication in this chat remains Japanese** as per user preference (see `.cursor/rules/00-base.mdc`).

---

## Questions?

If you need clarification on:
- Why specific content was archived
- How to find equivalent information in new docs
- Whether to restore archived content

→ Refer to ADR-0004 (if created) or open a GitHub issue.

---

Last updated: 2026-07-06
