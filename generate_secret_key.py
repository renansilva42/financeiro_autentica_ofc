#!/usr/bin/env python3
"""
Script para gerar SECRET_KEY segura para Flask
Execute este script para gerar uma nova chave secreta
"""

import secrets
import string
import os
import base64
from datetime import datetime

def generate_secret_key_methods():
    """Gera SECRET_KEY usando diferentes métodos"""
    
    print("🔐 GERADOR DE SECRET_KEY PARA FLASK")
    print("=" * 50)
    
    # Método 1: secrets.token_urlsafe (Recomendado)
    key1 = secrets.token_urlsafe(32)
    print(f"1️⃣  Método secrets.token_urlsafe(32):")
    print(f"   {key1}")
    print(f"   Tamanho: {len(key1)} caracteres")
    print()
    
    # Método 2: secrets.token_hex
    key2 = secrets.token_hex(32)
    print(f"2️⃣  Método secrets.token_hex(32):")
    print(f"   {key2}")
    print(f"   Tamanho: {len(key2)} caracteres")
    print()
    
    # Método 3: base64 + os.urandom
    key3 = base64.b64encode(os.urandom(32)).decode('utf-8')
    print(f"3️⃣  Método base64 + os.urandom(32):")
    print(f"   {key3}")
    print(f"   Tamanho: {len(key3)} caracteres")
    print()
    
    # Método 4: Combinação personalizada
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    key4 = ''.join(secrets.choice(alphabet) for _ in range(64))
    print(f"4️⃣  Método personalizado (64 chars):")
    print(f"   {key4}")
    print(f"   Tamanho: {len(key4)} caracteres")
    print()
    
    # Método 5: UUID + timestamp (menos seguro, mas único)
    import uuid
    timestamp = str(int(datetime.now().timestamp()))
    key5 = f"{uuid.uuid4().hex}{timestamp}{secrets.token_hex(16)}"
    print(f"5️⃣  Método UUID + timestamp:")
    print(f"   {key5}")
    print(f"   Tamanho: {len(key5)} caracteres")
    print()
    
    return key1, key2, key3, key4, key5

def update_env_file(secret_key):
    """Atualiza o arquivo .env com a nova SECRET_KEY"""
    env_path = '.env'
    
    if not os.path.exists(env_path):
        print(f"❌ Arquivo {env_path} não encontrado!")
        return False
    
    try:
        # Ler o arquivo atual
        with open(env_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Procurar e substituir a linha SECRET_KEY
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith('SECRET_KEY='):
                lines[i] = f'SECRET_KEY={secret_key}\n'
                updated = True
                break
        
        # Se não encontrou, adicionar no final
        if not updated:
            lines.append(f'\nSECRET_KEY={secret_key}\n')
        
        # Escrever de volta
        with open(env_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        
        print(f"✅ Arquivo {env_path} atualizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar {env_path}: {e}")
        return False

def create_backup_env():
    """Cria backup do arquivo .env"""
    env_path = '.env'
    backup_path = f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    try:
        if os.path.exists(env_path):
            with open(env_path, 'r') as original:
                with open(backup_path, 'w') as backup:
                    backup.write(original.read())
            print(f"📋 Backup criado: {backup_path}")
            return True
    except Exception as e:
        print(f"⚠️  Erro ao criar backup: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando geração de SECRET_KEY...\n")
    
    # Gerar chaves com diferentes métodos
    keys = generate_secret_key_methods()
    
    print("🎯 RECOMENDAÇÃO:")
    print("   Use o Método 1 (secrets.token_urlsafe) - é o mais seguro e compatível")
    print("   para aplicações Flask em produção.")
    print()
    
    # Perguntar se quer atualizar o .env
    while True:
        choice = input("Deseja atualizar o arquivo .env automaticamente? (s/n): ").lower().strip()
        if choice in ['s', 'sim', 'y', 'yes']:
            # Criar backup primeiro
            create_backup_env()
            
            # Usar a chave recomendada (método 1)
            recommended_key = keys[0]
            
            if update_env_file(recommended_key):
                print(f"\n🎉 SECRET_KEY atualizada com sucesso!")
                print(f"   Nova chave: {recommended_key}")
                print(f"\n⚠️  IMPORTANTE:")
                print(f"   - Reinicie sua aplicação Flask")
                print(f"   - Não compartilhe esta chave")
                print(f"   - Mantenha o arquivo .env seguro")
            break
            
        elif choice in ['n', 'não', 'nao', 'no']:
            print("\n📝 Para atualizar manualmente, copie uma das chaves acima")
            print("   e substitua no arquivo .env:")
            print(f"   SECRET_KEY={keys[0]}")
            break
        else:
            print("❌ Resposta inválida. Digite 's' para sim ou 'n' para não.")

def quick_generate():
    """Gera rapidamente uma chave sem interação"""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    main()
    
    print(f"\n" + "="*50)
    print("📚 INFORMAÇÕES ADICIONAIS:")
    print()
    print("🔒 O que é SECRET_KEY?")
    print("   - Usada pelo Flask para assinar cookies e sessões")
    print("   - Deve ser única para cada aplicação")
    print("   - Nunca deve ser compartilhada ou versionada")
    print()
    print("🛡️  Características de uma boa SECRET_KEY:")
    print("   - Pelo menos 32 caracteres")
    print("   - Caracteres aleatórios")
    print("   - Gerada criptograficamente")
    print("   - Única para cada ambiente")
    print()
    print("⚡ Comando rápido no terminal:")
    print("   python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    print()
    print("🐍 No código Python:")
    print("   import secrets")
    print("   secret_key = secrets.token_urlsafe(32)")
    print()
    print("🌐 Online (use com cuidado):")
    print("   https://flask.palletsprojects.com/en/2.3.x/config/#SECRET_KEY")
    print()
    print("✅ Configuração no Flask:")
    print("   app.secret_key = os.getenv('SECRET_KEY')")
    print("   # ou")
    print("   app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')")