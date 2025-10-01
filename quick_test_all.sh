#!/bin/bash
# Quick Test - One test per agent for speed

export GOOGLE_API_KEY="AIzaSyAaWHd56DFLuqQfz_djIG2-Io83jPKIrHE"
export PATH="$HOME/.local/bin:$PATH"
cd /workspace

echo "======================================================================"
echo "QUICK TEST SUITE - Reflection Test Only"
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
    echo -n "$agent ... "
    
    result=$(timeout 45s adk eval "adk-agentic-architectures/$agent/" \
        "tests/behavior/reflection/hello_world_reflection.test.json" \
        --config_file_path="tests/behavior/reflection/test_config.json" \
        2>&1)
    
    if echo "$result" | grep -q "Tests passed: 1"; then
        echo "✅ PASS"
        ((PASSED++))
    else
        echo "❌ FAIL"
        ((FAILED++))
    fi
done

echo ""
echo "======================================================================"
echo "Quick Test Results: $PASSED passed, $FAILED failed"
echo "======================================================================"
