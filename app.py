from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
import os
from dotenv import load_dotenv
import io
import pandas as pd
from fpdf import FPDF

# Carrega variáveis de ambiente
load_dotenv()

print("=" * 60)
print("🚀 SIMPLE - Sistema Financeiro PostgreSQL (RENDER)")
print("=" * 60)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sua-chave-secreta-render-2025')
app.permanent_session_lifetime = timedelta(hours=24)  # Sessão de 24 horas

# ============== CONFIGURAÇÃO POSTGRESQL ==============
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # Render usa postgres:// mas psycopg2 precisa de postgresql://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"📊 Database: {'PostgreSQL Render' if DATABASE_URL else 'Local PostgreSQL'}")
print("=" * 60)

def get_db_connection():
    """Cria conexão com PostgreSQL"""
    try:
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'gestao_financeira'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        raise

# ============== FUNÇÃO PARA CRIAR TABELAS ==============
def criar_tabelas_se_necessario():
    """Cria as tabelas se não existirem"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                modo_interface VARCHAR(20) DEFAULT 'simples',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de transações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                tipo VARCHAR(10) CHECK(tipo IN ('receita', 'despesa')) NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                descricao VARCHAR(200) NOT NULL,
                categoria VARCHAR(50) DEFAULT 'Outros',
                data DATE NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de metas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metas (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                titulo VARCHAR(100) NOT NULL,
                descricao TEXT,
                valor_alvo DECIMAL(10, 2) NOT NULL,
                valor_atual DECIMAL(10, 2) DEFAULT 0.00,
                categoria VARCHAR(50) DEFAULT 'Outros',
                data_inicio DATE NOT NULL,
                data_limite DATE,
                data_conclusao TIMESTAMP NULL,
                status VARCHAR(20) CHECK(status IN ('ativa', 'concluida', 'cancelada')) DEFAULT 'ativa',
                cor VARCHAR(7) DEFAULT '#6366F1',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        ''')
        
        # Criar índice para melhor performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transacoes_usuario_id ON transacoes(usuario_id);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metas_usuario_id ON metas(usuario_id);
        ''')
        
        conn.commit()
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== EXECUTA A CRIAÇÃO DAS TABELAS ==============
try:
    criar_tabelas_se_necessario()
except Exception as e:
    print(f"⚠️  Atenção: Erro ao criar tabelas: {e}")

# ============== FUNÇÃO HELPER PARA CORES ==============
def get_cor_clara(cor_hex, brilho=32):
    if not cor_hex:
        return '#E0E7FF'
    
    cor = str(cor_hex).strip()
    if cor.startswith('#'):
        cor = cor[1:]
    if len(cor) != 6:
        return '#E0E7FF'
    try:
        r = int(cor[0:2], 16)
        g = int(cor[2:4], 16)
        b = int(cor[4:6], 16)
    except ValueError:
        return '#E0E7FF'
    
    try:
        brilho_int = int(brilho)
    except (TypeError, ValueError):
        brilho_int = 32
    
    r = min(255, max(0, r + brilho_int))
    g = min(255, max(0, g + brilho_int))
    b = min(255, max(0, b + brilho_int))
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

# ============== CONFIGURAÇÃO JINJA2 ==============
app.jinja_env.globals['get_cor_clara'] = get_cor_clara
app.jinja_env.globals['now'] = datetime.now

@app.template_filter('cor_clara')
def cor_clara_filter(cor_hex, brilho=32):
    return get_cor_clara(cor_hex, brilho)

@app.template_filter('format_currency')
def format_currency_filter(value):
    try:
        return f"R$ {float(value):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return f"R$ {value}"

@app.context_processor
def utility_processor():
    return dict(
        get_cor_clara=get_cor_clara,
        now=datetime.now,
        format_currency=lambda v: f"R$ {float(v):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if v else "R$ 0,00"
    )

# ============== DECORATORS E MIDDLEWARE ==============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def before_request():
    session.permanent = True

# ============== ROTAS DE AUTENTICAÇÃO ==============
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            confirmar_senha = request.form.get('confirmar_senha', '')
            modo = request.form.get('modo', 'simples')
            
            # Validações
            if not nome or len(nome) < 3:
                flash('Nome deve ter pelo menos 3 caracteres!', 'danger')
                return redirect(url_for('registro'))
            
            if not email or '@' not in email:
                flash('Email inválido!', 'danger')
                return redirect(url_for('registro'))
            
            if not senha or len(senha) < 6:
                flash('Senha deve ter pelo menos 6 caracteres!', 'danger')
                return redirect(url_for('registro'))
            
            if senha != confirmar_senha:
                flash('Senhas não conferem!', 'danger')
                return redirect(url_for('registro'))
            
            if modo not in ['simples', 'avancado']:
                modo = 'simples'
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verifica se email já existe
            cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
            if cursor.fetchone():
                flash('Email já cadastrado!', 'danger')
                return redirect(url_for('registro'))
            
            # Cria novo usuário
            senha_hash = generate_password_hash(senha)
            cursor.execute(
                'INSERT INTO usuarios (nome, email, senha, modo_interface) VALUES (%s, %s, %s, %s)',
                (nome, email, senha_hash, modo)
            )
            conn.commit()
            
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
            
        except psycopg2.IntegrityError:
            flash('Email já cadastrado!', 'danger')
            return redirect(url_for('registro'))
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'danger')
            return redirect(url_for('registro'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            
            if not email or not senha:
                flash('Preencha email e senha!', 'danger')
                return redirect(url_for('login'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
            usuario = cursor.fetchone()
            
            if usuario and check_password_hash(usuario['senha'], senha):
                session['user_id'] = usuario['id']
                session['user_nome'] = usuario['nome']
                session['user_modo'] = usuario['modo_interface']
                flash(f'Bem-vindo(a), {usuario["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email ou senha incorretos!', 'danger')
                
        except Exception as e:
            flash(f'Erro ao fazer login: {str(e)}', 'danger')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('index'))

# ============== DASHBOARD ==============
@app.route('/dashboard')
@login_required
def dashboard():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Saldo total
        cursor.execute('''
            SELECT COALESCE(SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END), 0) as saldo
            FROM transacoes WHERE usuario_id = %s
        ''', (session['user_id'],))
        saldo = cursor.fetchone()['saldo'] or 0
        
        # Receitas e despesas do mês
        cursor.execute('''
            SELECT tipo, SUM(valor) as total
            FROM transacoes 
            WHERE usuario_id = %s 
            AND EXTRACT(MONTH FROM data) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM data) = EXTRACT(YEAR FROM CURRENT_DATE)
            GROUP BY tipo
        ''', (session['user_id'],))
        
        mes_atual = {'receitas': 0, 'despesas': 0}
        for row in cursor.fetchall():
            if row['tipo'] == 'receita':
                mes_atual['receitas'] = float(row['total'] or 0)
            else:
                mes_atual['despesas'] = float(row['total'] or 0)
        
        # Saldo do mês
        mes_atual['saldo'] = mes_atual['receitas'] - mes_atual['despesas']
        
        # Últimas transações
        cursor.execute('''
            SELECT * FROM transacoes 
            WHERE usuario_id = %s 
            ORDER BY data DESC, id DESC 
            LIMIT 10
        ''', (session['user_id'],))
        
        ultimas_transacoes = cursor.fetchall()
        
        # Metas ativas
        cursor.execute('''
            SELECT titulo, valor_atual, valor_alvo, cor,
                   CASE WHEN valor_alvo > 0 THEN (valor_atual / valor_alvo * 100) ELSE 0 END as progresso
            FROM metas 
            WHERE usuario_id = %s AND status = 'ativa'
            ORDER BY data_limite NULLS FIRST
            LIMIT 5
        ''', (session['user_id'],))
        
        metas_ativas = cursor.fetchall()
        
        modo = session.get('user_modo', 'simples')
        template = 'dashboard_simples.html' if modo == 'simples' else 'dashboard_avancado.html'
        
        return render_template(template, 
                             saldo=saldo, 
                             mes_atual=mes_atual,
                             transacoes=ultimas_transacoes,
                             metas_ativas=metas_ativas)
        
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== TRANSAÇÕES ==============
@app.route('/adicionar-transacao', methods=['GET', 'POST'])
@login_required
def adicionar_transacao():
    if request.method == 'POST':
        conn = None
        cursor = None
        try:
            tipo = request.form.get('tipo')
            if tipo not in ['receita', 'despesa']:
                flash('Tipo de transação inválido!', 'danger')
                return redirect(url_for('adicionar_transacao'))
            
            try:
                valor = float(request.form.get('valor', 0))
            except ValueError:
                flash('Valor inválido!', 'danger')
                return redirect(url_for('adicionar_transacao'))
            
            if valor <= 0:
                flash('Valor deve ser maior que zero!', 'danger')
                return redirect(url_for('adicionar_transacao'))
            
            descricao = request.form.get('descricao', '').strip()
            if not descricao or len(descricao) < 3:
                flash('Descrição deve ter pelo menos 3 caracteres!', 'danger')
                return redirect(url_for('adicionar_transacao'))
            
            if len(descricao) > 200:
                flash('Descrição muito longa (máximo 200 caracteres)!', 'danger')
                return redirect(url_for('adicionar_transacao'))
            
            categoria = request.form.get('categoria', 'Outros').strip()
            if not categoria:
                categoria = 'Outros'
            
            data_str = request.form.get('data')
            if not data_str:
                data = datetime.now().date()
            else:
                try:
                    data = datetime.strptime(data_str, '%Y-%m-%d').date()
                    # Não permite datas futuras
                    if data > datetime.now().date():
                        flash('Data não pode ser futura!', 'warning')
                        data = datetime.now().date()
                except ValueError:
                    flash('Data inválida!', 'danger')
                    return redirect(url_for('adicionar_transacao'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacoes (usuario_id, tipo, valor, descricao, categoria, data)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (session['user_id'], tipo, valor, descricao, categoria, data))
            conn.commit()
            
            mensagem = 'Receita' if tipo == 'receita' else 'Despesa'
            flash(f'{mensagem} adicionada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Erro ao adicionar transação: {str(e)}', 'danger')
            return redirect(url_for('adicionar_transacao'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # GET request
    modo = session.get('user_modo', 'simples')
    template = 'adicionar_transacao_simples.html' if modo == 'simples' else 'adicionar_transacao_avancado.html'
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template(template, today=today)

@app.route('/transacoes')
@login_required
def listar_transacoes():
    """Lista todas as transações com filtros"""
    conn = None
    cursor = None
    try:
        # Parâmetros de filtro
        tipo = request.args.get('tipo')
        categoria = request.args.get('categoria')
        mes = request.args.get('mes')
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query base
        query = '''
            SELECT * FROM transacoes 
            WHERE usuario_id = %s
        '''
        params = [session['user_id']]
        
        if tipo:
            query += ' AND tipo = %s'
            params.append(tipo)
        if categoria:
            query += ' AND categoria = %s'
            params.append(categoria)
        if mes:
            query += ' AND TO_CHAR(data, \'YYYY-MM\') = %s'
            params.append(mes)
        
        # Contar total
        count_query = query.replace('SELECT *', 'SELECT COUNT(*) as total')
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Paginação
        query += ' ORDER BY data DESC, id DESC LIMIT %s OFFSET %s'
        offset = (pagina - 1) * por_pagina
        params.extend([por_pagina, offset])
        
        cursor.execute(query, params)
        transacoes = cursor.fetchall()
        
        # Buscar categorias únicas
        cursor.execute('''
            SELECT DISTINCT categoria FROM transacoes 
            WHERE usuario_id = %s ORDER BY categoria
        ''', (session['user_id'],))
        categorias = [row['categoria'] for row in cursor.fetchall()]
        
        # Buscar meses disponíveis
        cursor.execute('''
            SELECT DISTINCT TO_CHAR(data, 'YYYY-MM') as mes
            FROM transacoes 
            WHERE usuario_id = %s 
            ORDER BY mes DESC
        ''', (session['user_id'],))
        meses = [row['mes'] for row in cursor.fetchall()]
        
        total_paginas = (total + por_pagina - 1) // por_pagina
        
        modo = session.get('user_modo', 'simples')
        template = 'transacoes_simples.html' if modo == 'simples' else 'transacoes_avancado.html'
        
        return render_template(template,
                             transacoes=transacoes,
                             categorias=categorias,
                             meses=meses,
                             pagina_atual=pagina,
                             total_paginas=total_paginas,
                             total_transacoes=total)
        
    except Exception as e:
        flash(f'Erro ao carregar transações: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/excluir-transacao/<int:id>')
@login_required
def excluir_transacao(id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM transacoes WHERE id = %s AND usuario_id = %s', 
                      (id, session['user_id']))
        
        if not cursor.fetchone():
            flash('Transação não encontrada!', 'danger')
            return redirect(request.referrer or url_for('dashboard'))
        
        cursor.execute('DELETE FROM transacoes WHERE id = %s AND usuario_id = %s', 
                      (id, session['user_id']))
        conn.commit()
        
        flash('Transação excluída com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao excluir transação: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(request.referrer or url_for('dashboard'))

# ============== CONFIGURAÇÕES ==============
@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'alterar_modo':
            conn = None
            cursor = None
            try:
                novo_modo = request.form.get('modo')
                
                if novo_modo not in ['simples', 'avancado']:
                    flash('Modo inválido!', 'danger')
                    return redirect(url_for('configuracoes'))
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE usuarios SET modo_interface = %s WHERE id = %s',
                             (novo_modo, session['user_id']))
                conn.commit()
                
                session['user_modo'] = novo_modo
                flash('Modo de interface atualizado!', 'success')
                
            except Exception as e:
                flash(f'Erro ao atualizar configurações: {str(e)}', 'danger')
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        elif action == 'alterar_senha':
            conn = None
            cursor = None
            try:
                senha_atual = request.form.get('senha_atual')
                nova_senha = request.form.get('nova_senha')
                confirmar_senha = request.form.get('confirmar_senha')
                
                if not senha_atual or not nova_senha or not confirmar_senha:
                    flash('Preencha todos os campos!', 'danger')
                    return redirect(url_for('configuracoes'))
                
                if nova_senha != confirmar_senha:
                    flash('Nova senha e confirmação não coincidem!', 'danger')
                    return redirect(url_for('configuracoes'))
                
                if len(nova_senha) < 6:
                    flash('Nova senha deve ter pelo menos 6 caracteres!', 'danger')
                    return redirect(url_for('configuracoes'))
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT senha FROM usuarios WHERE id = %s', (session['user_id'],))
                usuario = cursor.fetchone()
                
                if not usuario or not check_password_hash(usuario['senha'], senha_atual):
                    flash('Senha atual incorreta!', 'danger')
                    return redirect(url_for('configuracoes'))
                
                nova_senha_hash = generate_password_hash(nova_senha)
                cursor.execute('UPDATE usuarios SET senha = %s WHERE id = %s',
                             (nova_senha_hash, session['user_id']))
                conn.commit()
                
                flash('Senha alterada com sucesso!', 'success')
                
            except Exception as e:
                flash(f'Erro ao alterar senha: {str(e)}', 'danger')
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        return redirect(url_for('configuracoes'))
    
    return render_template('configuracoes.html')

# ============== RELATÓRIOS ==============
@app.route('/relatorios')
@login_required
def relatorios():
    if session.get('user_modo') != 'avancado':
        flash('Esta funcionalidade está disponível apenas no modo avançado.', 'info')
        return redirect(url_for('dashboard'))
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Despesas por categoria
        cursor.execute('''
            SELECT categoria, SUM(valor) as total
            FROM transacoes
            WHERE usuario_id = %s AND tipo = 'despesa'
            GROUP BY categoria
            ORDER BY total DESC
        ''', (session['user_id'],))
        
        despesas_categoria = cursor.fetchall()
        
        # Receitas por categoria
        cursor.execute('''
            SELECT categoria, SUM(valor) as total
            FROM transacoes
            WHERE usuario_id = %s AND tipo = 'receita'
            GROUP BY categoria
            ORDER BY total DESC
        ''', (session['user_id'],))
        
        receitas_categoria = cursor.fetchall()
        
        # Evolução mensal
        cursor.execute('''
            SELECT 
                TO_CHAR(data, 'YYYY-MM') as mes,
                SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as receitas,
                SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as despesas,
                SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END) as saldo
            FROM transacoes
            WHERE usuario_id = %s
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 12
        ''', (session['user_id'],))
        
        evolucao_mensal = cursor.fetchall()
        
        # Top 5 despesas
        cursor.execute('''
            SELECT descricao, categoria, valor, data
            FROM transacoes
            WHERE usuario_id = %s AND tipo = 'despesa'
            ORDER BY valor DESC
            LIMIT 5
        ''', (session['user_id'],))
        
        top_despesas = cursor.fetchall()
        
        return render_template('relatorios.html', 
                             despesas_categoria=despesas_categoria,
                             receitas_categoria=receitas_categoria,
                             evolucao_mensal=evolucao_mensal,
                             top_despesas=top_despesas)
        
    except Exception as e:
        flash(f'Erro ao carregar relatórios: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== METAS ==============
@app.route('/metas')
@login_required
def metas():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id, titulo, descricao, categoria, valor_alvo, valor_atual,
                (valor_alvo - valor_atual) AS valor_faltante,
                CASE 
                    WHEN valor_alvo > 0 THEN 
                        CASE 
                            WHEN (valor_atual / valor_alvo * 100) > 100 THEN 100
                            WHEN (valor_atual / valor_alvo * 100) < 0 THEN 0
                            ELSE (valor_atual / valor_alvo * 100)
                        END
                    ELSE 0 
                END AS progresso,
                status, data_inicio, data_limite, data_conclusao, cor,
                CASE
                    WHEN status = 'ativa' AND data_limite IS NOT NULL AND data_limite < CURRENT_DATE
                    THEN 1 ELSE 0
                END AS atrasada,
                CASE 
                    WHEN data_limite IS NOT NULL THEN data_limite - CURRENT_DATE
                    ELSE NULL
                END AS dias_restantes
            FROM metas
            WHERE usuario_id = %s
            ORDER BY
                CASE status 
                    WHEN 'ativa' THEN 1
                    WHEN 'concluida' THEN 2
                    WHEN 'cancelada' THEN 3
                END,
                data_limite NULLS FIRST
        ''', (session['user_id'],))
        
        metas_lista = cursor.fetchall()
        
        # Estatísticas
        cursor.execute('''
            SELECT
                COUNT(*) AS total_metas,
                SUM(CASE WHEN status = 'ativa' THEN 1 ELSE 0 END) AS metas_ativas,
                SUM(CASE WHEN status = 'concluida' THEN 1 ELSE 0 END) AS metas_concluidas,
                COALESCE(SUM(valor_atual), 0) AS total_economizado,
                COALESCE(SUM(CASE WHEN status = 'ativa' THEN valor_alvo ELSE 0 END), 0) AS total_objetivo
            FROM metas WHERE usuario_id = %s
        ''', (session['user_id'],))
        
        stat = cursor.fetchone()
        
        estatisticas = {
            'total_metas': int(stat['total_metas'] or 0),
            'metas_ativas': int(stat['metas_ativas'] or 0),
            'metas_concluidas': int(stat['metas_concluidas'] or 0),
            'total_economizado': float(stat['total_economizado'] or 0),
            'total_objetivo': float(stat['total_objetivo'] or 0),
        }
        
        if estatisticas['total_objetivo'] > 0:
            estatisticas['progresso_geral'] = (
                estatisticas['total_economizado'] / estatisticas['total_objetivo'] * 100
            )
        else:
            estatisticas['progresso_geral'] = 0.0
        
        # Metas próximas
        cursor.execute('''
            SELECT id, titulo, data_limite, data_limite - CURRENT_DATE as dias_restantes
            FROM metas
            WHERE usuario_id = %s AND status = 'ativa' AND data_limite IS NOT NULL
            AND data_limite BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY data_limite ASC
        ''', (session['user_id'],))
        
        metas_proximas = cursor.fetchall()
        
        today = datetime.now().strftime('%Y-%m-%d')
        modo = session.get('user_modo', 'simples')
        template = 'metas_simples.html' if modo == 'simples' else 'metas_avancado.html'
        
        return render_template(template, 
                             metas=metas_lista, 
                             estatisticas=estatisticas,
                             metas_proximas=metas_proximas, 
                             today=today)
        
    except Exception as e:
        flash(f'Erro ao carregar metas: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/adicionar-meta', methods=['POST'])
@login_required
def adicionar_meta():
    conn = None
    cursor = None
    try:
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        
        try:
            valor_alvo = float(request.form.get('valor_alvo', 0))
        except ValueError:
            flash('Valor alvo inválido!', 'danger')
            return redirect(url_for('metas'))
        
        categoria = request.form.get('categoria', 'Outros')
        data_inicio_str = request.form.get('data_inicio')
        data_limite_str = request.form.get('data_limite')
        cor = request.form.get('cor', '#6366F1')
        
        if not titulo or len(titulo) < 3:
            flash('Título deve ter pelo menos 3 caracteres!', 'danger')
            return redirect(url_for('metas'))
        
        if valor_alvo <= 0:
            flash('Valor alvo deve ser maior que zero!', 'danger')
            return redirect(url_for('metas'))
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            if data_inicio > datetime.now().date():
                flash('Data de início não pode ser futura!', 'warning')
                data_inicio = datetime.now().date()
        except (ValueError, TypeError):
            flash('Data de início inválida!', 'danger')
            return redirect(url_for('metas'))
        
        data_limite = None
        if data_limite_str:
            try:
                data_limite = datetime.strptime(data_limite_str, '%Y-%m-%d').date()
                if data_limite < data_inicio:
                    flash('Data limite não pode ser anterior à data de início!', 'danger')
                    return redirect(url_for('metas'))
            except (ValueError, TypeError):
                flash('Data limite inválida!', 'danger')
                return redirect(url_for('metas'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metas (usuario_id, titulo, descricao, valor_alvo, categoria, data_inicio, data_limite, cor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (session['user_id'], titulo, descricao, valor_alvo, categoria, data_inicio, data_limite, cor))
        conn.commit()
        
        flash('Meta criada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao criar meta: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('metas'))

@app.route('/adicionar-valor-meta', methods=['POST'])
@login_required
def adicionar_valor_meta():
    conn = None
    cursor = None
    try:
        meta_id = request.form.get('meta_id')
        valor_str = request.form.get('valor')
        
        if not meta_id or not valor_str:
            flash('Dados inválidos!', 'danger')
            return redirect(url_for('metas'))
        
        try:
            valor = float(valor_str)
        except ValueError:
            flash('Valor inválido!', 'danger')
            return redirect(url_for('metas'))
        
        if valor <= 0:
            flash('Valor deve ser maior que zero!', 'danger')
            return redirect(url_for('metas'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT valor_atual, valor_alvo FROM metas 
            WHERE id = %s AND usuario_id = %s AND status = 'ativa'
        ''', (meta_id, session['user_id']))
        
        meta = cursor.fetchone()
        if not meta:
            flash('Meta não encontrada ou não está ativa!', 'danger')
            return redirect(url_for('metas'))
        
        novo_valor = float(meta['valor_atual']) + valor
        
        cursor.execute('''
            UPDATE metas SET valor_atual = %s WHERE id = %s AND usuario_id = %s
        ''', (novo_valor, meta_id, session['user_id']))
        conn.commit()
        
        if novo_valor >= float(meta['valor_alvo']):
            cursor.execute('''
                UPDATE metas SET status = 'concluida', data_conclusao = CURRENT_TIMESTAMP 
                WHERE id = %s AND usuario_id = %s
            ''', (meta_id, session['user_id']))
            conn.commit()
            flash('Parabéns! Meta concluída! 🎉', 'success')
        else:
            flash('Valor adicionado à meta com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao adicionar valor: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('metas'))

@app.route('/concluir-meta/<int:id>')
@login_required
def concluir_meta(id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM metas WHERE id = %s AND usuario_id = %s', (id, session['user_id']))
        
        if not cursor.fetchone():
            flash('Meta não encontrada!', 'danger')
            return redirect(url_for('metas'))
        
        cursor.execute('''
            UPDATE metas SET status = 'concluida', data_conclusao = CURRENT_TIMESTAMP 
            WHERE id = %s AND usuario_id = %s
        ''', (id, session['user_id']))
        conn.commit()
        
        flash('Meta marcada como concluída!', 'success')
        
    except Exception as e:
        flash(f'Erro ao concluir meta: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('metas'))

@app.route('/editar-meta', methods=['POST'])
@login_required
def editar_meta():
    conn = None
    cursor = None
    try:
        meta_id = request.form.get('meta_id')
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        
        try:
            valor_alvo = float(request.form.get('valor_alvo', 0))
        except ValueError:
            flash('Valor alvo inválido!', 'danger')
            return redirect(url_for('metas'))
        
        categoria = request.form.get('categoria', 'Outros')
        data_limite_str = request.form.get('data_limite')
        cor = request.form.get('cor', '#6366F1')
        
        if not titulo or len(titulo) < 3:
            flash('Título deve ter pelo menos 3 caracteres!', 'danger')
            return redirect(url_for('metas'))
        
        if valor_alvo <= 0:
            flash('Valor alvo deve ser maior que zero!', 'danger')
            return redirect(url_for('metas'))
        
        data_limite = None
        if data_limite_str:
            try:
                data_limite = datetime.strptime(data_limite_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                flash('Data limite inválida!', 'danger')
                return redirect(url_for('metas'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM metas WHERE id = %s AND usuario_id = %s', 
                      (meta_id, session['user_id']))
        
        if not cursor.fetchone():
            flash('Meta não encontrada!', 'danger')
            return redirect(url_for('metas'))
        
        cursor.execute('''
            UPDATE metas 
            SET titulo = %s, descricao = %s, valor_alvo = %s, categoria = %s, data_limite = %s, cor = %s
            WHERE id = %s AND usuario_id = %s
        ''', (titulo, descricao, valor_alvo, categoria, data_limite, cor, meta_id, session['user_id']))
        conn.commit()
        
        flash('Meta atualizada com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao editar meta: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('metas'))

@app.route('/excluir-meta/<int:id>')
@login_required
def excluir_meta(id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM metas WHERE id = %s AND usuario_id = %s', 
                      (id, session['user_id']))
        
        if not cursor.fetchone():
            flash('Meta não encontrada!', 'danger')
            return redirect(url_for('metas'))
        
        cursor.execute('DELETE FROM metas WHERE id = %s AND usuario_id = %s', 
                      (id, session['user_id']))
        conn.commit()
        
        flash('Meta excluída com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao excluir meta: {str(e)}', 'danger')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return redirect(url_for('metas'))

# ============== EXPORTAÇÃO ==============
@app.route('/exportar/excel')
@login_required
def exportar_excel():
    conn = None
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                CASE tipo WHEN 'receita' THEN 'Receita' ELSE 'Despesa' END as "Tipo",
                categoria as "Categoria",
                descricao as "Descrição",
                valor as "Valor",
                TO_CHAR(data, 'DD/MM/YYYY') as "Data"
            FROM transacoes 
            WHERE usuario_id = %s 
            ORDER BY data DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(session['user_id'],))
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Transações')
            
            # Adicionar resumo
            resumo_data = {
                'Métrica': ['Total Receitas', 'Total Despesas', 'Saldo'],
                'Valor': [
                    df[df['Tipo'] == 'Receita']['Valor'].sum(),
                    df[df['Tipo'] == 'Despesa']['Valor'].sum(),
                    df[df['Tipo'] == 'Receita']['Valor'].sum() - df[df['Tipo'] == 'Despesa']['Valor'].sum()
                ]
            }
            resumo_df = pd.DataFrame(resumo_data)
            resumo_df.to_excel(writer, index=False, sheet_name='Resumo')
            
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'extrato_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        print(f"Erro export Excel: {e}")
        flash(f'Erro ao exportar Excel: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if conn:
            conn.close()

@app.route('/exportar/pdf')
@login_required
def exportar_pdf():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                tipo, categoria, descricao, valor, data,
                TO_CHAR(data, 'DD/MM/YYYY') as data_formatada
            FROM transacoes 
            WHERE usuario_id = %s 
            ORDER BY data DESC
            LIMIT 50
        """, (session['user_id'],))
        
        transacoes = cursor.fetchall()
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as total_receitas,
                SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as total_despesas,
                SUM(CASE WHEN tipo = 'receita' THEN valor ELSE -valor END) as saldo
            FROM transacoes 
            WHERE usuario_id = %s
        """, (session['user_id'],))
        
        resumo = cursor.fetchone()
        
        # Criação do PDF
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'Relatório Financeiro', 0, 1, 'C')
                self.set_font('Arial', '', 10)
                self.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
                self.ln(5)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Resumo
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Resumo Financeiro', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Total Receitas: R$ {resumo["total_receitas"] or 0:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'), 0, 1)
        pdf.cell(0, 8, f'Total Despesas: R$ {resumo["total_despesas"] or 0:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'), 0, 1)
        pdf.cell(0, 8, f'Saldo: R$ {resumo["saldo"] or 0:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'), 0, 1)
        pdf.ln(10)
        
        # Tabela de transações
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Transações Recentes', 0, 1)
        
        # Cabeçalho da tabela
        pdf.set_fill_color(200, 220, 255)
        pdf.set_font("Arial", 'B', 10)
        col_widths = [25, 35, 40, 60, 30]
        headers = ["Data", "Tipo", "Categoria", "Descrição", "Valor"]
        
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
        pdf.ln()
        
        # Linhas da tabela
        pdf.set_font("Arial", size=9)
        for t in transacoes:
            pdf.set_text_color(0, 0, 0)
            if t['tipo'] == 'despesa':
                pdf.set_text_color(180, 0, 0)
            elif t['tipo'] == 'receita':
                pdf.set_text_color(0, 100, 0)
            
            # Data
            pdf.cell(col_widths[0], 10, t['data_formatada'], 1, 0, 'C')
            # Tipo
            tipo_text = 'Receita' if t['tipo'] == 'receita' else 'Despesa'
            pdf.cell(col_widths[1], 10, tipo_text, 1, 0, 'C')
            # Categoria
            pdf.cell(col_widths[2], 10, t['categoria'][:15], 1, 0, 'L')
            # Descrição
            pdf.cell(col_widths[3], 10, t['descricao'][:30], 1, 0, 'L')
            # Valor
            valor_text = f"R$ {t['valor']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            pdf.cell(col_widths[4], 10, valor_text, 1, 1, 'R')
        
        return send_file(
            io.BytesIO(pdf.output(dest='S').encode('latin-1', 'replace')),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )

    except Exception as e:
        print(f"Erro export PDF: {e}")
        flash(f'Erro ao exportar PDF: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ============== ROTAS DE DEBUG E SAÚDE ==============
@app.route('/health')
def health_check():
    """Endpoint de saúde para o Render"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

@app.route('/debug')
def debug_info():
    """Informações de debug"""
    info = {
        'app_name': 'SIMPLE Financeiro',
        'database': 'PostgreSQL',
        'database_url_defined': bool(DATABASE_URL),
        'session_user_id': session.get('user_id'),
        'flask_debug': app.debug,
        'current_time': datetime.now().isoformat()
    }
    return info

# ============== TRATAMENTO DE ERROS ==============
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    flash('Ocorreu um erro interno. Tente novamente.', 'danger')
    return redirect(url_for('index'))

# ============== INICIALIZAÇÃO ==============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)