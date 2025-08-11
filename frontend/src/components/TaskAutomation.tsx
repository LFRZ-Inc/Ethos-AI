import React, { useState, useEffect } from 'react';
import { Play, Pause, Trash2, Plus, Clock, FileText, Search, BarChart3, Settings, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { API_ENDPOINTS } from '../config';
import toast from 'react-hot-toast';

interface TaskStep {
  id: string;
  name: string;
  action: string;
  parameters: Record<string, any>;
  dependencies?: string[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  start_time?: number;
  end_time?: number;
  retry_count: number;
}

interface Task {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  task_type: 'workflow' | 'scheduled' | 'triggered' | 'file_processing' | 'web_action' | 'data_analysis';
  created_at: number;
  scheduled_for?: number;
  started_at?: number;
  completed_at?: number;
  priority: number;
  tags: string[];
  steps: TaskStep[];
  result?: any;
  error?: string;
}

interface TaskTemplate {
  name: string;
  description: string;
  template: any;
}

const TaskAutomation: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [templates, setTemplates] = useState<TaskTemplate[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'tasks' | 'templates' | 'create'>('tasks');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    type: 'workflow' as const,
    steps: [] as any[],
    priority: 5,
    tags: [] as string[],
    scheduled_for: null as number | null
  });

  useEffect(() => {
    loadTasks();
    loadTemplates();
  }, []);

  const loadTasks = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(API_ENDPOINTS.tasks || '/api/tasks');
      if (response.ok) {
        const data = await response.json();
        setTasks(data.tasks || []);
      } else {
        throw new Error('Failed to load tasks');
      }
    } catch (error) {
      console.error('Error loading tasks:', error);
      toast.error('Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.tasks + '/templates', { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      } else {
        throw new Error('Failed to load templates');
      }
    } catch (error) {
      console.error('Error loading templates:', error);
      toast.error('Failed to load templates');
    }
  };

  const createTask = async (taskData: any) => {
    try {
      const response = await fetch(API_ENDPOINTS.tasks || '/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData)
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        setShowCreateModal(false);
        setNewTask({
          name: '',
          description: '',
          type: 'workflow',
          steps: [],
          priority: 5,
          tags: [],
          scheduled_for: null
        });
        loadTasks();
      } else {
        throw new Error('Failed to create task');
      }
    } catch (error) {
      console.error('Error creating task:', error);
      toast.error('Failed to create task');
    }
  };

  const executeTask = async (taskId: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.tasks || '/api/tasks'}/${taskId}/execute`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        loadTasks();
      } else {
        throw new Error('Failed to execute task');
      }
    } catch (error) {
      console.error('Error executing task:', error);
      toast.error('Failed to execute task');
    }
  };

  const cancelTask = async (taskId: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.tasks || '/api/tasks'}/${taskId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        const result = await response.json();
        toast.success(result.message);
        loadTasks();
      } else {
        throw new Error('Failed to cancel task');
      }
    } catch (error) {
      console.error('Error cancelling task:', error);
      toast.error('Failed to cancel task');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'running':
        return <Loader size={16} className="text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle size={16} className="text-red-500" />;
      case 'pending':
        return <Clock size={16} className="text-yellow-500" />;
      default:
        return <Clock size={16} className="text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  const addStep = () => {
    setNewTask(prev => ({
      ...prev,
      steps: [...prev.steps, {
        name: '',
        action: 'send_message',
        parameters: {},
        dependencies: []
      }]
    }));
  };

  const removeStep = (index: number) => {
    setNewTask(prev => ({
      ...prev,
      steps: prev.steps.filter((_, i) => i !== index)
    }));
  };

  const updateStep = (index: number, field: string, value: any) => {
    setNewTask(prev => ({
      ...prev,
      steps: prev.steps.map((step, i) => 
        i === index ? { ...step, [field]: value } : step
      )
    }));
  };

  const useTemplate = (template: TaskTemplate) => {
    setNewTask({
      name: template.template.name,
      description: template.template.description,
      type: template.template.type,
      steps: template.template.steps,
      priority: 5,
      tags: [],
      scheduled_for: null
    });
    setActiveTab('create');
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            🤖 Task Automation
          </h1>
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('tasks')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'tasks'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <FileText size={16} />
              <span>Tasks</span>
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'templates'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <Settings size={16} />
              <span>Templates</span>
            </button>
            <button
              onClick={() => setActiveTab('create')}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                activeTab === 'create'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              <Plus size={16} />
              <span>Create</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'tasks' && (
          <div className="h-full flex">
            {/* Task List */}
            <div className="w-1/3 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Tasks</h2>
                  <button
                    onClick={loadTasks}
                    className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  >
                    <RefreshCw size={16} />
                  </button>
                </div>
                
                {isLoading ? (
                  <div className="text-center py-8">
                    <Loader size={24} className="animate-spin mx-auto mb-2" />
                    <p>Loading tasks...</p>
                  </div>
                ) : tasks.length > 0 ? (
                  <div className="space-y-2">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        onClick={() => setSelectedTask(task)}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          selectedTask?.id === task.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium text-gray-900 dark:text-white">{task.name}</h3>
                          {getStatusIcon(task.status)}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{task.description}</p>
                        <div className="flex items-center justify-between">
                          <span className={`text-xs px-2 py-1 rounded ${getStatusColor(task.status)}`}>
                            {task.status}
                          </span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(task.created_at)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                    <FileText size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No tasks found</p>
                    <p className="text-sm">Create your first automated task</p>
                  </div>
                )}
              </div>
            </div>

            {/* Task Details */}
            <div className="flex-1 overflow-y-auto">
              {selectedTask ? (
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedTask.name}</h2>
                      <p className="text-gray-600 dark:text-gray-400">{selectedTask.description}</p>
                    </div>
                    <div className="flex space-x-2">
                      {selectedTask.status === 'pending' && (
                        <button
                          onClick={() => executeTask(selectedTask.id)}
                          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center space-x-2"
                        >
                          <Play size={16} />
                          <span>Execute</span>
                        </button>
                      )}
                      {selectedTask.status === 'running' && (
                        <button
                          onClick={() => cancelTask(selectedTask.id)}
                          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 flex items-center space-x-2"
                        >
                          <Pause size={16} />
                          <span>Cancel</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Task Info */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 dark:text-white mb-2">Task Information</h3>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Type:</span>
                          <span className="text-gray-900 dark:text-white">{selectedTask.task_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Priority:</span>
                          <span className="text-gray-900 dark:text-white">{selectedTask.priority}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Created:</span>
                          <span className="text-gray-900 dark:text-white">{formatTimestamp(selectedTask.created_at)}</span>
                        </div>
                        {selectedTask.started_at && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Started:</span>
                            <span className="text-gray-900 dark:text-white">{formatTimestamp(selectedTask.started_at)}</span>
                          </div>
                        )}
                        {selectedTask.completed_at && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Completed:</span>
                            <span className="text-gray-900 dark:text-white">{formatTimestamp(selectedTask.completed_at)}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                      <h3 className="font-medium text-gray-900 dark:text-white mb-2">Status</h3>
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(selectedTask.status)}
                          <span className={`text-sm px-2 py-1 rounded ${getStatusColor(selectedTask.status)}`}>
                            {selectedTask.status}
                          </span>
                        </div>
                        {selectedTask.error && (
                          <div className="text-sm text-red-600 dark:text-red-400">
                            Error: {selectedTask.error}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Steps */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Steps</h3>
                    <div className="space-y-3">
                      {selectedTask.steps.map((step, index) => (
                        <div key={step.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(step.status)}
                              <h4 className="font-medium text-gray-900 dark:text-white">{step.name}</h4>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(step.status)}`}>
                              {step.status}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            Action: {step.action}
                          </div>
                          {step.error && (
                            <div className="text-sm text-red-600 dark:text-red-400 mb-2">
                              Error: {step.error}
                            </div>
                          )}
                          {step.result && (
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                              Result: {JSON.stringify(step.result, null, 2)}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                  <div className="text-center">
                    <FileText size={48} className="mx-auto mb-4 opacity-50" />
                    <p>Select a task to view details</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="h-full overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Task Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {templates.map((template, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{template.name}</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">{template.description}</p>
                  <button
                    onClick={() => useTemplate(template)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2"
                  >
                    <Plus size={16} />
                    <span>Use Template</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'create' && (
          <div className="h-full overflow-y-auto p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Create New Task</h2>
            
            <div className="max-w-4xl space-y-6">
              {/* Basic Information */}
              <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Task Name
                    </label>
                    <input
                      type="text"
                      value={newTask.name}
                      onChange={(e) => setNewTask(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="Enter task name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Task Type
                    </label>
                    <select
                      value={newTask.type}
                      onChange={(e) => setNewTask(prev => ({ ...prev, type: e.target.value as any }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="workflow">Workflow</option>
                      <option value="scheduled">Scheduled</option>
                      <option value="triggered">Triggered</option>
                      <option value="file_processing">File Processing</option>
                      <option value="web_action">Web Action</option>
                      <option value="data_analysis">Data Analysis</option>
                    </select>
                  </div>
                </div>
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newTask.description}
                    onChange={(e) => setNewTask(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    rows={3}
                    placeholder="Enter task description"
                  />
                </div>
              </div>

              {/* Steps */}
              <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Task Steps</h3>
                  <button
                    onClick={addStep}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center space-x-2"
                  >
                    <Plus size={16} />
                    <span>Add Step</span>
                  </button>
                </div>
                
                <div className="space-y-4">
                  {newTask.steps.map((step, index) => (
                    <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-medium text-gray-900 dark:text-white">Step {index + 1}</h4>
                        <button
                          onClick={() => removeStep(index)}
                          className="p-1 text-red-500 hover:text-red-700"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Step Name
                          </label>
                          <input
                            type="text"
                            value={step.name}
                            onChange={(e) => updateStep(index, 'name', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                            placeholder="Enter step name"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Action
                          </label>
                          <select
                            value={step.action}
                            onChange={(e) => updateStep(index, 'action', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                          >
                            <option value="send_message">Send Message</option>
                            <option value="process_file">Process File</option>
                            <option value="web_search">Web Search</option>
                            <option value="data_analysis">Data Analysis</option>
                            <option value="file_operation">File Operation</option>
                            <option value="schedule_reminder">Schedule Reminder</option>
                            <option value="send_notification">Send Notification</option>
                            <option value="code_execution">Code Execution</option>
                            <option value="api_call">API Call</option>
                            <option value="data_extraction">Data Extraction</option>
                            <option value="content_generation">Content Generation</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Create Button */}
              <div className="flex justify-end">
                <button
                  onClick={() => createTask(newTask)}
                  disabled={!newTask.name || newTask.steps.length === 0}
                  className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Plus size={16} />
                  <span>Create Task</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper component for refresh icon
const RefreshCw: React.FC<{ size: number; className?: string }> = ({ size, className }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={className}>
    <path d="M23 4v6h-6"/>
    <path d="M1 20v-6h6"/>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
  </svg>
);

export default TaskAutomation; 