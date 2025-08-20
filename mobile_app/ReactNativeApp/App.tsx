import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  Platform,
  Alert,
  PermissionsAndroid,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Toast from 'react-native-toast-message';

// Screens
import HomeScreen from './src/screens/HomeScreen';
import ChatScreen from './src/screens/ChatScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import ModelManagerScreen from './src/screens/ModelManagerScreen';

// Services
import { EmbeddedAIService } from './src/services/EmbeddedAIService';
import { DeviceInfoService } from './src/services/DeviceInfoService';
import { StorageService } from './src/services/StorageService';

// Types
import { RootStackParamList } from './src/types/navigation';

const Stack = createStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [deviceInfo, setDeviceInfo] = useState<any>(null);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      console.log('🚀 Initializing Ethos AI Mobile App...');

      // Request permissions
      await requestPermissions();

      // Get device information
      const info = await DeviceInfoService.getDeviceInfo();
      setDeviceInfo(info);
      console.log('📱 Device Info:', info);

      // Initialize storage
      await StorageService.initialize();

      // Initialize embedded AI service
      await EmbeddedAIService.initialize(info);

      setIsInitialized(true);
      console.log('✅ App initialized successfully');

      Toast.show({
        type: 'success',
        text1: 'Ethos AI Ready!',
        text2: 'Your personal AI assistant is ready to use.',
      });

    } catch (error) {
      console.error('❌ App initialization failed:', error);
      Alert.alert(
        'Initialization Error',
        'Failed to initialize Ethos AI. Please restart the app.',
        [{ text: 'OK' }]
      );
    }
  };

  const requestPermissions = async () => {
    if (Platform.OS === 'android') {
      try {
        const permissions = [
          PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
          PermissionsAndroid.PERMISSIONS.INTERNET,
        ];

        const granted = await PermissionsAndroid.requestMultiple(permissions);
        
        const allGranted = Object.values(granted).every(
          permission => permission === PermissionsAndroid.RESULTS.GRANTED
        );

        if (!allGranted) {
          console.warn('⚠️ Some permissions were not granted');
        }
      } catch (error) {
        console.error('❌ Permission request failed:', error);
      }
    }
  };

  if (!isInitialized) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>🚀 Initializing Ethos AI...</Text>
        <Text style={styles.loadingSubtext}>Setting up your personal AI assistant</Text>
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar
        barStyle="light-content"
        backgroundColor="#1a1a1a"
        translucent={true}
      />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Home"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1a1a1a',
            },
            headerTintColor: '#ffffff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
            cardStyle: { backgroundColor: '#1a1a1a' },
          }}
        >
          <Stack.Screen
            name="Home"
            component={HomeScreen}
            options={{
              title: 'Ethos AI',
              headerShown: false,
            }}
          />
          <Stack.Screen
            name="Chat"
            component={ChatScreen}
            options={{
              title: 'AI Chat',
              headerBackTitle: 'Back',
            }}
          />
          <Stack.Screen
            name="Settings"
            component={SettingsScreen}
            options={{
              title: 'Settings',
              headerBackTitle: 'Back',
            }}
          />
          <Stack.Screen
            name="ModelManager"
            component={ModelManagerScreen}
            options={{
              title: 'Model Manager',
              headerBackTitle: 'Back',
            }}
          />
        </Stack.Navigator>
      </NavigationContainer>
      <Toast />
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
  },
  loadingText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
  },
  loadingSubtext: {
    fontSize: 16,
    color: '#888888',
    textAlign: 'center',
  },
});

export default App;
