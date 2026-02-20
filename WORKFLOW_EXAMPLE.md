# OpenClawde Supervisor Workflow Examples

This document provides real-world examples of using the OpenClawde Supervisor to manage OpenCode agent tasks with human oversight.

## Table of Contents

1. [Basic Workflow](#basic-workflow)
2. [OpenClaw Skill Usage](#openclaw-skill-usage)
3. [Complete Example Session](#complete-example-session)
4. [Integration with OpenClaw](#integration-with-openclaw)
5. [Handling Edge Cases](#handling-edge-cases)

---

## Basic Workflow

### Step 1: Start a Task

```bash
python supervisor.py "Your task description"
```

The supervisor will:
1. Call the OpenCode plan agent
2. Parse the generated plan
3. Extract all planned actions
4. Display the plan for approval
5. Emit signals for external systems

### Step 2: Review the Plan

The supervisor displays:
- All planned actions with arguments
- Session ID for tracking
- Clear approval signals

Example output:
```
============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. explore
     - objective: Search for configuration files
  2. edit
     - file: config.yaml
     - changes: Update API endpoint

Plan Details:
[Full JSON plan here]
============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_abc123xyz
⏸ Awaiting approval before build phase
```

### Step 3: Approve or Reject

**To approve:**
```bash
python supervisor.py approve
```

**To reject:**
```bash
python supervisor.py reject
```

**To check status:**
```bash
python supervisor.py status
```

---

## OpenClaw Skill Usage

When installed as an OpenClaw skill (via `install.sh`), you can interact with the supervisor through OpenClaw commands.

### Installation

```bash
# Clone and install
git clone https://github.com/shasankp000/OpenClawde-Dev.git
cd OpenClawde-Dev
bash install.sh

# Restart your shell
source ~/.bashrc  # or ~/.zshrc

# Restart OpenClaw
openclaw gateway restart
```

### Available Commands

```bash
/dev run <task>    # Start a new task
/dev status        # Check current status
/dev approve       # Approve the plan
/dev reject        # Reject the plan
```

### Example: Quick Task Execution

```bash
# In OpenClaw terminal
> /dev run "Add error handling to the API endpoints"

[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent plan ...
============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. explore
     - objective: Identify all API endpoint files
  2. edit
     - file: ApiController.java
     - changes: Add try-catch blocks and error responses

Plan Details:
...
============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_xyz789
⏸ Awaiting approval before build phase

# Check details
> /dev status

Task: Add error handling to the API endpoints
Status: awaiting_approval
Mode: approve_after_plan
Session ID: ses_xyz789

Planned Actions (2):
  1. explore
     - objective: Identify all API endpoint files
  2. edit
     - file: ApiController.java
     - changes: Add try-catch blocks and error responses

# Approve and execute
> /dev approve

✅ Plan approved, proceeding to build phase...
[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent build ...
✅ Task completed
```

### Example: Rejecting a Plan

```bash
> /dev run "Delete all test files and start fresh"

[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent plan ...
❌ Plan rejected by policy

# The supervisor automatically rejected due to "delete" keyword
```

### Example: Multi-Step Approval

```bash
> /dev run "Refactor the authentication system"

============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. explore
     - query: Analyze authentication implementation
  2. explore
     - query: Identify authentication dependencies
  3. refactor
     - target: AuthService.java

...
============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_abc456

# Review carefully
> /dev status

# After reviewing, approve
> /dev approve

✅ Plan approved, proceeding to build phase...
✅ Task completed
```

### OpenClaw + Notifications

You can set up OpenClaw to notify you when approval is needed:

```bash
# In your OpenClaw configuration or monitoring script
# Monitor for SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
# Then send notification via your preferred method

# Example: Discord webhook notification
curl -X POST "YOUR_DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"🔔 Dev Supervisor needs approval for session ses_xyz789\"}"
```

---

## Complete Example Session

### Scenario: Adding Documentation

**Goal:** Add a CONTRIBUTING.md file to a Java project

#### 1. Initialize the Task

```bash
$ cd /path/to/OpenClawde
$ python supervisor.py "Create a CONTRIBUTING.md file with guidelines for contributors"
```

#### 2. Supervisor Output

```
[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent plan --format json --title Create a CONTRIBUTING.md file with guidelines for contributors Create a CONTRIBUTING.md file with guidelines for contributors

============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. explore
     - objective: Examine existing project structure and documentation
  2. write_file
     - path: CONTRIBUTING.md
     - content: Contribution guidelines including code style, PR process, testing requirements

Plan Details:
{
  "name": "explore",
  "arguments": {
    "objective": "Examine existing project structure and documentation"
  }
}

{
  "name": "write_file",
  "arguments": {
    "path": "CONTRIBUTING.md",
    "content": "Contribution guidelines..."
  }
}
============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
🔔 SESSION_ID: ses_a1b2c3d4e5f6g7h8i9j0
⏸ Awaiting approval before build phase
```

#### 3. Check State

```bash
$ python supervisor.py status
```

Output:
```
Task: Create a CONTRIBUTING.md file with guidelines for contributors
Status: awaiting_approval
Mode: approve_after_plan
Session ID: ses_a1b2c3d4e5f6g7h8i9j0

Planned Actions (2):
  1. explore
     - objective: Examine existing project structure and documentation
  2. write_file
     - path: CONTRIBUTING.md
     - content: Contribution guidelines including code style, PR proc...
```

#### 4. Approve and Execute

```bash
$ python supervisor.py approve
```

Output:
```
✅ Plan approved, proceeding to build phase...
[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent build --session ses_a1b2c3d4e5f6g7h8i9j0 --continue --format json Proceed with executing the plan
✅ Task completed
```

#### 5. Verify State

```bash
$ python supervisor.py status
```

Output:
```
Task: Create a CONTRIBUTING.md file with guidelines for contributors
Status: done
Mode: approve_after_plan
Session ID: ses_a1b2c3d4e5f6g7h8i9j0

Planned Actions (2):
  1. explore
     - objective: Examine existing project structure and documentation
  2. write_file
     - path: CONTRIBUTING.md
     - content: Contribution guidelines including code style, PR proc...
```

---

## Integration with OpenClaw

OpenClaw can monitor the supervisor and notify you when approval is needed.

### OpenClaw Monitoring Script

```python
import subprocess
import time
import json
import os
from pathlib import Path

# Use the environment variable set by install.sh
SUPERVISOR_DIR = os.environ.get("OPENCLAW_SUPERVISOR_HOME", "/path/to/OpenClawde")
STATE_FILE = f"{SUPERVISOR_DIR}/state.json"

def monitor_supervisor():
    """Monitor supervisor state and send notifications"""
    last_status = None
    
    while True:
        if not Path(STATE_FILE).exists():
            time.sleep(5)
            continue
            
        with open(STATE_FILE) as f:
            state = json.load(f)
        
        current_status = state.get("status")
        
        # Detect status change to awaiting_approval
        if current_status == "awaiting_approval" and current_status != last_status:
            session_id = state.get("session_id")
            task = state.get("task")
            actions = state.get("actions", [])
            
            # Send notification
            notify_approval_required(
                task=task,
                session_id=session_id,
                action_count=len(actions)
            )
        
        last_status = current_status
        time.sleep(5)

def notify_approval_required(task, session_id, action_count):
    """Send notification that approval is required"""
    message = f"""
    🔔 OpenClawde Supervisor: Approval Required
    
    Task: {task}
    Session: {session_id}
    Actions: {action_count}
    
    Review: python supervisor.py status
    Approve: python supervisor.py approve
    Reject: python supervisor.py reject
    """
    
    # Send via your preferred method:
    # - Email
    # - Slack webhook
    # - Discord webhook
    # - Desktop notification
    # - SMS
    
    print(message)
    # Example: send_slack_notification(message)
    # Example: send_email(message)

if __name__ == "__main__":
    monitor_supervisor()
```

### Parsing Supervisor Signals

You can also parse stdout directly:

```python
import subprocess
import re
import os

def run_supervisor_task(task):
    """Run supervisor and detect approval requirement"""
    supervisor_dir = os.environ.get("OPENCLAW_SUPERVISOR_HOME")
    
    process = subprocess.Popen(
        ["python", f"{supervisor_dir}/supervisor.py", task],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=supervisor_dir
    )
    
    session_id = None
    needs_approval = False
    
    for line in process.stdout:
        print(line, end='')
        
        # Detect approval signal
        if "SUPERVISOR_SIGNAL: APPROVAL_REQUIRED" in line:
            needs_approval = True
        
        # Extract session ID
        match = re.search(r'SESSION_ID: (ses_[a-zA-Z0-9]+)', line)
        if match:
            session_id = match.group(1)
    
    process.wait()
    
    if needs_approval:
        # Notify user
        notify_user(f"Approval needed for session {session_id}")
        return session_id
    
    return None

### Using OpenClaw Skill Commands

```python
import subprocess
import os

def execute_dev_command(command, *args):
    """Execute /dev skill commands programmatically"""
    supervisor_dir = os.environ.get("OPENCLAW_SUPERVISOR_HOME")
    
    # Map skill commands to supervisor commands
    cmd_map = {
        "run": ["python", "supervisor.py"] + list(args),
        "status": ["python", "supervisor.py", "status"],
        "approve": ["python", "supervisor.py", "approve"],
        "reject": ["python", "supervisor.py", "reject"]
    }
    
    if command not in cmd_map:
        raise ValueError(f"Unknown command: {command}")
    
    result = subprocess.run(
        cmd_map[command],
        cwd=supervisor_dir,
        capture_output=True,
        text=True
    )
    
    return result.stdout, result.returncode

# Usage examples:
# Start a task
output, code = execute_dev_command("run", "Add unit tests")

# Check status
output, code = execute_dev_command("status")

# Approve
output, code = execute_dev_command("approve")
```

---

## Handling Edge Cases

### Case 1: No Executable Plan

Sometimes the plan agent doesn't generate actionable steps.

```bash
$ python supervisor.py "Hello"
```

Output:
```
[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent plan ...
❌ No executable plan generated
Plan text: {"name": "skill", "arguments": {"name": "plan"}}
```

**Solution:** Make your task more specific and actionable.

### Case 2: Policy Rejection

Plans with forbidden keywords are auto-rejected.

```bash
$ python supervisor.py "Delete entire database and start fresh"
```

Output:
```
[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent plan ...
❌ Plan rejected by policy
```

**Solution:** Rephrase your task or adjust forbidden keywords in config.json.

### Case 3: Build Failure

The build phase might encounter errors.

```bash
$ python supervisor.py approve
```

Output:
```
✅ Plan approved, proceeding to build phase...
[exec] opencode run --dir /mnt/gamedisk/Java_Projects/TideFall --agent build ...
❌ Build failed: RuntimeError: Command failed with return code 1
STDERR: Error message here
STDOUT: ...
```

**Check state:**
```bash
$ python supervisor.py status
```

Output:
```
Task: ...
Status: build_failed
Mode: approve_after_plan
Session ID: ses_...
```

### Case 4: Recovering from Rejected State

If you rejected a plan but want to retry:

```bash
# Check current state
$ python supervisor.py status

Task: Add feature X
Status: rejected
...

# Start a new task (same or different)
$ python supervisor.py "Add feature X with more details"
```

### Case 5: Exploring Action Loops

Some tasks trigger multiple exploration cycles:

```bash
$ python supervisor.py "Refactor the authentication module"
```

The supervisor may:
1. Run initial plan (explore action)
2. Execute explore action to gather info
3. Update plan based on findings
4. Request approval again before build

You'll see:
```
============================================================
PLAN REQUIRING APPROVAL
============================================================

Planned Actions:
  1. explore
     - objective: Analyze authentication code structure
  2. explore
     - objective: Identify all authentication-related files
  3. refactor
     - target: AuthService.java
     - changes: ...
============================================================

🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED
...
```

---

## Best Practices

### 1. Be Specific in Task Descriptions

**❌ Bad:**
```bash
/dev run "Fix the code"
```

**✅ Good:**
```bash
/dev run "Fix the NullPointerException in UserService.java line 42 by adding null check"
```

Or standalone:
```bash
python supervisor.py "Fix the NullPointerException in UserService.java line 42 by adding null check"
```

### 2. Review Plans Carefully

Always check:
- Which files will be modified
- What changes are planned
- Any potentially destructive operations
- Side effects (tests, dependencies, etc.)

### 3. Use Status Command Frequently

**With OpenClaw:**
```bash
# Before approving
/dev status

# Check what will happen
cat ~/.local/share/openclaw/opencode-supervisor/state.json | jq .actions

# Then approve
/dev approve
```

**Standalone:**
```bash
# Before approving
python supervisor.py status

# Check what will happen
cat state.json | jq .actions

# Then approve
python supervisor.py approve
```

### 4. Configure Forbidden Keywords

Customize for your project:

```json
{
  "forbidden_plan_keywords": [
    "delete entire",
    "drop database",
    "rm -rf",
    "rewrite whole",
    "remove all",
    "delete production"
  ]
}
```

### 5. Monitor State Files

Keep an eye on state.json for:
- Unexpected status changes
- Error messages
- Session continuity

### 6. Test in Safe Environments First

Before using on production code:
1. Test on a development branch
2. Verify rollback procedures
3. Set up proper backup strategies
4. Use version control (git)

---

## Troubleshooting Guide

### Issue: "No state found"

**Cause:** No task has been run yet or state.json is missing.

**Solution:**
```bash
# With OpenClaw
/dev run "Some task"

# Or standalone
python supervisor.py "Some task"
```

### Issue: "Current status is 'done', not awaiting approval"

**Cause:** Trying to approve/reject a completed task.

**Solution:** Start a new task.

### Issue: Session ID not found

**Cause:** OpenCode failed to create a session.

**Solution:**
1. Check OpenCode installation: `opencode --version`
2. Verify project path in config.json
3. Check network connectivity
4. Review OpenCode logs

### Issue: Empty plan text

**Cause:** Plan agent delegated instead of creating concrete actions.

**Solution:** The supervisor now extracts actions from JSON blocks, but if this persists:
1. Make task more specific
2. Provide more context in task description
3. Check if project path is correct

---

## Configuration Reference

### Minimal Configuration

```json
{
  "mode": "approve_after_plan",
  "project_path": "/path/to/your/project"
}
```

### Full Configuration

```json
{
  "mode": "approve_after_plan",
  "project_path": "/path/to/your/project",
  "max_action_loops": 5,
  "forbidden_plan_keywords": [
    "delete entire",
    "rewrite whole",
    "rm -rf",
    "drop database",
    "remove all",
    "delete production"
  ]
}
```

### Auto Mode (No Approval)

```json
{
  "mode": "auto",
  "project_path": "/path/to/your/project",
  "forbidden_plan_keywords": [
    "delete entire",
    "drop database"
  ]
}
```

**⚠️ Warning:** Auto mode bypasses human approval. Use only in controlled environments.

---

## Summary

The OpenClawde Supervisor provides:
- ✅ Safe execution with approval gates
- ✅ Clear plan visibility before execution
- ✅ Integration points for external systems (OpenClaw)
- ✅ Comprehensive state tracking
- ✅ Policy enforcement
- ✅ Session continuity
- ✅ OpenClaw skill interface (`/dev` commands)
- ✅ Standalone CLI for direct usage

### Quick Reference

**OpenClaw Skill (Recommended):**
```bash
/dev run <task>      # Start task
/dev status          # Check status
/dev approve         # Approve plan
/dev reject          # Reject plan
```

**Standalone:**
```bash
python supervisor.py <task>     # Start task
python supervisor.py status     # Check status
python supervisor.py approve    # Approve plan
python supervisor.py reject     # Reject plan
```

For more information, see [README.md](README.md).