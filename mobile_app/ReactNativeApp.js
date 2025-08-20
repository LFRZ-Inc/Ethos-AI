// React Native App with Embedded AI Server
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { WebView } from 'react-native-webview';
import { Platform } from 'react-native';

const EthosAIMobile = () => {
  const [serverRunning, setServerRunning] = useState(false);
  const [serverUrl, setServerUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [deviceInfo, setDeviceInfo] = useState({});

  useEffect(() => {
    // Get device information
    getDeviceInfo();
  }, []);

  const getDeviceInfo = async () => {
    try {
      // Get device specs for AI model selection
      const info = {
        platform: Platform.OS,
        version: Platform.Version,
        // Add more device info as needed
      };
      setDeviceInfo(info);
    } catch (error) {
      console.error('Error getting device info:', error);
    }
  };

  const startEmbeddedServer = async () => {
    setLoading(true);
    
    try {
      // Start the embedded AI server
      const response = await fetch('http://localhost:8000/start-server', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_type: 'mobile',
          device_specs: deviceInfo,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setServerUrl(data.server_url);
        setServerRunning(true);
        Alert.alert('Success', 'Embedded AI server started!');
      } else {
        throw new Error('Failed to start server');
      }
    } catch (error) {
      console.error('Error starting server:', error);
      Alert.alert('Error', 'Failed to start embedded AI server');
    } finally {
      setLoading(false);
    }
  };

  const stopEmbeddedServer = async () => {
    try {
      await fetch('http://localhost:8000/stop-server', {
        method: 'POST',
      });
      setServerRunning(false);
      setServerUrl('');
      Alert.alert('Success', 'Server stopped');
    } catch (error) {
      console.error('Error stopping server:', error);
    }
  };

  const renderServerControls = () => (
    <View style={styles.controlsContainer}>
      <Text style={styles.title}>Ethos AI - Embedded Server</Text>
      
      {!serverRunning ? (
        <TouchableOpacity
          style={styles.startButton}
          onPress={startEmbeddedServer}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>Start AI Server</Text>
          )}
        </TouchableOpacity>
      ) : (
        <TouchableOpacity
          style={styles.stopButton}
          onPress={stopEmbeddedServer}
        >
          <Text style={styles.buttonText}>Stop Server</Text>
        </TouchableOpacity>
      )}

      {serverRunning && (
        <View style={styles.serverInfo}>
          <Text style={styles.infoText}>Server Running: {serverUrl}</Text>
          <Text style={styles.infoText}>Access from any device on network</Text>
        </View>
      )}
    </View>
  );

  const renderWebInterface = () => (
    <WebView
      source={{ uri: serverUrl }}
      style={styles.webview}
      javaScriptEnabled={true}
      domStorageEnabled={true}
    />
  );

  return (
    <View style={styles.container}>
      {serverRunning ? (
        renderWebInterface()
      ) : (
        renderServerControls()
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  controlsContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 30,
    textAlign: 'center',
  },
  startButton: {
    backgroundColor: '#3b82f6',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 10,
    marginBottom: 20,
  },
  stopButton: {
    backgroundColor: '#ef4444',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 10,
    marginBottom: 20,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  serverInfo: {
    backgroundColor: '#374151',
    padding: 20,
    borderRadius: 10,
    alignItems: 'center',
  },
  infoText: {
    color: 'white',
    fontSize: 16,
    marginBottom: 10,
  },
  webview: {
    flex: 1,
  },
});

export default EthosAIMobile;
