#!/usr/bin/env bash
set -euo pipefail

# ===== CONFIG (edit later) =====
REPO_URL="https://github.com/shasankp000/OpenClawde-Dev.git"
INSTALL_ROOT="$HOME/.local/share/openclaw"
SUPERVISOR_DIR="$INSTALL_ROOT/opencode-supervisor"
SKILL_DIR="$HOME/.openclaw/skills/dev-supervisor"

# ===== PRECHECKS =====
command -v git >/dev/null || { echo "❌ git not found"; exit 1; }
command -v python >/dev/null || { echo "❌ python not found"; exit 1; }

echo "🔧 Installing OpenClaw Dev Supervisor..."

# ===== CLONE OR UPDATE =====
mkdir -p "$INSTALL_ROOT"

if [[ -d "$SUPERVISOR_DIR/.git" ]]; then
  echo "🔄 Updating existing supervisor repo..."
  git -C "$SUPERVISOR_DIR" pull
else
  echo "📥 Cloning supervisor repo..."
  git clone "$REPO_URL" "$SUPERVISOR_DIR"
fi

# ===== OPTIONAL: PYTHON DEPS =====
if [[ -f "$SUPERVISOR_DIR/requirements.txt" ]]; then
  echo "📦 Installing Python dependencies..."
  python -m pip install --user -r "$SUPERVISOR_DIR/requirements.txt"
fi

# ===== INSTALL SKILL =====
echo "🧩 Installing OpenClaw skill..."
mkdir -p "$SKILL_DIR"
cp "$SUPERVISOR_DIR/skill.json" "$SUPERVISOR_DIR/run.sh" "$SKILL_DIR"
chmod +x "$SKILL_DIR/run.sh"

# ===== ENV VAR SETUP =====
PROFILE_FILE="$HOME/.bashrc"

if [[ -n "${ZSH_VERSION:-}" ]]; then
  PROFILE_FILE="$HOME/.zshrc"
fi

if ! grep -q "OPENCLAW_SUPERVISOR_HOME" "$PROFILE_FILE"; then
  echo "🌱 Setting OPENCLAW_SUPERVISOR_HOME in $PROFILE_FILE"
  echo "" >> "$PROFILE_FILE"
  echo "export OPENCLAW_SUPERVISOR_HOME=\"$SUPERVISOR_DIR\"" >> "$PROFILE_FILE"
fi

# ===== DONE =====
echo ""
echo "✅ Installation complete."
echo ""
echo "➡ Restart your shell OR run:"
echo "   export OPENCLAW_SUPERVISOR_HOME=\"$SUPERVISOR_DIR\""
echo ""
echo "➡ Then restart OpenClaw:"
echo "   openclaw gateway restart"
echo ""
echo "➡ Try:"
echo "   /dev status"
