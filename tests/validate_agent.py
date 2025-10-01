#!/usr/bin/env python3
"""
Agent Structure Validator
Checks if an agent is correctly configured BEFORE running eval tests.
This catches code/config errors early, separate from AI behavior issues.
"""

import sys
import os
import importlib.util
from pathlib import Path

def validate_agent_structure(agent_path: str) -> tuple[bool, list[str]]:
    """
    Validate agent structure and configuration.
    
    Returns:
        (success: bool, errors: list[str])
    """
    errors = []
    agent_path = Path(agent_path)
    
    # Check 1: Directory exists
    if not agent_path.exists():
        return False, [f"Agent directory does not exist: {agent_path}"]
    
    # Check 2: __init__.py exists
    init_file = agent_path / "__init__.py"
    if not init_file.exists():
        errors.append(f"Missing __init__.py in {agent_path}")
        return False, errors
    
    # Check 3: Can import module
    try:
        spec = importlib.util.spec_from_file_location("test_agent", init_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules["test_agent"] = module
            spec.loader.exec_module(module)
        else:
            errors.append("Could not load module spec")
            return False, errors
    except Exception as e:
        errors.append(f"Import error: {e}")
        return False, errors
    
    # Check 4: Has 'agent' attribute
    if not hasattr(module, 'agent'):
        errors.append("Module missing 'agent' attribute. Add: agent = SimpleNamespace(root_agent=root_agent)")
        return False, errors
    
    # Check 5: agent has 'root_agent' attribute
    if not hasattr(module.agent, 'root_agent'):
        errors.append("agent object missing 'root_agent' attribute")
        return False, errors
    
    # Check 6: root_agent is not None
    if module.agent.root_agent is None:
        errors.append("root_agent is None")
        return False, errors
    
    root_agent = module.agent.root_agent
    
    # Check 7: root_agent has 'name' attribute
    if not hasattr(root_agent, 'name'):
        errors.append("root_agent missing 'name' attribute")
        return False, errors
    
    # Check 8: For multi-agent, check sub_agents
    if hasattr(root_agent, 'sub_agents'):
        if not isinstance(root_agent.sub_agents, list):
            errors.append(f"sub_agents must be a list, got {type(root_agent.sub_agents)}")
        
        # Check for duplicate names
        names = [sa.name for sa in root_agent.sub_agents if hasattr(sa, 'name')]
        if len(names) != len(set(names)):
            duplicates = [n for n in names if names.count(n) > 1]
            errors.append(f"Duplicate sub-agent names: {duplicates}")
        
        # Check each sub-agent has name and parent
        for i, sa in enumerate(root_agent.sub_agents):
            if not hasattr(sa, 'name'):
                errors.append(f"Sub-agent {i} missing 'name'")
            if hasattr(sa, 'parent_agent') and sa.parent_agent != root_agent:
                errors.append(f"Sub-agent '{sa.name}' has wrong parent")
    
    # Check 9: Config file exists (if using config pattern)
    config_dir = agent_path / "config"
    if config_dir.exists():
        yaml_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.yml"))
        if not yaml_files:
            errors.append(f"Config directory exists but no YAML files found in {config_dir}")
    
    if errors:
        return False, errors
    
    return True, []

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_agent.py <agent_directory>")
        print("Example: python validate_agent.py agent/")
        sys.exit(1)
    
    agent_path = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"Validating Agent Structure: {agent_path}")
    print(f"{'='*60}\n")
    
    success, errors = validate_agent_structure(agent_path)
    
    if success:
        print("✅ All structure checks PASSED")
        print("\nAgent is correctly configured and ready for eval testing.")
        print("\nNext step:")
        print(f"  adk eval {agent_path} tests/behavior/reflection/hello_world_reflection.test.json \\")
        print(f"    --config_file_path=tests/behavior/reflection/test_config.json")
        return 0
    else:
        print("❌ Structure validation FAILED\n")
        print("Errors found:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print("\nFix these issues before running eval tests.")
        print("These are CODE/CONFIGURATION errors, not AI issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

