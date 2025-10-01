#!/bin/bash
# Quick test script for first 3 agents to verify the fix

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/adk-agentic-architectures"

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set"
    exit 1
fi

echo "Testing first 3 agents to verify fix..."

# Test first 3 agents
AGENT_DIRS=($(find "$AGENTS_DIR" -maxdepth 1 -type d -name "[0-9][0-9]_*" | sort | head -3))

for agent_dir in "${AGENT_DIRS[@]}"; do
    agent_name=$(basename "$agent_dir")
    echo ""
    echo "Testing Agent: $agent_name"
    echo "========================"
    
    # Test just one behavior test
    test="reflection/hello_world_reflection"
    test_name=$(basename "$test")
    test_dir=$(dirname "$test")
    
    echo "Testing: $test_name"
    
    result=$(adk eval "$agent_dir" \
        "$SCRIPT_DIR/tests/behavior/$test.test.json" \
        --config_file_path="$SCRIPT_DIR/tests/behavior/$test_dir/test_config.json" \
        2>&1)
    
    if echo "$result" | grep -q "Tests passed: 1"; then
        echo "  ✅ PASS"
    else
        echo "  ❌ FAIL"
        echo "Output: $result"
    fi
done
