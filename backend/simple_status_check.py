#!/usr/bin/env python3
"""
Simple Backend Status Check - Check status, wait 5 seconds, check again
Never runs the backend, only monitors existing status
"""

import time
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.utils.terminal_monitor import terminal_monitor

def quick_status_check():
    """Quick status check with minimal output"""
    status = terminal_monitor.collect_terminal_status()
    
    print(f"🔍 Backend Status: {status.backend_status.value.upper()}")
    print(f"📡 Port 8000: {'🟢 ACTIVE' if status.ports_status[8000] else '🔴 INACTIVE'}")
    
    if status.backend_process:
        print(f"⚙️  Process: PID {status.backend_process.pid} ({status.backend_process.name})")
        print(f"💾 Memory: {status.backend_process.memory_mb:.1f} MB")
    else:
        print("❌ Process: No backend process found")
    
    print(f"🖥️  System: CPU {status.system_info.get('cpu_percent', 0):.1f}%, Memory {status.system_info.get('memory_percent', 0):.1f}%")
    return status

def main():
    """Check status, wait 5 seconds, check again"""
    print("🚀 Backend Terminal Status Monitor (No Backend Startup)")
    print("=" * 55)
    
    # First check
    print("\n📋 Status Check #1:")
    status1 = quick_status_check()
    
    # Wait 5 seconds with countdown
    print("\n⏳ Waiting 5 seconds...")
    for i in range(5, 0, -1):
        print(f"   {i}s remaining...", end="\r")
        time.sleep(1)
    print("   ✅ Wait complete!   ")
    
    # Second check
    print("\n📋 Status Check #2:")
    status2 = quick_status_check()
    
    # Simple comparison
    print("\n🔍 Quick Comparison:")
    if status1.backend_status == status2.backend_status:
        print(f"   Status: Unchanged ({status1.backend_status.value})")
    else:
        print(f"   Status: {status1.backend_status.value} → {status2.backend_status.value}")
    
    if status1.ports_status[8000] == status2.ports_status[8000]:
        print(f"   Port 8000: Unchanged ({'Active' if status1.ports_status[8000] else 'Inactive'})")
    else:
        print("   Port 8000: Changed!")
    
    print("\n✅ Done! Backend was never started by this script.")

if __name__ == "__main__":
    main()
