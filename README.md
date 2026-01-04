# Stilo - Consultor de Estilo

Este projeto utiliza a metodologia **Gemini Conductor (Context-Driven Development)**.

## 🧠 Para Agentes de IA
Antes de iniciar qualquer tarefa, leia os arquivos na pasta [`.context/`](file:///c:/Users/evani/Stilo/.context/) e o arquivo [`AGENTS.md`](file:///c:/Users/evani/Stilo/AGENTS.md) para entender a visão do produto, a stack tecnológica e as regras de trabalho.

1.  **Visão do Produto**: [`.context/vision.md`](file:///c:/Users/evani/Stilo/.context/vision.md)
2.  **Stack Tecnológica**: [`.context/tech-stack.md`](file:///c:/Users/evani/Stilo/.context/tech-stack.md)
3.  **Fluxos de Trabalho**: [`.context/workflows.md`](file:///c:/Users/evani/Stilo/.context/workflows.md)

## 🚀 Como Iniciar
Este é um monorepo com Frontend (React) e Backend (FastAPI).

- **Frontend**: `cd frontend && npm run dev` (Porta 3000)
- **Backend**: `cd backend && python -m uvicorn main:app --reload` (Porta 8000)
- **Docker**: `docker-compose up --build` (Recomendado para produção/testes locais integrados)

## 📁 Estrutura
- `/frontend`: Interface Web.
- `/backend`: Cérebro (Gemini), Webhooks (WhatsApp) e Serviços (VTON/Replicate).
- `.context`: Memória persistente do projeto para IA.
