# Agent Guide for Pareto Frontier

## Overview
The **Pareto Frontier** ecosystem employs a sophisticated, tiered agent architecture designed to maximize LLM stack efficiency while minimizing computational overhead. This guide documents the operational standards, communication protocols, and execution workflows for AI agents operating within this system.

---

### 1. Agent Roles & Hierarchy
- **Leaf Agents (`role='leaf'`)**: Focused workers that execute tasks but cannot delegate further.
- **Orchestrator Agents (`role='orchestrator'`)**: Can spawn additional leaf agents for parallel workloads (currently disabled due to `max_spawn_depth=1` constraint).

All child agents inherit the parent model's configuration, including fallback chains and available toolsets.

---

### 2. Task Lifecycle

| Phase | Action | Tool(s) |
|-------|--------|---------|
| **Plan** | Create a clear markdown plan in `.hermes/plans/<task_name>.md` outlining expected steps, success criteria, and fallback paths. | `terminal`, `read_file`, `search_files` |
| **Execute** | Run required tool calls (e.g., `delegate_task`, file I/O). Use absolute paths to ensure stability across contexts. | `execute_code`, `terminal`, etc. |
| **Verify** | Confirm exit codes, side effects, and performance metrics using the standardized verification loop (`[METRIC]` logs). Ensure no regressions in accuracy or cost metrics. | `read_file`, `search_files` |

---

### 2.1 Execution Verification Protocol
Success is defined by:
- Exit code `0`
- Confirmed file/directory creation (via `read_file`)
- Performance Delta: **Pareto Score** (`Semantic Accuracy / Compute Cost`) must not regress

Failure to meet any criterion marks the task as failed and triggers escalation according to the **Cascade Protocol**.

---

### 3. Communication Conventions
All agent outputs MUST adhere to these standardized prefixes:

| Prefix | Context | Example |
|--------|---------|----------|
| `[INFO]`   | General Progress | `[INFO] Initializing core pipeline...` |
| `[TRACE]`  | Data Flow      | `[TRACE] Normalized input: "hello world"` |
| `[DECISION]`| Reasoning     | `[DECISION] Escalating to Smart tier due to low confidence` |
| `[METRIC]` | Performance    | `[METRIC] Latency: 210ms, Throughput: 45 tok/s` |
| `[WARN]`   | Non‑Critical Issue | `[WARN] Fallback model used (reduced accuracy)` |
| `[ERROR]`  | Fatal Failure | `[ERROR] Failed to resolve dependencies` |

---

### 3. Skill Integration
Agents must load skills via the **Skill Management** subsystem:

```bash
# List available skills
skill_view

# Load a specific skill
skill_manage --load <skill_name>
```

All loaded skills are cached in `~/.hermes/skills/` and persist across agent restarts.

---

### 4. Scheduling with Cronjobs (Optional)
Agents can schedule recurring tasks using the **cronjob** tool:

```bash
# Create a new cron job that runs nightly at 2 AM
cronjob create --schedule "0 2 * * *" \
   --script "./scripts/nightly_audit.sh" \
   --task-name "NightlyAudit"
```

All cron jobs run in isolated sessions with no shared state; use `search_files` to share data between them.

---

### 5. Security & Compliance
- **Two‑Factor Authentication**: All GitHub interactions require 2FA enabled before July 30, 2026 (see repository security notice).
- **PII Sanitization**: Telemetry logs MUST truncate user inputs to `[user_input[:50]]` before writing to audit trails.
- **Locality Constraint**: All telemetry data (`evals/*.jsonl`) must remain on local storage; external transmission is prohibited unless explicitly authorized.

---

### 6. Production Readiness Checklist
Before any component reaches the edge environment:

1. Verify no Pareto Score regression (`bench_results.txt`).
2. Confirm equal observability parity (minimum `[TRACE]` and `[METRIC]` emissions per critical path).
3. Ensure all input/output sanitization paths are active to prevent raw character leakage.
4. Validate dependency integrity via `bin/pareto-doctor`.
5. Test graceful degradation: failure in a “Smart” tier must trigger appropriate fallback handling.

---

### 6. Maintenance Workflow
Periodic maintenance follows the **Cleanup Summary** schedule (e.g., 2026‑09‑27). Key actions include:
- Removing duplicated directory copies.
- Updating `.gitignore` patterns to ignore stray `*.egg-info/` folders.
- Verifying path resolution relative to project root.

---

## Quick Reference Commands
| Command | Purpose |
|---------|----------|
| `delegate_task --name task1 --goal "Run benchmark suite"` | Spawn a subagent for the given goal |
| `cronjob list` | List existing scheduled jobs |
| `bin/pareto-run "your prompt"` | Execute a direct prompt using the stack |
| `bin/pareto-doctor` | Run health check diagnostics |

---

**End of Guide**  

_This document was last updated on 2026‑10‑05 and will be versioned alongside the main repository._