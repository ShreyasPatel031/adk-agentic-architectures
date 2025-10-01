#!/bin/bash
# Final Comprehensive Test with result logging

export GOOGLE_API_KEY="AIzaSyAaWHd56DFLuqQfz_djIG2-Io83jPKIrHE"
export PATH="$HOME/.local/bin:$PATH"
cd /workspace

RESULTS_FILE="/workspace/final_test_results.txt"
JSON_FILE="/workspace/final_test_results.json"

echo "{" > "$JSON_FILE"
echo "  \"test_date\": \"$(date -u +'%Y-%m-%d %H:%M:%S UTC')\"," >> "$JSON_FILE"
echo "  \"agents\": {" >> "$JSON_FILE"

echo "======================================================================"  | tee "$RESULTS_FILE"
echo "FINAL COMPREHENSIVE TEST SUITE" | tee -a "$RESULTS_FILE"
echo "======================================================================"  | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"

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

declare -a TESTS=(
    "reflection/hello_world_reflection"
    "tool_use/tool_calling_basic"
    "react/simple_lookup"
    "planning/plan_then_act"
)

TOTAL_AGENTS=${#AGENTS[@]}
CURRENT=0
GLOBAL_PASSED=0
GLOBAL_FAILED=0

for agent in "${AGENTS[@]}"; do
    ((CURRENT++))
    echo "" | tee -a "$RESULTS_FILE"
    echo "Testing $CURRENT/$TOTAL_AGENTS: $agent" | tee -a "$RESULTS_FILE"
    echo "---" | tee -a "$RESULTS_FILE"
    
    AGENT_PASSED=0
    AGENT_FAILED=0
    
    for test in "${TESTS[@]}"; do
        test_name=$(basename "$test")
        test_dir=$(dirname "$test")
        
        result=$(timeout 60s adk eval "adk-agentic-architectures/$agent/" \
            "tests/behavior/$test.test.json" \
            --config_file_path="tests/behavior/$test_dir/test_config.json" \
            2>&1)
        
        if echo "$result" | grep -q "Tests passed: 1"; then
            echo "  $test_name: ✅ PASS" | tee -a "$RESULTS_FILE"
            ((AGENT_PASSED++))
            ((GLOBAL_PASSED++))
        else
            echo "  $test_name: ❌ FAIL" | tee -a "$RESULTS_FILE"
            ((AGENT_FAILED++))
            ((GLOBAL_FAILED++))
        fi
    done
    
    TOTAL_AGENT_TESTS=$((AGENT_PASSED + AGENT_FAILED))
    PERCENT=$((AGENT_PASSED * 100 / TOTAL_AGENT_TESTS))
    
    if [ $AGENT_PASSED -eq 4 ]; then
        STATUS="✅ PERFECT"
    elif [ $AGENT_PASSED -eq 3 ]; then
        STATUS="✅ ACCEPTABLE"
    elif [ $AGENT_PASSED -ge 2 ]; then
        STATUS="⚠️  REVIEW"
    else
        STATUS="❌ FAILED"
    fi
    
    echo "  Result: $STATUS ($AGENT_PASSED/4)" | tee -a "$RESULTS_FILE"
    
    # Write JSON
    if [ $CURRENT -lt $TOTAL_AGENTS ]; then
        COMMA=","
    else
        COMMA=""
    fi
    
    cat >> "$JSON_FILE" << EOF
    "$agent": {
      "tests_passed": $AGENT_PASSED,
      "tests_failed": $AGENT_FAILED,
      "percent": $PERCENT,
      "status": "$STATUS"
    }$COMMA
EOF
done

echo "  }" >> "$JSON_FILE"
echo "}" >> "$JSON_FILE"

echo "" | tee -a "$RESULTS_FILE"
echo "======================================================================" | tee -a "$RESULTS_FILE"
echo "FINAL RESULTS" | tee -a "$RESULTS_FILE"
echo "======================================================================" | tee -a "$RESULTS_FILE"
TOTAL_TESTS=$((GLOBAL_PASSED + GLOBAL_FAILED))
OVERALL_PERCENT=$((GLOBAL_PASSED * 100 / TOTAL_TESTS))
echo "Overall: $GLOBAL_PASSED / $TOTAL_TESTS tests passed (${OVERALL_PERCENT}%)" | tee -a "$RESULTS_FILE"
echo "" | tee -a "$RESULTS_FILE"
echo "Results saved to:" | tee -a "$RESULTS_FILE"
echo "  - $RESULTS_FILE" | tee -a "$RESULTS_FILE"
echo "  - $JSON_FILE" | tee -a "$RESULTS_FILE"
