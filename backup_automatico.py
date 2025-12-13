"""
Sistema de Backup Automático
Projeto: Gestão Financeira - Simplifica Finanças

Funcionalidades:
- Backup completo do banco de dados MySQL
- Backup de arquivos do projeto
- Compactação automática (ZIP)
- Rotação de backups (mantém últimos N backups)
- Limpeza automática de backups antigos
- Logs detalhados
- Suporte para backup manual ou agendado
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import zipfile
import logging
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# ============== CONFIGURAÇÕES ==============

BACKUP_CONFIG = {
    # Diretório onde os backups serão salvos
    'BACKUP_DIR': os.getenv('BACKUP_DIR', 'backups'),
    
    # Número máximo de backups a manter (os mais antigos serão deletados)
    'MAX_BACKUPS': int(os.getenv('MAX_BACKUPS', 7)),
    
    # Dias para manter backups
    'RETENTION_DAYS': int(os.getenv('BACKUP_RETENTION_DAYS', 30)),
    
    # Incluir arquivos do projeto no backup
    'BACKUP_FILES': os.getenv('BACKUP_FILES', 'true').lower() == 'true',
    
    # MySQL
    'DB_HOST': os.getenv('DB_HOST', 'localhost'),
    'DB_USER': os.getenv('DB_USER', 'root'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
    'DB_NAME': os.getenv('DB_NAME', 'gestao_financeira'),
}

# Configuração de logs
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'backup.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ============== CLASSE PRINCIPAL ==============

class BackupManager:
    """Gerenciador de backups do sistema"""
    
    def __init__(self):
        self.backup_dir = Path(BACKUP_CONFIG['BACKUP_DIR'])
        self.backup_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_name = f"backup_{self.timestamp}"
        
        # Diretórios temporários
        self.temp_dir = self.backup_dir / 'temp' / self.backup_name
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def executar_backup_completo(self):
        """Executa backup completo (banco + arquivos)"""
        logger.info("=" * 70)
        logger.info("🔐 INICIANDO BACKUP AUTOMÁTICO")
        logger.info("=" * 70)
        logger.info(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info(f"📂 Destino: {self.backup_dir.absolute()}")
        logger.info("")
        
        try:
            # 1. Backup do Banco de Dados
            db_backup_ok = self.backup_database()
            
            # 2. Backup de Arquivos (se habilitado)
            files_backup_ok = True
            if BACKUP_CONFIG['BACKUP_FILES']:
                files_backup_ok = self.backup_files()
            
            # 3. Compactar tudo
            if db_backup_ok and files_backup_ok:
                zip_path = self.compress_backup()
                
                # 4. Limpar backups antigos
                self.cleanup_old_backups()
                
                # 5. Remover diretório temporário
                shutil.rmtree(self.temp_dir.parent)
                
                logger.info("")
                logger.info("=" * 70)
                logger.info("✅ BACKUP CONCLUÍDO COM SUCESSO!")
                logger.info("=" * 70)
                logger.info(f"📦 Arquivo: {zip_path.name}")
                logger.info(f"💾 Tamanho: {self.get_file_size(zip_path)}")
                logger.info("")
                
                return True
            else:
                raise Exception("Falha em uma ou mais etapas do backup")
                
        except Exception as e:
            logger.error(f"❌ ERRO NO BACKUP: {str(e)}")
            # Limpa arquivos temporários em caso de erro
            if self.temp_dir.parent.exists():
                shutil.rmtree(self.temp_dir.parent)
            return False
    
    def backup_database(self):
        """Realiza backup do banco de dados MySQL"""
        logger.info("📊 Iniciando backup do banco de dados...")
        
        try:
            # Nome do arquivo de dump
            dump_file = self.temp_dir / f"{BACKUP_CONFIG['DB_NAME']}.sql"
            
            # Comando mysqldump
            cmd = [
                'mysqldump',
                f'--host={BACKUP_CONFIG["DB_HOST"]}',
                f'--user={BACKUP_CONFIG["DB_USER"]}',
                f'--password={BACKUP_CONFIG["DB_PASSWORD"]}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                BACKUP_CONFIG['DB_NAME']
            ]
            
            # Executa o dump
            with open(dump_file, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode != 0:
                logger.error(f"Erro no mysqldump: {result.stderr}")
                return False
            
            # Verifica se o arquivo foi criado
            if dump_file.exists() and dump_file.stat().st_size > 0:
                logger.info(f"   ✓ Banco exportado: {self.get_file_size(dump_file)}")
                return True
            else:
                logger.error("   ✗ Arquivo de dump vazio ou não criado")
                return False
                
        except FileNotFoundError:
            logger.error("   ✗ mysqldump não encontrado. Instale o MySQL Client.")
            logger.info("   💡 Windows: Adicione o MySQL ao PATH")
            logger.info("   💡 Linux: sudo apt-get install mysql-client")
            return False
            
        except Exception as e:
            logger.error(f"   ✗ Erro ao fazer backup do banco: {str(e)}")
            return False
    
    def backup_files(self):
        """Realiza backup dos arquivos do projeto"""
        logger.info("📁 Iniciando backup de arquivos...")
        
        try:
            # Arquivos e diretórios para incluir no backup
            items_to_backup = [
                'app.py',
                'templates',
                'static',
                '.env',
                'requirements.txt',
                'database_schema.sql',
                'README.md',
            ]
            
            # Diretórios/arquivos a ignorar
            ignore_patterns = [
                '__pycache__',
                '*.pyc',
                '.git',
                '.venv',
                'venv',
                'backups',
                'logs',
                '*.log'
            ]
            
            files_dir = self.temp_dir / 'projeto'
            files_dir.mkdir(exist_ok=True)
            
            copied_count = 0
            
            for item in items_to_backup:
                source = Path(item)
                
                if not source.exists():
                    logger.warning(f"   ⚠ Item não encontrado: {item}")
                    continue
                
                dest = files_dir / item
                
                try:
                    if source.is_file():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, dest)
                        copied_count += 1
                    elif source.is_dir():
                        shutil.copytree(
                            source, 
                            dest,
                            ignore=shutil.ignore_patterns(*ignore_patterns)
                        )
                        copied_count += 1
                        
                except Exception as e:
                    logger.warning(f"   ⚠ Erro ao copiar {item}: {str(e)}")
            
            logger.info(f"   ✓ {copied_count} itens copiados")
            return True
            
        except Exception as e:
            logger.error(f"   ✗ Erro ao fazer backup de arquivos: {str(e)}")
            return False
    
    def compress_backup(self):
        """Compacta o backup em arquivo ZIP"""
        logger.info("📦 Compactando backup...")
        
        try:
            zip_path = self.backup_dir / f"{self.backup_name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adiciona todos os arquivos do diretório temporário
                for file_path in self.temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.temp_dir)
                        zipf.write(file_path, arcname)
            
            logger.info(f"   ✓ Arquivo criado: {zip_path.name}")
            return zip_path
            
        except Exception as e:
            logger.error(f"   ✗ Erro ao compactar: {str(e)}")
            raise
    
    def cleanup_old_backups(self):
        """Remove backups antigos baseado na política de retenção"""
        logger.info("🧹 Limpando backups antigos...")
        
        try:
            # Lista todos os backups
            backups = sorted(
                self.backup_dir.glob('backup_*.zip'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Critério 1: Manter apenas os últimos N backups
            if len(backups) > BACKUP_CONFIG['MAX_BACKUPS']:
                for old_backup in backups[BACKUP_CONFIG['MAX_BACKUPS']:]:
                    try:
                        old_backup.unlink()
                        logger.info(f"   ✓ Removido (limite): {old_backup.name}")
                    except Exception as e:
                        logger.warning(f"   ⚠ Erro ao remover {old_backup.name}: {e}")
            
            # Critério 2: Remover backups mais antigos que RETENTION_DAYS
            cutoff_date = datetime.now() - timedelta(days=BACKUP_CONFIG['RETENTION_DAYS'])
            
            for backup in self.backup_dir.glob('backup_*.zip'):
                backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                
                if backup_time < cutoff_date:
                    try:
                        backup.unlink()
                        logger.info(f"   ✓ Removido (expirado): {backup.name}")
                    except Exception as e:
                        logger.warning(f"   ⚠ Erro ao remover {backup.name}: {e}")
            
            # Conta backups restantes
            remaining = len(list(self.backup_dir.glob('backup_*.zip')))
            logger.info(f"   ✓ Backups mantidos: {remaining}")
            
        except Exception as e:
            logger.error(f"   ✗ Erro na limpeza: {str(e)}")
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        logger.info("\n" + "=" * 70)
        logger.info("📋 BACKUPS DISPONÍVEIS")
        logger.info("=" * 70)
        
        backups = sorted(
            self.backup_dir.glob('backup_*.zip'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not backups:
            logger.info("Nenhum backup encontrado.")
            return
        
        total_size = 0
        
        for i, backup in enumerate(backups, 1):
            stat = backup.stat()
            size = stat.st_size
            total_size += size
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            
            logger.info(f"{i}. {backup.name}")
            logger.info(f"   📅 Data: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
            logger.info(f"   💾 Tamanho: {self.get_file_size(backup)}")
            logger.info("")
        
        logger.info(f"Total: {len(backups)} backup(s) | {self.format_size(total_size)}")
        logger.info("=" * 70 + "\n")
    
    @staticmethod
    def get_file_size(file_path):
        """Retorna tamanho do arquivo formatado"""
        size = file_path.stat().st_size
        return BackupManager.format_size(size)
    
    @staticmethod
    def format_size(size_bytes):
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


# ============== FUNÇÕES UTILITÁRIAS ==============

def restaurar_backup(backup_file):
    """Restaura um backup específico"""
    logger.info("=" * 70)
    logger.info("🔄 RESTAURANDO BACKUP")
    logger.info("=" * 70)
    
    try:
        backup_path = Path(BACKUP_CONFIG['BACKUP_DIR']) / backup_file
        
        if not backup_path.exists():
            logger.error(f"❌ Backup não encontrado: {backup_file}")
            return False
        
        # Extrai o backup
        restore_dir = Path('restore_temp')
        restore_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_dir)
        
        logger.info("✓ Backup extraído")
        
        # Restaura o banco de dados
        sql_file = list(restore_dir.glob('*.sql'))
        
        if sql_file:
            logger.info("📊 Restaurando banco de dados...")
            
            cmd = [
                'mysql',
                f'--host={BACKUP_CONFIG["DB_HOST"]}',
                f'--user={BACKUP_CONFIG["DB_USER"]}',
                f'--password={BACKUP_CONFIG["DB_PASSWORD"]}',
                BACKUP_CONFIG['DB_NAME']
            ]
            
            with open(sql_file[0], 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                logger.info("✓ Banco de dados restaurado")
            else:
                logger.error(f"✗ Erro: {result.stderr}")
        
        # Limpa diretório temporário
        shutil.rmtree(restore_dir)
        
        logger.info("=" * 70)
        logger.info("✅ RESTAURAÇÃO CONCLUÍDA")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na restauração: {str(e)}")
        return False


def menu_interativo():
    """Menu interativo para operações de backup"""
    while True:
        print("\n" + "=" * 70)
        print("🔐 SISTEMA DE BACKUP - GESTÃO FINANCEIRA")
        print("=" * 70)
        print("\n1. 📦 Criar novo backup")
        print("2. 📋 Listar backups")
        print("3. 🔄 Restaurar backup")
        print("4. 🗑️  Limpar backups antigos")
        print("5. ⚙️  Configurações")
        print("0. ❌ Sair")
        print("\n" + "=" * 70)
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == '1':
            manager = BackupManager()
            manager.executar_backup_completo()
            
        elif escolha == '2':
            manager = BackupManager()
            manager.listar_backups()
            
        elif escolha == '3':
            manager = BackupManager()
            manager.listar_backups()
            backup_name = input("\nDigite o nome do backup para restaurar: ").strip()
            if backup_name:
                restaurar_backup(backup_name)
                
        elif escolha == '4':
            manager = BackupManager()
            manager.cleanup_old_backups()
            
        elif escolha == '5':
            print("\n📋 CONFIGURAÇÕES ATUAIS:")
            print("=" * 70)
            for key, value in BACKUP_CONFIG.items():
                if 'PASSWORD' not in key:
                    print(f"{key}: {value}")
            print("=" * 70)
            
        elif escolha == '0':
            print("\n👋 Até logo!")
            break
            
        else:
            print("\n❌ Opção inválida!")


# ============== EXECUÇÃO ==============

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Backup Automático')
    parser.add_argument('--auto', action='store_true', help='Executa backup automaticamente')
    parser.add_argument('--list', action='store_true', help='Lista backups disponíveis')
    parser.add_argument('--restore', type=str, help='Restaura um backup específico')
    
    args = parser.parse_args()
    
    if args.auto:
        # Modo automático (para agendamento)
        manager = BackupManager()
        manager.executar_backup_completo()
        
    elif args.list:
        # Lista backups
        manager = BackupManager()
        manager.listar_backups()
        
    elif args.restore:
        # Restaura backup
        restaurar_backup(args.restore)
        
    else:
        # Menu interativo
        menu_interativo()