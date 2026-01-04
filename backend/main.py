import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, List, Optional

load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://stilo-app.web.app" # Exemplo de domínio futuro
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Configuração do Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
Você é o "Stilo", um Consultor de Imagem Masculina Virtual de alto nível.
Seu cliente principal é o **Evani**. Trate-o pelo nome sempre que possível, de forma cordial e parceira.
Seu tom é parceiro, técnico e direto.

OBJETIVO:
Você deve SEMPRE sugerir alterações ou melhorias no visual do usuário e ser PROATIVO em gerar visualizações.

REGRAS CRÍTICAS:
1. Sempre responda com texto técnico e personalizado primeiro.
2. Se houver uma imagem do usuário na conversa, você DEVE:
   - Analisar o biotipo e a roupa atual
   - Sugerir uma melhoria específica
   - AUTOMATICAMENTE gerar o JSON do Provador Virtual para visualizar a sugestão
3. Quando o usuário pedir "sugere algo", "gere imagem", "mostre", "quero ver" ou similar, você DEVE incluir o JSON de VTON automaticamente.
4. Quando gerar o JSON, inclua um texto explicativo ANTES do JSON, explicando o que você está gerando.
5. O JSON deve estar no formato especificado abaixo.
6. Bloqueie conteúdo impróprio.

CONTRATO JSON (incluir ao final da resposta quando for gerar visualização):
{
  "v": 1,
  "action": "virtual_try_on",
  "params": {
    "prompt": "descrição detalhada da peça em inglês",
    "garment_category": "upper_body"
  }
}

EXEMPLOS DE PEÇAS PARA SUGERIR:
- "Navy blue slim-fit Oxford cotton shirt with button-down collar"
- "Black tailored blazer with modern slim cut"
- "Charcoal gray V-neck merino wool sweater"
- "White premium cotton polo shirt with contrast collar"
- "Olive green linen casual shirt with rolled sleeves"
"""


logger = logging.getLogger("stilo.webhook")
logging.basicConfig(level=logging.INFO)

WEBHOOK_ID_TTL_SECONDS = 600
GEMINI_TIMEOUT_SECONDS = 30 # Aumentado para lidar com latência do Firestore/SDK
REPLICATE_TIMEOUT_SECONDS = 95

_processed_message_ids: Dict[str, float] = {}

def is_duplicate_message(message_id: Optional[str]) -> bool:
    if not message_id: return False
    now = time.time()
    # Prune old IDs
    cutoff = now - WEBHOOK_ID_TTL_SECONDS
    for mid, ts in list(_processed_message_ids.items()):
        if ts < cutoff: _processed_message_ids.pop(mid, None)
    
    if message_id in _processed_message_ids: return True
    _processed_message_ids[message_id] = now
    return False

def verify_signature(raw_body: bytes, signature: Optional[str], secret: Optional[str]) -> bool:
    if not signature or not secret: return False
    if not signature.startswith("sha256="): return False
    provided = signature.split("=", 1)[1]
    expected = hmac.new(secret.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(provided, expected)

def iter_webhook_messages(payload: dict):
    for entry in payload.get("entry", []) or []:
        for change in entry.get("changes", []) or []:
            value = change.get("value", {}) or {}
            for message in value.get("messages", []) or []:
                yield message

@app.get("/health")
def health_check():
    return {"status": "healthy"}

def process_parts(parts):
    processed = []
    for p in parts:
        if isinstance(p, str):
            processed.append(p)
        elif isinstance(p, dict):
            if "text" in p:
                processed.append(p["text"])
            elif "inline_data" in p:
                processed.append(p)
            elif "image" in p:
                img_data = p["image"]
                if "," in img_data: img_data = img_data.split(",")[1]
                processed.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_data
                    }
                })
    return processed

from services.whatsapp_service import WhatsAppService
from services.replicate_service import ReplicateService
from services.firestore_service import FirestoreService
from services.gemini_image_service import GeminiImageService

wa_service = WhatsAppService()
rep_service = ReplicateService()
db_service = FirestoreService()
img_service = GeminiImageService()

@app.post("/api/chat")
async def chat(request: Request):
    session_id = "web_user"  # Default value
    try:
        data = await request.json()
        messages = data.get("messages", [])
        session_id = data.get("session_id", "web_user")
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages")

        model = genai.GenerativeModel("models/gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)
        
        # Carrega histórico para contexto
        db_history = await db_service.get_history(session_id)
        
        last_msg = messages[-1]
        last_parts = process_parts(last_msg.get("parts", [last_msg.get("content", "")]))
        
        # Tenta achar a última imagem salva no histórico ou na última mensagem para VTON
        last_image_data = None
        # Primeiro checa a mensagem atual
        for p in last_parts:
            if isinstance(p, dict) and "inline_data" in p:
                last_image_data = p["inline_data"]["data"]
        
        # Se não achou na atual, checa as mensagens anteriores do payload (MVP simples)
        if not last_image_data:
            for msg in reversed(messages[:-1]):
                p_list = process_parts(msg.get("parts", [msg.get("content", "")]))
                for p in p_list:
                    if isinstance(p, dict) and "inline_data" in p:
                        last_image_data = p["inline_data"]["data"]
                        break
                if last_image_data: break

        # Salva mensagem do usuário
        await db_service.save_message(session_id, "user", last_parts)

        # Chat
        chat_session = model.start_chat(history=db_history or None)
        response = await asyncio.to_thread(chat_session.send_message, last_parts)
        
        raw_text = response.text
        clean_text = raw_text
        image_data = None
        
        # Extração de JSON para ações
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                command = json.loads(raw_text[start_idx:end_idx+1])
                if command.get("action") == "virtual_try_on":
                    clean_text = (raw_text[:start_idx] + raw_text[end_idx+1:]).strip()
                    garment_prompt = command.get("params", {}).get("prompt", "A stylish navy blue shirt")
                    
                    # Use Gemini Image Service
                    if last_image_data:
                        # Virtual try-on with user image
                        img_result, img_error = await img_service.generate_virtual_tryon(
                            user_image_base64=last_image_data,
                            garment_description=garment_prompt
                        )
                    else:
                        # Generate just the garment image
                        img_result, img_error = await img_service.generate_outfit_suggestion(
                            user_image_base64=None,
                            garment_description=garment_prompt
                        )
                    
                    if img_result:
                        image_data = f"data:image/png;base64,{img_result}"
                    else:
                        logger.warning(f"Image generation failed: {img_error}")
                        image_data = None
            except Exception as json_err:
                logger.warning(f"JSON parse error: {json_err}")

        # Salva resposta do modelo
        await db_service.save_message(session_id, "model", [clean_text])

        return {"text": clean_text, "image": image_data, "session_id": session_id}
    except Exception as e:
        import traceback
        logger.error(f"CRITICAL Error in chat: {traceback.format_exc()}")
        return {
            "text": "Tive um pequeno contratempo técnico na análise. 🛠️ Podemos tentar de novo?",
            "error": "Internal logic error", # Oculta detalhe técnico do usuário
            "session_id": session_id
        }

async def process_whatsapp_message(message: dict, request_id: str):
    sender_id = message.get("from")
    message_type = message.get("type")
    user_parts = []
    last_wa_image_bytes = None

    if message_type == "text":
        user_parts.append(message["text"].get("body", ""))
    elif message_type == "image":
        caption = message["image"].get("caption")
        if caption: user_parts.append(caption)
        
        try:
            media_url = await wa_service.get_media_url(message["image"].get("id"))
            if media_url:
                last_wa_image_bytes = await wa_service.download_media(media_url)
                user_parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(last_wa_image_bytes).decode("utf-8")
                    }
                })
        except Exception as e:
            logger.error(f"Media download error: {e}")

    if not user_parts: return

    # 🔐 FILTRO DE ATIVAÇÃO: Só processa mensagens que começam com "Stilo"
    # Extrai o texto da primeira parte para checagem
    first_text = ""
    if user_parts:
        if isinstance(user_parts[0], str):
            first_text = user_parts[0]
        elif isinstance(user_parts[0], dict) and "text" in user_parts[0]:
            first_text = user_parts[0]["text"]
    
    # Verifica se a mensagem começa com "Stilo" (case-insensitive)
    if not first_text.lower().startswith("stilo"):
        logger.info(f"[{request_id}] Mensagem ignorada (não inicia com 'Stilo'): {first_text[:50]}...")
        return  # Ignora silenciosamente
    
    # Remove a palavra-chave "Stilo" do início da mensagem
    cleaned_text = first_text[5:].strip()  # Remove "Stilo" (5 caracteres)
    # Remove vírgula ou espaço adicional se houver
    if cleaned_text.startswith(","):
        cleaned_text = cleaned_text[1:].strip()
    
    # Atualiza o user_parts com o texto limpo
    if isinstance(user_parts[0], str):
        user_parts[0] = cleaned_text
    elif isinstance(user_parts[0], dict) and "text" in user_parts[0]:
        user_parts[0]["text"] = cleaned_text

    # 🎮 SISTEMA DE COMANDOS COM /
    if cleaned_text.startswith("/"):
        command = cleaned_text.split()[0].lower() if cleaned_text.split() else "/"
        
        if command == "/" or command == "/menu" or command == "/comandos":
            # Menu de comandos
            menu_text = """📋 *Comandos Disponíveis*

/help - 🆘 Ajuda sobre o Stilo
/sugerir - 👕 Receber sugestão de look
/analisar - 📸 Analisar foto do seu visual
/estilos - 🎨 Ver estilos disponíveis
/cores - 🌈 Paleta de cores que combinam
/dicas - 💡 Dicas rápidas de estilo
/sobre - ℹ️ Sobre o Stilo

💬 Ou simplesmente converse comigo naturalmente!
Exemplo: "Stilo, que camisa combina com jeans?"
"""
            try:
                await wa_service.send_text_message(sender_id, menu_text)
            except Exception as e:
                logger.error(f"Error sending menu: {e}")
            return
        
        elif command == "/help":
            help_text = f"""👋 Olá, {sender_id}!

Sou o *Stilo*, seu consultor de imagem pessoal.

🎯 *Como Funciona:*
• Sempre comece com "Stilo" para me ativar
• Use "/" para ver comandos
• Ou converse naturalmente comigo

📸 *Exemplos:*
• Stilo, analisa essa roupa
• Stilo, me sugere um visual
• Stilo, /sugerir

Estou aqui para te ajudar a arrasar! ✨"""
            try:
                await wa_service.send_text_message(sender_id, help_text)
            except Exception as e:
                logger.error(f"Error sending help: {e}")
            return
        
        elif command == "/sugerir":
            suggestion_prompt = "Sugira um visual completo para mim hoje, considerando versatilidade e estilo moderno."
            cleaned_text = suggestion_prompt
            # Continua para processar com Gemini
        
        elif command == "/estilos":
            styles_text = """🎨 *Estilos Disponíveis:*

1. **Casual Urbano** - Confortável e descontraído
2. **Smart Casual** - Polido mas não formal
3. **Business Casual** - Profissional e elegante
4. **Esportivo** - Ativo e funcional
5. **Streetwear** - Moderno e ousado
6. **Minimalista** - Clean e sofisticado

💬 Me diga qual te interessa ou mande uma foto que eu te ajudo!"""
            try:
                await wa_service.send_text_message(sender_id, styles_text)
            except Exception as e:
                logger.error(f"Error sending styles: {e}")
            return
        
        elif command == "/cores":
            colors_text = """🌈 *Paleta de Cores Essenciais:*

**Neutras (Base):**
• Preto, Branco, Cinza, Bege, Navy

**Cores Versáteis:**
• Azul Marinho • Bordô • Verde Oliva • Marrom

**Combinações que Funcionam:**
✓ Azul + Branco
✓ Cinza + Bordô
✓ Bege + Preto
✓ Verde Oliva + Creme

💬 Mande uma foto da peça e eu te falo que cor combina!"""
            try:
                await wa_service.send_text_message(sender_id, colors_text)
            except Exception as e:
                logger.error(f"Error sending colors: {e}")
            return
        
        elif command == "/dicas":
            tips_text = """💡 *Dicas Rápidas de Estilo:*

1. **Caimento > Marca** - Roupa que cai bem vale mais
2. **Invista em Básicos** - Camiseta branca, jeans, sneaker
3. **Acessórios Discretos** - Menos é mais
4. **Cores Neutras** - 70% do guarda-roupa
5. **Uma Peça Statement** - Por look

🎯 Qual dessas você quer aprofundar?"""
            try:
                await wa_service.send_text_message(sender_id, tips_text)
            except Exception as e:
                logger.error(f"Error sending tips: {e}")
            return
        
        elif command == "/sobre":
            about_text = """ℹ️ *Sobre o Stilo*

Sou um consultor de imagem virtual criado para te ajudar a desenvolver seu estilo pessoal.

🧠 *Tecnologia:*
• Google Gemini AI
• Análise de imagens
• Geração de visualizações

👔 *Especialidades:*
• Moda masculina
• Análise de biotipo
• Combinações de roupas
• Sugestões personalizadas

Criado por Evani com ❤️"""
            try:
                await wa_service.send_text_message(sender_id, about_text)
            except Exception as e:
                logger.error(f"Error sending about: {e}")
            return
        
        else:
            # Comando desconhecido
            unknown_text = f"""❓ Comando "{command}" não reconhecido.

Digite "/" para ver todos os comandos disponíveis."""
            try:
                await wa_service.send_text_message(sender_id, unknown_text)
            except Exception as e:
                logger.error(f"Error sending unknown: {e}")
            return
    
    # Se não é comando, ou é /sugerir, continua com Gemini
    # Atualiza o user_parts com o texto final
    if isinstance(user_parts[0], str):
        user_parts[0] = cleaned_text
    elif isinstance(user_parts[0], dict) and "text" in user_parts[0]:
        user_parts[0]["text"] = cleaned_text

    # Firestore e Gemini
    db_history = await db_service.get_history(sender_id)
    await db_service.save_message(sender_id, "user", user_parts, channel="whatsapp")
    logger.info(f"[{request_id}] Processing message from {sender_id}: {user_parts}")

    model = genai.GenerativeModel("models/gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)
    try:
        chat_session = model.start_chat(history=db_history or None)
        response = await asyncio.wait_for(
            asyncio.to_thread(chat_session.send_message, user_parts),
            timeout=GEMINI_TIMEOUT_SECONDS
        )
        
        raw_text = response.text
        logger.info(f"[{request_id}] Gemini response: {raw_text}")
        clean_text = raw_text
        image_to_send = None

        # Ações JSON no WhatsApp
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            try:
                command = json.loads(raw_text[start_idx:end_idx+1])
                if command.get("action") == "virtual_try_on":
                    clean_text = (raw_text[:start_idx] + raw_text[end_idx+1:]).strip()
                    garment_prompt = command.get("params", {}).get("prompt", "A stylish navy blue shirt")
                    
                    if last_wa_image_bytes:
                        img_result, img_error = await img_service.generate_virtual_tryon(
                            user_image_base64=base64.b64encode(last_wa_image_bytes).decode('utf-8'),
                            garment_description=garment_prompt
                        )
                    else:
                        img_result, img_error = await img_service.generate_outfit_suggestion(
                            user_image_base64=None,
                            garment_description=garment_prompt
                        )
                    
                    if img_result:
                        image_to_send = f"data:image/png;base64,{img_result}"
            except Exception as json_err:
                logger.warning(f"WhatsApp JSON parse error: {json_err}")

        await db_service.save_message(sender_id, "model", [clean_text], channel="whatsapp")
        
        if clean_text: await wa_service.send_text_message(sender_id, clean_text)
        if image_to_send: await wa_service.send_image_message(sender_id, image_to_send, "Aqui está sua sugestão visual! ✨")
        
    except Exception as e:
        import traceback
        logger.error(f"Gemini/VTON WhatsApp error: {e}")
        logger.error(traceback.format_exc())

@app.get("/webhook")
def verify_whatsapp(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("WHATSAPP_VERIFY_TOKEN"):
        from fastapi.responses import Response
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return {"error": "Invalid token"}, 403

@app.post("/webhook")
async def whatsapp_events(request: Request):
    request_id = str(uuid.uuid4())
    raw_body = await request.body()
    
    app_secret = os.getenv("WHATSAPP_APP_SECRET")
    signature = request.headers.get("X-Hub-Signature-256")
    
    if app_secret and "PLACEHOLDER" not in app_secret and signature:
        if not verify_signature(raw_body, signature, app_secret):
            logger.warning(f"[{request_id}] Invalid signature detected.")
            return {"error": "Invalid signature"}, 403
    else:
        logger.info(f"[{request_id}] WHATSAPP_APP_SECRET not set. Skipping signature verification (DEVELOPMENT MODE).")

    try:
        data = json.loads(raw_body)
        for message in iter_webhook_messages(data):
            if not is_duplicate_message(message.get("id")):
                asyncio.create_task(process_whatsapp_message(message, request_id))
        return {"status": "accepted"}
    except Exception as e:
        import traceback
        logger.error(f"CRITICAL Webhook error: {traceback.format_exc()}")
        return {"status": "error", "message": "Unexpected processing error"}
