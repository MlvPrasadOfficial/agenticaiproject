import asyncio
import sys
import os
import time

# Update path to handle being in the tests directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.agents.planning_agent import PlanningAgent

async def test_planning_agent():
    """Test the planning agent directly"""
    
    try:
        print("🔍 Testing Planning Agent directly...")
        agent = PlanningAgent()
        
        # Create minimal test state
        test_state = {
            "user_query": "Show me total sales by category",
            "session_id": "direct_test_session",
        }
        
        # Execute the agent directly
        start_time = time.time()
        print("⏱️ Starting Planning Agent execution...")
        
        result = await agent.execute(test_state)
        
        execution_time = time.time() - start_time
        print(f"⏱️ Planning Agent completed in {execution_time:.2f} seconds")
        
        print("🔍 Planning Agent result:")
        print(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing Planning Agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_planning_agent())
