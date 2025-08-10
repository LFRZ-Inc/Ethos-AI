import React, { useState, useEffect } from 'react';
import { ChevronDown, Bot } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { API_ENDPOINTS } from '../config';

interface Model {
  id: string;
  name: string;
  type: string;
  status: string;
  capabilities: string[];
}

const ModelSelector: React.FC = () => {
  const [models, setModels] = useState<Model[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const { selectedModel, setSelectedModel } = useAppStore();

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.models);
      if (response.ok) {
        const modelData = await response.json();
        // Handle both array and object with models property
        const modelsArray = Array.isArray(modelData) ? modelData : (modelData.models || []);
        setModels(Array.isArray(modelsArray) ? modelsArray : []);
      } else {
        console.warn('Failed to load models:', response.status);
        setModels([]);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      setModels([]);
    } finally {
      setLoading(false);
    }
  };

  const handleModelSelect = (modelId: string) => {
    setSelectedModel(modelId);
    setIsOpen(false);
  };

  const selectedModelData = Array.isArray(models) ? models.find(m => m.id === selectedModel) : null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        <Bot size={16} />
        <span className="text-gray-700 dark:text-gray-300">
          {selectedModelData ? selectedModelData.name : 'Auto Select'}
        </span>
        <ChevronDown size={16} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-50">
          <div className="p-2">
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              Select Model
            </div>
            
            {loading ? (
              <div className="text-sm text-gray-500 dark:text-gray-400">Loading models...</div>
            ) : (
              <div className="space-y-1">
                <button
                  onClick={() => handleModelSelect('')}
                  className={`w-full text-left px-3 py-2 text-sm rounded ${
                    !selectedModel 
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="font-medium">Auto Select</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Let AI choose the best model
                  </div>
                </button>
                
                {Array.isArray(models) && models.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => handleModelSelect(model.id)}
                    className={`w-full text-left px-3 py-2 text-sm rounded ${
                      selectedModel === model.id 
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' 
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{model.name}</div>
                      <div className={`text-xs px-2 py-1 rounded ${
                        model.status === 'available' 
                          ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                          : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
                      }`}>
                        {model.status}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {model.type} • {model.capabilities.join(', ')}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector; 