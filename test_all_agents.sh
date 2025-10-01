#!/bin/bash
# Comprehensive Testing Script for All ADK Agentic Architectures
# Tests all 17 agents in the adk-agentic-architectures/ directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/adk-agentic-architectures"

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set"
    echo "   Run: export GOOGLE_API_KEY=your_key_here"
    exit 1
fi

echo ""
echo "======================================================================"
echo "COMPREHENSIVE ADK AGENTIC ARCHITECTURES TEST SUITE"
echo "======================================================================"
echo "Testing all agents in: $AGENTS_DIR"
echo ""

# Initialize counters
TOTAL_AGENTS=0
AGENTS_PASSED=0
AGENTS_FAILED=0
AGENTS_STRUCTURE_FAILED=0

# Get all agent directories (sorted by number)
AGENT_DIRS=($(find "$AGENTS_DIR" -maxdepth 1 -type d -name "[0-9][0-9]_*" | sort))

echo "Found ${#AGENT_DIRS[@]} agents to test:"
for agent_dir in "${AGENT_DIRS[@]}"; do
    agent_name=$(basename "$agent_dir")
    echo "  - $agent_name"
done
echo ""

# Create results file
RESULTS_FILE="$SCRIPT_DIR/test_results_$(date +%Y%m%d_%H%M%S).txt"
echo "Test Results - $(date)" > "$RESULTS_FILE"
echo "=================================" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

# Test each agent
for agent_dir in "${AGENT_DIRS[@]}"; do
    agent_name=$(basename "$agent_dir")
    agent_number=$(echo "$agent_name" | cut -d'_' -f1)
    
    echo "======================================================================"
    echo "Testing Agent: $agent_name"
    echo "======================================================================"
    
    # Log to results file
    echo "Agent: $agent_name" >> "$RESULTS_FILE"
    echo "Time: $(date)" >> "$RESULTS_FILE"
    
    ((TOTAL_AGENTS++))
    
    # Phase 1: Structure Validation
    echo "Phase 1: Structure Validation"
    echo "------------------------------"
    
    if python3 "$SCRIPT_DIR/tests/validate_agent.py" "$agent_dir" > /dev/null 2>&1; then
        echo "✅ Structure validation PASSED"
        STRUCTURE_PASSED=true
        echo "Structure: PASS" >> "$RESULTS_FILE"
    else
        echo "❌ Structure validation FAILED"
        STRUCTURE_PASSED=false
        ((AGENTS_STRUCTURE_FAILED++))
        echo "Structure: FAIL" >> "$RESULTS_FILE"
        
        # If structure fails, skip behavior tests
        echo "Skipping behavior tests due to structure failure."
        echo "Behavior: SKIPPED" >> "$RESULTS_FILE"
        echo "Overall: STRUCTURE_FAILED" >> "$RESULTS_FILE"
        echo "================================================" >> "$RESULTS_FILE"
        echo "" >> "$RESULTS_FILE"
        ((AGENTS_FAILED++))
        echo ""
        continue
    fi
    
    echo ""
    echo "Phase 2: Behavior Tests"
    echo "-----------------------"
    
    # Run behavior tests
    TESTS_PASSED=0
    TESTS_FAILED=0
    
    TESTS=(
        "reflection/hello_world_reflection"
        "tool_use/tool_calling_basic"
        "react/simple_lookup"
        "planning/plan_then_act"
    )
    
    for test in "${TESTS[@]}"; do
        test_name=$(basename "$test")
        test_dir=$(dirname "$test")
        
        echo "Testing: $test_name"
        
        # Run the test and capture output
        result=$(adk eval "$agent_dir" \
            "$SCRIPT_DIR/tests/behavior/$test.test.json" \
            --config_file_path="$SCRIPT_DIR/tests/behavior/$test_dir/test_config.json" \
            2>&1)
        
        # Check if test passed (look for "Tests passed: 1")
        if echo "$result" | grep -q "Tests passed: 1"; then
            echo "  ✅ PASS"
            ((TESTS_PASSED++))
        else
            echo "  ❌ FAIL"
            ((TESTS_FAILED++))
        fi
    done
    
    echo ""
    echo "Agent $agent_name Results:"
    echo "  Structure: PASS"
    echo "  Behavior: $TESTS_PASSED passed, $TESTS_FAILED failed"
    
    # Log behavior results
    echo "Behavior: $TESTS_PASSED/4 tests passed" >> "$RESULTS_FILE"
    
    # Determine overall agent status
    if [ $TESTS_FAILED -eq 0 ]; then
        echo "  Overall: 🎉 PERFECT (4/4 tests)"
        echo "Overall: PERFECT (4/4)" >> "$RESULTS_FILE"
        ((AGENTS_PASSED++))
    elif [ $TESTS_PASSED -ge 3 ]; then
        echo "  Overall: 🟡 GOOD ($TESTS_PASSED/4 tests)"
        echo "Overall: GOOD ($TESTS_PASSED/4)" >> "$RESULTS_FILE"
        ((AGENTS_PASSED++))
    elif [ $TESTS_PASSED -ge 1 ]; then
        echo "  Overall: 🟠 PARTIAL ($TESTS_PASSED/4 tests)"
        echo "Overall: PARTIAL ($TESTS_PASSED/4)" >> "$RESULTS_FILE"
        ((AGENTS_FAILED++))
    else
        echo "  Overall: ❌ FAILED (0/4 tests)"
        echo "Overall: FAILED (0/4)" >> "$RESULTS_FILE"
        ((AGENTS_FAILED++))
    fi
    
    echo "================================================" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    echo ""
done

# Final Summary
echo "======================================================================"
echo "FINAL COMPREHENSIVE RESULTS"
echo "======================================================================"
echo "Total Agents Tested: $TOTAL_AGENTS"
echo "Agents Passed (3+ tests): $AGENTS_PASSED"
echo "Agents Failed (<3 tests): $AGENTS_FAILED"
echo "Structure Failures: $AGENTS_STRUCTURE_FAILED"
echo ""

# Log final summary to results file
echo "" >> "$RESULTS_FILE"
echo "FINAL SUMMARY" >> "$RESULTS_FILE"
echo "=============" >> "$RESULTS_FILE"
echo "Total Agents Tested: $TOTAL_AGENTS" >> "$RESULTS_FILE"
echo "Agents Passed (3+ tests): $AGENTS_PASSED" >> "$RESULTS_FILE"
echo "Agents Failed (<3 tests): $AGENTS_FAILED" >> "$RESULTS_FILE"
echo "Structure Failures: $AGENTS_STRUCTURE_FAILED" >> "$RESULTS_FILE"

echo "DETAILED RESULTS:"
echo "=================="
printf "%-25s %-12s %-12s %-12s\n" "Agent" "Structure" "Behavior" "Overall"
echo "----------------------------------------------------------------"

# Read and display results from file
while IFS= read -r line; do
    if [[ $line == "Agent:"* ]]; then
        agent_name=$(echo "$line" | cut -d' ' -f2-)
    elif [[ $line == "Structure:"* ]]; then
        structure_result=$(echo "$line" | cut -d' ' -f2)
    elif [[ $line == "Behavior:"* ]]; then
        behavior_result=$(echo "$line" | cut -d' ' -f2)
    elif [[ $line == "Overall:"* ]]; then
        overall_result=$(echo "$line" | cut -d' ' -f2-)
        printf "%-25s %-12s %-12s %-12s\n" "$agent_name" "$structure_result" "$behavior_result" "$overall_result"
    fi
done < "$RESULTS_FILE"

echo ""
echo "SUMMARY BY CATEGORY:"
echo "===================="

# Count by category
PERFECT_COUNT=0
GOOD_COUNT=0
PARTIAL_COUNT=0
FAILED_COUNT=0
STRUCTURE_FAILED_COUNT=0

while IFS= read -r line; do
    if [[ $line == "Overall: PERFECT"* ]]; then
        ((PERFECT_COUNT++))
    elif [[ $line == "Overall: GOOD"* ]]; then
        ((GOOD_COUNT++))
    elif [[ $line == "Overall: PARTIAL"* ]]; then
        ((PARTIAL_COUNT++))
    elif [[ $line == "Overall: FAILED"* ]]; then
        ((FAILED_COUNT++))
    elif [[ $line == "Overall: STRUCTURE_FAILED"* ]]; then
        ((STRUCTURE_FAILED_COUNT++))
    fi
done < "$RESULTS_FILE"

echo "🎉 Perfect (4/4 tests): $PERFECT_COUNT agents"
echo "🟡 Good (3/4 tests): $GOOD_COUNT agents"
echo "🟠 Partial (1-2/4 tests): $PARTIAL_COUNT agents"
echo "❌ Failed (0/4 tests): $FAILED_COUNT agents"
echo "🔧 Structure Failed: $STRUCTURE_FAILED_COUNT agents"
echo ""

# Log category summary
echo "" >> "$RESULTS_FILE"
echo "CATEGORY SUMMARY" >> "$RESULTS_FILE"
echo "================" >> "$RESULTS_FILE"
echo "Perfect (4/4 tests): $PERFECT_COUNT agents" >> "$RESULTS_FILE"
echo "Good (3/4 tests): $GOOD_COUNT agents" >> "$RESULTS_FILE"
echo "Partial (1-2/4 tests): $PARTIAL_COUNT agents" >> "$RESULTS_FILE"
echo "Failed (0/4 tests): $FAILED_COUNT agents" >> "$RESULTS_FILE"
echo "Structure Failed: $STRUCTURE_FAILED_COUNT agents" >> "$RESULTS_FILE"

# Overall assessment
SUCCESS_RATE=$(( (AGENTS_PASSED * 100) / TOTAL_AGENTS ))

echo "Results saved to: $RESULTS_FILE"
echo ""

if [ $AGENTS_FAILED -eq 0 ]; then
    echo "🎉 EXCELLENT: All $TOTAL_AGENTS agents are functional!"
    exit 0
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo "🟡 GOOD: $AGENTS_PASSED/$TOTAL_AGENTS agents are functional ($SUCCESS_RATE% success rate)"
    exit 0
elif [ $SUCCESS_RATE -ge 50 ]; then
    echo "🟠 FAIR: $AGENTS_PASSED/$TOTAL_AGENTS agents are functional ($SUCCESS_RATE% success rate)"
    echo "   Consider fixing the failing agents for better coverage."
    exit 1
else
    echo "❌ POOR: Only $AGENTS_PASSED/$TOTAL_AGENTS agents are functional ($SUCCESS_RATE% success rate)"
    echo "   Significant issues detected. Review and fix failing agents."
    exit 1
fi