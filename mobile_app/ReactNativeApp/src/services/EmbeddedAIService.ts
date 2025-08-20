import { Platform } from 'react-native';
import RNFS from 'react-native-fs';
import DeviceInfo from 'react-native-device-info';

export interface AIModel {
  name: string;
  size_gb: number;
  type: 'text_generation' | 'code_generation' | 'multimodal';
  priority: number;
  min_ram: number;
  status: 'available' | 'downloading' | 'not_available';
  local_path?: string;
}

export interface DeviceSpecs {
  platform: string;
  architecture: string;
  memory_gb: number;
  storage_gb: number;
  processor: string;
  device_id: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  model_used?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: number;
  updated_at: number;
  model_preference?: string;
}

class EmbeddedAIService {
  private static instance: EmbeddedAIService;
  private deviceSpecs: DeviceSpecs | null = null;
  private availableModels: AIModel[] = [];
  private isInitialized = false;
  private serverPort = 8000;
  private serverRunning = false;

  // Model configurations (excluding 20B and 70B models)
  private readonly modelConfigs: Record<string, Omit<AIModel, 'status' | 'local_path'>> = {
    'phi:latest': {
      name: 'phi:latest',
      size_gb: 1.6,
      type: 'text_generation',
      priority: 1,
      min_ram: 2,
    },
    'sailor2:1b': {
      name: 'sailor2:1b',
      size_gb: 1.1,
      type: 'text_generation',
      priority: 2,
      min_ram: 2,
    },
    'llama2:latest': {
      name: 'llama2:latest',
      size_gb: 3.8,
      type: 'text_generation',
      priority: 3,
      min_ram: 6,
    },
    'llama3.2:3b': {
      name: 'llama3.2:3b',
      size_gb: 2.0,
      type: 'text_generation',
      priority: 4,
      min_ram: 4,
    },
    'codellama:7b': {
      name: 'codellama:7b',
      size_gb: 3.8,
      type: 'code_generation',
      priority: 5,
      min_ram: 8,
    },
    'llava:7b': {
      name: 'llava:7b',
      size_gb: 4.7,
      type: 'multimodal',
      priority: 6,
      min_ram: 10,
    },
  };

  static getInstance(): EmbeddedAIService {
    if (!EmbeddedAIService.instance) {
      EmbeddedAIService.instance = new EmbeddedAIService();
    }
    return EmbeddedAIService.instance;
  }

  async initialize(deviceInfo: any): Promise<void> {
    try {
      console.log('🤖 Initializing Embedded AI Service...');

      // Get device specifications
      this.deviceSpecs = await this.getDeviceSpecs(deviceInfo);
      console.log('📱 Device Specs:', this.deviceSpecs);

      // Select appropriate models for device
      this.availableModels = this.selectModelsForDevice();
      console.log('🎯 Selected Models:', this.availableModels);

      // Initialize storage directories
      await this.initializeStorage();

      // Check for existing models
      await this.checkExistingModels();

      this.isInitialized = true;
      console.log('✅ Embedded AI Service initialized');

    } catch (error) {
      console.error('❌ Failed to initialize Embedded AI Service:', error);
      throw error;
    }
  }

  private async getDeviceSpecs(deviceInfo: any): Promise<DeviceSpecs> {
    const memory = await DeviceInfo.getTotalMemory();
    const storage = await DeviceInfo.getTotalDiskCapacity();
    
    return {
      platform: Platform.OS,
      architecture: await DeviceInfo.getArchitecture(),
      memory_gb: Math.round(memory / (1024 * 1024 * 1024)),
      storage_gb: Math.round(storage / (1024 * 1024 * 1024)),
      processor: await DeviceInfo.getCpuCount().then(count => `${count} cores`),
      device_id: await DeviceInfo.getUniqueId(),
    };
  }

  private selectModelsForDevice(): AIModel[] {
    if (!this.deviceSpecs) return [];

    const { memory_gb, storage_gb } = this.deviceSpecs;
    const models: AIModel[] = [];

    // Select models based on device capabilities
    for (const [modelName, config] of Object.entries(this.modelConfigs)) {
      if (memory_gb >= config.min_ram && storage_gb >= config.size_gb) {
        models.push({
          ...config,
          status: 'not_available', // Will be updated when checking existing models
        });
      }
    }

    // Sort by priority
    models.sort((a, b) => a.priority - b.priority);
    return models;
  }

  private async initializeStorage(): Promise<void> {
    try {
      const baseDir = Platform.OS === 'ios' 
        ? RNFS.DocumentDirectoryPath 
        : RNFS.ExternalDirectoryPath;

      const aiDir = `${baseDir}/EthosAI`;
      const modelsDir = `${aiDir}/models`;
      const dataDir = `${aiDir}/data`;

      // Create directories
      await RNFS.mkdir(aiDir);
      await RNFS.mkdir(modelsDir);
      await RNFS.mkdir(dataDir);

      console.log('📁 Storage initialized:', aiDir);
    } catch (error) {
      console.error('❌ Failed to initialize storage:', error);
      throw error;
    }
  }

  private async checkExistingModels(): Promise<void> {
    try {
      const baseDir = Platform.OS === 'ios' 
        ? RNFS.DocumentDirectoryPath 
        : RNFS.ExternalDirectoryPath;
      const modelsDir = `${baseDir}/EthosAI/models`;

      for (const model of this.availableModels) {
        const modelPath = `${modelsDir}/${model.name}`;
        const exists = await RNFS.exists(modelPath);
        
        if (exists) {
          model.status = 'available';
          model.local_path = modelPath;
        }
      }

      console.log('📋 Model availability checked');
    } catch (error) {
      console.error('❌ Failed to check existing models:', error);
    }
  }

  async startAIServer(): Promise<boolean> {
    try {
      if (this.serverRunning) {
        console.log('✅ AI Server already running');
        return true;
      }

      console.log('🚀 Starting AI Server...');

      // For now, we'll use a WebView approach
      // In a full implementation, this would start a local HTTP server
      // using a native module or WebView with local HTML/JS

      this.serverRunning = true;
      console.log('✅ AI Server started on port', this.serverPort);
      return true;

    } catch (error) {
      console.error('❌ Failed to start AI server:', error);
      return false;
    }
  }

  async stopAIServer(): Promise<void> {
    try {
      this.serverRunning = false;
      console.log('🛑 AI Server stopped');
    } catch (error) {
      console.error('❌ Failed to stop AI server:', error);
    }
  }

  async sendMessage(message: string, modelName?: string): Promise<string> {
    try {
      if (!this.serverRunning) {
        await this.startAIServer();
      }

      // Select model
      const model = modelName 
        ? this.availableModels.find(m => m.name === modelName)
        : this.availableModels.find(m => m.status === 'available');

      if (!model || model.status !== 'available') {
        throw new Error('No available AI models');
      }

      // For now, return a mock response
      // In full implementation, this would call the local AI server
      const response = `[${model.name}] ${message}`;
      
      console.log('🤖 AI Response:', response);
      return response;

    } catch (error) {
      console.error('❌ Failed to send message:', error);
      throw error;
    }
  }

  async downloadModel(modelName: string): Promise<boolean> {
    try {
      const model = this.availableModels.find(m => m.name === modelName);
      if (!model) {
        throw new Error(`Model ${modelName} not found`);
      }

      model.status = 'downloading';
      console.log(`📥 Downloading ${modelName}...`);

      // For now, simulate download
      // In full implementation, this would download from Ollama or other source
      await new Promise(resolve => setTimeout(resolve, 2000));

      model.status = 'available';
      console.log(`✅ ${modelName} downloaded successfully`);
      return true;

    } catch (error) {
      console.error(`❌ Failed to download ${modelName}:`, error);
      const model = this.availableModels.find(m => m.name === modelName);
      if (model) {
        model.status = 'not_available';
      }
      return false;
    }
  }

  getAvailableModels(): AIModel[] {
    return this.availableModels;
  }

  getDeviceSpecs(): DeviceSpecs | null {
    return this.deviceSpecs;
  }

  isServerRunning(): boolean {
    return this.serverRunning;
  }

  getServerUrl(): string {
    return `http://localhost:${this.serverPort}`;
  }
}

export { EmbeddedAIService };
