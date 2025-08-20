#!/usr/bin/env python3
"""
Setup script for React Native Ethos AI Mobile App
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        'node': 'Node.js',
        'npm': 'npm',
        'npx': 'npx',
    }
    
    missing = []
    
    for cmd, name in requirements.items():
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {name}: {version}")
            else:
                missing.append(name)
        except:
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing requirements: {', '.join(missing)}")
        print("\n📥 Please install:")
        print("   Node.js: https://nodejs.org/")
        print("   React Native CLI: npm install -g @react-native-community/cli")
        return False
    
    return True

def create_react_native_app():
    """Create the React Native app"""
    print("\n🚀 Creating React Native app...")
    
    app_name = "EthosAIMobile"
    app_dir = Path(app_name)
    
    if app_dir.exists():
        print(f"⚠️ App directory {app_name} already exists")
        response = input("Do you want to remove it and create a new one? (y/N): ")
        if response.lower() == 'y':
            shutil.rmtree(app_dir)
        else:
            print("❌ Setup cancelled")
            return False
    
    try:
        # Create React Native app
        result = subprocess.run([
            'npx', 'react-native@0.72.6', 'init', app_name,
            '--template', 'react-native-template-typescript'
        ], check=True)
        
        print(f"✅ React Native app created: {app_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create React Native app: {e}")
        return False

def copy_app_files():
    """Copy our app files to the React Native project"""
    print("\n📁 Copying app files...")
    
    app_dir = Path("EthosAIMobile")
    source_dir = Path(__file__).parent / "ReactNativeApp"
    
    try:
        # Copy package.json
        shutil.copy2(source_dir / "package.json", app_dir / "package.json")
        print("✅ package.json copied")
        
        # Copy App.tsx
        shutil.copy2(source_dir / "App.tsx", app_dir / "App.tsx")
        print("✅ App.tsx copied")
        
        # Copy src directory
        src_source = source_dir / "src"
        src_dest = app_dir / "src"
        
        if src_dest.exists():
            shutil.rmtree(src_dest)
        
        shutil.copytree(src_source, src_dest)
        print("✅ src directory copied")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to copy app files: {e}")
        return False

def install_dependencies():
    """Install app dependencies"""
    print("\n📦 Installing dependencies...")
    
    app_dir = Path("EthosAIMobile")
    
    try:
        # Change to app directory
        os.chdir(app_dir)
        
        # Install dependencies
        result = subprocess.run(['npm', 'install'], check=True)
        print("✅ Dependencies installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_android():
    """Setup Android development environment"""
    print("\n🤖 Setting up Android...")
    
    try:
        # Check if Android SDK is available
        android_home = os.environ.get('ANDROID_HOME')
        if not android_home:
            print("⚠️ ANDROID_HOME not set")
            print("📥 Please install Android Studio and set ANDROID_HOME")
            return False
        
        print(f"✅ Android SDK found: {android_home}")
        
        # Check for Android emulator or connected device
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')[1:]
            connected_devices = [d for d in devices if d.strip() and 'device' in d]
            
            if connected_devices:
                print(f"✅ Found {len(connected_devices)} connected device(s)")
                return True
            else:
                print("⚠️ No Android devices connected")
                print("📱 Please connect your Z Fold 4 or start an emulator")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Android setup failed: {e}")
        return False

def build_and_run():
    """Build and run the app"""
    print("\n🚀 Building and running the app...")
    
    try:
        # Start Metro bundler
        print("📱 Starting Metro bundler...")
        metro_process = subprocess.Popen(['npx', 'react-native', 'start'])
        
        # Wait a moment for Metro to start
        import time
        time.sleep(3)
        
        # Run on Android
        print("🤖 Running on Android...")
        result = subprocess.run(['npx', 'react-native', 'run-android'], check=True)
        
        print("✅ App built and installed successfully!")
        print("\n🎉 Ethos AI Mobile App is now running on your device!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build and run: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Ethos AI - React Native Mobile App Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Create React Native app
    if not create_react_native_app():
        return
    
    # Copy app files
    if not copy_app_files():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Setup Android
    if not setup_android():
        print("\n⚠️ Android setup incomplete, but you can still build the app")
        print("📱 Make sure to connect your Z Fold 4 or start an emulator")
    
    # Build and run
    if not build_and_run():
        return
    
    print("\n🎯 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. The app should now be running on your Z Fold 4")
    print("2. Download AI models from the Model Manager")
    print("3. Start chatting with your personal AI assistant!")
    print("\n🔧 Development:")
    print("- Edit files in EthosAIMobile/src/")
    print("- Run 'npx react-native run-android' to rebuild")
    print("- Check logs with 'npx react-native log-android'")

if __name__ == "__main__":
    main()
