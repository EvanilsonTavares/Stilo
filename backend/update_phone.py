#!/usr/bin/env python3
"""
Script para atualizar o WHATSAPP_PHONE_ID no arquivo .env
Uso: python update_phone.py <novo_phone_id>
"""
import sys
import os

def update_phone_id(new_phone_id):
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print("❌ Arquivo .env não encontrado!")
        return False
    
    # Lê o arquivo atual
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Atualiza a linha do WHATSAPP_PHONE_ID
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('WHATSAPP_PHONE_ID='):
            old_id = line.strip().split('=')[1]
            lines[i] = f'WHATSAPP_PHONE_ID={new_phone_id}\n'
            print(f"✅ Atualizado: {old_id} → {new_phone_id}")
            updated = True
            break
    
    if not updated:
        print("❌ WHATSAPP_PHONE_ID não encontrado no .env")
        return False
    
    # Salva o arquivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Arquivo .env atualizado com sucesso!")
    print("\n🚀 Próximos passos:")
    print("1. Reinicie o backend: python -m uvicorn main:app --reload --port 8000")
    print("2. Teste mandando 'Stilo, oi' do seu celular para o novo número")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("❌ Uso: python update_phone.py <novo_phone_id>")
        print("Exemplo: python update_phone.py 123456789012345")
        sys.exit(1)
    
    new_id = sys.argv[1].strip()
    if not new_id.isdigit():
        print("❌ Phone ID deve conter apenas números")
        sys.exit(1)
    
    update_phone_id(new_id)