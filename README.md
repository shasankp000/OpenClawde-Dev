# OpenClawde Supervisor

A Python-based supervisor for managing OpenCode agent workflows with approval gates and policy enforcement for integration with OpenClaw as a skill.

**OpenClaw Compatible** - This project is designed as an OpenClaw skill and can be installed using `install.sh` for seamless integration with the OpenClaw ecosystem.

## Overview

The OpenClawde Supervisor orchestrates OpenCode agents (plan and build) to execute tasks while providing human oversight through configurable approval gates. It tracks session state, extracts executable plans, and enforces safety policies before execution.

## Features

- **Approval Modes**: Control when human approval is required
- **Plan Extraction**: Automatically detects and parses executable plans from agent output
- **Policy Enforcement**: Reject plans containing forbidden keywords
- **State Management**: Persistent state tracking across sessions
- **Signal Emission**: Clear signals for integration with external systems (e.g., OpenClaw)
- **Session Continuity**: Seamlessly continue OpenCode sessions across approval boundaries

## Installation

### Prerequisites

- Python 3.x
- `opencode` CLI tool
- `git`
- OpenClaw (optional, for skill integration)

### Quick Install (OpenClaw Skill)

**One-line install (recommended):**

```bash
curl -fsSL https://raw.githubusercontent.com/shasankp000/OpenClawde-Dev/main/install.sh | bash
```

**Or clone and install:**

```bash
git clone https://github.com/shasankp000/OpenClawde-Dev.git
cd OpenClawde-Dev
bash install.sh
```

This will:
1. Clone/update the supervisor repository to `~/.local/share/openclaw/opencode-supervisor`
2. Install Python dependencies (if `requirements.txt` exists)
3. Install the OpenClaw skill to `~/.openclaw/skills/dev-supervisor`
4. Set up the `OPENCLAW_SUPERVISOR_HOME` environment variable
5. Make the skill available via `/dev` commands in OpenClaw

After installation:
```bash
# Restart your shell or source your profile
source ~/.bashrc  # or ~/.zshrc

# Restart OpenClaw gateway
openclaw gateway restart

# Test the skill
/dev status
```

### Manual Installation (Standalone)

If you want to use the supervisor without OpenClaw:

```bash
# Clone the repository
git clone https://github.com/shasankp000/OpenClawde-Dev.git
cd OpenClawde-Dev

# Run directly
python supervisor.py "Your task here"
```

## Configuration

The supervisor uses `config.json` for configuration. If it doesn't exist, a default configuration is created automatically.

### Default Configuration

```json
{
  "mode": "approve_after_plan",
  "project_path": "/mnt/gamedisk/Java_Projects/TideFall",
  "max_action_loops": 5,
  "forbidden_plan_keywords": [
    "delete entire",
    "rewrite whole",
    "rm -rf",
    "drop database"
  ]
}
```

### Configuration Options

- **mode**: Approval mode for the supervisor
  - `approve_after_plan`: Require approval after planning phase (default)
  - `auto`: Execute automatically without approval (use with caution)

- **project_path**: Path to the project directory where OpenCode will operate

- **max_action_loops**: Maximum number of exploration/action loops before proceeding to build

- **forbidden_plan_keywords**: List of keywords that will cause automatic plan rejection

## Usage

### Start a New Task

```bash
python supervisor.py "Your task description here"
```

Example:
```bash
python supervisor.py "Add a README file to the project"
```

### Check Current Status

```bash
python supervisor.py status
```

Output:
```
Task: Add a README file to the project
Status: awaiting_approval
Mode: approve_after_plan
Session ID: ses_abc123...

Planned Actions (2):
  1. explore
     - objective: Examine project structure
  2. edit
     - file: README.md
```

### Approve a Plan

Once a plan is awaiting approval, review the displayed actions and approve:

```bash
python supervisor.py approve
```

### Reject a Plan

If the plan is not acceptable:

```bash
python supervisor.py reject
```

## Workflow

### Approval Mode Workflow

1. **Planning Phase**: Supervisor calls the plan agent with your task
2. **Plan Extraction**: Extracts and parses all planned actions from agent output
3. **Validation**: Checks for forbidden keywords and executable actions
4. **Approval Signal**: Emits signal and displays plan for human review
5. **Wait**: Pauses until human approves or rejects
6. **Build Phase**: If approved, executes the plan with the build agent
7. **Completion**: Saves final state and build events

### Automatic Mode Workflow

1. **Planning Phase**: Supervisor calls the plan agent with your task
2. **Plan Extraction**: Extracts and parses all planned actions
3. **Validation**: Checks for forbidden keywords
4. **Build Phase**: Immediately proceeds to build agent
5. **Completion**: Saves final state and build events

## State Management

The supervisor maintains state in `state.json`:

```json
{
  "task": "Task description",
  "mode": "approve_after_plan",
  "status": "awaiting_approval",
  "session_id": "ses_abc123...",
  "actions": [
    {
      "name": "explore",
      "arguments": {
        "objective": "..."
      }
    }
  ],
  "plan": "Raw plan text",
  "build_events": []
}
```

### Status Values

- `planning`: Initial planning in progress
- `no_plan`: No executable plan was generated
- `plan_rejected`: Plan rejected by policy or user
- `awaiting_approval`: Waiting for human approval
- `exploring`: Executing exploration actions
- `building`: Build phase in progress
- `build_failed`: Build phase encountered an error
- `done`: Task completed successfully
- `rejected`: User rejected the plan

## Integration with OpenClaw

The supervisor emits special signals that can be detected by monitoring systems like OpenClaw:

```
🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_abc123...
```

These signals are printed to stdout and can be:
- Parsed by external monitoring tools
- Trigger notifications (email, Slack, etc.)
- Initiate approval workflows
- Log to centralized systems

## Safety Features

### Policy Enforcement

Plans containing forbidden keywords are automatically rejected:

```python
"forbidden_plan_keywords": [
  "delete entire",
  "rewrite whole", 
  "rm -rf",
  "drop database"
]
```

### Plan Validation

The supervisor validates that a real executable plan exists before proceeding. Plans that only delegate or contain no actions are rejected.

### Approval Gates

In `approve_after_plan` mode, all plans must be explicitly approved by a human before execution, providing a critical safety checkpoint.

## Error Handling

The supervisor includes comprehensive error handling:

- **Missing Session ID**: Aborts if session cannot be established
- **No Executable Plan**: Rejects tasks that generate no actionable plan
- **Build Failures**: Captures and logs build phase errors
- **State Persistence**: All errors are recorded in state.json

## Examples

### Example 1: Simple Code Change with Approval

```bash
# Start the task
$ python supervisor.py "Fix the typo in README.md"

[exec] opencode run --dir /path/to/project --agent plan ...
============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. edit
     - path: README.md
     - changes: Fix typo in line 42

============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_abc123...
⏸ Awaiting approval before build phase

# Review the plan, then approve
$ python supervisor.py approve

✅ Plan approved, proceeding to build phase...
[exec] opencode run --dir /path/to/project --agent build ...
✅ Task completed
```

### Example 2: Rejected Plan

```bash
$ python supervisor.py "Delete all test files"

[exec] opencode run --dir /path/to/project --agent plan ...
❌ Plan rejected by policy
```

### Example 3: No Plan Generated

```bash
$ python supervisor.py "Hello"

[exec] opencode run --dir /path/to/project --agent plan ...
❌ No executable plan generated
Plan text: ...
```

## Troubleshooting

### "No executable plan generated"

The plan agent didn't produce actionable steps. Try:
- Making your task more specific
- Breaking down complex tasks into smaller ones
- Checking that the project path is correct

### "Plan rejected by policy"

Your task contains forbidden keywords. Either:
- Rephrase your task description
- Modify `forbidden_plan_keywords` in config.json (carefully!)

### "No session ID found"

The OpenCode session failed to initialize. Check:
- OpenCode is properly installed (`opencode --version`)
- Project path exists and is accessible
- You have network connectivity (for API calls)

## OpenClaw Integration

When installed as an OpenClaw skill, you can use these commands:

```bash
# Start a new task
/dev run "Add logging to authentication module"

# Check status
/dev status

# Approve the current plan
/dev approve

# Reject the current plan
/dev reject
```

### Skill Commands

The OpenClaw skill provides four commands:

1. **`/dev run <task>`** - Start a new autonomous development task
2. **`/dev status`** - Show current supervisor status and planned actions
3. **`/dev approve`** - Approve the current plan and proceed to build phase
4. **`/dev reject`** - Reject the current plan and abort execution

### Example OpenClaw Workflow

```bash
# In OpenClaw terminal
> /dev run "Refactor the user authentication code"

[Supervisor output showing plan]
🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_abc123...

# Review the plan
> /dev status

# If acceptable, approve
> /dev approve

# Or reject if not acceptable
> /dev reject
```

## Advanced Usage

### Custom Approval Workflows

You can integrate the supervisor into custom workflows by:

1. Monitoring stdout for `SUPERVISOR_SIGNAL: APPROVAL_REQUIRED`
2. Parsing `state.json` for plan details
3. Implementing custom approval logic
4. Calling `python supervisor.py approve` or `reject` programmatically

### Continuous Integration

For CI/CD pipelines, use automatic mode:

```json
{
  "mode": "auto"
}
```

**Warning**: Only use auto mode in controlled environments with proper testing and rollback procedures.

## Architecture

```
supervisor.py
├── Configuration Management (config.json)
├── State Management (state.json)
├── OpenCode Integration
│   ├── Plan Agent
│   └── Build Agent
├── Event Processing
│   ├── NDJSON Parsing
│   ├── Session Extraction
│   └── Action Parsing
├── Policy Enforcement
├── Approval Gates
└── CLI Commands
```

## Skill Structure

This repository is structured as an OpenClaw skill:

```
OpenClawde/
├── supervisor.py          # Main supervisor logic
├── skill.json            # OpenClaw skill manifest
├── run.sh               # Skill execution wrapper
├── install.sh           # Installation script
├── config.json          # Configuration file
├── state.json           # Runtime state (auto-generated)
├── README.md            # This file
└── WORKFLOW_EXAMPLE.md  # Detailed workflow examples
```

### Skill Manifest (`skill.json`)

```json
{
  "name": "dev",
  "description": "Autonomous development supervisor (OpenCode-based)",
  "commands": {
    "run": {
      "description": "Start a new autonomous development task",
      "args": ["task"]
    },
    "status": {
      "description": "Show current supervisor status"
    },
    "approve": {
      "description": "Approve the current plan and continue"
    },
    "reject": {
      "description": "Reject the current plan"
    }
  }
}
```

## Environment Variables

- **`OPENCLAW_SUPERVISOR_HOME`** - Path to the supervisor installation directory
  - Set automatically by `install.sh`
  - Required for the OpenClaw skill to function
  - Example: `~/.local/share/openclaw/opencode-supervisor`

## Uninstallation

To remove the supervisor skill:

```bash
# Remove the skill directory
rm -rf ~/.openclaw/skills/dev-supervisor

# Remove the supervisor installation
rm -rf ~/.local/share/openclaw/opencode-supervisor

# Remove environment variable from your profile
# Edit ~/.bashrc or ~/.zshrc and remove the OPENCLAW_SUPERVISOR_HOME line
```

## Contributing

Contributions welcome! Areas for improvement:

- Additional approval modes (approval after each action, etc.)
- More sophisticated policy rules (regex, AST analysis)
- Integration with notification systems
- Web UI for approval workflows
- Enhanced logging and observability
- Additional OpenClaw skill commands

## License

See project root for license information.
