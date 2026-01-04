
import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import { ChatMessage as ChatMessageType } from './types';
import { analyzeStyle } from './services/geminiService';

const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessageType[]>([
    {
      id: 'welcome',
      role: 'stilo',
      parts: [{ text: 'Fala, parceiro! Sou o Stilo, seu consultor de imagem. 👔\n\nEstou aqui para dar um upgrade no seu visual com base no seu biotipo e na ocasião que você precisa.\n\nComo posso te ajudar hoje? Pode mandar uma foto sua ou de alguma peça que você curtiu para a gente começar a análise.' }],
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = async (text: string, image?: string) => {
    const userMsg: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      parts: [
        ...(text ? [{ text }] : []),
        ...(image ? [{ image }] : [])
      ],
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const response = await analyzeStyle([...messages, userMsg]);
      
      const stiloMsgParts = [];
      
      if (response.text) {
        stiloMsgParts.push({ text: response.text });
      }

      if (response.image) {
        stiloMsgParts.push({ image: response.image });
      }

      if (stiloMsgParts.length === 0) {
        stiloMsgParts.push({ text: 'Não consegui processar a visualização agora, mas posso te orientar no texto.' });
      }

      const stiloMsg: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'stilo',
        parts: stiloMsgParts,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, stiloMsg]);
    } catch (error) {
      console.error("Erro na comunicação com a IA:", error);
      setMessages(prev => [...prev, {
        id: 'error',
        role: 'stilo',
        parts: [{ text: 'Houve um erro técnico na minha análise. Poderia repetir a mensagem? 🛠️' }],
        timestamp: new Date()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-[#e5ddd5] shadow-2xl relative overflow-hidden border-x border-gray-300">
      <div className="chat-bg"></div>
      <Header />
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 z-10">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isTyping && (
           <ChatMessage 
             message={{ 
               id: 'typing', 
               role: 'stilo', 
               parts: [], 
               timestamp: new Date(), 
               isGenerating: true 
             }} 
           />
        )}
      </div>
      <ChatInput onSend={handleSendMessage} disabled={isTyping} />
    </div>
  );
};

export default App;
