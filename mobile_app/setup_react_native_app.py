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
    
    # Add Node.js to PATH if not already there
    nodejs_path = r"C:\Program Files\nodejs"
    current_path = os.environ.get('PATH', '')
    if nodejs_path not in current_path:
        os.environ['PATH'] = nodejs_path + os.pathsep + current_path
        print(f"✅ Added {nodejs_path} to PATH")
    
    # Check Node.js first
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if node_result.returncode == 0:
            node_version = node_result.stdout.strip()
            print(f"✅ Node.js: {node_version}")
        else:
            print("❌ Node.js not found")
            return False
    except:
        print("❌ Node.js not found")
        return False
    
    # Check npm (should come with Node.js)
    try:
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if npm_result.returncode == 0:
            npm_version = npm_result.stdout.strip()
            print(f"✅ npm: {npm_version}")
        else:
            print("❌ npm not found")
            return False
    except:
        print("❌ npm not found")
        return False
    
    # Check npx (should come with npm)
    try:
        npx_result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        if npx_result.returncode == 0:
            npx_version = npx_result.stdout.strip()
            print(f"✅ npx: {npx_version}")
        else:
            print("❌ npx not found")
            return False
    except:
        print("❌ npx not found")
        return False
    
    # Check React Native CLI
    try:
        rn_result = subprocess.run(['npx', 'react-native', '--version'], capture_output=True, text=True)
        if rn_result.returncode == 0:
            rn_version = rn_result.stdout.strip()
            print(f"✅ React Native CLI: {rn_version}")
        else:
            print("⚠️ React Native CLI not found, will install automatically")
    except:
        print("⚠️ React Native CLI not found, will install automatically")
    
    return True

def install_react_native_cli():
    """Install React Native CLI globally"""
    print("\n📦 Installing React Native CLI...")
    try:
        result = subprocess.run(['npm', 'install', '-g', '@react-native-community/cli'], check=True)
        print("✅ React Native CLI installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install React Native CLI: {e}")
        return False

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
        # Create React Native app using npx
        print("⏳ Creating React Native app (this may take a few minutes)...")
        result = subprocess.run([
            'npx', 'react-native@0.72.6', 'init', app_name,
            '--template', 'react-native-template-typescript'
        ], check=True, capture_output=True, text=True)
        
        print(f"✅ React Native app created: {app_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create React Native app: {e}")
        print(f"Error output: {e.stderr}")
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
        print("⏳ Installing dependencies (this may take a few minutes)...")
        result = subprocess.run(['npm', 'install'], check=True, capture_output=True, text=True)
        print("✅ Dependencies installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_android():
    """Setup Android development environment"""
    print("\n🤖 Setting up Android...")
    
    try:
        # Check if Android SDK is available
        android_home = os.environ.get('ANDROID_HOME')
        if not android_home:
            # Try common Android Studio paths
            common_paths = [
                os.path.expanduser("~/AppData/Local/Android/Sdk"),
                "C:/Users/Public/Android/Sdk",
                "C:/Program Files/Android/Android Studio/Sdk",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    android_home = path
                    print(f"✅ Found Android SDK at: {android_home}")
                    break
        
        if not android_home:
            print("⚠️ ANDROID_HOME not set and Android SDK not found in common locations")
            print("📥 Please install Android Studio and set ANDROID_HOME")
            print("   Or manually set ANDROID_HOME environment variable")
            return False
        
        print(f"✅ Android SDK found: {android_home}")
        
        # Check for Android emulator or connected device
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')[1:]
                connected_devices = [d for d in devices if d.strip() and 'device' in d]
                
                if connected_devices:
                    print(f"✅ Found {len(connected_devices)} connected device(s)")
                    for device in connected_devices:
                        print(f"   📱 {device}")
                    return True
                else:
                    print("⚠️ No Android devices connected")
                    print("📱 Please connect your Z Fold 4 or start an emulator")
                    print("   Make sure USB debugging is enabled on your device")
                    return False
            else:
                print("⚠️ adb command not found")
                print("📥 Please install Android SDK platform-tools")
                return False
        except FileNotFoundError:
            print("⚠️ adb command not found")
            print("📥 Please install Android SDK platform-tools")
            return False
        
    except Exception as e:
        print(f"❌ Android setup failed: {e}")
        return False

def build_and_run():
    """Build and run the app"""
    print("\n🚀 Building and running the app...")
    
    try:
        # Start Metro bundler in background
        print("📱 Starting Metro bundler...")
        metro_process = subprocess.Popen(['npx', 'react-native', 'start'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)
        
        # Wait a moment for Metro to start
        import time
        time.sleep(5)
        
        # Run on Android
        print("🤖 Building and installing on Android...")
        print("⏳ This may take several minutes on first build...")
        
        result = subprocess.run(['npx', 'react-native', 'run-android'], 
                              check=True, 
                              capture_output=True, 
                              text=True)
        
        print("✅ App built and installed successfully!")
        print("\n🎉 Ethos AI Mobile App is now running on your device!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build and run: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Ethos AI - React Native Mobile App Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed")
        print("📥 Please ensure Node.js is properly installed and in your PATH")
        return
    
    # Install React Native CLI if needed
    try:
        subprocess.run(['npx', 'react-native', '--version'], check=True, capture_output=True)
    except:
        if not install_react_native_cli():
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
    android_ok = setup_android()
    if not android_ok:
        print("\n⚠️ Android setup incomplete, but you can still build the app")
        print("📱 Make sure to:")
        print("   1. Connect your Z Fold 4 via USB")
        print("   2. Enable Developer Options and USB Debugging")
        print("   3. Or start an Android emulator")
    
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
