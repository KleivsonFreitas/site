#!/usr/bin/env python3
"""
Script de Testes Básicos
Testa as principais funcionalidades do sistema
"""

import argparse
import logging
import os
import getpass
from datetime import datetime

import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

# Configuração base do banco
DB_CONFIG_BASE = {
    'host': 'localhost',
    'user': 'root',
    'database': 'gestao_financeira'
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def obter_config_db(senha: str | None) -> dict:
    """Retorna a configuração do banco com a senha definida."""
    config = DB_CONFIG_BASE.copy()
    config['password'] = senha
    return config


def solicitar_senha() -> str:
    """Obtém a senha via argumento, variável de ambiente ou prompt."""
    env_senha = os.getenv('MYSQL_ROOT_PASSWORD')
    if env_senha:
        logging.info("Senha do MySQL obtida via variável de ambiente.")
        return env_senha
    return getpass.getpass("Senha do MySQL (root): ")


def conectar(config: dict):
    """Cria conexão com o banco de dados."""
    return mysql.connector.connect(**config)


def testar_conexao(db_config: dict) -> bool:
    logging.info("🧪 Testando conexão com banco de dados...")
    try:
        with conectar(db_config) as conn:
            if conn.is_connected():
                logging.info("✅ Conexão estabelecida com sucesso!")
                return True
    except Exception as e:
        logging.error("❌ Erro na conexão: %s", e)
    return False


def testar_criar_usuario(db_config: dict) -> bool:
    logging.info("🧪 Testando criação de usuário...")
    try:
        with conectar(db_config) as conn:
            with conn.cursor() as cursor:
                nome = "Teste Usuário"
                email = f"teste_{int(datetime.now().timestamp())}@teste.com"
                senha = "123456"
                senha_hash = generate_password_hash(senha)

                cursor.execute(
                    'INSERT INTO usuarios (nome, email, senha, modo_interface) VALUES (%s, %s, %s, %s)',
                    (nome, email, senha_hash, 'simples')
                )
                conn.commit()
                user_id = cursor.lastrowid
                logging.info("✅ Usuário criado com ID: %s", user_id)

                cursor.execute('SELECT nome, email FROM usuarios WHERE id = %s', (user_id,))
                usuario = cursor.fetchone()
                if usuario:
                    logging.info("✅ Usuário verificado: %s (%s)", usuario[0], usuario[1])

                cursor.execute('DELETE FROM usuarios WHERE id = %s', (user_id,))
                conn.commit()
                logging.info("✅ Usuário de teste removido")
                return True

    except Exception as e:
        logging.error("❌ Erro ao criar usuário: %s", e)
    return False


def testar_criar_transacao(db_config: dict) -> bool:
    logging.info("🧪 Testando criação de transação...")
    try:
        with conectar(db_config) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id FROM usuarios LIMIT 1')
                result = cursor.fetchone()
                if not result:
                    logging.warning("⚠️  Nenhum usuário encontrado. Crie um usuário primeiro.")
                    return False

                user_id = result[0]
                cursor.execute('''
                    INSERT INTO transacoes (usuario_id, tipo, valor, descricao, categoria, data)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (user_id, 'receita', 100.00, 'Teste de Receita', 'Outros', datetime.now().date()))
                conn.commit()
                transacao_id = cursor.lastrowid
                logging.info("✅ Transação criada com ID: %s", transacao_id)

                cursor.execute('SELECT tipo, valor, categoria FROM transacoes WHERE id = %s', (transacao_id,))
                transacao = cursor.fetchone()
                if transacao:
                    logging.info("✅ Transação verificada: R$ %.2f - %s", transacao[1], transacao[2])

                cursor.execute('DELETE FROM transacoes WHERE id = %s', (transacao_id,))
                conn.commit()
                logging.info("✅ Transação de teste removida")
                return True

    except Exception as e:
        logging.error("❌ Erro ao criar transação: %s", e)
    return False


def testar_calculo_saldo(db_config: dict) -> bool:
    logging.info("🧪 Testando cálculo de saldo...")
    try:
        with conectar(db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute('SELECT id FROM usuarios LIMIT 1')
                result = cursor.fetchone()
                if not result:
                    logging.warning("⚠️  Nenhum usuário encontrado.")
                    return False

                user_id = result['id']
                cursor.execute('''
                    SELECT COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END), 0) as saldo
                    FROM transacoes 
                    WHERE usuario_id = %s
                ''', (user_id,))
                resultado = cursor.fetchone()
                if resultado is None:
                    logging.warning("⚠️  Nenhum resultado retornado ao calcular o saldo.")
                    return False

                saldo = resultado['saldo']
                logging.info("✅ Saldo calculado: R$ %.2f", saldo)
                return True

    except Exception as e:
        logging.error("❌ Erro ao calcular saldo: %s", e)
    return False


def testar_senha() -> bool:
    logging.info("🧪 Testando sistema de senhas...")
    try:
        senha = "teste123"
        senha_hash = generate_password_hash(senha)
        logging.info("✅ Senha: %s", senha)
        logging.info("✅ Hash gerado: %s...", senha_hash[:30])

        if not check_password_hash(senha_hash, senha):
            logging.error("❌ Erro na verificação de senha")
            return False

        logging.info("✅ Verificação de senha correta!")

        if check_password_hash(senha_hash, "senha_errada"):
            logging.error("❌ Erro: senha incorreta foi aceita!")
            return False

        logging.info("✅ Rejeição de senha incorreta funcionando!")
        return True

    except Exception as e:
        logging.error("❌ Erro ao testar senhas: %s", e)
    return False


def verificar_usuarios_exemplo(db_config: dict) -> bool:
    logging.info("🧪 Verificando usuários de exemplo...")
    try:
        with conectar(db_config) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT modo_interface FROM usuarios WHERE email = 'maria@email.com'")
                maria = cursor.fetchone()
                if maria:
                    logging.info("✅ Usuário Maria encontrado (Modo: %s)", maria['modo_interface'])
                else:
                    logging.warning("⚠️  Usuário Maria não encontrado")

                cursor.execute("SELECT modo_interface FROM usuarios WHERE email = 'carlos@email.com'")
                carlos = cursor.fetchone()
                if carlos:
                    logging.info("✅ Usuário Carlos encontrado (Modo: %s)", carlos['modo_interface'])
                else:
                    logging.warning("⚠️  Usuário Carlos não encontrado")

                return True

    except Exception as e:
        logging.error("❌ Erro ao verificar usuários: %s", e)
    return False


def executar_testes(db_config: dict) -> list[bool]:
    return [
        testar_conexao(db_config),
        testar_senha(),
        testar_criar_usuario(db_config),
        testar_criar_transacao(db_config),
        testar_calculo_saldo(db_config),
        verificar_usuarios_exemplo(db_config)
    ]


def main():
    logging.info("=" * 60)
    logging.info("🧪 TESTES DO SISTEMA DE GESTÃO FINANCEIRA")
    logging.info("=" * 60)

    parser = argparse.ArgumentParser(description="Executa testes básicos do sistema financeiro.")
    parser.add_argument("--senha", help="Senha do MySQL (root)", default=None)
    args = parser.parse_args()

    senha = args.senha or os.getenv('MYSQL_ROOT_PASSWORD')
    if not senha:
        senha = solicitar_senha()

    db_config = obter_config_db(senha)
    resultados = executar_testes(db_config)

    logging.info("=" * 60)
    logging.info("📊 RESUMO DOS TESTES")
    logging.info("=" * 60)

    total = len(resultados)
    sucesso = sum(resultados)
    falhas = total - sucesso

    logging.info("Total de testes: %d", total)
    logging.info("✅ Sucessos: %d", sucesso)
    logging.info("❌ Falhas: %d", falhas)

    if all(resultados):
        logging.info("🎉 TODOS OS TESTES PASSARAM! O sistema está funcionando corretamente.")
    else:
        logging.warning("⚠️  ALGUNS TESTES FALHARAM! Verifique os erros acima.")

    logging.info("=" * 60)


if __name__ == "__main__":
    main()