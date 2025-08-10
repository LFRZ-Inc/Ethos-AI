import React, { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Send, Upload, Settings, Bot, User } from 'lucide-react';
import { useChatStore, Message } from '../stores/appStore';
import { useAppStore } from '../stores/appStore';
import { useConversationStore } from '../stores/appStore';
import toast from 'react-hot-toast';
import MessageComponent from './MessageComponent';
import ModelSelector from './ModelSelector';
import ToolPanel from './ToolPanel';
import { API_ENDPOINTS } from '../config';

const ChatInterface: React.FC = () => {
  const { conversationId } = useParams();
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, isLoading, addMessage, setLoading, setError } = useChatStore();
  const { currentConversationId, selectedModel, useTools, setCurrentConversation } = useAppStore();
  const { conversations, loadConversations, addConversation } = useConversationStore();

  useEffect(() => {
    if (conversationId) {
      setCurrentConversation(conversationId);
      loadConversation(conversationId);
    } else {
      setCurrentConversation(null);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversation = async (id: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.conversations}/${id}`);
      if (response.ok) {
        const conversation = await response.json();
        // Load messages into chat store
        const chatMessages: Message[] = conversation.messages.map((msg: any) => ({
          id: `${msg.timestamp}-${Math.random()}`,
          role: msg.user ? 'user' : 'assistant',
          content: msg.user || msg.assistant,
          timestamp: msg.timestamp,
          modelUsed: msg.model_used,
        }));
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

  const handleSend = async () => {
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
      // Create conversation if needed
      let convId = currentConversationId;
      if (!convId) {
        try {
          const response = await fetch(API_ENDPOINTS.conversations, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: input.substring(0, 50) + '...' }),
          });
          if (response.ok) {
            const result = await response.json();
            convId = result.conversation_id;
            setCurrentConversation(convId);
          } else {
            console.error('Failed to create conversation:', response.status);
          }
        } catch (error) {
          console.error('Error creating conversation:', error);
        }
      }

      // Send message to backend
      const response = await fetch(API_ENDPOINTS.chat, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: input,
          conversation_id: convId,
          model_override: selectedModel || null,
          use_tools: useTools,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const result = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.content,
        timestamp: result.timestamp,
        modelUsed: result.model_used,
        toolsCalled: result.tools_called,
      };

      addMessage(assistantMessage);

      // Reload conversations to update the list
      await loadConversations();

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
      handleSend();
    }
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

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
            Ethos AI
          </h1>
          <ModelSelector />
        </div>
        <div className="flex items-center space-x-2">
          <ToolPanel />
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
              <p className="text-sm">Start a conversation by typing a message below</p>
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
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

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
              onClick={handleSend}
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