# React Native Ethos AI Mobile App Setup Script
Write-Host "🚀 Ethos AI - React Native Mobile App Setup" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Add Node.js to PATH
$nodejsPath = "C:\Program Files\nodejs"
if ($env:PATH -notlike "*$nodejsPath*") {
    $env:PATH = "$nodejsPath;$env:PATH"
    Write-Host "✅ Added Node.js to PATH" -ForegroundColor Green
}

# Check requirements
Write-Host "`n🔍 Checking requirements..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found" -ForegroundColor Red
    exit 1
}

# Check npx
try {
    $npxVersion = npx --version
    Write-Host "✅ npx: $npxVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npx not found" -ForegroundColor Red
    exit 1
}

# Check React Native CLI
try {
    $rnVersion = npx react-native --version
    Write-Host "✅ React Native CLI: $rnVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ React Native CLI not found, will install automatically" -ForegroundColor Yellow
}

# Create React Native app
Write-Host "`n🚀 Creating React Native app..." -ForegroundColor Yellow

$appName = "EthosAIMobile"
$appDir = Get-Location | Join-Path -ChildPath $appName

if (Test-Path $appDir) {
    Write-Host "⚠️ App directory $appName already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove it and create a new one? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force $appDir
    } else {
        Write-Host "❌ Setup cancelled" -ForegroundColor Red
        exit 1
    }
}

try {
    Write-Host "⏳ Creating React Native app (this may take a few minutes)..." -ForegroundColor Yellow
    npx react-native@0.72.6 init $appName --template react-native-template-typescript
    Write-Host "✅ React Native app created: $appName" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create React Native app" -ForegroundColor Red
    exit 1
}

# Copy app files
Write-Host "`n📁 Copying app files..." -ForegroundColor Yellow

try {
    # Copy package.json
    Copy-Item "ReactNativeApp\package.json" "$appDir\package.json" -Force
    Write-Host "✅ package.json copied" -ForegroundColor Green
    
    # Copy App.tsx
    Copy-Item "ReactNativeApp\App.tsx" "$appDir\App.tsx" -Force
    Write-Host "✅ App.tsx copied" -ForegroundColor Green
    
    # Copy src directory
    if (Test-Path "$appDir\src") {
        Remove-Item -Recurse -Force "$appDir\src"
    }
    Copy-Item "ReactNativeApp\src" "$appDir\src" -Recurse -Force
    Write-Host "✅ src directory copied" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to copy app files" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow

try {
    Set-Location $appDir
    Write-Host "⏳ Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup Android
Write-Host "`n🤖 Setting up Android..." -ForegroundColor Yellow

try {
    # Check if Android SDK is available
    $androidHome = $env:ANDROID_HOME
    if (-not $androidHome) {
        # Try common Android Studio paths
        $commonPaths = @(
            "$env:USERPROFILE\AppData\Local\Android\Sdk",
            "C:\Users\Public\Android\Sdk",
            "C:\Program Files\Android\Android Studio\Sdk"
        )
        
        foreach ($path in $commonPaths) {
            if (Test-Path $path) {
                $androidHome = $path
                Write-Host "✅ Found Android SDK at: $androidHome" -ForegroundColor Green
                break
            }
        }
    }
    
    if (-not $androidHome) {
        Write-Host "⚠️ ANDROID_HOME not set and Android SDK not found in common locations" -ForegroundColor Yellow
        Write-Host "📥 Please install Android Studio and set ANDROID_HOME" -ForegroundColor Yellow
        Write-Host "   Or manually set ANDROID_HOME environment variable" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Android SDK found: $androidHome" -ForegroundColor Green
    }
    
    # Check for Android emulator or connected device
    try {
        $devices = adb devices
        $connectedDevices = $devices | Where-Object { $_ -match "device$" }
        
        if ($connectedDevices) {
            Write-Host "✅ Found $($connectedDevices.Count) connected device(s)" -ForegroundColor Green
            foreach ($device in $connectedDevices) {
                Write-Host "   📱 $device" -ForegroundColor Green
            }
        } else {
            Write-Host "⚠️ No Android devices connected" -ForegroundColor Yellow
            Write-Host "📱 Please connect your Z Fold 4 or start an emulator" -ForegroundColor Yellow
            Write-Host "   Make sure USB debugging is enabled on your device" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ adb command not found" -ForegroundColor Yellow
        Write-Host "📥 Please install Android SDK platform-tools" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Android setup failed" -ForegroundColor Red
}

# Build and run
Write-Host "`n🚀 Building and running the app..." -ForegroundColor Yellow

try {
    # Start Metro bundler in background
    Write-Host "📱 Starting Metro bundler..." -ForegroundColor Yellow
    Start-Process -NoNewWindow -FilePath "npx" -ArgumentList "react-native", "start"
    
    # Wait a moment for Metro to start
    Start-Sleep -Seconds 5
    
    # Run on Android
    Write-Host "🤖 Building and installing on Android..." -ForegroundColor Yellow
    Write-Host "⏳ This may take several minutes on first build..." -ForegroundColor Yellow
    
    npx react-native run-android
    
    Write-Host "✅ App built and installed successfully!" -ForegroundColor Green
    Write-Host "`n🎉 Ethos AI Mobile App is now running on your device!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to build and run" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 Setup Complete!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. The app should now be running on your Z Fold 4" -ForegroundColor White
Write-Host "2. Download AI models from the Model Manager" -ForegroundColor White
Write-Host "3. Start chatting with your personal AI assistant!" -ForegroundColor White
Write-Host "`n🔧 Development:" -ForegroundColor Yellow
Write-Host "- Edit files in EthosAIMobile/src/" -ForegroundColor White
Write-Host "- Run 'npx react-native run-android' to rebuild" -ForegroundColor White
Write-Host "- Check logs with 'npx react-native log-android'" -ForegroundColor White
