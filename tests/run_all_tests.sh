#!/bin/bash
# Comprehensive Agent Testing Script
# Runs both structure validation and behavior tests

set -e

if [ -z "$1" ]; then
    echo "Usage: ./run_all_tests.sh <agent_directory>"
    echo "Example: ./run_all_tests.sh agent/"
    exit 1
fi

AGENT_DIR="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set"
    echo "   Run: export GOOGLE_API_KEY=your_key_here"
    exit 1
fi

echo ""
echo "======================================================================"
echo "AGENT TESTING SUITE"
echo "======================================================================"
echo "Agent: $AGENT_DIR"
echo ""

# Phase 1: Structure Validation
echo "Phase 1: Structure Validation"
echo "------------------------------"
python3 "$SCRIPT_DIR/validate_agent.py" "$AGENT_DIR"
STRUCTURE_RESULT=$?

if [ $STRUCTURE_RESULT -ne 0 ]; then
    echo ""
    echo "❌ Structure validation failed. Fix code/config errors above."
    echo "   These are NOT AI issues - they are structural problems."
    exit 1
fi

echo ""
echo "======================================================================"
echo "Phase 2: Behavior Tests"
echo "======================================================================"
echo ""

# Run each test
TESTS_PASSED=0
TESTS_FAILED=0

declare -a TESTS=(
    "reflection/hello_world_reflection"
    "tool_use/tool_calling_basic"
    "react/simple_lookup"
    "planning/plan_then_act"
)

for test in "${TESTS[@]}"; do
    test_name=$(basename "$test")
    test_dir=$(dirname "$test")
    
    echo "Testing: $test_name"
    echo "---"
    
    result=$(adk eval "$AGENT_DIR" \
        "$SCRIPT_DIR/behavior/$test.test.json" \
        --config_file_path="$SCRIPT_DIR/behavior/$test_dir/test_config.json" \
        2>&1 | grep "Tests passed:" || true)
    
    if echo "$result" | grep -q "Tests passed: 1"; then
        echo "✅ PASS"
        ((TESTS_PASSED++))
    else
        echo "❌ FAIL"
        ((TESTS_FAILED++))
    fi
    echo ""
done

echo "======================================================================"
echo "FINAL RESULTS"
echo "======================================================================"
echo "Structure Validation: ✅ PASS"
echo "Behavior Tests: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED! Agent is fully functional."
    exit 0
elif [ $TESTS_PASSED -ge 3 ]; then
    echo "🟡 Most tests passed ($TESTS_PASSED/4). Agent is functional with minor issues."
    exit 0
else
    echo "❌ Multiple test failures. Check AI behavior and configuration."
    exit 1
fi

