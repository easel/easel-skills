# Easel Skills

Reusable agent skills for planning, prose quality, adversarial review, repo
triage, release management, data workflows, and execution hygiene.

## Install With Codex

Install from the GitHub marketplace configuration:

```bash
codex plugin marketplace add https://github.com/easel/easel-skills.git --ref main
codex plugin add all@easel-skills
```

Install individual skills with `sloptimizer@easel-skills`,
`adversarial-review@easel-skills`, `repo-triage@easel-skills`,
`release-management@easel-skills`, `data-quality@easel-skills`,
`data-documentation@easel-skills`, `data-mapping@easel-skills`,
`research-review@easel-skills`, or `plan-lifecycle@easel-skills`.

For local development:

```bash
git clone https://github.com/easel/easel-skills.git
cd easel-skills
codex plugin marketplace add "$PWD"
codex plugin add all@easel-skills
```

Start a new Codex thread after installing or reinstalling so the skill metadata
is loaded into the session.

## Install With Claude Code

Install from the Claude Code marketplace configuration:

```bash
claude plugin marketplace add https://github.com/easel/easel-skills.git
claude plugin install all@easel-skills
```

Install individual Claude Code skills with `sloptimizer@easel-skills`,
`adversarial-review@easel-skills`, `repo-triage@easel-skills`,
`release-management@easel-skills`, `data-quality@easel-skills`,
`data-documentation@easel-skills`, `data-mapping@easel-skills`,
`research-review@easel-skills`, or `plan-lifecycle@easel-skills`.

Use the explicit HTTPS URL for Claude Code. The `owner/repo` shorthand may try
SSH depending on local Git configuration. For a private repository, make sure
GitHub HTTPS credentials are available first, for example with `gh auth login`.

For local development:

```bash
git clone https://github.com/easel/easel-skills.git
cd easel-skills
claude plugin marketplace add "$PWD"
claude plugin install all@easel-skills
```

Start a new Claude Code session after installing or reinstalling so the skill
metadata is loaded into the session.

## Manual Skill Install

If you are not using the Codex plugin marketplace, copy the skills into the
agent skill directory used by your runtime:

```bash
mkdir -p ~/.agents/skills ~/.claude/skills
cp -R skills/* ~/.agents/skills/
cp -R skills/* ~/.claude/skills/
```

## Included Skills

- `sloptimizer`: audits AI-generated prose, plans, specs, prompts, and work
  items for vague claims, filler, missing actors, weak acceptance criteria, and
  unsupported implementation promises.
- `adversarial-review`: pressure-tests plans, specs, prompts, work items, code
  changes, or PRs with independent critical review.
- `repo-triage`: summarizes local Git state, dirty worktrees, branch
  comparisons, changed files, recent commits, and optional PR or issue context.
- `release-management`: audits repository state, version metadata, validation
  commands, marketplace manifests, commits, tags, and pushes before release
  execution.
- `data-quality`: generates and audits portable data validation rules from
  schemas, profiles, sample rows, and business constraints.
- `data-documentation`: creates evidence-backed dataset, table, and column
  documentation from schemas, profiles, lineage, examples, and glossary terms.
- `data-mapping`: derives source-to-target mappings, extraction rules,
  canonical names, conflict policies, and survivorship specs.
- `research-review`: researches technical questions, compares options, verifies
  current behavior, and returns source-backed recommendations.
- `plan-lifecycle`: creates, refines, reviews, and hands off implementation,
  release, test, migration, data, and post-implementation plans while
  delegating specialist checks to the narrower skills.

## Validate

Run the portable validation script locally:

```bash
bash scripts/validate.sh
```

Run the same checks in Docker:

```bash
docker build -t easel-skills-validate .
docker run --rm easel-skills-validate
```

The Docker check validates Codex and Claude plugin metadata, marketplace
wiring, skill frontmatter, agent metadata, Python syntax, shell syntax, the
Sloptimizer Vale fixtures, and the bundled redundancy audit.
