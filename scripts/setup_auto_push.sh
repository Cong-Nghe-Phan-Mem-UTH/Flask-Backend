#!/bin/bash
# Script to setup auto-push git hook

GIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.git"
HOOK_FILE="$GIT_DIR/hooks/post-commit"

if [ ! -d "$GIT_DIR" ]; then
    echo "❌ Git repository not found. Please run 'git init' first."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$GIT_DIR/hooks"

# Create post-commit hook
cat > "$HOOK_FILE" << 'EOF'
#!/bin/bash
# Auto push after commit

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Push to remote
echo "🚀 Auto pushing to origin/$BRANCH..."
git push origin "$BRANCH"

# If push failed, show error but don't block
if [ $? -ne 0 ]; then
    echo "⚠️  Push failed. You may need to push manually."
    exit 0  # Don't fail the commit
fi

echo "✅ Successfully pushed to origin/$BRANCH"
EOF

# Make it executable
chmod +x "$HOOK_FILE"

echo "✅ Auto-push hook installed successfully!"
echo "📝 Now every time you commit, it will automatically push to GitHub"
echo ""
echo "To disable auto-push, run:"
echo "  rm $HOOK_FILE"

