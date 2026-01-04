
export type MessageRole = 'user' | 'stilo';

export interface MessagePart {
  text?: string;
  image?: string; // base64
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  parts: MessagePart[];
  timestamp: Date;
  isGenerating?: boolean;
}

export interface StiloConfig {
  apiKey: string;
}
