
import asyncio
import os
from dotenv import load_dotenv
from services.whatsapp_service import WhatsAppService

load_dotenv(override=True)

async def main():
    wa = WhatsAppService()
    # Número identificado no dashboard da Meta
    recipient = "5583996702675" 
    
    message = "Olá! Aqui é o Stilo, seu consultor de imagem. 👔\n\nEstou passando para avisar que meu sistema foi atualizado e agora estou pronto para analisar seus looks aqui no WhatsApp. \n\nPosso te ajudar com alguma sugestão hoje?"
    
    print(f"Enviando mensagem para {recipient}...")
    try:
        result = await wa.send_text_message(recipient, message)
        print("Sucesso! Resposta da API:", result)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

if __name__ == "__main__":
    asyncio.run(main())
