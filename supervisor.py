import json
import subprocess
import sys
from pathlib import Path

CONFIG_FILE = "config.json"
STATE_FILE = "state.json"


# ---------------------------
# Utilities
# ---------------------------


def load_config():
    default_config = {
        "mode": "approve_after_plan",
        "project_path": "/mnt/gamedisk/Java_Projects/TideFall",
        "max_action_loops": 5,
        "forbidden_plan_keywords": [
            "delete entire",
            "rewrite whole",
            "rm -rf",
            "drop database",
        ],
    }

    config_path = Path(CONFIG_FILE)

    # Case 1: file does not exist → create with defaults
    if not config_path.exists():
        config_path.write_text(json.dumps(default_config, indent=2))
        return default_config

    raw = config_path.read_text().strip()

    # Case 2: file exists but is empty → overwrite with defaults
    if not raw:
        config_path.write_text(json.dumps(default_config, indent=2))
        return default_config

    # Case 3: valid JSON
    return json.loads(raw)


def save_state(state):
    Path(STATE_FILE).write_text(json.dumps(state, indent=2))


def load_state():
    if Path(STATE_FILE).exists():
        return json.loads(Path(STATE_FILE).read_text())
    return {}


def run(cmd):
    print(f"[exec] {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = f"Command failed with return code {result.returncode}\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}"
        raise RuntimeError(error_msg)
    return result.stdout


def parse_ndjson(output: str):
    events = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        events.append(json.loads(line))
    return events


# ---------------------------
# OpenCode interaction
# ---------------------------


def run_plan(task, project_path, session_id=None, title=None):
    cmd = [
        "opencode",
        "run",
        "--dir",
        project_path,
        "--agent",
        "plan",
        "--format",
        "json",
    ]

    if session_id:
        cmd.extend(["--session", session_id, "--continue"])
    elif title:
        cmd.extend(["--title", title])

    cmd.append(task)

    raw = run(cmd)
    return parse_ndjson(raw)


def run_build(project_path, session_id, message="Proceed with executing the plan"):
    cmd = [
        "opencode",
        "run",
        "--dir",
        project_path,
        "--agent",
        "build",
        "--session",
        session_id,
        "--continue",
        "--format",
        "json",
        message,
    ]

    raw = run(cmd)
    return parse_ndjson(raw)


def run_followup_plan(project_path, session_id, message):
    cmd = [
        "opencode",
        "run",
        "--dir",
        project_path,
        "--agent",
        "plan",
        "--session",
        session_id,
        "--continue",
        "--format",
        "json",
        message,
    ]

    raw = run(cmd)
    return parse_ndjson(raw)


# ---------------------------
# Event extraction
# ---------------------------


def extract_session_and_action(events):
    session_id = None
    action = None
    text = []
    actions = []

    for ev in events:
        ev_type = ev.get("type")

        # Extract session ID from sessionID field (camelCase)
        if not session_id and "sessionID" in ev:
            session_id = ev["sessionID"]

        # Session creation
        if ev_type == "session.created":
            session_id = ev["session"]["id"]

        # Some events carry session id implicitly
        if not session_id:
            meta = ev.get("session") or ev.get("context")
            if isinstance(meta, dict):
                session_id = meta.get("id") or meta.get("session_id")

        # Agent action
        if ev_type == "agent.action":
            action = ev.get("action")

        # Extract text and parse JSON actions
        if ev_type == "text":
            part = ev.get("part", {})
            content = part.get("text", "")
            if content:
                text.append(content)
                # Try to parse JSON actions from text - handle multiple JSON blocks
                # Split by markdown code fences to find all JSON blocks
                blocks = content.split("```")
                for block in blocks:
                    block = block.strip()
                    # Skip empty blocks
                    if not block:
                        continue
                    # Remove "json" language identifier if present
                    if block.startswith("json"):
                        block = block[4:].strip()

                    # Try to parse as JSON
                    try:
                        parsed = json.loads(block)
                        if isinstance(parsed, dict) and "name" in parsed:
                            actions.append(parsed)
                    except (json.JSONDecodeError, ValueError):
                        # Not valid JSON, continue
                        pass

        # Human-readable text
        if ev_type == "agent.message":
            content = ev.get("content")
            if content:
                text.append(content)

    return session_id, action, "\n".join(text), actions


# ---------------------------
# Policy checks
# ---------------------------


def approve_plan_text(plan_text, forbidden):
    lowered = plan_text.lower()
    return not any(word in lowered for word in forbidden)


def has_executable_plan(actions):
    """Check if there are any executable actions in the plan"""
    return len(actions) > 0


def format_plan_for_approval(actions, plan_text):
    """Format the plan in a human-readable way for approval"""
    lines = []
    lines.append("=" * 60)
    lines.append("PLAN REQUIRING APPROVAL")
    lines.append("=" * 60)

    if actions:
        lines.append("\nPlanned Actions:")
        for idx, action in enumerate(actions, 1):
            action_name = action.get("name", "unknown")
            action_args = action.get("arguments", {})
            lines.append(f"  {idx}. {action_name}")
            if action_args:
                for key, value in action_args.items():
                    lines.append(f"     - {key}: {value}")

    if plan_text and plan_text.strip():
        lines.append("\nPlan Details:")
        lines.append(plan_text)

    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------
# Action handlers
# ---------------------------


def handle_explore(action_args, project_path, session_id):
    search_task = action_args["search_task"]
    depth = action_args.get("depth", "full")

    message = f"{search_task} (depth: {depth})"
    return run_followup_plan(project_path, session_id, message)


# ---------------------------
# Supervisor core
# ---------------------------


def supervise(task):
    config = load_config()
    project_path = config["project_path"]
    mode = config["mode"]
    max_loops = config.get("max_action_loops", 5)
    forbidden = config.get("forbidden_plan_keywords", [])

    state = {"task": task, "mode": mode, "status": "planning"}
    save_state(state)

    # Initial plan
    events = run_plan(task, project_path, title=task)
    session_id, action, plan_text, actions = extract_session_and_action(events)

    state["session_id"] = session_id
    state["plan"] = plan_text
    state["actions"] = actions
    save_state(state)

    # Check if we have an executable plan
    if not has_executable_plan(actions):
        state["status"] = "no_plan"
        save_state(state)
        print("❌ No executable plan generated")
        print(f"Plan text: {plan_text}")
        return

    if not approve_plan_text(plan_text, forbidden):
        state["status"] = "plan_rejected"
        save_state(state)
        print("❌ Plan rejected by policy")
        return

    loops = 0

    # Execute actions (explore, etc.)
    while action and loops < max_loops:
        loops += 1

        if action["name"] == "explore":
            state["status"] = "exploring"
            save_state(state)

            events = handle_explore(action["arguments"], project_path, session_id)

            _, action, plan_text, new_actions = extract_session_and_action(events)
            actions.extend(new_actions)
            state["plan"] = plan_text
            state["actions"] = actions
            save_state(state)

            # Stop here if approval mode
            if mode == "approve_after_plan":
                state["status"] = "awaiting_approval"
                save_state(state)

                # Emit approval signal
                approval_text = format_plan_for_approval(actions, plan_text)
                print(approval_text)
                print("\n🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED")
                print(f"🔔 SESSION_ID: {session_id}")
                print("⏸ Awaiting approval after exploration")
                return
        else:
            break

    # Check if we need approval before building
    if mode == "approve_after_plan":
        state["status"] = "awaiting_approval"
        save_state(state)

        # Emit approval signal
        approval_text = format_plan_for_approval(actions, plan_text)
        print(approval_text)
        print("\n🔔 SUPERVISOR_SIGNAL: APPROVAL_REQUIRED")
        print(f"🔔 SESSION_ID: {session_id}")
        print("⏸ Awaiting approval before build phase")
        return

    # Build phase
    state["status"] = "building"
    save_state(state)

    if not session_id:
        raise RuntimeError(
            "No session_id detected after planning. Cannot continue to build safely."
        )

    build_events = run_build(project_path, session_id)
    state["build_events"] = build_events
    state["status"] = "done"
    save_state(state)

    print("✅ Task completed")


def approve_and_continue():
    """Approve the plan and continue to build phase"""
    state = load_state()

    if not state:
        print("❌ No state found. Please run a task first.")
        return

    if state.get("status") != "awaiting_approval":
        print(f"❌ Current status is '{state.get('status')}', not awaiting approval")
        return

    session_id = state.get("session_id")
    if not session_id:
        print("❌ No session ID found in state")
        return

    config = load_config()
    project_path = config["project_path"]

    print("✅ Plan approved, proceeding to build phase...")

    # Build phase
    state["status"] = "building"
    save_state(state)

    try:
        build_events = run_build(project_path, session_id)
        state["build_events"] = build_events
        state["status"] = "done"
        save_state(state)
        print("✅ Task completed")
    except Exception as e:
        state["status"] = "build_failed"
        state["error"] = str(e)
        save_state(state)
        print(f"❌ Build failed: {e}")
        raise


def reject_plan():
    """Reject the plan and abort"""
    state = load_state()

    if not state:
        print("❌ No state found. Please run a task first.")
        return

    if state.get("status") != "awaiting_approval":
        print(f"❌ Current status is '{state.get('status')}', not awaiting approval")
        return

    state["status"] = "rejected"
    save_state(state)
    print("❌ Plan rejected by user")


def show_status():
    """Show current supervisor status"""
    state = load_state()

    if not state:
        print("No active task")
        return

    print(f"Task: {state.get('task')}")
    print(f"Status: {state.get('status')}")
    print(f"Mode: {state.get('mode')}")
    print(f"Session ID: {state.get('session_id')}")

    actions = state.get("actions", [])
    if actions:
        print(f"\nPlanned Actions ({len(actions)}):")
        for idx, action in enumerate(actions, 1):
            print(f"  {idx}. {action.get('name')}")
            action_args = action.get("arguments", {})
            if action_args:
                for key, value in action_args.items():
                    value_str = str(value)
                    if len(value_str) > 60:
                        value_str = value_str[:57] + "..."
                    print(f"     - {key}: {value_str}")


# ---------------------------
# Entry point
# ---------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python supervisor.py <task>          - Start a new task")
        print("  python supervisor.py approve         - Approve the current plan")
        print("  python supervisor.py reject          - Reject the current plan")
        print("  python supervisor.py status          - Show current status")
        sys.exit(1)

    command = sys.argv[1]

    if command == "approve":
        approve_and_continue()
    elif command == "reject":
        reject_plan()
    elif command == "status":
        show_status()
    else:
        # Treat as task
        task = " ".join(sys.argv[1:])
        supervise(task)
