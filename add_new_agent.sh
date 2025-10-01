#!/bin/bash
# Script to add a new agent to the test suite

set -e

if [ -z "$1" ]; then
    echo "Usage: ./add_new_agent.sh <agent_name>"
    echo "Example: ./add_new_agent.sh my_new_agent"
    exit 1
fi

AGENT_NAME="$1"
AGENT_DIR="adk-agentic-architectures/$AGENT_NAME"
TEMPLATE_DIR="agent_examples/template_agent"

echo "🚀 Creating new agent: $AGENT_NAME"
echo "=================================="

# Check if agent already exists
if [ -d "$AGENT_DIR" ]; then
    echo "❌ Error: Agent directory '$AGENT_DIR' already exists"
    exit 1
fi

# Copy template
echo "📁 Copying template..."
cp -r "$TEMPLATE_DIR" "$AGENT_DIR"

# Rename files
cd "$AGENT_DIR"
mv template_agent.py "${AGENT_NAME}_agent.py"

# Update __init__.py
sed -i '' "s/template_agent/${AGENT_NAME}_agent/g" __init__.py

# Update agent file
AGENT_NAME_CAPITALIZED=$(echo "$AGENT_NAME" | sed 's/^./\U&/')
sed -i '' "s/TemplateAgent/${AGENT_NAME_CAPITALIZED}Agent/g" "${AGENT_NAME}_agent.py"
sed -i '' "s/template_agent/${AGENT_NAME}_agent/g" "${AGENT_NAME}_agent.py"

echo " Agent created successfully!"
echo ""
echo " Agent location: $AGENT_DIR"
echo ""
echo " Next steps:"
echo "1. Edit $AGENT_DIR/${AGENT_NAME}_agent.py to implement your logic"
echo "2. Test your agent: ./tests/run_all_tests.sh $AGENT_DIR"
echo "3. Test interactively: adk web $AGENT_DIR"
echo ""
echo " Run tests:"
echo "  ./tests/run_all_tests.sh $AGENT_DIR"
echo ""
echo " Interactive testing:"
echo "  adk web $AGENT_DIR"
echo ""
echo " Your agent will automatically be included in ./test_all_agents.sh"
