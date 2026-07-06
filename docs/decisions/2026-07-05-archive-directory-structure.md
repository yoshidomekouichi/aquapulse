# ADR-0002: Adoption of Archive Directory Structure

## Status

Approved (2026-07-05)

## Context

Migration to ESP32+GCP (ADR-0001) means existing Raspberry Pi files (docker-compose.yml, Python scripts, etc.) will no longer be operational files.

However, these files have value:
- Useful as reference for future implementations
- Preserve project history
- Record design decisions

Need to decide how to manage existing files and where to place new architecture files.

## Alternatives Considered

### 1. Archive Directory (Adopted)

```
aquapulse/
├─ archive/raspberry-pi/
│  ├─ docker-compose.yml
│  ├─ scripts/
│  └─ README.md
├─ esp32/
├─ cloud-functions/
├─ terraform/
└─ docs/
```

- pros: Easy to reference, Git history preserved, clear separation
- cons: Directory structure changes

### 2. Git Tag + Deletion

```
git tag v1.0-raspberry-pi
(Delete existing files)
```

- pros: Clean root, focus on new architecture
- cons: Cumbersome to reference (need to checkout tag), confusing for beginners

### 3. Branch Separation

```
legacy/raspberry-pi: Old architecture
main: New architecture
```

- pros: Complete separation
- cons: Requires branch switching, difficult to share documentation

### 4. Parallel Operation

```
raspberry-pi/
esp32-gcp/
```

- cons: Unclear which is current project, ambiguous handling of root files (README, etc.)

## Decision

Adopt **Archive Directory**

Reasons:
- Balance between easy reference and clear separation
- Understandable for beginners (myself)
- Documentation (docs/) can be shared
- Git history preserved

## Consequences

### Positive
- Existing files easily referenceable
- New architecture files at root, clear
- Can explain "why archived" in README

### Negative
- Directory restructuring work needed
- Some paths change (documentation links need fixing)

### Risks
- File move errors (carefully execute with Git operations)

## Related Materials

- [ADR-0001](2026-07-05-migrate-to-esp32-gcp.md) (Migration background)
- [docs/cloud-migration/](../cloud-migration/) (New architecture guide)
