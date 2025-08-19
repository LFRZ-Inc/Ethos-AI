import React, { useState, useEffect } from 'react';
import { Zap, Loader, CheckCircle, XCircle, Play, Cpu } from 'lucide-react';
import { API_ENDPOINTS } from '../config';

interface ModelStatus {
  available: boolean;
  status: string;
  model: string;
  name: string;
  size: string;
}

interface ModelsStatusResponse {
  models: Record<string, ModelStatus>;
  ollama_available: boolean;
  total_available: number;
  error?: string;
}

const ModelSystemStatus: React.FC = () => {
  const [status, setStatus] = useState<ModelsStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStatus();
    // Poll status every 10 seconds
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.modelsStatus);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to load model system status:', error);
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

  // Check if Ollama is available
  if (!status.ollama_available) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-red-100 dark:bg-red-900 rounded-lg">
        <XCircle size={16} className="text-red-600 dark:text-red-400" />
        <span className="text-red-700 dark:text-red-300">Ollama Not Available</span>
      </div>
    );
  }

  // Count available models
  const availableModels = Object.values(status.models).filter(model => model.available);
  const totalModels = Object.keys(status.models).length;

  if (availableModels.length === 0) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-yellow-100 dark:bg-yellow-900 rounded-lg">
        <XCircle size={16} className="text-yellow-600 dark:text-yellow-400" />
        <span className="text-yellow-700 dark:text-yellow-300">No Models Downloaded</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 px-3 py-2 text-sm bg-green-100 dark:bg-green-900 rounded-lg">
      <CheckCircle size={16} className="text-green-600 dark:text-green-400" />
      <span className="text-green-700 dark:text-green-300">
        {availableModels.length}/{totalModels} Models Ready
      </span>
    </div>
  );
};

export default ModelSystemStatus;
