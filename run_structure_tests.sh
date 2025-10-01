#!/bin/bash
# Structure Validation for All Agents (no API key required)

export PATH="$HOME/.local/bin:$PATH"
cd /workspace

echo "======================================================================"
echo "STRUCTURE VALIDATION TEST SUITE"
echo "======================================================================"
echo ""

# Array of all agents
declare -a AGENTS=(
    "01_reflection"
    "02_tool_use"
    "03_ReAct"
    "04_planning"
    "05_multi_agent"
    "06_PEV"
    "07_blackboard"
    "08_episodic_with_semantic"
    "09_tree_of_thoughts"
    "10_mental_loop"
    "11_meta_controller"
    "12_graph"
    "13_ensemble"
    "14_dry_run"
    "15_RLHF"
    "16_cellular_automata"
    "17_reflexive_metacognitive"
)

PASSED=0
FAILED=0

for agent in "${AGENTS[@]}"; do
    echo "Testing: $agent"
    echo "---"
    
    if python3 tests/validate_agent.py "adk-agentic-architectures/$agent/" 2>&1 | grep -q "All structure checks PASSED"; then
        echo "✅ PASS"
        ((PASSED++))
    else
        echo "❌ FAIL"
        ((FAILED++))
        # Show error details
        python3 tests/validate_agent.py "adk-agentic-architectures/$agent/" 2>&1 | grep -A 5 "Errors found:"
    fi
    echo ""
done

echo "======================================================================"
echo "STRUCTURE TEST RESULTS"
echo "======================================================================"
echo "Passed: $PASSED / ${#AGENTS[@]}"
echo "Failed: $FAILED / ${#AGENTS[@]}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL AGENTS PASS STRUCTURE VALIDATION"
    echo "Ready for behavior testing (requires GOOGLE_API_KEY)"
else
    echo "⚠️  Some agents have structure errors"
    echo "Fix these before running eval tests"
fi
