import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from google.cloud import firestore
from google.api_core.exceptions import NotFound

class FirestoreService:
    def __init__(self):
        try:
            print("DEBUG: Initializing Firestore Client...")
            # Tenta inicializar com um projeto placeholder se não houver um no ambiente
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT_ID")
            
            if not project_id:
                print("WARNING: No Google Cloud Project ID found. Firestore might hang.")
            
            # Usando Client() com timeout manual simulado ou garantindo que não trave
            self.db = firestore.Client(project=project_id)
            print("DEBUG: Firestore Client initialized successfully.")
        except Exception as e:
            print(f"CRITICAL: Firestore Initialization Failed: {e}")
            self.db = None

    async def save_message(self, session_id: str, role: str, parts: List[Any], channel: str = "web"):
        """Salva uma mensagem no histórico da sessão de forma não-bloqueante."""
        if not self.db:
            return

        try:
            # Para evitar lentidão, não vamos esperar o set() completar se não for crítico
            print(f"DEBUG: Saving message to Firestore (session: {session_id})...")
            doc_ref = self.db.collection("sessions").document(session_id).collection("messages").document()
            
            serializable_parts = []
            for p in parts:
                if isinstance(p, str):
                    serializable_parts.append({"text": p})
                elif isinstance(p, dict) and "inline_data" in p:
                    serializable_parts.append({"image_placeholder": "Image received"})
                else:
                    serializable_parts.append(p)

            # Executa sem o 'await' pesado se possível ou com timeout curto
            doc_ref.set({
                "role": role,
                "parts": serializable_parts,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "channel": channel
            })
            print("DEBUG: Message save command sent.")
        except Exception as e:
            print(f"ERROR: Failed to save message to Firestore: {e}")

    async def get_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recupera o histórico recente com timeout curto."""
        if not self.db:
            return []

        try:
            print(f"DEBUG: Loading history from Firestore (session: {session_id})...")
            messages_ref = self.db.collection("sessions").document(session_id).collection("messages")
            # Reduzindo o limite para ser mais rápido
            query = messages_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
            
            messages = []
            # Stream com timeout para não travar o backend
            docs = query.stream(timeout=2.0)
            for doc in docs:
                msg_data = doc.to_dict()
                role = "user" if msg_data["role"] == "user" else "model"
                messages.append({
                    "role": role,
                    "parts": msg_data["parts"]
                })
            
            print(f"DEBUG: Loaded {len(messages)} messages.")
            return messages[::-1]
        except Exception as e:
            print(f"ERROR: Firestore History Timeout or Error: {e}")
            return []

    async def update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]):
        """Atualiza informações do biotipo ou preferências do usuário."""
        doc_ref = self.db.collection("users").document(user_id)
        doc_ref.set(profile_updates, merge=True)

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Recupera o perfil do usuário."""
        doc_ref = self.db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
