import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { SafeAreaView } from 'react-native-safe-area-context';
import Toast from 'react-native-toast-message';

// Services
import { EmbeddedAIService } from '../services/EmbeddedAIService';
import { DeviceInfoService } from '../services/DeviceInfoService';

// Types
import { RootStackParamList } from '../types/navigation';
import { AIModel, DeviceSpecs } from '../services/EmbeddedAIService';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [isLoading, setIsLoading] = useState(true);
  const [deviceSpecs, setDeviceSpecs] = useState<DeviceSpecs | null>(null);
  const [availableModels, setAvailableModels] = useState<AIModel[]>([]);
  const [serverStatus, setServerStatus] = useState(false);

  useEffect(() => {
    loadAppData();
  }, []);

  const loadAppData = async () => {
    try {
      setIsLoading(true);

      // Get device specs
      const specs = await DeviceInfoService.getDeviceInfo();
      setDeviceSpecs(specs);

      // Get AI service instance
      const aiService = EmbeddedAIService.getInstance();
      
      // Get available models
      const models = aiService.getAvailableModels();
      setAvailableModels(models);

      // Check server status
      const serverRunning = aiService.isServerRunning();
      setServerStatus(serverRunning);

      setIsLoading(false);

    } catch (error) {
      console.error('❌ Failed to load app data:', error);
      setIsLoading(false);
      Alert.alert('Error', 'Failed to load app data');
    }
  };

  const startChat = async () => {
    try {
      const aiService = EmbeddedAIService.getInstance();
      
      // Check if we have available models
      const availableModel = availableModels.find(m => m.status === 'available');
      
      if (!availableModel) {
        Alert.alert(
          'No AI Models Available',
          'Please download at least one AI model to start chatting.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Download Models', onPress: () => navigation.navigate('ModelManager') }
          ]
        );
        return;
      }

      // Start AI server if not running
      if (!serverStatus) {
        const success = await aiService.startAIServer();
        if (success) {
          setServerStatus(true);
          Toast.show({
            type: 'success',
            text1: 'AI Server Started',
            text2: 'Ready to chat!',
          });
        }
      }

      navigation.navigate('Chat');

    } catch (error) {
      console.error('❌ Failed to start chat:', error);
      Alert.alert('Error', 'Failed to start chat');
    }
  };

  const getModelStatusColor = (status: string) => {
    switch (status) {
      case 'available': return '#10B981';
      case 'downloading': return '#F59E0B';
      case 'not_available': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getModelStatusText = (status: string) => {
    switch (status) {
      case 'available': return '✓ Available';
      case 'downloading': return '⏳ Downloading';
      case 'not_available': return '✗ Not Available';
      default: return 'Unknown';
    }
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3B82F6" />
          <Text style={styles.loadingText}>Loading Ethos AI...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>🚀 Ethos AI</Text>
          <Text style={styles.subtitle}>Your Personal AI Assistant</Text>
        </View>

        {/* Device Info */}
        {deviceSpecs && (
          <View style={styles.deviceInfo}>
            <Text style={styles.deviceInfoTitle}>📱 Device Information</Text>
            <View style={styles.deviceInfoRow}>
              <Text style={styles.deviceInfoLabel}>Platform:</Text>
              <Text style={styles.deviceInfoValue}>{deviceSpecs.platform}</Text>
            </View>
            <View style={styles.deviceInfoRow}>
              <Text style={styles.deviceInfoLabel}>Memory:</Text>
              <Text style={styles.deviceInfoValue}>{deviceSpecs.memory_gb}GB</Text>
            </View>
            <View style={styles.deviceInfoRow}>
              <Text style={styles.deviceInfoLabel}>Storage:</Text>
              <Text style={styles.deviceInfoValue}>{deviceSpecs.storage_gb}GB</Text>
            </View>
            <View style={styles.deviceInfoRow}>
              <Text style={styles.deviceInfoLabel}>Processor:</Text>
              <Text style={styles.deviceInfoValue}>{deviceSpecs.processor}</Text>
            </View>
          </View>
        )}

        {/* AI Models */}
        <View style={styles.modelsSection}>
          <Text style={styles.sectionTitle}>🤖 AI Models</Text>
          {availableModels.map((model) => (
            <View key={model.name} style={styles.modelCard}>
              <View style={styles.modelInfo}>
                <Text style={styles.modelName}>{model.name}</Text>
                <Text style={styles.modelType}>{model.type}</Text>
                <Text style={styles.modelSize}>{model.size_gb}GB</Text>
              </View>
              <View style={styles.modelStatus}>
                <View 
                  style={[
                    styles.statusIndicator, 
                    { backgroundColor: getModelStatusColor(model.status) }
                  ]} 
                />
                <Text style={styles.statusText}>
                  {getModelStatusText(model.status)}
                </Text>
              </View>
            </View>
          ))}
        </View>

        {/* Server Status */}
        <View style={styles.serverStatus}>
          <Text style={styles.sectionTitle}>🌐 Server Status</Text>
          <View style={styles.statusCard}>
            <View style={styles.statusRow}>
              <View 
                style={[
                  styles.statusDot, 
                  { backgroundColor: serverStatus ? '#10B981' : '#EF4444' }
                ]} 
              />
              <Text style={styles.statusLabel}>
                AI Server: {serverStatus ? 'Running' : 'Stopped'}
              </Text>
            </View>
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actions}>
          <TouchableOpacity style={styles.primaryButton} onPress={startChat}>
            <Text style={styles.primaryButtonText}>💬 Start Chat</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={() => navigation.navigate('ModelManager')}
          >
            <Text style={styles.secondaryButtonText}>📦 Manage Models</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.secondaryButton} 
            onPress={() => navigation.navigate('Settings')}
          >
            <Text style={styles.secondaryButtonText}>⚙️ Settings</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  scrollContent: {
    padding: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#ffffff',
    marginTop: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#888888',
  },
  deviceInfo: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  deviceInfoTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  deviceInfoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  deviceInfoLabel: {
    fontSize: 14,
    color: '#888888',
  },
  deviceInfoValue: {
    fontSize: 14,
    color: '#ffffff',
    fontWeight: '500',
  },
  modelsSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  modelCard: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  modelInfo: {
    flex: 1,
  },
  modelName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  modelType: {
    fontSize: 12,
    color: '#888888',
    marginBottom: 2,
  },
  modelSize: {
    fontSize: 12,
    color: '#888888',
  },
  modelStatus: {
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginBottom: 4,
  },
  statusText: {
    fontSize: 12,
    color: '#888888',
  },
  serverStatus: {
    marginBottom: 24,
  },
  statusCard: {
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    padding: 16,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 12,
  },
  statusLabel: {
    fontSize: 16,
    color: '#ffffff',
  },
  actions: {
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  primaryButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  secondaryButton: {
    backgroundColor: '#374151',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  secondaryButtonText: {
    fontSize: 16,
    color: '#ffffff',
  },
});

export default HomeScreen;
