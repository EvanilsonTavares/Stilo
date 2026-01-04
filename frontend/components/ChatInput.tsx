
import React, { useState, useRef } from 'react';

interface Props {
  onSend: (text: string, image?: string) => void;
  disabled: boolean;
}

const ChatInput: React.FC<Props> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if ((!text.trim() && !preview) || disabled) return;
    onSend(text, preview || undefined);
    setText('');
    setPreview(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="bg-[#f0f2f5] p-2 sticky bottom-0 z-50">
      {preview && (
        <div className="mb-2 p-2 bg-white rounded-lg shadow-inner relative inline-block">
          <img src={preview} alt="Preview" className="h-20 w-20 object-cover rounded-md border" />
          <button 
            onClick={() => setPreview(null)}
            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
          >
            ✕
          </button>
        </div>
      )}
      <div className="flex items-center gap-2 max-w-4xl mx-auto">
        <button 
          onClick={() => fileInputRef.current?.click()}
          className="p-2 text-gray-500 hover:text-gray-700 bg-white rounded-full shadow-sm"
          disabled={disabled}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <input 
          type="file" 
          accept="image/*" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
        />
        
        <div className="flex-1 bg-white rounded-full flex items-center px-4 py-2 shadow-sm border border-gray-200">
          <textarea
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Mensagem"
            className="w-full focus:outline-none resize-none bg-transparent py-1 text-[15px]"
            disabled={disabled}
          />
        </div>

        <button 
          onClick={handleSend}
          disabled={disabled || (!text.trim() && !preview)}
          className={`p-3 rounded-full shadow-md transition-all ${
            (text.trim() || preview) ? 'bg-[#00a884] text-white active:scale-95' : 'bg-gray-300 text-gray-100 cursor-not-allowed'
          }`}
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
