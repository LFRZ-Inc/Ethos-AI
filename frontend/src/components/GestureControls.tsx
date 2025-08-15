import React, { useState, useRef, useEffect } from 'react';
import { Hand, MousePointer, RotateCw, ZoomIn, ZoomOut, Fingerprint } from 'lucide-react';

interface GestureControlsProps {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onPinchIn?: () => void;
  onPinchOut?: () => void;
  onDoubleTap?: () => void;
  onLongPress?: () => void;
  enabled?: boolean;
  className?: string;
}

interface TouchPoint {
  x: number;
  y: number;
  timestamp: number;
}

const GestureControls: React.FC<GestureControlsProps> = ({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onPinchIn,
  onPinchOut,
  onDoubleTap,
  onLongPress,
  enabled = true,
  className = ''
}) => {
  const [isActive, setIsActive] = useState(false);
  const [gestureType, setGestureType] = useState<string>('');
  const [touchPoints, setTouchPoints] = useState<TouchPoint[]>([]);
  const [initialDistance, setInitialDistance] = useState<number>(0);
  const [lastTapTime, setLastTapTime] = useState<number>(0);
  const [longPressTimer, setLongPressTimer] = useState<number | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const isLongPressActive = useRef<boolean>(false);

  useEffect(() => {
    if (!enabled) return;

    const container = containerRef.current;
    if (!container) return;

    const handleTouchStart = (e: TouchEvent) => {
      e.preventDefault();
      setIsActive(true);
      setGestureType('');
      
      const touches = Array.from(e.touches);
      const points: TouchPoint[] = touches.map(touch => ({
        x: touch.clientX,
        y: touch.clientY,
        timestamp: Date.now()
      }));
      
      setTouchPoints(points);
      
      // Handle single touch gestures
      if (touches.length === 1) {
        const touch = touches[0];
        
        // Start long press timer
        const timer = setTimeout(() => {
          if (onLongPress) {
            setGestureType('long-press');
            onLongPress();
            isLongPressActive.current = true;
          }
        }, 500);
        
        setLongPressTimer(timer as any);
      }
      
      // Handle multi-touch gestures
      if (touches.length === 2) {
        const distance = getDistance(touches[0], touches[1]);
        setInitialDistance(distance);
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      e.preventDefault();
      
      if (isLongPressActive.current) return;
      
      const touches = Array.from(e.touches);
      
      // Handle pinch gestures
      if (touches.length === 2 && initialDistance > 0) {
        const currentDistance = getDistance(touches[0], touches[1]);
        const scale = currentDistance / initialDistance;
        
        if (scale < 0.8 && onPinchIn) {
          setGestureType('pinch-in');
          onPinchIn();
        } else if (scale > 1.2 && onPinchOut) {
          setGestureType('pinch-out');
          onPinchOut();
        }
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      e.preventDefault();
      setIsActive(false);
      
      // Clear long press timer
      if (longPressTimer) {
        clearTimeout(longPressTimer as any);
        setLongPressTimer(null);
      }
      
      isLongPressActive.current = false;
      
      if (touchPoints.length === 1) {
        const startPoint = touchPoints[0];
        const endPoint = {
          x: e.changedTouches[0].clientX,
          y: e.changedTouches[0].clientY,
          timestamp: Date.now()
        };
        
        // Calculate swipe distance and direction
        const deltaX = endPoint.x - startPoint.x;
        const deltaY = endPoint.y - startPoint.y;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const duration = endPoint.timestamp - startPoint.timestamp;
        
        // Minimum distance and maximum duration for swipe
        const minDistance = 50;
        const maxDuration = 300;
        
        if (distance > minDistance && duration < maxDuration) {
          const absDeltaX = Math.abs(deltaX);
          const absDeltaY = Math.abs(deltaY);
          
          if (absDeltaX > absDeltaY) {
            // Horizontal swipe
            if (deltaX > 0 && onSwipeRight) {
              setGestureType('swipe-right');
              onSwipeRight();
            } else if (deltaX < 0 && onSwipeLeft) {
              setGestureType('swipe-left');
              onSwipeLeft();
            }
          } else {
            // Vertical swipe
            if (deltaY > 0 && onSwipeDown) {
              setGestureType('swipe-down');
              onSwipeDown();
            } else if (deltaY < 0 && onSwipeUp) {
              setGestureType('swipe-up');
              onSwipeUp();
            }
          }
        } else if (distance < 10 && duration < 200) {
          // Check for double tap
          const currentTime = Date.now();
          const timeDiff = currentTime - lastTapTime;
          
          if (timeDiff < 300 && onDoubleTap) {
            setGestureType('double-tap');
            onDoubleTap();
          }
          
          setLastTapTime(currentTime);
        }
      }
      
      setTouchPoints([]);
      setInitialDistance(0);
      
      // Clear gesture type after a delay
      setTimeout(() => setGestureType(''), 1000);
    };

    // Add event listeners
    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: false });
    
    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [
    enabled,
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    onPinchIn,
    onPinchOut,
    onDoubleTap,
    onLongPress,
    initialDistance,
    lastTapTime,
    longPressTimer,
    touchPoints
  ]);

  const getDistance = (touch1: Touch, touch2: Touch): number => {
    const deltaX = touch1.clientX - touch2.clientX;
    const deltaY = touch1.clientY - touch2.clientY;
    return Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  };

  const getGestureIcon = () => {
    switch (gestureType) {
      case 'swipe-left':
        return <MousePointer size={20} className="text-blue-500" />;
      case 'swipe-right':
        return <MousePointer size={20} className="text-blue-500" />;
      case 'swipe-up':
        return <MousePointer size={20} className="text-blue-500" />;
      case 'swipe-down':
        return <MousePointer size={20} className="text-blue-500" />;
      case 'pinch-in':
        return <ZoomOut size={20} className="text-green-500" />;
      case 'pinch-out':
        return <ZoomIn size={20} className="text-green-500" />;
      case 'double-tap':
        return <Fingerprint size={20} className="text-purple-500" />;
      case 'long-press':
        return <Hand size={20} className="text-orange-500" />;
      default:
        return <Fingerprint size={20} className="text-gray-400" />;
    }
  };

  const getGestureLabel = () => {
    switch (gestureType) {
      case 'swipe-left':
        return 'Swipe Left';
      case 'swipe-right':
        return 'Swipe Right';
      case 'swipe-up':
        return 'Swipe Up';
      case 'swipe-down':
        return 'Swipe Down';
      case 'pinch-in':
        return 'Pinch In';
      case 'pinch-out':
        return 'Pinch Out';
      case 'double-tap':
        return 'Double Tap';
      case 'long-press':
        return 'Long Press';
      default:
        return 'Touch to interact';
    }
  };

  if (!enabled) {
    return null;
  }

  return (
    <div className={`relative ${className}`}>
      {/* Gesture Area */}
      <div
        ref={containerRef}
        className={`
          w-full h-full min-h-[200px] rounded-lg border-2 border-dashed
          flex items-center justify-center transition-all duration-200
          ${isActive 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800'
          }
          ${gestureType ? 'border-solid' : 'border-dashed'}
        `}
        style={{ touchAction: 'none' }}
      >
        {/* Gesture Feedback */}
        <div className="text-center">
          <div className="mb-2">
            {getGestureIcon()}
          </div>
          <div className={`
            text-sm font-medium transition-colors duration-200
            ${gestureType 
              ? 'text-gray-900 dark:text-white' 
              : 'text-gray-500 dark:text-gray-400'
            }
          `}>
            {getGestureLabel()}
          </div>
          
          {/* Active indicator */}
          {isActive && (
            <div className="mt-2 flex items-center justify-center space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-xs text-blue-600 dark:text-blue-400">
                Active
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Gesture Instructions */}
      <div className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center space-x-1">
            <Fingerprint size={12} />
            <span>Tap</span>
          </div>
          <div className="flex items-center space-x-1">
            <RotateCw size={12} />
            <span>Double tap</span>
          </div>
          <div className="flex items-center space-x-1">
            <Hand size={12} />
            <span>Long press</span>
          </div>
          <div className="flex items-center space-x-1">
            <MousePointer size={12} />
            <span>Swipe</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GestureControls; 