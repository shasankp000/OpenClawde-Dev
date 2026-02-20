---
name: dev
description: Autonomous development supervisor powered by OpenCode
---

# Dev Supervisor

The **Dev Supervisor** is an autonomous development orchestration tool.
It manages planning, exploration, and building using OpenCode, while exposing
simple slash commands via OpenClaw.

## Core idea

- OpenClaw provides the interface
- The Supervisor enforces policy and workflow
- OpenCode performs planning and coding
- Humans approve only when required

## Commands

### `/dev run <task>`
Start a new autonomous development task.

Depending on configuration:
- `auto` mode: completes the task autonomously
- `approve_after_plan` mode: pauses after planning for approval

### `/dev status`
Show the current supervisor state:
- planning
- exploring
- awaiting approval
- building
- done

### `/dev approve`
Approve the current plan and allow execution to continue.

### `/dev reject`
Reject the current plan and stop execution.

## Safety model

- Plans are evaluated before execution
- Dangerous operations are blocked by policy
- Build never runs without a finalized plan
- State is persisted in `state.json`

## Configuration

The supervisor behavior is controlled via `config.json`, not prompts.
This ensures deterministic and auditable behavior.

## Notes

This skill executes real processes on the host system.
Ensure OpenCode is properly configured before use.