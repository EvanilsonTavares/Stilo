
import React from 'react';
import { ChatMessage as ChatMessageType } from '../types';

interface Props {
  message: ChatMessageType;
}

const ChatMessage: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex w-full mb-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] rounded-lg px-3 py-2 shadow-sm relative ${
        isUser ? 'bg-[#dcf8c6] text-gray-800 rounded-tr-none' : 'bg-white text-gray-800 rounded-tl-none'
      }`}>
        {message.parts.map((part, idx) => (
          <div key={idx} className="space-y-2">
            {part.image && (
              <img 
                src={part.image} 
                alt="Uploaded style" 
                className="rounded-md max-w-full h-auto mb-1 border border-black/5" 
              />
            )}
            {part.text && (
              <p className="text-[14.5px] whitespace-pre-wrap leading-relaxed">
                {part.text}
              </p>
            )}
          </div>
        ))}
        
        {message.isGenerating && (
          <div className="flex gap-1 py-1">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
          </div>
        )}
        
        <div className="text-[10px] text-gray-500 mt-1 text-right flex items-center justify-end gap-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          {isUser && (
             <svg className="w-3.5 h-3.5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
               <path d="M20 6L9 17l-5-5" />
             </svg>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
