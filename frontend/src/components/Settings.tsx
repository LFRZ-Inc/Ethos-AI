import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save, Key, Globe, Database, Activity, HardDrive, Cpu, Monitor } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { API_ENDPOINTS } from '../config';
import toast from 'react-hot-toast';

const Settings: React.FC = () => {
  const { theme, setTheme } = useAppStore();
  const [apiKeys, setApiKeys] = useState({
    anthropic: '',
    openai: '',
    huggingface: '',
  });
  const [loading, setLoading] = useState(false);
  const [ramData, setRamData] = useState<any>(null);
  const [ramLoading, setRamLoading] = useState(false);

  useEffect(() => {
    loadSettings();
    fetchRAMData();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.config);
      if (response.ok) {
        const config = await response.json();
        // Load API keys from config (if available)
        if (config.api_keys) {
          setApiKeys(config.api_keys);
        } else {
          // Initialize with empty API keys if not provided
          setApiKeys({
            anthropic: '',
            openai: '',
            huggingface: '',
          });
        }
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.config, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_keys: apiKeys,
        }),
      });

      if (response.ok) {
        toast.success('Settings saved successfully');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const fetchRAMData = async () => {
    setRamLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.ramUsage);
      if (response.ok) {
        const data = await response.json();
        setRamData(data);
      }
    } catch (error) {
      console.error('Failed to fetch RAM data:', error);
    } finally {
      setRamLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => window.history.back()}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <ArrowLeft size={20} />
          </button>
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Settings
          </h1>
        </div>
        <button
          onClick={handleSave}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
        >
          <Save size={16} />
          <span>{loading ? 'Saving...' : 'Save'}</span>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl space-y-8">
          {/* Theme Settings */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Globe size={20} className="text-gray-500" />
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                Appearance
              </h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Theme
                </label>
                <select
                  value={theme}
                  onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>
            </div>
          </div>

          {/* API Keys */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Key size={20} className="text-gray-500" />
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                API Keys
              </h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Anthropic API Key (Claude)
                </label>
                <input
                  type="password"
                  value={apiKeys.anthropic}
                  onChange={(e) => setApiKeys({ ...apiKeys, anthropic: e.target.value })}
                  placeholder="sk-ant-..."
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Get your API key from{' '}
                  <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                    Anthropic Console
                  </a>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  OpenAI API Key (GPT-4)
                </label>
                <input
                  type="password"
                  value={apiKeys.openai}
                  onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
                  placeholder="sk-..."
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Get your API key from{' '}
                  <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                    OpenAI Platform
                  </a>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Hugging Face Token
                </label>
                <input
                  type="password"
                  value={apiKeys.huggingface}
                  onChange={(e) => setApiKeys({ ...apiKeys, huggingface: e.target.value })}
                  placeholder="hf_..."
                  className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Optional: For accessing Hugging Face models
                </p>
              </div>
            </div>
          </div>

          {/* Data Management */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Database size={20} className="text-gray-500" />
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                Data Management
              </h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
                  All your data is stored locally on your device in the EthosAIData folder.
                </p>
                
                <div className="space-y-2">
                  <button
                    onClick={() => {
                      // Export conversations
                      toast('Export feature coming soon');
                    }}
                    className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg text-left hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <div className="font-medium text-gray-900 dark:text-white">Export Conversations</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Download all conversations as JSON</div>
                  </button>
                  
                  <button
                    onClick={() => {
                      if (confirm('This will delete all conversations and data. Are you sure?')) {
                        toast('Clear data feature coming soon');
                      }
                    }}
                    className="w-full p-3 border border-red-300 dark:border-red-600 rounded-lg text-left hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <div className="font-medium text-red-700 dark:text-red-300">Clear All Data</div>
                    <div className="text-sm text-red-500 dark:text-red-400">Delete all conversations and settings</div>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* System Information */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Monitor size={20} className="text-gray-500" />
                <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                  System Information
                </h2>
              </div>
              <button
                onClick={fetchRAMData}
                disabled={ramLoading}
                className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
              >
                {ramLoading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
            
            {ramLoading && !ramData ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-sm text-gray-500 mt-2">Loading system information...</p>
              </div>
            ) : ramData ? (
              <div className="space-y-6">
                {/* Device Memory Info */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <Database size={16} className="text-blue-500" />
                    <h3 className="font-medium text-gray-900 dark:text-white">Device Memory</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Storage Size:</span>
                      <span className="ml-2 font-medium">0.0 KB</span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Conversations:</span>
                      <span className="ml-2 font-medium">0</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Your conversations are stored locally on this device for privacy
                  </p>
                </div>

                {/* System RAM */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <Activity size={16} className="text-blue-500" />
                    <h3 className="font-medium text-gray-900 dark:text-white">System RAM</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Total:</span>
                      <span className="ml-2 font-medium">{ramData.system_ram.total_gb} GB</span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Used:</span>
                      <span className="ml-2 font-medium">{ramData.system_ram.used_gb} GB</span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Available:</span>
                      <span className="ml-2 font-medium">{ramData.system_ram.available_gb} GB</span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Usage:</span>
                      <span className={`ml-2 font-medium ${
                        ramData.system_ram.percent_used > 80 ? 'text-red-600' :
                        ramData.system_ram.percent_used > 60 ? 'text-yellow-600' :
                        'text-green-600'
                      }`}>
                        {ramData.system_ram.percent_used}%
                      </span>
                    </div>
                  </div>
                  {/* RAM Usage Bar */}
                  <div className="mt-3 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        ramData.system_ram.percent_used > 80 ? 'bg-red-500' :
                        ramData.system_ram.percent_used > 60 ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`}
                      style={{ width: `${ramData.system_ram.percent_used}%` }}
                    ></div>
                  </div>
                </div>

                {/* Ollama Processes */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <Cpu size={16} className="text-green-500" />
                    <h3 className="font-medium text-gray-900 dark:text-white">Ollama Processes</h3>
                  </div>
                  {ramData.ollama_processes.length > 0 ? (
                    <div className="space-y-2">
                      {ramData.ollama_processes.map((proc: any, index: number) => (
                        <div key={index} className="flex justify-between items-center text-sm">
                          <span className="text-gray-700 dark:text-gray-300">{proc.name} (PID: {proc.pid})</span>
                          <span className="font-medium">{proc.ram_mb.toFixed(1)} MB</span>
                        </div>
                      ))}
                      <div className="border-t pt-2 mt-2">
                        <div className="flex justify-between items-center font-medium">
                          <span>Total Ollama RAM:</span>
                          <span>{(ramData.ollama_processes.reduce((sum: number, proc: any) => sum + proc.ram_mb, 0) / 1024).toFixed(1)} GB</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500">No Ollama processes running</p>
                  )}
                </div>

                {/* Model RAM Estimates */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <HardDrive size={16} className="text-purple-500" />
                    <h3 className="font-medium text-gray-900 dark:text-white">Model RAM Requirements</h3>
                  </div>
                  <div className="space-y-2">
                    {Object.entries(ramData.model_estimates).map(([modelId, modelInfo]: [string, any]) => (
                      <div key={modelId} className="flex justify-between items-center text-sm">
                        <span className="text-gray-700 dark:text-gray-300">{modelInfo.name}</span>
                        <span className="font-medium">{modelInfo.estimated_ram_gb} GB</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Last Updated */}
                <div className="text-xs text-gray-500 text-center">
                  Last updated: {new Date(ramData.timestamp).toLocaleString()}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm text-gray-500">Failed to load system information</p>
                <button
                  onClick={fetchRAMData}
                  className="mt-2 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Retry
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 