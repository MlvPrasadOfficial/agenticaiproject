#!/usr/bin/env python3
"""
Backend Status Checker - Check terminal status without starting backend
"""

import time
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.utils.terminal_monitor import TerminalMonitor

def check_backend_status():
    """Check backend status and display results"""
    print("🔍 Checking backend terminal status...")
    
    monitor = TerminalMonitor()
    
    # Get current status
    status_data = monitor.collect_terminal_status()
    
    print(f"\n📊 Backend Status Report:")
    print(f"├── Status: {status_data.backend_status.value.upper()}")
    print(f"├── Port 8000: {'🟢 ACTIVE' if status_data.ports_status[8000] else '🔴 INACTIVE'}")
    print(f"├── Port 3000: {'🟢 ACTIVE' if status_data.ports_status[3000] else '🔴 INACTIVE'}")
    
    if status_data.backend_process:
        proc = status_data.backend_process
        print(f"├── Process Info:")
        print(f"│   ├── PID: {proc.pid}")
        print(f"│   ├── Name: {proc.name}")
        print(f"│   ├── CPU: {proc.cpu_percent:.1f}%")
        print(f"│   ├── Memory: {proc.memory_mb:.1f} MB")
        print(f"│   └── Status: {proc.status}")
    else:
        print(f"├── Process: No backend process found")
    
    # System info
    sys_info = status_data.system_info
    print(f"├── System Resources:")
    print(f"│   ├── CPU Usage: {sys_info.get('cpu_percent', 'N/A')}%")
    print(f"│   ├── Memory Usage: {sys_info.get('memory_percent', 'N/A')}%")
    print(f"│   └── Available Memory: {sys_info.get('memory_available_gb', 'N/A')} GB")
    
    # Log summary
    log_info = status_data.log_summary
    print(f"└── Logs: {log_info.get('total_log_files', 0)} files, {log_info.get('total_size_mb', 0)} MB total")
    
    return status_data

def main():
    """Main function to check status, wait, and check again"""
    print("🚀 Backend Terminal Status Monitor")
    print("=" * 50)
    
    # First check
    print("\n📋 Initial Status Check:")
    status1 = check_backend_status()
    
    # Wait 5 seconds
    print(f"\n⏱️  Waiting 5 seconds...")
    for i in range(5, 0, -1):
        print(f"   {i}...", end="", flush=True)
        time.sleep(1)
    print(" Done!")
    
    # Second check
    print(f"\n📋 Status Check After 5 Seconds:")
    status2 = check_backend_status()
    
    # Compare results
    print(f"\n🔄 Comparison:")
    if status1.backend_status == status2.backend_status:
        print(f"├── Backend Status: Unchanged ({status1.backend_status.value})")
    else:
        print(f"├── Backend Status: Changed from {status1.backend_status.value} to {status2.backend_status.value}")
    
    port_8000_changed = status1.ports_status[8000] != status2.ports_status[8000]
    if port_8000_changed:
        print(f"├── Port 8000: Changed from {'ACTIVE' if status1.ports_status[8000] else 'INACTIVE'} to {'ACTIVE' if status2.ports_status[8000] else 'INACTIVE'}")
    else:
        print(f"├── Port 8000: Unchanged ({'ACTIVE' if status1.ports_status[8000] else 'INACTIVE'})")
    
    # CPU comparison
    cpu1 = status1.system_info.get('cpu_percent', 0)
    cpu2 = status2.system_info.get('cpu_percent', 0)
    cpu_diff = abs(cpu2 - cpu1)
    print(f"└── CPU Usage: {cpu1:.1f}% → {cpu2:.1f}% (Δ{cpu_diff:+.1f}%)")
    
    print(f"\n✅ Status check completed!")
    
    # Save detailed report
    report_file = Path("logs") / f"status_check_{int(time.time())}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    report = {
        "check_timestamp": time.time(),
        "initial_status": {
            "timestamp": status1.timestamp.isoformat(),
            "backend_status": status1.backend_status.value,
            "ports": status1.ports_status,
            "system": status1.system_info,
            "process": status1.backend_process.__dict__ if status1.backend_process else None
        },
        "after_5_seconds": {
            "timestamp": status2.timestamp.isoformat(),
            "backend_status": status2.backend_status.value,
            "ports": status2.ports_status,
            "system": status2.system_info,
            "process": status2.backend_process.__dict__ if status2.backend_process else None
        }
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()
