#!/usr/bin/env python3
"""
Test script to verify all agents are properly integrated into the orchestrator
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_agent_integration():
    """Test that all agents can be imported and orchestrator works"""
    
    print("🧪 Testing Agent Integration")
    print("=" * 50)
    
    # Test individual agent imports
    agents_to_test = [
        ("Planning Agent", "app.agents.planning_agent", "PlanningAgent"),
        ("Query Agent", "app.agents.query_agent", "QueryAgent"),
        ("Data Agent", "app.agents.data_agent", "DataAgent"),
        ("Retrieval Agent", "app.agents.retrieval_agent", "RetrievalAgent"),
        ("SQL Agent", "app.agents.sql_agent", "SQLAgent"),
        ("Insight Agent", "app.agents.insight_agent", "InsightAgent"),
        ("Chart Agent", "app.agents.chart_agent", "ChartAgent"),
        ("Critique Agent", "app.agents.critique_agent", "CritiqueAgent"),
        ("Debate Agent", "app.agents.debate_agent", "DebateAgent"),
        ("Narrative Agent", "app.agents.narrative_agent", "NarrativeAgent"),
        ("Report Agent", "app.agents.report_agent", "ReportAgent"),
    ]
    
    imported_agents = []
    
    for agent_name, module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            imported_agents.append(agent_name)
            print(f"✅ {agent_name} - Import successful")
        except Exception as e:
            print(f"❌ {agent_name} - Import failed: {e}")
    
    print(f"\n📊 Agent Import Summary: {len(imported_agents)}/11 agents imported successfully")
    
    # Test orchestrator import and initialization
    print("\n🎯 Testing Orchestrator Integration")
    print("-" * 40)
    
    try:
        from app.services.agent_orchestrator import AgentOrchestrator
        print("✅ Orchestrator import successful")
        
        # Test orchestrator initialization
        orchestrator = AgentOrchestrator()
        agent_count = len(orchestrator.agents)
        agent_names = list(orchestrator.agents.keys())
        
        print(f"✅ Orchestrator initialized with {agent_count} agents")
        print(f"✅ Available agents: {', '.join(agent_names)}")
          # Check that all expected agents are present
        expected_agents = [
            "planning", "query", "data", "retrieval", "sql", 
            "insight", "chart", "critique", "debate", "narrative_gen", "report"
        ]
        
        missing_agents = [agent for agent in expected_agents if agent not in agent_names]
        
        if missing_agents:
            print(f"⚠️  Missing agents in orchestrator: {', '.join(missing_agents)}")
        else:
            print("✅ All expected agents are present in orchestrator")
            
        # Test that the workflow graph was built
        if hasattr(orchestrator, 'graph') and orchestrator.graph:
            print("✅ LangGraph workflow compiled successfully")
        else:
            print("❌ LangGraph workflow compilation failed")
            
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Integration Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_agent_integration()
