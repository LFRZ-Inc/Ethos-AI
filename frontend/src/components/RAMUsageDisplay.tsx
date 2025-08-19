import React, { useState, useEffect } from 'react';
import { Activity, HardDrive, Cpu } from 'lucide-react';
import { API_ENDPOINTS } from '../config';

interface RAMUsageData {
  system_ram: {
    total_gb: number;
    available_gb: number;
    used_gb: number;
    percent_used: number;
  };
  ollama_processes: Array<{
    pid: number;
    name: string;
    ram_mb: number;
  }>;
  model_estimates: {
    [key: string]: {
      name: string;
      estimated_ram_gb: number;
      model_size: string;
    };
  };
  timestamp: string;
}

const RAMUsageDisplay: React.FC = () => {
  const [ramData, setRamData] = useState<RAMUsageData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRAMData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_ENDPOINTS.ramUsage);
      if (response.ok) {
        const data = await response.json();
        setRamData(data);
      } else {
        setError('Failed to fetch RAM data');
      }
    } catch (err) {
      setError('Error fetching RAM data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRAMData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchRAMData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !ramData) {
    return (
      <div className="px-2 py-1 rounded text-xs bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200">
        📊 Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-2 py-1 rounded text-xs bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
        📊 Error
      </div>
    );
  }

  if (!ramData) return null;

  const totalOllamaRAM = ramData.ollama_processes.reduce((sum, proc) => sum + proc.ram_mb, 0);
  const totalOllamaGB = (totalOllamaRAM / 1024).toFixed(1);

  return (
    <div className="flex items-center space-x-2">
      {/* System RAM */}
      <div className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
        💾 {ramData.system_ram.used_gb.toFixed(1)}/{ramData.system_ram.total_gb.toFixed(1)} GB
      </div>
      
      {/* Ollama RAM */}
      <div className="px-2 py-1 rounded text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        🤖 {totalOllamaGB} GB
      </div>
      
      {/* RAM Usage Percentage */}
      <div className={`px-2 py-1 rounded text-xs ${
        ramData.system_ram.percent_used > 80 ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
        ramData.system_ram.percent_used > 60 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
        'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      }`}>
        📊 {ramData.system_ram.percent_used}%
      </div>
    </div>
  );
};

export default RAMUsageDisplay;
