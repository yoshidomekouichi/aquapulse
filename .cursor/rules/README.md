# AquaPulse Rules

This directory manages rules for AI agent development.

## Rule Structure

```
.cursor/rules/
├─ README.md                # This file
├─ 00-base.mdc              # Project foundation
├─ 10-collaboration.mdc     # Human-AI collaboration
└─ 20-version-control.mdc   # Git/PR strategy
```

## Load Order

Numeric prefixes control load order:
- `00-` loads first (foundation)
- `20-` loads last (details)
- Later files take precedence (on conflict)

## Role of Each File

### 00-base.mdc (Project Foundation)

```
Contents:
  - Project overview (AquaPulse: freshwater aquarium monitoring)
  - Tech stack (ESP32, GCP, Terraform)
  - Hardware constraints (sensors fixed, USB physical connection required)
  - Code conventions (Python: Black + isort)
  - Absolute rules

Application: All sessions
Update frequency: Rare (only on project structure changes)
```

### 10-collaboration.mdc (Human-AI Collaboration)

```
Contents:
  1. Interactive Development
     - Explain before implementing
     - Present options
     - Decision gates (3 types)
  
  2. Communication
     - Avoid confirmation bias
     - Flat evaluation
     - Prioritize technical accuracy
  
  3. Error Transparency
     - Level 1-3 error reporting
     - Pre-operation checks
     - Trial-and-error transparency

Application: All sessions
Update frequency: Low (only on stance changes)
```

### 20-version-control.mdc (Git/PR Strategy)

```
Contents:
  1. Git Workflow (GitHub Flow)
     - Branch strategy
     - Commit conventions
     - Prohibitions
  
  2. PR Strategy
     - PR size constraints (200-400 lines)
     - Vertical slicing
     - 1 PR = 1 logical change
  
  3. Dependency Judgment
     - Technical vs logical dependencies
     - Stacked vs parallel PRs

Application: Git/PR operations
Update frequency: Low (only on workflow changes)
```

## Rule Management Principles

### 1. Maintain Appropriate Size

```
Recommended:
  - Each file: 100-500 lines
  - Total: ≤ 2,000 tokens

When exceeded:
  - Split into subdirectories
  - Reference details in separate files
```

### 2. Avoid Duplication

```
NG: Same content in multiple files
OK: Write once, reference elsewhere
```

### 3. Be Specific

```
NG: "Write good code"
OK: "Functions ≤ 50 lines, single responsibility"
```

### 4. Maintain Balance

```
Avoid excessive rules:
  - Don't specify everything
  - Leave room for creativity
  - Trust judgment
```

## Adding New Rules

### Step 1: Classify

```
Determine which layer:
  - Foundation (00-): Project-specific constraints
  - Core (10-20): Development stance, communication
  - Process (30-40): Git, PR, deployment
  - Domain (50-60): Technology-specific (ESP32, GCP, etc.)
```

### Step 2: Add to Existing or Create New

```
Criteria:
  - Related to existing file → Add
  - New area → Create new
  - File exceeds 500 lines → Consider splitting
```

### Step 3: Create PR

```
Required:
  - Reason for change
  - Impact scope
  - Usage examples
```

## Troubleshooting

### Q: Rules not applying

```
Check:
  1. YAML frontmatter correct?
  2. alwaysApply: true set?
  3. metadata.environments: cloud configured?
```

### Q: Rules conflicting

```
Solutions:
  1. Check numeric prefixes (later takes precedence)
  2. Place more specific rules later
  3. Remove duplicates
```

### Q: Too many files

```
Recommended: 5-8 files

When exceeded:
  - Consolidate related rules
  - Remove infrequently used rules
  - Organize into subdirectories
```

## Conflict Resolution Strategy

```
When multiple rules conflict:

1. Later file takes precedence
   00-base.mdc < 20-version-control.mdc

2. More specific rule takes precedence
   General rule < Domain-specific rule

3. Security first (deny-wins)
   Permission rule < Prohibition rule
```

## Periodic Review

```
Monthly review:
  - Remove unused rules
  - Review frequently violated rules
  - Formalize new patterns

Quarterly review:
  - Review file structure
  - Optimize size
  - Remove duplicates
```

## References

- [Cursor Rules Best Practices (2026)](https://www.morphllm.com/cursor-rules-best-practices)
- [CLAUDE.md Convention](https://agentpatterns.ai/instructions/claude-md-convention/)
- [Agent Governance Toolkit](https://microsoft.github.io/agent-governance-toolkit/)

---

Last updated: 2026-07-05
