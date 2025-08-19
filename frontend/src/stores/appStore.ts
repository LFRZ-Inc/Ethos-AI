import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { API_ENDPOINTS } from '../config';

interface AppState {
  theme: 'light' | 'dark';
  currentConversationId: string | null;
  selectedModel: string | null;
  useTools: boolean;
  setTheme: (theme: 'light' | 'dark') => void;
  setCurrentConversation: (id: string | null) => void;
  setSelectedModel: (model: string | null) => void;
  setUseTools: (use: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'dark',
      currentConversationId: null,
      selectedModel: null,
      useTools: true,
      setTheme: (theme) => set({ theme }),
      setCurrentConversation: (id) => set({ currentConversationId: id }),
      setSelectedModel: (model) => set({ selectedModel: model }),
      setUseTools: (use) => set({ useTools: use }),
    }),
    {
      name: 'ethos-ai-storage',
    }
  )
);

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
  setMessages: (messages: Message[]) => void;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  modelUsed?: string;
  toolsCalled?: any[];
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  clearMessages: () => set({ messages: [] }),
  setMessages: (messages) => set({ messages }),
}));

interface ConversationState {
  conversations: Conversation[];
  isLoading: boolean;
  loadConversations: () => Promise<void>;
  addConversation: (conversation: Conversation) => void;
  deleteConversation: (id: string) => void;
  updateConversation: (id: string, updates: Partial<Conversation>) => void;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  conversations: [],
  isLoading: false,
  loadConversations: async () => {
    set({ isLoading: true });
    try {
      const response = await fetch(API_ENDPOINTS.conversations);
      if (response.ok) {
        const data = await response.json();
        // Handle both direct array and object with conversations property
        const conversationsArray = Array.isArray(data) ? data : (data.conversations || []);
        set({ conversations: conversationsArray, isLoading: false });
      } else {
        console.warn('Failed to load conversations:', response.status, response.statusText);
        set({ conversations: [], isLoading: false });
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
      set({ conversations: [], isLoading: false });
    }
  },
  addConversation: (conversation) => set((state) => ({
    conversations: [conversation, ...state.conversations]
  })),
  deleteConversation: (id) => set((state) => ({
    conversations: state.conversations.filter(c => c.id !== id)
  })),
  updateConversation: (id, updates) => set((state) => ({
    conversations: state.conversations.map(c => 
      c.id === id ? { ...c, ...updates } : c
    )
  })),
})); 