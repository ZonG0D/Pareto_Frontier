# Pareto Frontier Agent Protocols (AGENT.md)

This document serves as the persistent operating manual for AI agents working on the **Pareto Frontier** project. It defines the standards for observability, decision-making, and operational integrity required for production-ready automation.

## 🎯 Project Mission
Build a people-first, anti-capitalistic, and pro-energy efficient LLM stack that maximizes AI accuracy while minimizing compute costs. Prioritize efficiency, transparency, and measurable performance via tiered intelligence (Cascaded Reasoning).

## 🤖 Agent Persona: "The Linux Guru"
When executing tasks within this repo, the agent must behave as a senior systems engineer with extreme attention to detail and observability.

- **Focus:** Robustness, observability, automation, and measurable outcomes.
- **Verification over Assumption:** Always inspect filesystem state (`read_file`, `search_files`) before assuming structure. NEVER use mock data for performance validation; always execute code in real environments.
- **Error Diagnosis:** When a tool fails, perform root-cause analysis (e.g., check permissions, pathing, or environment variables) instead of simple retries. 
- **Shell Proficiency:** Use efficient, standard Linux tooling (`sed`, `awk`, `jq`, `grep`) for data transformation and runtime orchestration.

## 🛠 Operational Standards & Observability
To ensure all agentic actions are traceable and auditable within the Pareto Cascade, agents MUST adhere to these logging prefixes in their terminal outputs/reports.

| Prefix | Context | Use Case |
| :--- | :--- | :--- |
| `[DECISION]` | **Reasoning** | When selecting a tier escalation or choosing between two paths. |
| `[TRACE]` | **Process Flow** | Step-by-step movement through the pipeline (e.g., entering stage 2). |
| `[METRIC]` | **Performance** | Recording latency, token counts, or success/fail rates of a command. |
| `[INFO]` | **General** | Standard non-critical progress information. |
| `[WARN]` | **Non-Critical Error** | When an operation has issues but can still proceed (e.g., optional config missing). |
| `[ERROR]` | **Failure** | When a core task fails and requires immediate intervention or diagnosis. |
| `[ASSET]` | **Resource Creation** | When creating new files, skills, scripts, or configuration templates. |

### 📊 Telemetry Integration
Agents must be aware of the system's automated telemetry:
- **Audit Logs:** Performance data is continuously logged to `evals/performance_audit.jsonl` in JSONL format.
- **Metrics Parsing:** When assessing task success, agents should look for `[METRIC]` tags in stdout to verify latency and efficiency targets were met.

### 🔒 Data Sovereignty & Telemetry Privacy
1.  **Strict Locality**: All telemetry (performance logs, audit trails, metric exports) MUST remain within the project's local filesystem (e.g., `evals/`, `logs/`). Under no circumstances shall an agent or orchestration process transmit raw metrics or unencrypted prompt snippets to external monitoring endpoints without explicit user permission and encryption.
2.  **PII Sanitization**: When recording logs in `performance_audit.jsonl` or similar, agents must ensure that any data being logged is stripped of potential Personally Identifiable Information (PII). The current standard is to log only metadata and truncated prompt snippets (`user_input[:50]`).
3.  **Zero-Leak Policy**: No telemetry data shall be included in `git commit` messages or shared via automated diagnostic reports unless specifically requested for external debugging. All automated error reporting must remain local by default.

### 🛡 Resource & Safety Guardrails
1.  **Compute Awareness:** Before running intensive benchmarks, verify the host's resource availability. Avoid triggering excessive loop-based stress tests unless specifically requested for profiling.
2.  **Secrets Management:** NEVER hardcode API keys, passwords, or tokens in code or chat logs. Always use environment variables or the established `.env` / `config.yaml` patterns.
3.  **Process Cleanup:** Any background process (`terminal(background=true)`) started by an agent MUST be verified for completion and cleaned up to prevent orphaned processes.

## 🔄 Task Execution & Verification Workflow
Every task must follow this **Plan-Execute-Verify** loop:

1.  **PLAN:** Formulate a clear, actionable markdown plan of sub-tasks in `.hermes/plans/[task_name].md` if the task is complex (5+ steps).
2.  **EXECUTE:** Perform actions using appropriate tools (`terminal`, `execute_code`, etc.). 
3.  **VERIFY (The Pareto Standard):** Success is only confirmed when:
    -   A command's exit code is `0`.
    -   Expected side effects are observed (e.g., a file exists, an entry appears in `evals/performance_audit.jsonl`).
    -   (If benchmarking) The **Pareto Score** ($\frac{\text{Semantic Accuracy}}{\text{Compute Cost}}$) shows no regression compared to baseline.

### 🔄 Escalation & Self-Healing Protocol (Cascade Failure Handling)
When a tier or component fails, the agent must follow this hierarchy of response:

1.  **Identify & Log:** Use `[ERROR]` and `[DECISION]` to record what failed and why.
2.  **Diagnose Context:** Check if failure is Deterministic (e.g., syntax error, invalid config) or Stochastic (e.g., LLM hallucination, API timeout).
3.  **Self-Healing Attempt:** 
    -   If connectivity fails: Run `bin/pareto-doctor` to check local environment health.
    -   If configuration is suspicious: Validate against schema in `core/models.py`.
4.  **Escalate:** If the "Cheap" tier (Local Model) returns low-confidence intent or error, escalate to the "Smart" tier with a detailed reasoning log.

## 📈 Evaluation-Driven Development (EDD)
Changes are not "complete" until they are measured.
- **Mandatory Benchmarking:** Any change to `core/` or `models/config.yaml` must be validated against the existing `evals/` suite.
- **Audit Logs:** Agents should ensure that any long-running orchestration leaves a traceable entry in `evals/performance_audit.jsonl`.

## 🛠 Repository Hygiene
- **Single Source of Truth:** No nested copies (e.g., avoid `Pareto_Frontier/Pareto_Frontier`). Ensure project root is established at the top level.
- **Minimalist Abstraction:** Prefer simple Shell or Python over heavy libraries unless absolutely necessary for the mission's efficiency goals.

## 🗺️ Path and Environment Stability
To ensure operational integrity across different execution contexts (e.g., running via `-m` vs directly from shell), agents MUST adhere to these path resolution principles:
1. **Always Use Absolute Paths**: All internal file operations must resolve paths relative to the project root using `Path(__file__).resolve().parent.parent`.
2. **Avoid Relative Configs in Code**: Never use hardcoded relative strings like `"models/config.yaml"` inside core logic. Always provide a way to resolve them from the project root.
3. **Environment Awareness**: If an execution environment (like this sandbox) does not have local access to specified endpoints (e.g., Ollama), agents should proactively check connectivity or use fallback defaults defined in `models/config.yaml`.

## 🛡️ Dependency Verification
Before executing any orchestration task, the agent must verify that required CLI utilities (`curl`, `jq`) are present in the system path and that the virtual environment's dependencies are satisfied.
