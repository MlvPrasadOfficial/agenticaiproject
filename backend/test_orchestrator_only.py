import sys
import os
sys.path.insert(0, os.getcwd())

print("Testing orchestrator with new agents...")

try:
    # Test the orchestrator import
    from app.services.agent_orchestrator import AgentOrchestrator
    print("✅ Orchestrator imported successfully")
    
    # Test orchestrator initialization
    orchestrator = AgentOrchestrator()
    print(f"✅ Orchestrator created with {len(orchestrator.agents)} agents")
    print(f"✅ Agent names: {list(orchestrator.agents.keys())}")
      # Check for the new agents specifically
    expected_agents = ["critique", "debate", "narrative_gen"]
    for agent_name in expected_agents:
        if agent_name in orchestrator.agents:
            print(f"✅ {agent_name} agent found in orchestrator")
        else:
            print(f"❌ {agent_name} agent missing from orchestrator")
    
    print("✅ Orchestrator test completed successfully!")
    
except Exception as e:
    print(f"❌ Orchestrator test failed: {e}")
    import traceback
    traceback.print_exc()
