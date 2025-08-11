import React, { useState, useEffect } from 'react';
import { Sun, Moon, Monitor, Palette } from 'lucide-react';

type Theme = 'light' | 'dark' | 'auto';

interface ThemeSwitcherProps {
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({
  className = '',
  showLabel = false,
  size = 'md'
}) => {
  const [theme, setTheme] = useState<Theme>('auto');
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('ethos-theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
      applyTheme(savedTheme);
    } else {
      // Check system preference
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      setTheme('auto');
      applyTheme(systemTheme);
    }
  }, []);

  useEffect(() => {
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (theme === 'auto') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const applyTheme = (newTheme: 'light' | 'dark' | 'auto') => {
    const root = document.documentElement;
    
    if (newTheme === 'dark') {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    } else if (newTheme === 'light') {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    } else {
      // Auto theme - use system preference
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      if (systemTheme === 'dark') {
        root.classList.add('dark');
        root.setAttribute('data-theme', 'dark');
      } else {
        root.classList.remove('dark');
        root.setAttribute('data-theme', 'light');
      }
    }
  };

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('ethos-theme', newTheme);
    
    if (newTheme === 'auto') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      applyTheme(systemTheme);
    } else {
      applyTheme(newTheme);
    }
    
    setIsOpen(false);
  };

  const getIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun size={getIconSize()} />;
      case 'dark':
        return <Moon size={getIconSize()} />;
      case 'auto':
        return <Monitor size={getIconSize()} />;
      default:
        return <Palette size={getIconSize()} />;
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm':
        return 16;
      case 'lg':
        return 24;
      default:
        return 20;
    }
  };

  const getButtonSize = () => {
    switch (size) {
      case 'sm':
        return 'w-8 h-8';
      case 'lg':
        return 'w-12 h-12';
      default:
        return 'w-10 h-10';
    }
  };

  const getMenuSize = () => {
    switch (size) {
      case 'sm':
        return 'w-32';
      case 'lg':
        return 'w-40';
      default:
        return 'w-36';
    }
  };

  const themes = [
    {
      value: 'light' as Theme,
      label: 'Light',
      icon: <Sun size={16} />,
      description: 'Light theme'
    },
    {
      value: 'dark' as Theme,
      label: 'Dark',
      icon: <Moon size={16} />,
      description: 'Dark theme'
    },
    {
      value: 'auto' as Theme,
      label: 'Auto',
      icon: <Monitor size={16} />,
      description: 'Follow system'
    }
  ];

  return (
    <div className={`relative ${className}`}>
      {/* Theme Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          ${getButtonSize()} rounded-lg flex items-center justify-center transition-all duration-200
          bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700
          text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white
          border border-gray-200 dark:border-gray-700
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900
        `}
        aria-label="Toggle theme"
      >
        {getIcon()}
      </button>

      {/* Theme Options Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown Menu */}
          <div className={`
            absolute right-0 top-full mt-2 ${getMenuSize()} z-20
            bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
            py-2 overflow-hidden
          `}>
            {themes.map((themeOption) => (
              <button
                key={themeOption.value}
                onClick={() => handleThemeChange(themeOption.value)}
                className={`
                  w-full px-4 py-3 flex items-center space-x-3 text-left
                  transition-colors duration-150
                  ${theme === themeOption.value
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                  }
                `}
              >
                <div className={`
                  ${theme === themeOption.value
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                  }
                `}>
                  {themeOption.icon}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-sm">{themeOption.label}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {themeOption.description}
                  </div>
                </div>
                {theme === themeOption.value && (
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                )}
              </button>
            ))}
          </div>
        </>
      )}

      {/* Label (optional) */}
      {showLabel && (
        <div className="mt-2 text-center">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {theme === 'auto' ? 'Auto' : theme === 'light' ? 'Light' : 'Dark'}
          </span>
        </div>
      )}
    </div>
  );
};

export default ThemeSwitcher; 