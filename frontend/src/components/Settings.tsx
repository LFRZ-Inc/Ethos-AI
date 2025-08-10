import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save, Key, Globe, Database } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import toast from 'react-hot-toast';

const Settings: React.FC = () => {
  const { theme, setTheme } = useAppStore();
  const [apiKeys, setApiKeys] = useState({
    anthropic: '',
    openai: '',
    huggingface: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch('http://localhost:8002/api/config');
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
      const response = await fetch('http://localhost:8002/api/config', {
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
        </div>
      </div>
    </div>
  );
};

export default Settings; 