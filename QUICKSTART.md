# OpenClawde Supervisor - Quick Start Guide

Get started with the OpenClawde Supervisor in 5 minutes!

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/shasankp000/OpenClawde-Dev.git
cd OpenClawde-Dev

# 2. Run the installer
bash install.sh

# 3. Restart your shell
source ~/.bashrc  # or source ~/.zshrc for zsh

# 4. Restart OpenClaw
openclaw gateway restart
```

## First Task

```bash
# In OpenClaw terminal, run:
/dev run "Add a README file to explain what this project does"
```

You'll see:
```
============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. explore
     - objective: Examine project structure
  2. create_file
     - path: README.md
     - content: Project documentation

============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_abc123...
⏸ Awaiting approval before build phase
```

## Review and Approve

```bash
# Check the plan details
/dev status

# If it looks good, approve
/dev approve

# If not, reject
/dev reject
```

## That's It!

The supervisor will:
- ✅ Plan your task using OpenCode's plan agent
- ✅ Show you what it will do
- ✅ Wait for your approval
- ✅ Execute with the build agent
- ✅ Keep you informed every step

## Common Commands

```bash
/dev run "task description"    # Start a new task
/dev status                    # Check current status
/dev approve                   # Approve and execute
/dev reject                    # Reject and abort
```

## Configuration

Edit `~/.local/share/openclaw/opencode-supervisor/config.json`:

```json
{
  "mode": "approve_after_plan",
  "project_path": "/path/to/your/project",
  "max_action_loops": 5,
  "forbidden_plan_keywords": [
    "delete entire",
    "rewrite whole",
    "rm -rf",
    "drop database"
  ]
}
```

## Examples

### Add a feature
```bash
/dev run "Add authentication middleware to all API routes"
```

### Fix a bug
```bash
/dev run "Fix the null pointer exception in UserService.java line 42"
```

### Refactor code
```bash
/dev run "Refactor the database connection logic to use connection pooling"
```

### Add documentation
```bash
/dev run "Add JSDoc comments to all public methods in AuthController"
```

## Tips

1. **Be specific** - More details = better plans
2. **Review carefully** - Always check the plan before approving
3. **Use status often** - Check what's happening anytime with `/dev status`
4. **Start small** - Try simple tasks first to get comfortable

## Troubleshooting

### "OPENCLAW_SUPERVISOR_HOME is not set"
Run `bash install.sh` again and restart your shell.

### "No executable plan generated"
Make your task more specific and actionable.

### "Plan rejected by policy"
Your task contains a forbidden keyword. Rephrase or adjust config.json.

## Next Steps

- Read [README.md](README.md) for full documentation
- See [WORKFLOW_EXAMPLE.md](WORKFLOW_EXAMPLE.md) for detailed examples
- Configure `config.json` for your project
- Set up notifications for approval requests

## Help

- Check status: `/dev status`
- View logs: `cat ~/.local/share/openclaw/opencode-supervisor/state.json`
- Report issues: https://github.com/shasankp000/OpenClawde-Dev/issues

Happy coding! 🚀