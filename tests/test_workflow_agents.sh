#!/bin/bash

# Test script for workflow agents

AGENTS=("sequential_example" "loop_example" "parallel_example")

echo "======================================================================"
echo "WORKFLOW AGENT VALIDATION"
echo "======================================================================"
echo ""

TOTAL_PASSED=0
TOTAL_FAILED=0

for agent in "${AGENTS[@]}"; do
    echo "Testing: $agent"
    echo "---"
    
    # Run structure validation
    python3 tests/validate_agent.py "agent/$agent/" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "  ❌ Structure validation failed"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
        echo ""
        continue
    fi
    
    # Run basic response test
    result=$(adk eval "agent/$agent/" tests/workflow/basic_response.test.json --config_file_path=tests/workflow/test_config.json 2>&1 | grep "Tests passed:")
    
    if echo "$result" | grep -q "Tests passed: 1"; then
        echo "  ✅ Basic response: PASS"
        TOTAL_PASSED=$((TOTAL_PASSED + 1))
    else
        echo "  ❌ Basic response: FAIL"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
    
    # Run tool usage test for all agents (all have tools now)
    result=$(adk eval "agent/$agent/" tests/workflow/tool_usage.test.json --config_file_path=tests/workflow/tool_test_config.json 2>&1 | grep "Tests passed:")
    
    if echo "$result" | grep -q "Tests passed: 1"; then
        echo "  ✅ Tool usage: PASS"
        TOTAL_PASSED=$((TOTAL_PASSED + 1))
    else
        echo "  ❌ Tool usage: FAIL"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
    
    echo ""
done

echo "======================================================================"
echo "FINAL RESULTS"
echo "======================================================================"
echo "Passed: $TOTAL_PASSED"
echo "Failed: $TOTAL_FAILED"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo "🎉 ALL WORKFLOW AGENTS VALIDATED!"
    exit 0
else
    echo "❌ Some agents failed validation"
    exit 1
fi
