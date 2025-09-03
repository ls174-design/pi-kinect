#!/usr/bin/env python3
"""
Comprehensive SSH failure analysis
This script will systematically analyze why SSH connections are failing
"""

import subprocess
import sys
import socket
import time

def test_network_connectivity(host, port=22):
    """Test basic network connectivity to the Pi"""
    print(f"🔍 Testing network connectivity to {host}:{port}")
    print("="*60)
    
    # Test 1: Ping test
    print("1. Ping test...")
    try:
        result = subprocess.run(f"ping -n 1 {host}", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ping successful - Pi is reachable")
        else:
            print("❌ Ping failed - Pi is not reachable")
            print("   This could be:")
            print("   - Pi is powered off")
            print("   - Network connectivity issue")
            print("   - Pi IP address changed")
            return False
    except Exception as e:
        print(f"❌ Ping test error: {e}")
        return False
    
    # Test 2: Port connectivity test
    print("\n2. Port connectivity test...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is open and accepting connections")
        else:
            print(f"❌ Port {port} is not accessible")
            print("   This indicates:")
            print("   - SSH service is not running")
            print("   - Firewall is blocking the port")
            print("   - Service is bound to wrong interface")
            return False
    except Exception as e:
        print(f"❌ Port test error: {e}")
        return False
    
    return True

def test_ssh_service_status(host):
    """Test SSH service status using various methods"""
    print(f"\n🔍 Testing SSH service status on {host}")
    print("="*60)
    
    # Test 1: Telnet test
    print("1. Telnet test...")
    try:
        result = subprocess.run(f"telnet {host} 22", shell=True, capture_output=True, text=True, timeout=10)
        if "Connected" in result.stdout or "SSH" in result.stdout:
            print("✅ SSH service is responding")
            print(f"   Response: {result.stdout.strip()[:100]}...")
        else:
            print("❌ SSH service is not responding")
            print("   This could be:")
            print("   - SSH service is not running")
            print("   - SSH is configured on different port")
            print("   - Firewall is blocking connections")
    except Exception as e:
        print(f"❌ Telnet test error: {e}")
    
    # Test 2: Nmap port scan
    print("\n2. Port scan test...")
    try:
        result = subprocess.run(f"nmap -p 22 {host}", shell=True, capture_output=True, text=True, timeout=15)
        if "open" in result.stdout:
            print("✅ Port 22 is open (nmap)")
        elif "filtered" in result.stdout:
            print("⚠️  Port 22 is filtered (likely firewall)")
        elif "closed" in result.stdout:
            print("❌ Port 22 is closed (service not running)")
        else:
            print("❌ Port 22 status unknown")
    except Exception as e:
        print(f"❌ Nmap test error: {e}")

def analyze_firewall_indicators(host):
    """Analyze indicators that suggest firewall issues"""
    print(f"\n🔍 Analyzing firewall indicators for {host}")
    print("="*60)
    
    # Test multiple ports to see if it's a blanket block
    ports_to_test = [22, 80, 443, 8080, 21, 23]
    
    print("Testing multiple ports to detect firewall patterns...")
    open_ports = []
    filtered_ports = []
    closed_ports = []
    
    for port in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                open_ports.append(port)
            elif result == 10061:  # Windows: Connection refused
                closed_ports.append(port)
            elif result == 10060:  # Windows: Connection timed out
                filtered_ports.append(port)
            else:
                filtered_ports.append(port)
                
        except Exception as e:
            filtered_ports.append(port)
    
    print(f"Open ports: {open_ports}")
    print(f"Closed ports: {closed_ports}")
    print(f"Filtered/Timed out ports: {filtered_ports}")
    
    # Analyze the pattern
    if len(filtered_ports) > len(open_ports) + len(closed_ports):
        print("\n🚨 FIREWALL DETECTED!")
        print("   Most ports are filtered/timing out")
        print("   This strongly suggests a firewall is blocking connections")
        return True
    elif 22 in filtered_ports:
        print("\n⚠️  SSH PORT FILTERED!")
        print("   Port 22 is being filtered/timing out")
        print("   This suggests SSH is blocked by firewall")
        return True
    elif 22 in closed_ports:
        print("\n❌ SSH SERVICE NOT RUNNING!")
        print("   Port 22 is closed (connection refused)")
        print("   SSH service is not running on the Pi")
        return False
    else:
        print("\n✅ No obvious firewall blocking detected")
        return False

def test_ssh_connection_attempts(host, user):
    """Test different SSH connection methods"""
    print(f"\n🔍 Testing SSH connection methods to {user}@{host}")
    print("="*60)
    
    methods = [
        {
            "name": "Basic SSH",
            "cmd": f"ssh -o ConnectTimeout=5 -o BatchMode=yes {user}@{host} 'echo test'"
        },
        {
            "name": "SSH with password auth",
            "cmd": f"ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=5 -o BatchMode=yes {user}@{host} 'echo test'"
        },
        {
            "name": "SSH with no host key check",
            "cmd": f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 -o BatchMode=yes {user}@{host} 'echo test'"
        },
        {
            "name": "SSH with verbose output",
            "cmd": f"ssh -v -o ConnectTimeout=5 -o BatchMode=yes {user}@{host} 'echo test'"
        }
    ]
    
    for method in methods:
        print(f"\nTesting: {method['name']}")
        try:
            result = subprocess.run(method['cmd'], shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ {method['name']}: SUCCESS")
            else:
                print(f"❌ {method['name']}: FAILED")
                if result.stderr:
                    error_msg = result.stderr.strip()
                    print(f"   Error: {error_msg}")
                    
                    # Analyze error messages
                    if "Connection refused" in error_msg:
                        print("   → SSH service is not running")
                    elif "Connection timed out" in error_msg:
                        print("   → Firewall is blocking SSH")
                    elif "Permission denied" in error_msg:
                        print("   → Authentication failed (service is running)")
                    elif "Host key verification failed" in error_msg:
                        print("   → Host key issue (service is running)")
                        
        except subprocess.TimeoutExpired:
            print(f"⏰ {method['name']}: TIMEOUT")
        except Exception as e:
            print(f"❌ {method['name']}: ERROR - {e}")

def generate_firewall_fix_instructions():
    """Generate instructions to fix firewall issues"""
    print("\n🔧 FIREWALL FIX INSTRUCTIONS")
    print("="*60)
    
    instructions = """
## Pi Firewall Configuration Fix

### Method 1: Disable UFW Firewall (Temporary)
```bash
# On the Pi, run:
sudo ufw disable
sudo ufw status
```

### Method 2: Allow SSH through UFW
```bash
# On the Pi, run:
sudo ufw allow ssh
sudo ufw allow 22
sudo ufw enable
sudo ufw status
```

### Method 3: Check iptables rules
```bash
# On the Pi, run:
sudo iptables -L
sudo iptables -F  # Flush all rules (temporary)
```

### Method 4: Check SSH service status
```bash
# On the Pi, run:
sudo systemctl status ssh
sudo systemctl start ssh
sudo systemctl enable ssh
```

### Method 5: Check SSH configuration
```bash
# On the Pi, run:
sudo nano /etc/ssh/sshd_config
# Look for:
# Port 22
# PermitRootLogin no
# PasswordAuthentication yes
# PubkeyAuthentication yes

# Then restart SSH:
sudo systemctl restart ssh
```

### Method 6: Check if SSH is bound to correct interface
```bash
# On the Pi, run:
sudo netstat -tlnp | grep ssh
# Should show: 0.0.0.0:22 (not 127.0.0.1:22)
```

## Quick Fix Commands (Run on Pi):
```bash
# Disable firewall temporarily
sudo ufw disable

# Start SSH service
sudo systemctl start ssh

# Check status
sudo systemctl status ssh
sudo ufw status
```

## Test from Windows:
```bash
# Test connection
ssh ls@192.168.1.9

# Or with verbose output
ssh -v ls@192.168.1.9
```
"""
    
    print(instructions)
    
    # Save to file
    with open("FIREWALL_FIX_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    print("✅ Instructions saved to FIREWALL_FIX_INSTRUCTIONS.txt")

def main():
    """Main analysis function"""
    print("🔍 SSH CONNECTION FAILURE ANALYSIS")
    print("="*60)
    print("This tool will systematically analyze why SSH connections are failing")
    print()
    
    host = "192.168.1.9"
    user = "ls"
    
    # Step 1: Test basic connectivity
    if not test_network_connectivity(host):
        print("\n❌ BASIC CONNECTIVITY FAILED")
        print("   Cannot proceed with SSH analysis")
        print("   Check Pi power, network, and IP address")
        return
    
    # Step 2: Test SSH service status
    test_ssh_service_status(host)
    
    # Step 3: Analyze firewall indicators
    firewall_detected = analyze_firewall_indicators(host)
    
    # Step 4: Test SSH connection methods
    test_ssh_connection_attempts(host, user)
    
    # Step 5: Generate fix instructions
    if firewall_detected:
        print("\n🚨 CONCLUSION: FIREWALL IS LIKELY BLOCKING SSH")
        generate_firewall_fix_instructions()
    else:
        print("\n🔍 CONCLUSION: FIREWALL NOT DETECTED")
        print("   Issue is likely:")
        print("   - SSH service not running")
        print("   - SSH configuration problem")
        print("   - Authentication issue")
        generate_firewall_fix_instructions()  # Still provide instructions
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
