import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import ChatInterface from './components/ChatInterface';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';
import { useAppStore } from './stores/appStore';
import './App.css';

function App() {
  const { theme } = useAppStore();

  return (
    <ErrorBoundary>
      <div className={`App ${theme}`}>
        <Router>
          <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
            <Sidebar />
            <main className="flex-1 flex flex-col">
              <Routes>
                <Route path="/" element={<ChatInterface />} />
                <Route path="/chat/:conversationId" element={<ChatInterface />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
        </Router>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: theme === 'dark' ? '#374151' : '#fff',
              color: theme === 'dark' ? '#fff' : '#000',
            },
          }}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App; 