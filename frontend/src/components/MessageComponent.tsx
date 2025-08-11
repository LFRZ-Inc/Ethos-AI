import React from 'react';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Message } from '../stores/appStore';

interface MessageComponentProps {
  message: Message;
}

const MessageComponent: React.FC<MessageComponentProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-gray-500'
        }`}>
          {isUser ? (
            <User size={16} className="text-white" />
          ) : (
            <Bot size={16} className="text-white" />
          )}
        </div>
        
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block p-4 rounded-lg ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
          }`}>
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={tomorrow as any}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
          
          <div className={`mt-2 text-xs text-gray-500 ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
            {!isUser && (
              <span className="ml-2 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                Ethos AI
              </span>
            )}
          </div>
          
          {message.toolsCalled && message.toolsCalled.length > 0 && (
            <div className="mt-2 text-xs text-gray-500">
              <div className="font-medium">Tools used:</div>
              {message.toolsCalled.map((tool, index) => (
                <div key={index} className="ml-2">
                  • {tool.tool_name}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageComponent; 