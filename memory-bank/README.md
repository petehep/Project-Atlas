# ATLAS Memory Bank

This folder is the **Cline Memory Bank** for Project ATLAS. It captures durable
project knowledge so that a fresh AI session can reconstruct full context
quickly, without re-reading the whole codebase.

## How to use
At the start of any new session, read these files **in this order** (each file
references the ones before it):

1. `projectbrief.md`   — what the project is, at the highest level.
2. `productContext.md` — why it exists, who it's for, working style.
3. `activeContext.md`  — current state, recent changes, next steps.
4. `systemPatterns.md` — architecture, patterns, and key decisions.
5. `techContext.md`    — stack, constraints, dependencies, gotchas.
6. `progress.md`       — version history, what works, known gaps.

## Rules
- **Read the user's actual files before changing anything.** This memory bank is
  a summary, not the source of truth — the code and docs are.
- **Update this memory bank** whenever you finish a meaningful change (bump
  `activeContext.md` and `progress.md`, and any pattern/tech file that changed).
- These files are designed to be committed to git so they persist across sessions
  and machines.

## Rebuild the full context (fresh session)
```bash
cat memory-bank/*.md
```
Then point the agent at the relevant files as needed.
