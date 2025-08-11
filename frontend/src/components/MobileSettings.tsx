import React, { useState } from 'react';
import { 
  Settings, 
  Mic, 
  Palette, 
  Hand, 
  Smartphone, 
  Volume2, 
  VolumeX, 
  RotateCw,
  Sun,
  Moon,
  Monitor,
  Check,
  X
} from 'lucide-react';
import VoiceInput from './VoiceInput';
import ThemeSwitcher from './ThemeSwitcher';
import GestureControls from './GestureControls';

interface MobileSettingsProps {
  onClose: () => void;
}

const MobileSettings: React.FC<MobileSettingsProps> = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState<'voice' | 'theme' | 'gestures' | 'general'>('voice');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [gestureEnabled, setGestureEnabled] = useState(true);
  const [autoTheme, setAutoTheme] = useState(true);

  const tabs = [
    { id: 'voice', label: 'Voice', icon: <Mic size={20} /> },
    { id: 'theme', label: 'Theme', icon: <Palette size={20} /> },
    { id: 'gestures', label: 'Gestures', icon: <Hand size={20} /> },
    { id: 'general', label: 'General', icon: <Settings size={20} /> }
  ];

  const handleGestureAction = (action: string) => {
    console.log(`Gesture action: ${action}`);
    // Handle different gesture actions
    switch (action) {
      case 'swipe-left':
        // Navigate back
        break;
      case 'swipe-right':
        // Navigate forward
        break;
      case 'swipe-up':
        // Scroll to top
        break;
      case 'swipe-down':
        // Refresh
        break;
      case 'double-tap':
        // Quick action
        break;
      case 'long-press':
        // Context menu
        break;
    }
  };

  return (
    <div className="fixed inset-0 bg-white dark:bg-gray-900 z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Mobile Settings</h1>
        <button
          onClick={onClose}
          className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <X size={24} />
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`
              flex-1 flex flex-col items-center py-3 px-2 transition-colors
              ${activeTab === tab.id
                ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }
            `}
          >
            {tab.icon}
            <span className="text-xs mt-1">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'voice' && (
          <div className="p-4 space-y-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Voice Input Settings
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Configure voice input and speech recognition
              </p>
            </div>

            {/* Voice Input Demo */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-3">Test Voice Input</h3>
              <VoiceInput
                onTranscript={(text) => console.log('Voice transcript:', text)}
                onError={(error) => console.error('Voice error:', error)}
                placeholder="Tap to test voice input..."
              />
            </div>

            {/* Voice Settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Enable Voice Input</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Allow voice input in conversations
                  </p>
                </div>
                <button
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  className={`
                    w-12 h-6 rounded-full transition-colors
                    ${voiceEnabled 
                      ? 'bg-blue-500' 
                      : 'bg-gray-300 dark:bg-gray-600'
                    }
                  `}
                >
                  <div className={`
                    w-5 h-5 bg-white rounded-full transition-transform
                    ${voiceEnabled ? 'translate-x-6' : 'translate-x-1'}
                  `} />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Auto-send Voice</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Automatically send voice input when you stop speaking
                  </p>
                </div>
                <button className="w-12 h-6 rounded-full bg-gray-300 dark:bg-gray-600">
                  <div className="w-5 h-5 bg-white rounded-full translate-x-1" />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Voice Feedback</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Play sounds for voice input events
                  </p>
                </div>
                <button className="w-12 h-6 rounded-full bg-blue-500">
                  <div className="w-5 h-5 bg-white rounded-full translate-x-6" />
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'theme' && (
          <div className="p-4 space-y-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Theme Settings
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Customize the appearance of Ethos AI
              </p>
            </div>

            {/* Theme Switcher */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-3">Choose Theme</h3>
              <div className="flex justify-center">
                <ThemeSwitcher size="lg" showLabel />
              </div>
            </div>

            {/* Theme Options */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Auto Theme</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Follow system theme preference
                  </p>
                </div>
                <button
                  onClick={() => setAutoTheme(!autoTheme)}
                  className={`
                    w-12 h-6 rounded-full transition-colors
                    ${autoTheme 
                      ? 'bg-blue-500' 
                      : 'bg-gray-300 dark:bg-gray-600'
                    }
                  `}
                >
                  <div className={`
                    w-5 h-5 bg-white rounded-full transition-transform
                    ${autoTheme ? 'translate-x-6' : 'translate-x-1'}
                  `} />
                </button>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="text-center">
                  <div className="w-16 h-16 bg-white border-2 border-gray-300 rounded-lg mx-auto mb-2 flex items-center justify-center">
                    <Sun size={24} className="text-yellow-500" />
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Light</span>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gray-800 border-2 border-gray-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                    <Moon size={24} className="text-blue-400" />
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Dark</span>
                </div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-white to-gray-800 border-2 border-gray-400 rounded-lg mx-auto mb-2 flex items-center justify-center">
                    <Monitor size={24} className="text-gray-600" />
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Auto</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'gestures' && (
          <div className="p-4 space-y-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Gesture Controls
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Configure touch gestures for mobile interaction
              </p>
            </div>

            {/* Gesture Demo */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-3">Test Gestures</h3>
              <GestureControls
                onSwipeLeft={() => handleGestureAction('swipe-left')}
                onSwipeRight={() => handleGestureAction('swipe-right')}
                onSwipeUp={() => handleGestureAction('swipe-up')}
                onSwipeDown={() => handleGestureAction('swipe-down')}
                onDoubleTap={() => handleGestureAction('double-tap')}
                onLongPress={() => handleGestureAction('long-press')}
                enabled={gestureEnabled}
              />
            </div>

            {/* Gesture Settings */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Enable Gestures</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Allow touch gestures for navigation
                  </p>
                </div>
                <button
                  onClick={() => setGestureEnabled(!gestureEnabled)}
                  className={`
                    w-12 h-6 rounded-full transition-colors
                    ${gestureEnabled 
                      ? 'bg-blue-500' 
                      : 'bg-gray-300 dark:bg-gray-600'
                    }
                  `}
                >
                  <div className={`
                    w-5 h-5 bg-white rounded-full transition-transform
                    ${gestureEnabled ? 'translate-x-6' : 'translate-x-1'}
                  `} />
                </button>
              </div>

              <div className="space-y-3">
                <h3 className="font-medium text-gray-900 dark:text-white">Gesture Actions</h3>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Swipe Left</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Go back</div>
                  </div>
                  <Check size={16} className="text-green-500" />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Swipe Right</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Go forward</div>
                  </div>
                  <Check size={16} className="text-green-500" />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Swipe Up</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Scroll to top</div>
                  </div>
                  <Check size={16} className="text-green-500" />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Double Tap</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Quick action</div>
                  </div>
                  <Check size={16} className="text-green-500" />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Long Press</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Context menu</div>
                  </div>
                  <Check size={16} className="text-green-500" />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'general' && (
          <div className="p-4 space-y-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                General Settings
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                General mobile preferences and options
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Mobile Optimized</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Optimize interface for mobile devices
                  </p>
                </div>
                <button className="w-12 h-6 rounded-full bg-blue-500">
                  <div className="w-5 h-5 bg-white rounded-full translate-x-6" />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Haptic Feedback</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Enable vibration feedback for interactions
                  </p>
                </div>
                <button className="w-12 h-6 rounded-full bg-blue-500">
                  <div className="w-5 h-5 bg-white rounded-full translate-x-6" />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Auto-rotate</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Allow screen rotation
                  </p>
                </div>
                <button className="w-12 h-6 rounded-full bg-gray-300 dark:bg-gray-600">
                  <div className="w-5 h-5 bg-white rounded-full translate-x-1" />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Battery Saver</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Optimize for battery life
                  </p>
                </div>
                <button className="w-12 h-6 rounded-full bg-gray-300 dark:bg-gray-600">
                  <div className="w-5 h-5 bg-white rounded-full translate-x-1" />
                </button>
              </div>
            </div>

            {/* Device Info */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 dark:text-white mb-3">Device Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Platform:</span>
                  <span className="text-gray-900 dark:text-white">Mobile Web</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Screen Size:</span>
                  <span className="text-gray-900 dark:text-white">{window.innerWidth} × {window.innerHeight}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Touch Support:</span>
                  <span className="text-gray-900 dark:text-white">Yes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Voice Support:</span>
                  <span className="text-gray-900 dark:text-white">Yes</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileSettings; 