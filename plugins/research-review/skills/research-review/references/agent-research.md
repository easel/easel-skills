# Agent Research Workflows

Use this reference when research requires multiple turns, tools, or agents.

## Single-Agent Research

Use one agent when the question is narrow, sources are known, or the report is
short. Keep an explicit research ledger so the agent can update its plan as
sources confirm, refute, or redirect the work.

Recommended loop:

1. Clarify the decision and constraints.
2. Search for primary sources.
3. Open and inspect sources.
4. Update the source plan.
5. Synthesize claims with citations.
6. Review the answer against the question and evidence.

Clarification is part of the research work. If the prompt is underspecified,
ask for the missing decision criteria, target audience, source class, date
range, or output format. If asking would stall useful progress, record the
assumption and continue.

## Multi-Agent Research

Use multiple agents only when independent branches can run in parallel:

- distinct ecosystems or vendors;
- independent options in a comparison;
- source discovery separate from critique;
- one agent gathers evidence while another checks the draft against sources.

Keep agents isolated until they produce their own findings. Merge results by
evidence quality, not by vote count.

For open-ended research, a planner can split independent search branches by
ecosystem, option, vendor, standard, or source class. Each branch should return
a source ledger and confidence label. The synthesizer should discard duplicate
or weak evidence before writing the final report.

## Context Discipline

- Pass only the research question, scope, and source constraints to subagents.
- Do not pass the intended answer unless the task is to verify it.
- Ask agents for source ledgers, not just conclusions.
- Drop irrelevant source summaries before final synthesis.
- Preserve claims, source identifiers, dates, conflicts, and confidence; discard
  background text that does not change the decision.

## Tool Discipline

- Use search tools for discovery and source tools for verification.
- Use local file search for repo evidence before external browsing when the
  question concerns local implementation.
- For long-running research, prefer resumable/background execution when the
  platform supports it.
- Set a tool-call or source-count budget for bounded reviews. Increase the
  budget only when the current evidence changes the likely answer or exposes a
  material conflict.
- Treat external connectors and private indexes as read-only research surfaces
  unless the user explicitly asks for a modifying action.

## Evidence From Agent Research Practice

- Anthropic's agent guidance distinguishes fixed workflows from agents that
  dynamically direct their process and tool use; choose the simpler workflow
  when the research path is predictable.
- Anthropic's multi-agent research writeup describes research as open-ended and
  path-dependent, which supports iterative source planning and parallel search
  branches for genuinely broad questions.
- OpenAI's deep research guide emphasizes multi-step research, visible inline
  citations, clarification or prompt rewriting for underspecified tasks, and
  budget controls such as tool-call limits.
- ReAct research supports interleaving reasoning with actions so an agent can
  update plans while consulting external sources.
- Context-engineering guidance treats context as finite, so research agents
  should keep source ledgers and drop irrelevant source detail before synthesis.

Sources:

- Anthropic, "Building effective agents" (2024-12-19):
  https://www.anthropic.com/engineering/building-effective-agents
- Anthropic, "How we built our multi-agent research system" (2025-06-13):
  https://www.anthropic.com/engineering/multi-agent-research-system
- OpenAI, "Deep research" API guide:
  https://developers.openai.com/api/docs/guides/deep-research
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models"
  (2022): https://arxiv.org/abs/2210.03629
- Anthropic, "Effective context engineering for AI agents" (2025-09-29):
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
