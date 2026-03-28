# Skill Registry - Miura Forge

## Project Context
- **Name:** Miura Forge Engine
- **Stack:** Python 3.10+, setuptools, Google Sheets, multiple AI APIs
- **Architecture:** Modular pipeline (9 fases SDD ya implementado)
- **Test Framework:** pytest, pytest-cov
- **Linting:** ruff, black, mypy
- **Line Length:** 100
- **Docstrings:** Google convention

## Convention Files
- `engram-convention.md` - Engram memory conventions

## User-Level Skills (Global)
| Skill | Trigger | Location |
|-------|---------|----------|
| skill-creator | Creating new AI agent skills | `~/.config/opencode/skills/skill-creator/` |
| go-testing | Go/Bubbletea TUI testing | `~/.config/opencode/skills/go-testing/` |
| judgment-day | "judgment day", "review adversarial" | `~/.config/opencode/skills/judgment-day/` |
| sdd-init | Initialize SDD context | `~/.config/opencode/skills/sdd-init/` |
| sdd-explore | Research/investigation phase | `~/.config/opencode/skills/sdd-explore/` |
| sdd-propose | Create change proposal | `~/.config/opencode/skills/sdd-propose/` |
| sdd-spec | Write specifications | `~/.config/opencode/skills/sdd-spec/` |
| sdd-design | Technical design | `~/.config/opencode/skills/sdd-design/` |
| sdd-tasks | Task breakdown | `~/.config/opencode/skills/sdd-tasks/` |
| sdd-apply | Implementation | `~/.config/opencode/skills/sdd-apply/` |
| sdd-verify | Validation | `~/.config/opencode/skills/sdd-verify/` |
| sdd-archive | Archive changes | `~/.config/opencode/skills/sdd-archive/` |

## Project Conventions
- `AGENTS.md` - Agent behavior rules (to be created if needed)

## SDD Workflow
1. **sdd-init** → Initialize context (this project is initialized)
2. **sdd-explore** → Research trends/features
3. **sdd-propose** → Create change proposal
4. **sdd-spec** → Write specifications
5. **sdd-design** → Technical design
6. **sdd-tasks** → Break down tasks
7. **sdd-apply** → Implement
8. **sdd-verify** → Validate
9. **sdd-archive** → Archive

## Next Steps
- Use `/sdd-new <change-name>` to start a new change
- Or `/sdd-explore <topic>` to investigate ideas
