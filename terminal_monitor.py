#!/usr/bin/env python3
"""
Frontend & Backend Terminal Status Monitor
Check existing terminal processes without starting new ones
"""

import time
import psutil
import sys
from pathlib import Path
from datetime import datetime

def check_process_by_port(port, service_name):
    """Check if a process is running on specific port"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time', 'cwd']):
            try:
                connections = proc.connections(kind='inet')
                for conn in connections:
                    if conn.laddr.port == port:
                        return {
                            'found': True,
                            'pid': proc.pid,
                            'name': proc.info['name'],
                            'status': proc.info['status'],
                            'cmdline': ' '.join(proc.info['cmdline'] or []),
                            'cwd': proc.info['cwd'] or 'N/A',
                            'cpu_percent': proc.cpu_percent(),
                            'memory_mb': proc.memory_info().rss / 1024 / 1024,
                            'create_time': datetime.fromtimestamp(proc.info['create_time']).strftime('%H:%M:%S')
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error checking {service_name}: {e}")
    
    return {'found': False}

def check_port_active(port):
    """Simple port check"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def display_service_status(name, port, process_info, port_active):
    """Display formatted service status"""
    status_icon = "🟢" if port_active else "🔴"
    print(f"\n{status_icon} {name} (Port {port}):")
    
    if process_info['found']:
        print(f"   📱 Process: {process_info['name']} (PID: {process_info['pid']})")
        print(f"   📂 Directory: {process_info['cwd']}")
        print(f"   💾 Memory: {process_info['memory_mb']:.1f} MB")
        print(f"   ⚡ CPU: {process_info['cpu_percent']:.1f}%")
        print(f"   🕐 Started: {process_info['create_time']}")
        print(f"   📋 Status: {process_info['status']}")
        if len(process_info['cmdline']) > 80:
            print(f"   💻 Command: {process_info['cmdline'][:80]}...")
        else:
            print(f"   💻 Command: {process_info['cmdline']}")
    else:
        print(f"   ❌ No process found on port {port}")
    
    print(f"   🔌 Port Status: {'ACTIVE' if port_active else 'INACTIVE'}")

def get_system_overview():
    """Get basic system stats"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'memory_available_gb': memory.available / 1024 / 1024 / 1024
    }

def main():
    """Main monitoring function"""
    print("🔍 Frontend & Backend Terminal Status Monitor")
    print("=" * 55)
    print("📝 Note: This script never starts any services, only monitors existing ones")
    
    # Check 1: Initial status
    print(f"\n📋 Status Check #1 - {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 40)
    
    # Backend check (port 8000)
    backend_proc_1 = check_process_by_port(8000, "Backend")
    backend_port_1 = check_port_active(8000)
    display_service_status("Backend", 8000, backend_proc_1, backend_port_1)
    
    # Frontend check (port 3000) 
    frontend_proc_1 = check_process_by_port(3000, "Frontend")
    frontend_port_1 = check_port_active(3000)
    display_service_status("Frontend", 3000, frontend_proc_1, frontend_port_1)
    
    # System overview
    sys_1 = get_system_overview()
    print(f"\n🖥️  System Overview:")
    print(f"   CPU: {sys_1['cpu_percent']:.1f}% | Memory: {sys_1['memory_percent']:.1f}% | Available: {sys_1['memory_available_gb']:.1f} GB")
    
    # Wait 5 seconds with countdown
    print(f"\n⏳ Waiting 5 seconds to re-check...")
    for i in range(5, 0, -1):
        print(f"   {i}s remaining...", end="\r")
        time.sleep(1)
    print("   ✅ Wait complete!   ")
    
    # Check 2: After 5 seconds
    print(f"\n📋 Status Check #2 - {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 40)
    
    # Backend check
    backend_proc_2 = check_process_by_port(8000, "Backend")
    backend_port_2 = check_port_active(8000)
    display_service_status("Backend", 8000, backend_proc_2, backend_port_2)
    
    # Frontend check
    frontend_proc_2 = check_process_by_port(3000, "Frontend")
    frontend_port_2 = check_port_active(3000)
    display_service_status("Frontend", 3000, frontend_proc_2, frontend_port_2)
    
    # System overview
    sys_2 = get_system_overview()
    print(f"\n🖥️  System Overview:")
    print(f"   CPU: {sys_2['cpu_percent']:.1f}% | Memory: {sys_2['memory_percent']:.1f}% | Available: {sys_2['memory_available_gb']:.1f} GB")
    
    # Comparison
    print(f"\n🔄 5-Second Comparison:")
    print("-" * 25)
    
    # Backend comparison
    if backend_proc_1['found'] == backend_proc_2['found']:
        if backend_proc_1['found']:
            print(f"🔸 Backend: Process unchanged (PID {backend_proc_1['pid']})")
        else:
            print(f"🔸 Backend: No process found (both checks)")
    else:
        print(f"🔸 Backend: Process status changed!")
    
    if backend_port_1 == backend_port_2:
        print(f"🔸 Backend Port: Unchanged ({'Active' if backend_port_1 else 'Inactive'})")
    else:
        print(f"🔸 Backend Port: Changed from {'Active' if backend_port_1 else 'Inactive'} to {'Active' if backend_port_2 else 'Inactive'}")
    
    # Frontend comparison
    if frontend_proc_1['found'] == frontend_proc_2['found']:
        if frontend_proc_1['found']:
            print(f"🔸 Frontend: Process unchanged (PID {frontend_proc_1['pid']})")
        else:
            print(f"🔸 Frontend: No process found (both checks)")
    else:
        print(f"🔸 Frontend: Process status changed!")
    
    if frontend_port_1 == frontend_port_2:
        print(f"🔸 Frontend Port: Unchanged ({'Active' if frontend_port_1 else 'Inactive'})")
    else:
        print(f"🔸 Frontend Port: Changed from {'Active' if frontend_port_1 else 'Inactive'} to {'Active' if frontend_port_2 else 'Inactive'}")
    
    # System comparison
    cpu_diff = sys_2['cpu_percent'] - sys_1['cpu_percent']
    mem_diff = sys_2['memory_percent'] - sys_1['memory_percent']
    print(f"🔸 CPU Usage: {sys_1['cpu_percent']:.1f}% → {sys_2['cpu_percent']:.1f}% ({cpu_diff:+.1f}%)")
    print(f"🔸 Memory Usage: {sys_1['memory_percent']:.1f}% → {sys_2['memory_percent']:.1f}% ({mem_diff:+.1f}%)")
    
    print(f"\n✅ Terminal monitoring complete - No services were started!")

if __name__ == "__main__":
    main()
