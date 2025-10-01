#!/bin/bash
# Comprehensive Test Suite for All ADK Agents with API calls

export GOOGLE_API_KEY="AIzaSyAaWHd56DFLuqQfz_djIG2-Io83jPKIrHE"
export PATH="$HOME/.local/bin:$PATH"
cd /workspace

echo "======================================================================"
echo "COMPREHENSIVE ADK AGENT TEST SUITE"
echo "======================================================================"
echo "Testing 17 agents with 4 behavior tests each (68 total tests)"
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

# Test categories
declare -a TESTS=(
    "reflection/hello_world_reflection"
    "tool_use/tool_calling_basic"
    "react/simple_lookup"
    "planning/plan_then_act"
)

# Results tracking
declare -A AGENT_RESULTS
TOTAL_TESTS=0
TOTAL_PASSED=0

for agent in "${AGENTS[@]}"; do
    echo ""
    echo "======================================================================"
    echo "Testing: $agent"
    echo "======================================================================"
    
    AGENT_DIR="adk-agentic-architectures/$agent"
    AGENT_PASSED=0
    AGENT_FAILED=0
    
    for test in "${TESTS[@]}"; do
        test_name=$(basename "$test")
        test_dir=$(dirname "$test")
        
        echo -n "  $test_name ... "
        
        # Run test with timeout
        result=$(timeout 90s adk eval "$AGENT_DIR" \
            "tests/behavior/$test.test.json" \
            --config_file_path="tests/behavior/$test_dir/test_config.json" \
            2>&1)
        
        if echo "$result" | grep -q "Tests passed: 1"; then
            echo "✅ PASS"
            ((AGENT_PASSED++))
            ((TOTAL_PASSED++))
        else
            echo "❌ FAIL"
            ((AGENT_FAILED++))
            # Show brief error info
            if echo "$result" | grep -q "Error"; then
                echo "$result" | grep "Error" | head -1 | sed 's/^/    /'
            fi
        fi
        ((TOTAL_TESTS++))
    done
    
    # Calculate agent score
    SCORE="$AGENT_PASSED/4"
    PERCENT=$((AGENT_PASSED * 100 / 4))
    
    # Determine status
    if [ $AGENT_PASSED -eq 4 ]; then
        STATUS="✅ PERFECT"
    elif [ $AGENT_PASSED -eq 3 ]; then
        STATUS="✅ ACCEPTABLE"
    elif [ $AGENT_PASSED -eq 2 ]; then
        STATUS="⚠️  NEEDS REVIEW"
    else
        STATUS="❌ FAILED"
    fi
    
    echo "  Summary: $STATUS ($SCORE tests, ${PERCENT}%)"
    AGENT_RESULTS[$agent]="$STATUS|$SCORE|$PERCENT"
done

echo ""
echo "======================================================================"
echo "FINAL TEST RESULTS"
echo "======================================================================"
echo ""
echo "Overall: $TOTAL_PASSED / $TOTAL_TESTS tests passed ($((TOTAL_PASSED * 100 / TOTAL_TESTS))%)"
echo ""
echo "Agent-by-Agent Results:"
echo "----------------------------------------------------------------------"
printf "%-30s %-20s %s\n" "Agent" "Status" "Score"
echo "----------------------------------------------------------------------"

for agent in "${AGENTS[@]}"; do
    IFS='|' read -r status score percent <<< "${AGENT_RESULTS[$agent]}"
    printf "%-30s %-20s %s\n" "$agent" "$status" "$score"
done

echo ""
echo "======================================================================"
echo "SUMMARY BY STATUS"
echo "======================================================================"

PERFECT=$(echo "${AGENT_RESULTS[@]}" | tr ' ' '\n' | grep -c "✅ PERFECT" || echo 0)
ACCEPTABLE=$(echo "${AGENT_RESULTS[@]}" | tr ' ' '\n' | grep -c "✅ ACCEPTABLE" || echo 0)
REVIEW=$(echo "${AGENT_RESULTS[@]}" | tr ' ' '\n' | grep -c "⚠️  NEEDS REVIEW" || echo 0)
FAILED=$(echo "${AGENT_RESULTS[@]}" | tr ' ' '\n' | grep -c "❌ FAILED" || echo 0)

echo "✅ Perfect (4/4):        $PERFECT agents"
echo "✅ Acceptable (3/4):     $ACCEPTABLE agents"
echo "⚠️  Needs Review (2/4):  $REVIEW agents"
echo "❌ Failed (0-1/4):       $FAILED agents"
echo ""
echo "Success Rate: $((PERFECT + ACCEPTABLE)) / 17 agents ($((((PERFECT + ACCEPTABLE) * 100) / 17))%)"
