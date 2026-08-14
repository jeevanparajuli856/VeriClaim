# Operator quickstart

The repo should carry the workflow; the human should not paste a giant prompt for every phase.

## Brand-new project

Tell Codex:

```text
This is a brand-new project. Treat my idea as PROJECT INCEPTION.
Follow AGENTS.md and the project-inception skill.
Do not implement or create tasks yet.
Separate confirmed requirements, assumptions, recommendations, and open questions.
Continue automatically unless a material decision genuinely requires me.
```

## Approve first task

```text
Approve <TASK-ID> as the first implementation task.
Proceed using AGENTS.md and the task-orchestration skill.
Continue automatically until human action is genuinely required.
```

## Start Gemini

Open the frontend worktree prepared by Codex and tell Gemini:

```text
Implement frontend for <TASK-ID>. Follow AGENTS.md and GEMINI.md.
```

## Return from Gemini

```text
Gemini finished/stopped <TASK-ID>. Read frontend-report.json and continue orchestration.
```

## After PR merge

```text
The PR for <TASK-ID> is approved and merged. Perform post-merge closure.
```
