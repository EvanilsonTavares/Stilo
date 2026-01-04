
import { GoogleGenAI } from "@google/genai";
import { ChatMessage } from "../types";

/**
 * SYSTEM_PROMPT: Implementação fiel ao DOSSIÊ MESTRE – PROJETO “STILO”
 */
const SYSTEM_PROMPT = `
Você é o "Stilo", um Consultor de Imagem Masculina Virtual de alto nível.
Seu tom é parceiro, técnico e direto.

VOCÊ ANALISA:
- Biotipo
- Colorimetria
- Caimento (fit)
- Ocasião de uso

REGRAS CRÍTICAS (OPERACIONAIS):
1. Sempre responda com texto técnico e personalizado primeiro.
2. Só gere visualização se o usuário pedir explicitamente (ex: "me mostra", "gera imagem", "como fica em mim").
3. Se o gatilho de visualização for acionado, sua resposta deve ser ÚNICA e EXCLUSIVAMENTE o objeto JSON definido abaixo. NÃO escreva texto antes ou depois.
4. Nunca explique decisões internas ou mencione o JSON para o usuário.
5. Bloqueie conteúdo impróprio (nudez, menores, etc).

CONTRATO DE COMUNICAÇÃO (JSON SCHEMA V1):
{
  "v": 1,
  "request_id": "gerar-uuid-v4",
  "action": "generate_reference_image | virtual_try_on",
  "params": {
    "prompt": "string em inglês detalhando o look, tecido, luz e cenário fotorrealista",
    "user_image_url": "string (se houver foto do usuário)",
    "garment_category": "upper_body | lower_body | dresses",
    "crop": false,
    "aspect_ratio": "3:4"
  }
}

DIRETRIZES DE AÇÃO:
- "generate_reference_image": Para sugestões visuais em modelos genéricos.
- "virtual_try_on": Quando o usuário quer ver a peça no próprio corpo (requer foto do usuário enviada anteriormente).
`;

export const analyzeStyle = async (messages: ChatMessage[]) => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  // Mapeamento de mensagens para o Gemini
  const contents = messages.map(msg => ({
    role: msg.role === 'user' ? 'user' : 'model',
    parts: msg.parts.map(p => {
      if (p.image) {
        return {
          inlineData: {
            mimeType: 'image/jpeg',
            data: p.image.split(',')[1]
          }
        };
      }
      return { text: p.text || "" };
    })
  }));

  // Cérebro (LLM): Gemini 3 Pro para lógica complexa
  const textResponse = await ai.models.generateContent({
    model: 'gemini-3-pro-preview',
    contents: contents as any,
    config: {
      systemInstruction: SYSTEM_PROMPT,
      temperature: 0.2, // Baixa temperatura para garantir fidelidade ao JSON
      topP: 0.95,
      topK: 64,
    }
  });

  const rawText = textResponse.text || "";
  let cleanText = rawText;
  let generatedImageBase64 = "";
  let actionDetected = null;

  // Extração de JSON robusta (ignora textos adjacentes e markdown)
  const startIdx = rawText.indexOf('{');
  const endIdx = rawText.lastIndexOf('}');

  if (startIdx !== -1 && endIdx !== -1 && endIdx > startIdx) {
    const jsonCandidate = rawText.substring(startIdx, endIdx + 1);
    
    try {
      const command = JSON.parse(jsonCandidate);
      
      if (command.action && (command.action === "generate_reference_image" || command.action === "virtual_try_on")) {
        actionDetected = command.action;
        
        // Se detectou JSON de ação, remove do texto final exibido ao usuário
        cleanText = (rawText.substring(0, startIdx) + rawText.substring(endIdx + 1)).trim();
        cleanText = cleanText.replace(/```json\s?/g, "").replace(/```/g, "").trim();

        // Mãos (Image Generation): Gemini 2.5 Flash Image para simular o visual
        const promptParaImagem = command.params?.prompt || "A stylish man in high fashion clothing, cinematic lighting.";
        
        const imgAi = new GoogleGenAI({ apiKey: process.env.API_KEY });
        const imgResponse = await imgAi.models.generateContent({
          model: 'gemini-2.5-flash-image',
          contents: {
            parts: [{ text: promptParaImagem }]
          },
          config: {
            imageConfig: { 
              aspectRatio: command.params?.aspect_ratio || "3:4"
            }
          }
        });

        // Extrai a imagem gerada
        if (imgResponse.candidates?.[0]?.content?.parts) {
          for (const part of imgResponse.candidates[0].content.parts) {
            if (part.inlineData) {
              generatedImageBase64 = `data:image/png;base64,${part.inlineData.data}`;
              break;
            }
          }
        }
      }
    } catch (e) {
      console.error("Erro ao interpretar comando JSON do Stilo:", e);
      // Fallback: se o parsing falhar, tentamos apenas limpar o markdown para exibir o texto
      cleanText = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
    }
  }

  // Fallback caso o modelo retorne apenas o JSON (comum quando visual é solicitado)
  if (!cleanText && generatedImageBase64) {
    cleanText = actionDetected === "virtual_try_on" 
      ? "Aqui está o resultado do seu provador virtual! 👔✨" 
      : "Preparei essa referência visual para você conferir o estilo:";
  }

  return { 
    text: cleanText, 
    image: generatedImageBase64 
  };
};
