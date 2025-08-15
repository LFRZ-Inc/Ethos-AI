import React, { useState, useEffect } from 'react';
import { Zap, Loader, CheckCircle, XCircle, Play, Cpu } from 'lucide-react';
import { API_ENDPOINTS } from '../config';

interface ModelInfo {
  model_id: string;
  model_name: string;
  is_loaded: boolean;
  device: string;
  cuda_available: boolean;
  load_time: number;
  last_used: number;
  error_count: number;
  avg_response_time: number;
}

interface ModelSystemStatus {
  available: boolean;
  system_status: {
    total_models: number;
    healthy_models: number;
    available_models: string[];
    system_status: string;
    models: Record<string, ModelInfo>;
  };
  models: Record<string, ModelInfo>;
}

const ModelSystemStatus: React.FC = () => {
  const [status, setStatus] = useState<ModelSystemStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    // Poll status every 5 seconds
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.models}/status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to load model system status:', error);
    }
  };

  const initializeModel = async (modelId: string) => {
    setInitializing(modelId);
    try {
      const response = await fetch(`${API_ENDPOINTS.models}/${modelId}/initialize`, {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        console.log(`Model ${modelId} initialization response:`, data);
        // Reload status after a short delay
        setTimeout(loadStatus, 2000);
      } else {
        const error = await response.json();
        console.error(`Failed to initialize model ${modelId}:`, error);
      }
    } catch (error) {
      console.error(`Error initializing model ${modelId}:`, error);
    } finally {
      setInitializing(null);
    }
  };

  if (!status) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg">
        <Loader size={16} className="animate-spin" />
        <span className="text-gray-600 dark:text-gray-400">Loading model status...</span>
      </div>
    );
  }

  if (!status.available) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-red-100 dark:bg-red-900 rounded-lg">
        <XCircle size={16} className="text-red-600 dark:text-red-400" />
        <span className="text-red-700 dark:text-red-300">AI Models Unavailable</span>
      </div>
    );
  }

  const { system_status } = status;
  const healthyModels = system_status.healthy_models;
  const totalModels = system_status.total_models;

  return (
    <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-blue-100 dark:bg-blue-900 rounded-lg">
      <Zap size={16} className="text-blue-600 dark:text-blue-400" />
      
      {healthyModels > 0 ? (
        <>
          <CheckCircle size={16} className="text-green-600 dark:text-green-400" />
          <span className="text-green-700 dark:text-green-300">
            {healthyModels}/{totalModels} Models Ready
          </span>
          
          {/* Show available models */}
          <div className="flex space-x-1">
            {system_status.available_models.map((modelId) => {
              const model = system_status.models[modelId];
              const isInitializing = initializing === modelId;
              
              return (
                <div key={modelId} className="flex items-center space-x-1">
                  <span className="text-xs text-blue-600 dark:text-blue-400">
                    {modelId.replace('ethos-', '')}
                  </span>
                  {isInitializing && (
                    <Loader size={12} className="animate-spin text-blue-600 dark:text-blue-400" />
                  )}
                </div>
              );
            })}
          </div>
        </>
      ) : (
        <>
          <span className="text-blue-700 dark:text-blue-300">AI Models Available</span>
          <button
            onClick={() => initializeModel('ethos-3b')} // Start with fastest model
            disabled={initializing !== null}
            className="flex items-center space-x-1 px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded transition-colors"
          >
            <Play size={12} />
            <span>Initialize</span>
          </button>
        </>
      )}
    </div>
  );
};

export default ModelSystemStatus;
