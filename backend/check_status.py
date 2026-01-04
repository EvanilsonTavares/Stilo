#!/usr/bin/env python3
"""
Script para verificar o status da integração WhatsApp do Stilo
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_status():
    print("VERIFICACAO DO STATUS - STILO WHATSAPP")
    print("=" * 50)
    
    # 1. Verificar variáveis de ambiente
    print("\nVARIAVEIS DE AMBIENTE:")
    
    phone_id = os.getenv("WHATSAPP_PHONE_ID")
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    print(f"WHATSAPP_PHONE_ID: {phone_id}")
    print(f"WHATSAPP_ACCESS_TOKEN: {'OK Configurado' if access_token else 'ERRO Nao encontrado'}")
    print(f"WHATSAPP_VERIFY_TOKEN: {'OK Configurado' if verify_token else 'ERRO Nao encontrado'}")
    
    # 2. Verificar se é número de teste
    if phone_id == "905401945993424":
        print("\nPROBLEMA IDENTIFICADO:")
        print("Voce esta usando o numero de TESTE (+1 555 154 7553)")
        print("Este numero NAO recebe mensagens reais do WhatsApp!")
        print("\nSOLUCAO:")
        print("1. Adicione um numero real na Meta Business")
        print("2. Use: python update_phone.py <novo_phone_id>")
        return False
    else:
        print(f"\nOK Usando numero real: {phone_id}")
    
    # 3. Verificar se o backend está rodando
    print("\nVERIFICANDO BACKEND:")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("OK Backend rodando em http://localhost:8000")
        else:
            print(f"ERRO Backend respondeu com status {response.status_code}")
    except requests.exceptions.RequestException:
        print("ERRO Backend nao esta rodando")
        print("Execute: python -m uvicorn main:app --reload --port 8000")
        return False
    
    # 4. Verificar tunnel (se possível)
    print("\nTUNNEL PUBLICO:")
    print("Verifique se o localtunnel esta ativo:")
    print("https://stilo-test-agent.loca.lt/health")
    
    print("\nCOMO TESTAR:")
    print("1. Do seu celular (+55 83 99670-2675)")
    print("2. Mande mensagem para o numero do bot")
    print("3. IMPORTANTE: Comece com 'Stilo,' (ex: 'Stilo, oi')")
    print("4. O bot deve responder")
    
    return True

if __name__ == "__main__":
    check_status()