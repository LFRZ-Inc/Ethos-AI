#!/usr/bin/env python3
"""
Test script to diagnose Node.js installation issues
"""

import os
import subprocess
import sys

def test_command(cmd, name):
    """Test if a command is available"""
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {name}: {version}")
            return True
        else:
            print(f"❌ {name}: Command failed")
            return False
    except FileNotFoundError:
        print(f"❌ {name}: Command not found")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def check_path():
    """Check PATH environment variable"""
    print("\n🔍 Checking PATH environment variable...")
    path = os.environ.get('PATH', '')
    path_dirs = path.split(os.pathsep)
    
    print(f"PATH contains {len(path_dirs)} directories:")
    for i, dir_path in enumerate(path_dirs[:10]):  # Show first 10
        print(f"  {i+1}. {dir_path}")
    
    if len(path_dirs) > 10:
        print(f"  ... and {len(path_dirs) - 10} more")
    
    # Check for Node.js related paths
    node_paths = [p for p in path_dirs if 'node' in p.lower()]
    if node_paths:
        print(f"\n✅ Found Node.js related paths:")
        for path in node_paths:
            print(f"  📁 {path}")
    else:
        print("\n⚠️ No Node.js related paths found in PATH")

def check_common_node_locations():
    """Check common Node.js installation locations"""
    print("\n🔍 Checking common Node.js installation locations...")
    
    common_locations = [
        "C:\\Program Files\\nodejs",
        "C:\\Program Files (x86)\\nodejs",
        os.path.expanduser("~\\AppData\\Roaming\\npm"),
        os.path.expanduser("~\\AppData\\Local\\npm"),
    ]
    
    for location in common_locations:
        if os.path.exists(location):
            print(f"✅ Found: {location}")
            # Check for node.exe
            node_exe = os.path.join(location, "node.exe")
            if os.path.exists(node_exe):
                print(f"  📄 node.exe found")
            # Check for npm.cmd
            npm_cmd = os.path.join(location, "npm.cmd")
            if os.path.exists(npm_cmd):
                print(f"  📄 npm.cmd found")
        else:
            print(f"❌ Not found: {location}")

def main():
    """Main test function"""
    print("🔍 Node.js Installation Diagnostic")
    print("=" * 40)
    
    # Test commands
    print("Testing commands...")
    node_ok = test_command('node', 'Node.js')
    npm_ok = test_command('npm', 'npm')
    npx_ok = test_command('npx', 'npx')
    
    # Check PATH
    check_path()
    
    # Check common locations
    check_common_node_locations()
    
    # Summary
    print("\n📊 Summary:")
    if node_ok and npm_ok and npx_ok:
        print("✅ All commands working correctly!")
        print("🚀 You should be able to run the React Native setup")
    else:
        print("❌ Some commands are not working")
        print("\n🔧 Troubleshooting:")
        if not node_ok:
            print("  - Node.js not found in PATH")
            print("  - Try reinstalling Node.js from https://nodejs.org/")
        if not npm_ok:
            print("  - npm not found (should come with Node.js)")
            print("  - Try reinstalling Node.js")
        if not npx_ok:
            print("  - npx not found (should come with npm)")
            print("  - Try reinstalling Node.js")
        
        print("\n💡 Quick fix:")
        print("  1. Download Node.js from https://nodejs.org/")
        print("  2. Install with default settings")
        print("  3. Restart your terminal/PowerShell")
        print("  4. Try running the setup script again")

if __name__ == "__main__":
    main()
