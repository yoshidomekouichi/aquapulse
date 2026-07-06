# ADR-0003: Explicit working_directory in Shell Tool Git Operations

## Status

Approved (2026-07-05)

## Context

During PR #40-42 creation, `git branch --show-current` did not return the correct branch, causing work on unintended branch.

Specific problem:
- Executed `git checkout -b cursor/add-adr-v3-0d1c`
- But `git branch --show-current` returned `main` or different branch name
- Result: Direct commit to main branch (prohibited)

Cause:
- Did not specify Shell tool's `working_directory` parameter
- Depended on previous command's state

## Alternatives Considered

### 1. Use `cd /workspace &&` Every Time

```bash
Shell(command="cd /workspace && git checkout -b ...")
```

- pros: Works, previously successful
- cons: Verbose, error-prone (&& chaining)

### 2. Explicitly Specify working_directory Parameter (Adopted)

```python
Shell(
  command="git checkout -b ...",
  working_directory="/workspace"
)
```

- pros: Clear, correct Shell tool usage, avoids state dependency
- cons: Parameter specification required every time

### 3. Do Nothing

- cons: Problem recurs

## Decision

**Explicitly specify `working_directory="/workspace"` for all Git operations**

Reasons:
- Structurally avoid Shell tool state dependency
- More explicit and understandable
- Correct tool usage

## Consequences

### Positive
- Structurally prevent Git operation errors
- Easy to verify in code review
- Applicable to other Shell commands

### Negative
- Parameter specification required every time (verbose)
- Slightly increased code volume

### Risks
- Problem recurs if rule forgotten
- → Formalized in 20-version-control.mdc

## Related Materials

- [20-version-control.mdc](../../.cursor/rules/20-version-control.mdc) (Mandatory parameters for Git operations)
- PR #40-42 (PRs where problem occurred)
