import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Settings, RotateCcw } from 'lucide-react';

// Type declarations for speech recognition
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

const VoiceInput: React.FC<VoiceInputProps> = ({
  onTranscript,
  onError,
  disabled = false,
  placeholder = "Tap to speak...",
  className = ""
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const [volume, setVolume] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const microphoneRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      setIsSupported(true);
      const recognitionInstance = new SpeechRecognition();
      
      // Configure recognition settings
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';
      
      // Event handlers
      recognitionInstance.onstart = () => {
        setIsListening(true);
        setError('');
        startVolumeVisualization();
      };
      
      recognitionInstance.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        const fullTranscript = finalTranscript + interimTranscript;
        setTranscript(fullTranscript);
        
        if (finalTranscript) {
          setIsProcessing(true);
          // Send final transcript to parent
          onTranscript(finalTranscript.trim());
          setTranscript('');
          setIsProcessing(false);
        }
      };
      
      recognitionInstance.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setError(event.error);
        setIsListening(false);
        stopVolumeVisualization();
        if (onError) {
          onError(event.error);
        }
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false);
        stopVolumeVisualization();
      };
      
      setRecognition(recognitionInstance);
    } else {
      setIsSupported(false);
      setError('Speech recognition not supported in this browser');
    }
    
    return () => {
      if (recognition) {
        recognition.stop();
      }
      stopVolumeVisualization();
    };
  }, [onTranscript, onError]);

  const startVolumeVisualization = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      microphoneRef.current = audioContextRef.current.createMediaStreamSource(stream);
      
      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      microphoneRef.current.connect(analyserRef.current);
      
      const updateVolume = () => {
        if (!analyserRef.current || isMuted) {
          setVolume(0);
          return;
        }
        
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / bufferLength;
        setVolume(average / 255);
        
        if (isListening) {
          animationFrameRef.current = requestAnimationFrame(updateVolume);
        }
      };
      
      updateVolume();
    } catch (err) {
      console.error('Error accessing microphone:', err);
      setError('Microphone access denied');
    }
  };

  const stopVolumeVisualization = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (microphoneRef.current) {
      microphoneRef.current.disconnect();
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    setVolume(0);
  };

  const toggleListening = () => {
    if (!isSupported || disabled) return;
    
    if (isListening) {
      recognition?.stop();
    } else {
      setTranscript('');
      setError('');
      recognition?.start();
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const resetTranscript = () => {
    setTranscript('');
    setError('');
  };

  const getVolumeBars = () => {
    const bars = [];
    const barCount = 20;
    const activeBars = Math.floor(volume * barCount);
    
    for (let i = 0; i < barCount; i++) {
      const isActive = i < activeBars;
      const height = isActive ? Math.max(2, (i + 1) * 2) : 2;
      bars.push(
        <div
          key={i}
          className={`w-1 rounded-full transition-all duration-75 ${
            isActive 
              ? 'bg-blue-500 dark:bg-blue-400' 
              : 'bg-gray-300 dark:bg-gray-600'
          }`}
          style={{ height: `${height}px` }}
        />
      );
    }
    return bars;
  };

  if (!isSupported) {
    return (
      <div className={`flex items-center justify-center p-4 text-red-500 dark:text-red-400 ${className}`}>
        <MicOff size={20} className="mr-2" />
        <span>Voice input not supported</span>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center space-y-4 ${className}`}>
      {/* Voice Input Button */}
      <div className="relative">
        <button
          onClick={toggleListening}
          disabled={disabled}
          className={`
            relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300
            ${isListening 
              ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/50' 
              : 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-500/50'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            ${isProcessing ? 'animate-pulse' : ''}
          `}
        >
          {isListening ? (
            <MicOff size={24} className="text-white" />
          ) : (
            <Mic size={24} className="text-white" />
          )}
          
          {/* Ripple effect when listening */}
          {isListening && (
            <div className="absolute inset-0 rounded-full border-2 border-red-400 animate-ping" />
          )}
        </button>
        
        {/* Volume visualization */}
        {isListening && (
          <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 flex items-end space-x-1 h-8">
            {getVolumeBars()}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center space-x-4">
        <button
          onClick={toggleMute}
          className={`p-2 rounded-full transition-colors ${
            isMuted 
              ? 'bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400' 
              : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
          }`}
        >
          {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </button>
        
        <button
          onClick={resetTranscript}
          className="p-2 rounded-full bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          <RotateCcw size={16} />
        </button>
      </div>

      {/* Status and Transcript */}
      <div className="w-full max-w-md text-center">
        {/* Status */}
        <div className="mb-2">
          {isListening && (
            <div className="flex items-center justify-center space-x-2 text-blue-600 dark:text-blue-400">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Listening...</span>
            </div>
          )}
          {isProcessing && (
            <div className="flex items-center justify-center space-x-2 text-yellow-600 dark:text-yellow-400">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Processing...</span>
            </div>
          )}
          {error && (
            <div className="flex items-center justify-center space-x-2 text-red-600 dark:text-red-400">
              <span className="text-sm">{error}</span>
            </div>
          )}
        </div>

        {/* Transcript */}
        {transcript && (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-sm text-gray-700 dark:text-gray-300">
            <div className="font-medium mb-1">Transcript:</div>
            <div>{transcript}</div>
          </div>
        )}

        {/* Instructions */}
        {!isListening && !transcript && (
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {placeholder}
          </div>
        )}
      </div>

      {/* Mobile-specific instructions */}
      <div className="text-xs text-gray-400 dark:text-gray-500 text-center max-w-sm">
        <p>Tap the microphone to start speaking</p>
        <p>Tap again to stop recording</p>
        <p>Your speech will be automatically converted to text</p>
      </div>
    </div>
  );
};

export default VoiceInput; 