"""
Script para corrigir usuários de teste no banco de dados
Cria/atualiza usuários Maria e Carlos com senhas funcionais
"""

import mysql.connector
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Banco
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'gestao_financeira')
}

def criar_usuarios_teste():
    """Cria ou atualiza usuários de teste"""
    
    print("=" * 60)
    print("CRIAÇÃO DE USUÁRIOS DE TESTE")
    print("=" * 60)
    print()
    
    try:
        # Conecta ao banco
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Senha padrão: 123456
        senha_hash = generate_password_hash('123456')
        
        print(f"✓ Hash da senha gerado: {senha_hash[:50]}...")
        print()
        
        # Usuários de teste
        usuarios = [
            {
                'nome': 'Maria Silva',
                'email': 'maria@email.com',
                'modo': 'simples',
                'descricao': 'Modo Simples - Aposentada'
            },
            {
                'nome': 'Carlos Souza',
                'email': 'carlos@email.com',
                'modo': 'avancado',
                'descricao': 'Modo Avançado - Empreendedor'
            }
        ]
        
        for usuario in usuarios:
            # Verifica se usuário já existe
            cursor.execute('SELECT id FROM usuarios WHERE email = %s', (usuario['email'],))
            existe = cursor.fetchone()
            
            if existe:
                # Atualiza senha existente
                cursor.execute('''
                    UPDATE usuarios 
                    SET senha = %s, modo_interface = %s, nome = %s
                    WHERE email = %s
                ''', (senha_hash, usuario['modo'], usuario['nome'], usuario['email']))
                print(f"✓ Usuário atualizado: {usuario['nome']} ({usuario['descricao']})")
            else:
                # Cria novo usuário
                cursor.execute('''
                    INSERT INTO usuarios (nome, email, senha, modo_interface)
                    VALUES (%s, %s, %s, %s)
                ''', (usuario['nome'], usuario['email'], senha_hash, usuario['modo']))
                print(f"✓ Usuário criado: {usuario['nome']} ({usuario['descricao']})")
        
        conn.commit()
        
        print()
        print("=" * 60)
        print("SUCESSO! Usuários de teste configurados:")
        print("=" * 60)
        print()
        print("📧 Email: maria@email.com")
        print("🔑 Senha: 123456")
        print("📱 Modo: Simples (botões grandes, interface clara)")
        print()
        print("📧 Email: carlos@email.com")
        print("🔑 Senha: 123456")
        print("📱 Modo: Avançado (gráficos e relatórios)")
        print()
        print("Agora você pode fazer login no sistema!")
        print("=" * 60)
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"✗ Erro ao conectar ao banco de dados:")
        print(f"  {str(e)}")
        print()
        print("Verifique:")
        print("  1. MySQL está rodando?")
        print("  2. Credenciais no .env estão corretas?")
        print("  3. Banco 'gestao_financeira' existe?")
        
    except Exception as e:
        print(f"✗ Erro inesperado: {str(e)}")

def adicionar_transacoes_exemplo():
    """Adiciona transações de exemplo para os usuários de teste"""
    
    print()
    print("Deseja adicionar transações de exemplo? (s/n): ", end='')
    resposta = input().lower()
    
    if resposta != 's':
        print("Transações de exemplo não adicionadas.")
        return
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Busca IDs dos usuários
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', ('maria@email.com',))
        maria_id = cursor.fetchone()
        
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', ('carlos@email.com',))
        carlos_id = cursor.fetchone()
        
        if not maria_id or not carlos_id:
            print("✗ Usuários não encontrados. Crie os usuários primeiro.")
            return
        
        maria_id = maria_id[0]
        carlos_id = carlos_id[0]
        
        # Limpa transações antigas (opcional)
        cursor.execute('DELETE FROM transacoes WHERE usuario_id IN (%s, %s)', (maria_id, carlos_id))
        
        # Transações para Maria (Modo Simples)
        transacoes_maria = [
            ('receita', 1500.00, 'Aposentadoria', 'Salário', '2025-11-01'),
            ('despesa', 350.00, 'Conta de luz', 'Moradia', '2025-11-02'),
            ('despesa', 280.00, 'Supermercado', 'Alimentação', '2025-11-03'),
            ('despesa', 120.00, 'Farmácia', 'Saúde', '2025-11-04'),
            ('despesa', 85.00, 'Celular', 'Serviços', '2025-11-05'),
        ]
        
        for tipo, valor, desc, cat, data in transacoes_maria:
            cursor.execute('''
                INSERT INTO transacoes (usuario_id, tipo, valor, descricao, categoria, data)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (maria_id, tipo, valor, desc, cat, data))
        
        # Transações para Carlos (Modo Avançado)
        transacoes_carlos = [
            ('receita', 3500.00, 'Vendas da semana', 'Vendas', '2025-11-01'),
            ('despesa', 800.00, 'Fornecedor de mercadorias', 'Estoque', '2025-11-02'),
            ('despesa', 450.00, 'Aluguel da loja', 'Moradia', '2025-11-03'),
            ('receita', 2100.00, 'Vendas da semana', 'Vendas', '2025-11-05'),
            ('despesa', 180.00, 'Conta de luz comercial', 'Serviços', '2025-11-06'),
            ('despesa', 320.00, 'Marketing digital', 'Serviços', '2025-11-07'),
            ('receita', 1800.00, 'Vendas da semana', 'Vendas', '2025-11-08'),
        ]
        
        for tipo, valor, desc, cat, data in transacoes_carlos:
            cursor.execute('''
                INSERT INTO transacoes (usuario_id, tipo, valor, descricao, categoria, data)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (carlos_id, tipo, valor, desc, cat, data))
        
        conn.commit()
        
        print()
        print("✓ Transações de exemplo adicionadas!")
        print(f"  - {len(transacoes_maria)} transações para Maria")
        print(f"  - {len(transacoes_carlos)} transações para Carlos")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro ao adicionar transações: {str(e)}")

if __name__ == '__main__':
    criar_usuarios_teste()
    adicionar_transacoes_exemplo()