
import { ChatMessage } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const analyzeStyle = async (messages: ChatMessage[]) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages }),
    });

    if (!response.ok) {
      throw new Error(`Backend Error: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      text: data.text,
      image: data.image
    };
  } catch (error) {
    console.error("Erro na comunicação com o backend:", error);
    throw error;
  }
};
