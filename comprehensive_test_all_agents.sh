#!/bin/bash
# Comprehensive Test Suite for All ADK Agents
# Tests all 17 architectures and generates a complete report

set -e

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ ERROR: GOOGLE_API_KEY not set"
    echo "   Run: export GOOGLE_API_KEY=your_key_here"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_FILE="$SCRIPT_DIR/test_results.json"

echo "{" > "$RESULTS_FILE"
echo "  \"test_date\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"," >> "$RESULTS_FILE"
echo "  \"agents\": {" >> "$RESULTS_FILE"

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

TOTAL_AGENTS=${#AGENTS[@]}
CURRENT=0

for agent_num in "${AGENTS[@]}"; do
    ((CURRENT++))
    AGENT_DIR="adk-agentic-architectures/$agent_num"
    
    echo ""
    echo "======================================================================"
    echo "Testing Agent $CURRENT/$TOTAL_AGENTS: $agent_num"
    echo "======================================================================"
    
    # Check if agent directory exists
    if [ ! -d "$AGENT_DIR" ]; then
        echo "⚠️  SKIP: Directory not found"
        continue
    fi
    
    # Structure validation
    echo "Phase 1: Structure Validation"
    echo "------------------------------"
    STRUCTURE_PASS=false
    if python3 tests/validate_agent.py "$AGENT_DIR" > /dev/null 2>&1; then
        echo "✅ Structure: PASS"
        STRUCTURE_PASS=true
    else
        echo "❌ Structure: FAIL"
        python3 tests/validate_agent.py "$AGENT_DIR" 2>&1 | head -20
    fi
    
    # Behavior tests
    echo ""
    echo "Phase 2: Behavior Tests"
    echo "------------------------------"
    
    TESTS_PASSED=0
    TESTS_FAILED=0
    TEST_DETAILS=""
    
    if [ "$STRUCTURE_PASS" = true ]; then
        for test in "${TESTS[@]}"; do
            test_name=$(basename "$test")
            test_dir=$(dirname "$test")
            
            result=$(timeout 60s adk eval "$AGENT_DIR" \
                "tests/behavior/$test.test.json" \
                --config_file_path="tests/behavior/$test_dir/test_config.json" \
                2>&1 | grep "Tests passed:" || echo "Tests passed: 0")
            
            if echo "$result" | grep -q "Tests passed: 1"; then
                echo "✅ $test_name: PASS"
                ((TESTS_PASSED++))
            else
                echo "❌ $test_name: FAIL"
                ((TESTS_FAILED++))
            fi
        done
    fi
    
    # Calculate score
    TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
    if [ $TOTAL_TESTS -gt 0 ]; then
        SCORE_PCT=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    else
        SCORE_PCT=0
    fi
    
    # Status determination
    STATUS="❌ FAILED"
    if [ "$STRUCTURE_PASS" = false ]; then
        STATUS="❌ STRUCTURAL_ERROR"
    elif [ $TESTS_PASSED -eq 4 ]; then
        STATUS="✅ PERFECT"
    elif [ $TESTS_PASSED -eq 3 ]; then
        STATUS="✅ ACCEPTABLE"
    elif [ $TESTS_PASSED -ge 2 ]; then
        STATUS="⚠️  NEEDS_REVIEW"
    fi
    
    echo ""
    echo "Summary: $STATUS ($TESTS_PASSED/$TOTAL_TESTS tests passed)"
    
    # Write JSON results
    if [ $CURRENT -lt $TOTAL_AGENTS ]; then
        COMMA=","
    else
        COMMA=""
    fi
    
    cat >> "$RESULTS_FILE" << EOF
    "$agent_num": {
      "structure_valid": $STRUCTURE_PASS,
      "tests_passed": $TESTS_PASSED,
      "tests_failed": $TESTS_FAILED,
      "score_percent": $SCORE_PCT,
      "status": "$STATUS"
    }$COMMA
EOF
done

echo "  }" >> "$RESULTS_FILE"
echo "}" >> "$RESULTS_FILE"

echo ""
echo "======================================================================"
echo "COMPREHENSIVE TEST RESULTS"
echo "======================================================================"

# Generate summary
python3 << 'PYEOF'
import json

with open('test_results.json') as f:
    results = json.load(f)

agents = results['agents']
total = len(agents)
perfect = sum(1 for a in agents.values() if '✅ PERFECT' in a['status'])
acceptable = sum(1 for a in agents.values() if '✅ ACCEPTABLE' in a['status'])
review = sum(1 for a in agents.values() if '⚠️' in a['status'])
failed = sum(1 for a in agents.values() if '❌' in a['status'])

print(f"Total Agents: {total}")
print(f"✅ Perfect (4/4): {perfect}")
print(f"✅ Acceptable (3/4): {acceptable}")
print(f"⚠️  Needs Review (2/4): {review}")
print(f"❌ Failed (0-1/4): {failed}")
print(f"\nOverall Success Rate: {perfect + acceptable}/{total} ({(perfect + acceptable) * 100 // total}%)")

print("\n" + "=" * 70)
print("DETAILED RESULTS BY AGENT")
print("=" * 70)

for agent, data in sorted(agents.items()):
    print(f"{agent:30} {data['status']:20} ({data['tests_passed']}/4)")

print("\n" + "=" * 70)
print("AGENTS REQUIRING ATTENTION")
print("=" * 70)

for agent, data in sorted(agents.items()):
    if '❌' in data['status'] or '⚠️' in data['status']:
        print(f"• {agent}: {data['status']} ({data['tests_passed']}/4 tests)")

PYEOF

echo ""
echo "Full results saved to: test_results.json"
