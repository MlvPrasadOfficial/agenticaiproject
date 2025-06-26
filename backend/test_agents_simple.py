import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

print("Testing agent creation...")

try:
    from app.agents.narrative_agent import NarrativeAgent
    agent = NarrativeAgent()
    print("✅ NarrativeAgent created successfully")
    fields = agent.get_required_fields()
    print(f"✅ Required fields: {fields}")
except Exception as e:
    print(f"❌ NarrativeAgent error: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.agents.critique_agent import CritiqueAgent
    agent = CritiqueAgent()
    print("✅ CritiqueAgent created successfully")
except Exception as e:
    print(f"❌ CritiqueAgent error: {e}")

try:
    from app.agents.debate_agent import DebateAgent
    agent = DebateAgent()
    print("✅ DebateAgent created successfully")
except Exception as e:
    print(f"❌ DebateAgent error: {e}")

print("Agent testing complete.")
