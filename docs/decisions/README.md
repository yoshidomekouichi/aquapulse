# Architecture Decision Records (ADR)

This directory records important technical and architectural decisions for the AquaPulse project.

## Why Write ADRs

- **Preserve project-specific context**: Record "why this choice" that web search cannot answer
- **Prevent repeated discussions**: No need to explain "why it is this way" every time
- **Onboard new AI sessions**: Prevent context loss
- **Review decisions**: Verify "was that decision correct"

## When to Write an ADR

Create ADR for decisions that meet these conditions:

- **Hard-to-reverse decisions**: Architecture changes, tech stack choices
- **Decisions with multiple alternatives considered**: Clear trade-offs
- **Decisions affecting future choices**: Constrain other options
- **Decisions needing explanation**: Choices that may seem strange at first glance

**Don't write ADRs for**:
- Choices reversible in one sprint
- Obvious choices (e.g., JSON library selection)
- Personal preferences

## Active Decisions

- [ADR-0003](2026-07-05-shell-working-directory.md): Explicit working_directory in Shell tool Git operations (Approved)
- [ADR-0002](2026-07-05-archive-directory-structure.md): Archive directory structure (Approved)
- [ADR-0001](2026-07-05-migrate-to-esp32-gcp.md): Migration from Raspberry Pi to ESP32+GCP (Approved)

## Superseded

None

## How to Write

1. Copy [template.md](template.md)
2. Filename: `YYYY-MM-DD-title.md`
3. Write in 5-10 minutes (longer = too detailed)
4. Add to this README

## Status Meanings

- **Proposed**: Under discussion, not yet decided
- **Approved**: Adopted decision
- **Deprecated**: No longer used (record reason)
- **Superseded**: Replaced by new ADR (include link)

## References

- [MADR (Markdown Any Decision Records)](https://adr.github.io/madr/)
- [Architecture Decision Records - ThoughtWorks](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
