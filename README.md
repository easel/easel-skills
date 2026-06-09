# Easel Skills

Reusable agent skills for prose quality, adversarial review, and execution
hygiene.

## Install With Codex

Install from the GitHub marketplace configuration:

```bash
codex plugin marketplace add https://github.com/easel/easel-skills.git --ref main
codex plugin add all@easel-skills
```

Install individual skills with `sloptimizer@easel-skills` or
`adversarial-review@easel-skills`.

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

Install individual Claude Code skills with `sloptimizer@easel-skills` or
`adversarial-review@easel-skills`.

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
