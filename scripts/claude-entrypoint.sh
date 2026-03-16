#!/bin/bash
set -e

# Get user info from environment or defaults
USER_ID=${CLAUDE_USER_ID:-1000}
GROUP_ID=${CLAUDE_GROUP_ID:-1000}
USERNAME=${CLAUDE_USERNAME:-claude}

# If using default user, just ensure permissions and run
if [ "$USER_ID" = "1000" ] && [ "$GROUP_ID" = "1000" ] && [ "$USERNAME" = "claude" ]; then
    chown -R claude:claude /workspace
    exec sudo -u claude env PATH="/home/claude/.local/bin:$PATH" "$@"
fi

# For custom users, use a unique username pattern
RUNTIME_USERNAME="user_${USER_ID}"

# Create group if it doesn't exist
if ! getent group "$GROUP_ID" >/dev/null 2>&1; then
    groupadd -g "$GROUP_ID" "$RUNTIME_USERNAME"
fi

# Create user if it doesn't exist
if ! getent passwd "$USER_ID" >/dev/null 2>&1; then
    # Handle macOS UIDs that are outside typical Linux range
    if [ "$USER_ID" -lt 1000 ] || [ "$USER_ID" -gt 60000 ]; then
        useradd -u "$USER_ID" -g "$GROUP_ID" -m -s /bin/bash "$RUNTIME_USERNAME" --badname 2>/dev/null || \
        useradd -u "$USER_ID" -g "$GROUP_ID" -m -s /bin/bash "$RUNTIME_USERNAME" 2>/dev/null || true
    else
        useradd -u "$USER_ID" -g "$GROUP_ID" -m -s /bin/bash "$RUNTIME_USERNAME"
    fi
fi

# Get the actual username for this user ID
ACTUAL_USER=$(getent passwd "$USER_ID" | cut -d: -f1)

# Ensure user has sudo access
usermod -aG sudo "$ACTUAL_USER" 2>/dev/null || true
echo "$ACTUAL_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy mise and claude from default install to new user
USER_HOME=$(getent passwd "$USER_ID" | cut -d: -f6)
mkdir -p "$USER_HOME/.local/bin"
cp /home/claude/.local/bin/mise "$USER_HOME/.local/bin/"
cp /home/claude/.local/bin/claude "$USER_HOME/.local/bin/"

# Create claude config directory if it doesn't exist
mkdir -p "$USER_HOME/.claude"
# Copy existing claude config if available and not already present
if [ -d "/home/claude/.claude" ] && [ ! -f "$USER_HOME/.claude/settings.json" ]; then
    cp -r /home/claude/.claude/* "$USER_HOME/.claude/" 2>/dev/null || true
fi

# Setup mise directories with correct ownership
mkdir -p "$USER_HOME/.local/share/mise"
mkdir -p "$USER_HOME/.config/mise"
mkdir -p "$USER_HOME/.cache/mise"

# Ensure workspace is owned by the user (suppress errors for files we can't change)
chown -R "$ACTUAL_USER":"$GROUP_ID" /workspace 2>/dev/null || true
chown -R "$ACTUAL_USER":"$GROUP_ID" "$USER_HOME" 2>/dev/null || true

mise trust --quiet --all
mise install --yes --quiet

# Switch to the user for execution with proper PATH
exec sudo -u "$ACTUAL_USER" env PATH="$USER_HOME/.local/bin:$PATH" "$@"
