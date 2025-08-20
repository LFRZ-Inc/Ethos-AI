import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Send, Upload, Settings, Bot, User, Search, Mic } from 'lucide-react';
import { useChatStore, Message } from '../stores/appStore';
import { useAppStore } from '../stores/appStore';
import { useConversationStore } from '../stores/appStore';
import toast from 'react-hot-toast';
import MessageComponent from './MessageComponent';
import ModelSelector from './ModelSelector';
import ModelSystemStatus from './Model70BStatus';
import ToolPanel from './ToolPanel';
import VoiceInput from './VoiceInput';
import ThemeSwitcher from './ThemeSwitcher';
import WebSearchButton from './WebSearchButton';
import { API_ENDPOINTS, API_BASE_URL } from '../config';

// Device memory management
class DeviceMemory {
  private static instance: DeviceMemory;
  private deviceId: string;
  private memoryKey = 'ethos_device_memory';

  constructor() {
    this.deviceId = this.generateDeviceId();
  }

  static getInstance(): DeviceMemory {
    if (!DeviceMemory.instance) {
      DeviceMemory.instance = new DeviceMemory();
    }
    return DeviceMemory.instance;
  }

  private generateDeviceId(): string {
    let deviceId = localStorage.getItem('ethos_device_id');
    if (!deviceId) {
      deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('ethos_device_id', deviceId);
    }
    return deviceId;
  }

  getDeviceId(): string {
    return this.deviceId;
  }

  loadMemory(): any[] {
    try {
      const memory = localStorage.getItem(this.memoryKey);
      return memory ? JSON.parse(memory) : [];
    } catch (error) {
      console.error('Error loading device memory:', error);
      return [];
    }
  }

  saveMemory(memory: any[]): void {
    try {
      localStorage.setItem(this.memoryKey, JSON.stringify(memory));
    } catch (error) {
      console.error('Error saving device memory:', error);
    }
  }

  getMemorySize(): number {
    try {
      const memory = localStorage.getItem(this.memoryKey);
      return memory ? new Blob([memory]).size / 1024 : 0; // Size in KB
    } catch (error) {
      return 0;
    }
  }

  clearMemory(): void {
    localStorage.removeItem(this.memoryKey);
  }

  deleteConversation(conversationId: string): void {
    try {
      const memory = this.loadMemory();
      const updatedMemory = memory.filter(item => item.id !== conversationId);
      this.saveMemory(updatedMemory);
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  }

  deleteAllConversations(): void {
    this.clearMemory();
  }

  getConversationCount(): number {
    try {
      const memory = this.loadMemory();
      return memory.length;
    } catch (error) {
      return 0;
    }
  }
}

const ChatInterface: React.FC = () => {
  const { conversationId } = useParams();
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showVoiceInput, setShowVoiceInput] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, isLoading, addMessage, setLoading, setError, setMessages } = useChatStore();
  const { currentConversationId, selectedModel, useTools, setCurrentConversation } = useAppStore();
  const { conversations, loadConversations, addConversation } = useConversationStore();
  const [networkStatus, setNetworkStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [lastWebSearch, setLastWebSearch] = useState<{
    performed: boolean;
    sourcesUsed: { duckduckgo?: boolean; wikipedia?: boolean; news?: boolean };
  } | null>(null);
  
  // Device memory instance
  const deviceMemory = DeviceMemory.getInstance();

  useEffect(() => {
    if (conversationId) {
      setCurrentConversation(conversationId);
      loadConversation(conversationId);
    } else {
      setCurrentConversation(null);
      // Load device memory for new conversations
      loadDeviceMemory();
    }
    
    // Test network connectivity
    const testConnectivity = async () => {
      try {
        console.log('Testing connectivity to backend...');
        console.log('API Base URL:', API_BASE_URL);
        console.log('Current location:', window.location.href);
        
        const healthResponse = await fetch(API_ENDPOINTS.health);
        console.log('Health check status:', healthResponse.status);
        
        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          console.log('Backend health:', healthData);
          setNetworkStatus('connected');
        } else {
          setNetworkStatus('disconnected');
        }
      } catch (error) {
        console.error('Connectivity test failed:', error);
        setNetworkStatus('disconnected');
      }
    };
    
    testConnectivity();
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadDeviceMemory = () => {
    try {
      const memory = deviceMemory.loadMemory();
      if (memory.length > 0) {
        // Convert device memory to chat messages
        const chatMessages: Message[] = [];
        for (const item of memory.slice(-20)) { // Load last 20 conversations
          if (item.message) {
            chatMessages.push({
              id: `user-${item.id}`,
              role: 'user',
              content: item.message,
              timestamp: item.timestamp,
              modelUsed: item.model,
            });
          }
          if (item.response) {
            chatMessages.push({
              id: `assistant-${item.id}`,
              role: 'assistant',
              content: item.response,
              timestamp: item.timestamp,
              modelUsed: item.model,
            });
          }
        }
        setMessages(chatMessages);
      }
    } catch (error) {
      console.error('Error loading device memory:', error);
    }
  };

  const loadConversation = async (id: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.conversations}/${id}`);
      if (response.ok) {
        const conversation = await response.json();
        console.log('Loaded conversation:', conversation);
        console.log('Messages:', conversation.messages);
        // Load messages into chat store
        const chatMessages: Message[] = [];
        for (const msg of conversation.messages) {
          // Add user message if it exists
          if (msg.user) {
            chatMessages.push({
              id: `user-${msg.timestamp}-${Math.random()}`,
              role: 'user',
              content: msg.user,
              timestamp: msg.timestamp,
              modelUsed: msg.model_used,
            });
          }
          // Add assistant message if it exists
          if (msg.assistant) {
            chatMessages.push({
              id: `assistant-${msg.timestamp}-${Math.random()}`,
              role: 'assistant',
              content: msg.assistant,
              timestamp: msg.timestamp,
              modelUsed: msg.model_used,
            });
          }
        }
        useChatStore.setState({ messages: chatMessages });
      } else {
        console.warn('Failed to load conversation:', response.status);
        // Don't show error toast for now, just log it
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
      // Don't show error toast for now, just log it
    }
  };

  const handleSend = async (forceWebSearch: boolean = false) => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    setLoading(true);
    setIsTyping(true);

    try {
      // Get current device memory
      const deviceMemoryData = deviceMemory.loadMemory();
      
      // Send message using client-side storage API
      console.log('Sending message to:', API_ENDPOINTS.clientChat);
      console.log('Device ID:', deviceMemory.getDeviceId());
      console.log('Device memory size:', deviceMemory.getMemorySize(), 'KB');
      console.log('Force web search:', forceWebSearch);
      
      const response = await fetch(API_ENDPOINTS.clientChat, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          device_id: deviceMemory.getDeviceId(),
          device_memory: deviceMemoryData,
          model_override: selectedModel || null,
          force_web_search: forceWebSearch,
        }),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`Failed to send message: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      console.log('AI Response:', result);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.response,
        timestamp: new Date().toISOString(),
        modelUsed: result.model,
      };

      addMessage(assistantMessage);

      // Save updated memory to device
      if (result.updated_memory) {
        deviceMemory.saveMemory(result.updated_memory);
        console.log('Updated device memory, new size:', result.storage_size_kb, 'KB');
      }

      // Handle web search information
      if (result.web_search) {
        setLastWebSearch({
          performed: result.web_search.performed,
          sourcesUsed: result.web_search.sources_used || {}
        });
        
        if (result.web_search.performed) {
          const sources = [];
          if (result.web_search.sources_used?.duckduckgo) sources.push('DuckDuckGo');
          if (result.web_search.sources_used?.wikipedia) sources.push('Wikipedia');
          if (result.web_search.sources_used?.news) sources.push('News');
          
          if (sources.length > 0) {
            toast.success(`Web search performed using: ${sources.join(', ')}`);
          }
        }
      }

      // Show context usage info
      if (result.context_used) {
        toast.success(`Used conversation context (${deviceMemoryData.length} previous messages)`);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message');
      toast.error('Failed to send message');
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(false);
    }
  };

  const handleVoiceInput = (transcript: string) => {
    setInput(transcript);
    setShowVoiceInput(false);
  };

  const handleFileUpload = async (files: File[]) => {
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(API_ENDPOINTS.upload, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          toast.success(`File uploaded: ${file.name}`);
          
          // Add file info to chat
          const fileMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: `📎 Uploaded: ${file.name}\n\n${result.analysis?.summary || 'File uploaded successfully'}`,
            timestamp: new Date().toISOString(),
          };
          addMessage(fileMessage);
        } else {
          throw new Error('Upload failed');
        }
      } catch (error) {
        console.error('Upload error:', error);
        toast.error(`Failed to upload ${file.name}`);
      }
    }
  };

  const handleDeleteCurrentConversation = () => {
    if (messages.length > 0) {
      const confirmed = window.confirm('Are you sure you want to delete this conversation? This action cannot be undone.');
      if (confirmed) {
        // Clear current messages
        setMessages([]);
        // Clear device memory for this session
        deviceMemory.clearMemory();
        toast.success('Conversation deleted successfully');
      }
    }
  };

  const handleDeleteAllConversations = () => {
    const confirmed = window.confirm('Are you sure you want to delete ALL conversations? This action cannot be undone.');
    if (confirmed) {
      deviceMemory.deleteAllConversations();
      setMessages([]);
      toast.success('All conversations deleted successfully');
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Ethos AI
          </h1>
          <ModelSelector />
          <ModelSystemStatus />
        </div>
        
        {/* Global Search Bar */}
        <div className="flex-1 max-w-md mx-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <input
              type="text"
              placeholder="Search all conversations..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white text-sm"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const query = (e.target as HTMLInputElement).value;
                  if (query.trim()) {
                    window.open(`/search?q=${encodeURIComponent(query)}`, '_blank');
                  }
                }
              }}
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {/* Network Status Indicator */}
          <div className={`px-2 py-1 rounded text-xs ${
            networkStatus === 'connected' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
            networkStatus === 'disconnected' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
            'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          }`}>
            {networkStatus === 'connected' ? '🟢 Connected' :
             networkStatus === 'disconnected' ? '🔴 Disconnected' :
             '🟡 Checking...'}
          </div>
          
          {/* Delete Buttons */}
          {messages.length > 0 && (
            <>
              <button
                onClick={handleDeleteCurrentConversation}
                className="px-2 py-1 text-xs bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                title="Delete current conversation"
              >
                🗑️ Clear
              </button>
              <button
                onClick={handleDeleteAllConversations}
                className="px-2 py-1 text-xs bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                title="Delete all conversations"
              >
                🗑️ All
              </button>
            </>
          )}
          
          <ToolPanel />
          <ThemeSwitcher size="sm" />
          <button
            onClick={() => setShowVoiceInput(!showVoiceInput)}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <Mic size={20} />
          </button>
          <button
            onClick={() => window.location.href = '/settings'}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <Settings size={20} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <Bot size={48} className="mx-auto mb-4" />
              <p className="text-lg font-medium">Welcome to Ethos AI</p>
              <p className="text-sm mb-4">I'm Ethos, your personal AI assistant with real AI models! I remember our conversations and I'm here to help with anything you need!</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-2">💻 Coding & Development</h3>
                  <p className="text-sm text-blue-600 dark:text-blue-300">Write, debug, and review code in any language</p>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <h3 className="font-medium text-green-800 dark:text-green-200 mb-2">📊 Analysis & Research</h3>
                  <p className="text-sm text-green-600 dark:text-green-300">Analyze data, research topics, and solve problems</p>
                </div>
                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                  <h3 className="font-medium text-purple-800 dark:text-purple-200 mb-2">🖼️ Image & Vision</h3>
                  <p className="text-sm text-purple-600 dark:text-purple-300">Analyze images and generate visual content</p>
                </div>
                <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
                  <h3 className="font-medium text-orange-800 dark:text-orange-200 mb-2">📝 Writing & Content</h3>
                  <p className="text-sm text-orange-600 dark:text-orange-300">Create stories, articles, and creative content</p>
                </div>
              </div>
              <p className="text-sm mt-4">Start a conversation by typing a message below</p>
              <p className="text-xs mt-2 text-gray-400">Your conversations are stored locally on this device for privacy</p>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <MessageComponent key={message.id} message={message} />
        ))}

        {isTyping && (
          <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-sm">Ethos is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Voice Input Overlay */}
      {showVoiceInput && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Voice Input
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Speak your message to Ethos
              </p>
            </div>
            <VoiceInput
              onTranscript={handleVoiceInput}
              onError={(error) => toast.error(`Voice input error: ${error}`)}
              placeholder="Speak your message..."
            />
            <button
              onClick={() => setShowVoiceInput(false)}
              className="mt-4 w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
            />
          </div>
          
          <div className="flex space-x-2">
            {/* Web Search Button */}
            <WebSearchButton
              onWebSearch={(forceSearch) => handleSend(forceSearch)}
              isSearching={isLoading}
              searchPerformed={lastWebSearch?.performed || false}
              sourcesUsed={lastWebSearch?.sourcesUsed || {}}
            />
            
            <label className="cursor-pointer p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <Upload size={20} />
              <input
                type="file"
                multiple
                className="hidden"
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  handleFileUpload(files);
                }}
              />
            </label>
            
            <button
              onClick={() => handleSend(false)}
              disabled={!input.trim() || isLoading}
              className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
        
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 