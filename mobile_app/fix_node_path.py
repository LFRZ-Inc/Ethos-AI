#!/usr/bin/env python3
"""
Fix Node.js PATH for current session
"""

import os
import subprocess
import sys

def fix_path():
    """Add Node.js to PATH for current session"""
    nodejs_path = r"C:\Program Files\nodejs"
    
    # Get current PATH
    current_path = os.environ.get('PATH', '')
    
    # Check if Node.js path is already in PATH
    if nodejs_path not in current_path:
        # Add Node.js path to beginning of PATH
        new_path = nodejs_path + os.pathsep + current_path
        os.environ['PATH'] = new_path
        print(f"✅ Added {nodejs_path} to PATH")
    else:
        print(f"✅ {nodejs_path} already in PATH")
    
    # Test the commands
    print("\n🔍 Testing commands with fixed PATH...")
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm: {result.stdout.strip()}")
        else:
            print("❌ npm still not working")
    except:
        print("❌ npm still not working")
    
    try:
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npx: {result.stdout.strip()}")
        else:
            print("❌ npx still not working")
    except:
        print("❌ npx still not working")

def main():
    """Main function"""
    print("🔧 Fixing Node.js PATH for current session...")
    fix_path()
    
    print("\n💡 Note: This fix only applies to the current session.")
    print("   For a permanent fix, add 'C:\\Program Files\\nodejs' to your PATH environment variable.")
    print("\n🚀 You can now run the React Native setup script!")

if __name__ == "__main__":
    main()
