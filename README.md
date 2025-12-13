# 💰 Sistema de Gestão Financeira - Simplifica Finanças

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/mysql-8.0-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/license-Academic-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-15%20passing-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-~85%25-brightgreen.svg)](tests/)

> **Sistema web de controle financeiro pessoal** com interface adaptativa (simples/avançada), desenvolvido como projeto A3 de Gestão e Qualidade de Software - FPB 2025.2

---

## 🔗 Links Importantes

| Recurso | Link |
|---------|------|
| 🌐 **Repositório GitHub** | [github.com/KleivsonFreitas/Simplifica_Financas](https://github.com/KleivsonFreitas/Simplifica_Financas) |
| 📸 **Screenshots e Vídeos** | [Google Drive - Demonstrações](https://drive.google.com/drive/folders/1BEIK509JvN_ix2QaX9444uPEb_iNrUY3?hl=pt-br) |
| 📦 **Download Completo (.rar)** | [Google Drive - Arquivo Compactado](https://drive.google.com/drive/folders/1BEIK509JvN_ix2QaX9444uPEb_iNrUY3?hl=pt-br) |
| 📽️ **Apresentação Interativa** | [Ver Slides do Projeto](docs/apre.html) |

---

## 📑 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [Arquitetura do Sistema](#️-arquitetura-do-sistema)
- [Guia de Instalação](#-guia-de-instalação)
- [Como Usar](#-como-usar)
- [Testes Automatizados](#-testes-automatizados)
- [Capturas de Tela](#-capturas-de-tela)
- [Vídeos Demonstrativos](#-vídeos-demonstrativos)
- [Métricas de Qualidade](#-métricas-de-qualidade)
- [Backup Automático](#-backup-automático)
- [Roadmap Futuro](#️-roadmap-futuro)
- [Equipe de Desenvolvimento](#-equipe-de-desenvolvimento)
- [Agradecimentos](#-agradecimentos)
- [Contato](#-contato)

---

## 🎯 Sobre o Projeto

O **Simplifica Finanças** é um sistema web inovador que facilita o controle financeiro pessoal através de **interfaces adaptativas**, atendendo desde usuários iniciantes até avançados.

### 🔴 Problema Identificado

- **Complexidade desnecessária**: Apps financeiros exigem sincronização bancária e configurações complicadas
- **Interface única**: Não atende diferentes perfis (iniciantes vs. experientes)
- **Curva de aprendizado alta**: Muitos usuários desistem antes de começar
- **Falta de acompanhamento de metas**: Dificuldade em visualizar progresso de objetivos

### 💡 Nossa Solução

Sistema com **DOIS MODOS DE INTERFACE**:

#### 🟢 Modo Simples
**Público-alvo:** Idosos, aposentados, iniciantes em tecnologia

✅ Botões grandes e coloridos (alta legibilidade)  
✅ Interface limpa - apenas o essencial  
✅ Fontes maiores e alto contraste  
✅ Ideal para uso rápido do dia a dia  
✅ Sem termos técnicos  

#### 🔵 Modo Avançado
**Público-alvo:** Empreendedores, usuários experientes

✅ Gráficos interativos (Chart.js)  
✅ Relatórios detalhados por categoria  
✅ Análise de tendências temporais  
✅ Exportação Excel/PDF  
✅ Dashboard com múltiplos indicadores  

### ✨ Diferenciais Competitivos

| Diferencial | Descrição |
|-------------|-----------|
| 🚀 **Zero Complicação** | Não precisa cadastrar banco, conta ou cartão |
| 🎨 **Interface Adaptativa** | Mesmas funcionalidades em 2 estilos diferentes |
| 📱 **Design Responsivo** | Funciona perfeitamente em mobile e desktop |
| 📊 **Sistema de Metas** | Acompanhamento visual com gamificação |
| 💾 **Backup Automático** | Sistema agendado de backup do banco de dados |
| 🔐 **Segurança Total** | Senhas criptografadas (Scrypt) e isolamento de dados |
| 💰 **100% Gratuito** | Open-source e sem anúncios |
| 🧪 **Alta Qualidade** | 15 testes automatizados (~85% cobertura) |

---

## ⚡ Funcionalidades Principais

### 💸 Gestão de Transações
- ✏️ Cadastro rápido de receitas e despesas
- 🏷️ Categorização inteligente (10+ categorias)
- 💰 Cálculo automático de saldo em tempo real
- 📅 Filtros por período e categoria
- 🗑️ Exclusão com confirmação de segurança
- 📊 Histórico completo de movimentações

### 🎯 Sistema de Metas Financeiras *(Novidade!)*
- 🎯 Criação ilimitada de metas personalizadas
- 📈 Barra de progresso visual e animada
- 🎨 Cores customizáveis para cada meta
- 🏆 Notificações de conquista ao atingir 100%
- ⏰ Alertas de prazo próximo (7 dias)
- 💵 Adição rápida de valores às metas
- 📊 Painel de estatísticas gerais

### 📊 Relatórios Avançados *(Modo Avançado)*
- 🥧 **Gráfico de Pizza**: Despesas por categoria
- 📈 **Gráfico de Linha**: Evolução mensal (receitas vs despesas)
- 💡 **Insights Automáticos**: Análise de padrões de consumo
- 📋 **Tabelas Resumidas**: Com percentuais e totais
- 🎯 **Identificação de Gastos**: Maiores despesas destacadas

### 📥 Exportação de Dados
- 📗 **Excel (.xlsx)**: Planilha formatada com todas as transações
- 📕 **PDF**: Relatório visual pronto para impressão
- 💾 **Backup Completo**: Sistema automatizado de backup MySQL
- 🔄 **Agendamento**: Backup diário via Task Scheduler (Windows)

### 🔒 Segurança e Privacidade
- 🔐 Autenticação com hash Scrypt (Werkzeug 3.0)
- 🛡️ Proteção CSRF nativa do Flask
- 🚪 Sessões seguras com timeout automático
- ✅ Validação dupla (client-side + server-side)
- 🔑 Senhas NUNCA armazenadas em texto plano
- 👤 Isolamento total de dados por usuário
- 🚫 Proteção de rotas com decoradores

---

## 🛠️ Tecnologias Utilizadas

### Backend Core
```python
Python 3.10+          # Linguagem principal
Flask 3.0.0           # Micro-framework web
MySQL 8.0             # Banco de dados relacional
Werkzeug 3.0.1        # Segurança (hashing Scrypt)
python-dotenv 1.0.0   # Gestão de variáveis de ambiente
```

### Bibliotecas de Dados
```python
mysql-connector-python 8.2.0  # Driver MySQL oficial
pandas 2.1.4                   # Manipulação de dados
openpyxl 3.1.2                # Geração de arquivos Excel
fpdf 1.7.2                    # Geração de PDFs
```

### Frontend
```html
HTML5 / CSS3          # Estrutura semântica
Bootstrap 5.3.0       # Framework CSS responsivo
JavaScript ES6+       # Interatividade (Vanilla JS)
Chart.js 4.4.0        # Gráficos interativos
Font Awesome 6.4.0    # Biblioteca de ícones
Bootstrap Icons 1.10  # Ícones complementares
```

### Infraestrutura
```bash
Git                   # Controle de versão
unittest              # Framework de testes Python
Coverage.py           # Medição de cobertura
Gunicorn 21.2.0      # Servidor WSGI (produção)
GitHub                # Hospedagem do código
```

---

## 🗂️ Arquitetura do Sistema

### Estrutura de Diretórios
```
Simplifica_Financas/
│
├── 📄 app.py                    # Aplicação Flask (~1.900 linhas)
├── 🗄️ database_schema.sql       # Script de criação do BD
├── 📋 requirements.txt          # Dependências Python
├── 🔐 .env.example              # Template de variáveis de ambiente
├── 🚫 .gitignore                # Arquivos ignorados
├── 📘 README.md                 # Esta documentação
│
├── 📂 templates/                # Templates Jinja2 (12 arquivos)
│   ├── base.html               # Template base (navbar + footer)
│   ├── index.html              # Landing page
│   ├── login.html              # Autenticação
│   ├── registro.html           # Cadastro de usuário
│   ├── dashboard_simples.html  # Dashboard modo simples
│   ├── dashboard_avancado.html # Dashboard modo avançado
│   ├── adicionar_transacao_simples.html
│   ├── adicionar_transacao_avancado.html
│   ├── metas_simples.html      # Metas modo simples
│   ├── metas_avancado.html     # Metas modo avançado
│   ├── configuracoes.html      # Configurações do usuário
│   └── relatorios.html         # Relatórios e gráficos
│
├── 📂 tests/                    # Suite de testes
│   └── test_app.py             # 15 testes (100% aprovação)
│
├── 📂 backups/                  # Backups automáticos (criado automaticamente)
│   └── backup_YYYYMMDD_HHMMSS.zip
│
├── 📂 logs/                     # Logs do sistema (criado automaticamente)
│   └── backup.log
│
└── 📂 docs/                     # Documentação adicional
    └── apre.html               # Apresentação em slides
```

### Diagrama de Arquitetura (MVC)

```
┌──────────────────────────────────────────────────────┐
│              CAMADA DE APRESENTAÇÃO                  │
│  ┌───────────────────┐    ┌──────────────────────┐  │
│  │  Modo Simples     │    │  Modo Avançado       │  │
│  │  • UX Intuitiva   │    │  • Gráficos Chart.js │  │
│  │  • Botões Grandes │    │  • Relatórios PDF    │  │
│  └─────────┬─────────┘    └──────────┬───────────┘  │
└────────────┼────────────────────────── ┼──────────────┘
             │      Templates Jinja2     │
             └──────────┬────────────────┘
                        │ HTTP (GET/POST)
                        ▼
┌──────────────────────────────────────────────────────┐
│                CAMADA DE CONTROLE                     │
│  ┌────────────────────────────────────────────────┐  │
│  │         Flask Routes (@app.route)              │  │
│  │  / → index                                     │  │
│  │  /login → autenticação                         │  │
│  │  /dashboard → painel dinâmico                  │  │
│  │  /metas → gestão de objetivos                  │  │
│  │  /relatorios → análises (modo avançado)       │  │
│  │  /exportar/{excel|pdf} → downloads            │  │
│  └──────────────────┬─────────────────────────────┘  │
│                     │                                 │
│  ┌──────────────────▼─────────────────────────────┐  │
│  │        CAMADA DE LÓGICA DE NEGÓCIO             │  │
│  │  • Autenticação (Werkzeug)                     │  │
│  │  • CRUD Transações                             │  │
│  │  • Cálculos de saldo                           │  │
│  │  • Progresso de metas                          │  │
│  │  • Geração de relatórios                       │  │
│  │  • Validações de entrada                       │  │
│  └──────────────────┬─────────────────────────────┘  │
└────────────────────┼────────────────────────────────┘
                     │ SQL Queries
                     ▼
┌──────────────────────────────────────────────────────┐
│            CAMADA DE PERSISTÊNCIA                     │
│                  MySQL 8.0                            │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  usuarios    │  │  transacoes  │  │   metas   │  │
│  │• id (PK)     │  │• id (PK)     │  │• id (PK)  │  │
│  │• nome        │  │• usuario_id  │  │• titulo   │  │
│  │• email       │  │• tipo        │  │• valor    │  │
│  │• senha_hash  │  │• valor       │  │• progresso│  │
│  │• modo        │  │• categoria   │  │• status   │  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Guia de Instalação

### ✅ Pré-requisitos Obrigatórios

Certifique-se de ter instalado:

- ✔️ **Python 3.10+** → [Download](https://www.python.org/downloads/)
- ✔️ **MySQL 8.0+** → [Download](https://dev.mysql.com/downloads/)
- ✔️ **Git** → [Download](https://git-scm.com/)

### Passo 1️⃣: Clone o Repositório

```bash
git clone https://github.com/KleivsonFreitas/Simplifica_Financas.git
cd Simplifica_Financas
```

### Passo 2️⃣: Crie o Ambiente Virtual

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

💡 O prompt deve mostrar `(.venv)` indicando que está ativo.

### Passo 3️⃣: Instale as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4️⃣: Configure o Banco de Dados

```bash
# Inicie o MySQL
mysql -u root -p

# Execute o script de criação
source database_schema.sql
# Ou: mysql -u root -p < database_schema.sql

# Verifique a criação
SHOW DATABASES;
USE gestao_financeira;
SHOW TABLES;
```

### Passo 5️⃣: Configure as Variáveis de Ambiente

```bash
# Copie o template
cp .env.example .env  # Linux/Mac
copy .env.example .env  # Windows

# Edite o arquivo .env e configure:
```

```env
SECRET_KEY=sua_chave_secreta_aqui
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=SUA_SENHA_MYSQL
DB_NAME=gestao_financeira
FLASK_ENV=development
FLASK_DEBUG=True
```

💡 **Gere uma SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Passo 6️⃣: Execute a Aplicação

```bash
python app.py
```

**Saída esperada:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Passo 7️⃣: Acesse o Sistema

🌐 Abra seu navegador em: **http://localhost:5000**

---

### 👤 Contas de Teste Pré-Cadastradas

| Email | Senha | Modo | Perfil |
|-------|-------|------|--------|
| maria@email.com | 123456 | 🟢 Simples | Aposentada |
| carlos@email.com | 123456 | 🔵 Avançado | Empreendedor |

---

## 📖 Como Usar

### 🆕 Primeiro Acesso

1. Acesse **http://localhost:5000**
2. Clique em **"Cadastrar"**
3. Escolha seu modo (Simples ou Avançado)
4. Preencha: nome, email, senha
5. Faça login com suas credenciais

### 💸 Adicionar Transação

**Modo Simples:**
1. Botão **"Adicionar Movimentação"**
2. Escolha: **RECEBI** ou **GASTEI**
3. Preencha valor, descrição, categoria
4. Clique **"SALVAR"**

**Modo Avançado:**
1. Menu **"Nova Transação"**
2. Tipo: Receita ⬆️ ou Despesa ⬇️
3. Dados detalhados + data opcional
4. Botão **"Salvar Transação"**

### 🎯 Criar Meta

1. Menu **"Metas"**
2. Botão **"Nova Meta"**
3. Preencha: título, valor alvo, categoria, cor
4. Defina prazo (opcional)
5. Adicione valores conforme economizar

### 📊 Exportar Dados

- **Excel:** Dashboard → Botão **"Excel"**
- **PDF:** Dashboard → Botão **"PDF"**

### ⚙️ Alternar Modo

1. Menu **"Configurações"**
2. Escolha novo modo
3. Botão **"Salvar Alterações"**

---

## 🧪 Testes Automatizados

### Executar Suite Completa

```bash
python tests/test_app.py
```

### Com Cobertura

```bash
coverage run -m unittest tests/test_app.py
coverage report
coverage html  # Gera relatório HTML em htmlcov/
```

### Resumo dos Testes

| Categoria | Quantidade | Status |
|-----------|------------|--------|
| **Autenticação** | 5 | ✅ 100% |
| **Banco de Dados** | 2 | ✅ 100% |
| **Transações** | 2 | ✅ 100% |
| **Metas** | 2 | ✅ 100% |
| **Utilitários** | 2 | ✅ 100% |
| **Integração** | 2 | ✅ 100% |
| **TOTAL** | **15** | **✅ 100%** |

**Cobertura:** ~85% do código testado  
**Taxa de Sucesso:** 100% (15/15 aprovados)

---

## 📸 Capturas de Tela

**🔗 Todas as imagens:** [Google Drive - Screenshots](https://drive.google.com/drive/folders/1BEIK509JvN_ix2QaX9444uPEb_iNrUY3?hl=pt-br)

### Principais Telas
- 🔐 Login e Cadastro
- 📊 Dashboard (Simples e Avançado)
- 🎯 Sistema de Metas
- 💸 Adicionar Transação
- 📈 Relatórios e Gráficos
- ⚙️ Configurações

---

## 🎥 Vídeos Demonstrativos

**🔗 Todos os vídeos:** [Google Drive - Vídeos](https://drive.google.com/drive/folders/1BEIK509JvN_ix2QaX9444uPEb_iNrUY3?hl=pt-br)

### Conteúdo
- 🎬 Pitch do Projeto (5 minutos)
- 🎬 Demonstração Completa
- 🧪 Execução dos Testes
- 🎯 Tutorial Passo a Passo

---

## 📊 Métricas de Qualidade

### Indicadores

| Métrica | Valor | Status |
|---------|-------|--------|
| Linhas de Código | ~1.900 | ✅ |
| Cobertura de Testes | ~85% | ✅ |
| Complexidade Ciclomática | 3.2 (Baixa) | ✅ |
| Testes Aprovados | 15/15 (100%) | ✅ |
| Bugs Críticos | 0 | ✅ |

### Pontos de Função

| Funcionalidade | Complexidade | PF |
|----------------|--------------|-----|
| Autenticação | Baixa | 3 |
| CRUD Transações | Média | 4 |
| Dashboard | Alta | 6 |
| Metas Financeiras | Média | 4 |
| Relatórios | Alta | 6 |
| Exportação | Média | 4 |
| **TOTAL** | | **27 PF** |

**Estimativa de Esforço:**
- Produtividade: 5 horas/PF
- Estimado: 135 horas
- Real: 140 horas
- Variação: +3.7% ✅

---

## 💾 Backup Automático

### Funcionalidades

✅ Backup completo do banco MySQL  
✅ Compactação automática (.zip)  
✅ Rotação de backups (mantém últimos 7)  
✅ Agendamento via Task Scheduler (Windows)  
✅ Logs detalhados  

### Como Usar

```bash
# Manual
python backup_automatico.py --auto

# Agendar (Windows - execute como Administrador)
agendar_backup.bat
# Digite hora e minuto desejados

# Listar backups
python backup_automatico.py --list

# Restaurar backup
python backup_automatico.py --restore nome_do_arquivo.zip
```

---

## 🗺️ Roadmap Futuro

### Versão 2.0 (Planejado Q1 2026)
- [ ] Modo escuro automático
- [ ] PWA (Progressive Web App)
- [ ] Notificações push
- [ ] Compartilhamento de metas (social)

### Versão 3.0 (Futuro)
- [ ] IA para sugestões personalizadas
- [ ] Suporte multi-moeda
- [ ] API REST pública
- [ ] Integração com Open Banking

---

## 👥 Equipe de Desenvolvimento

| Nome | RA | Função Principal |
|------|-----|-----------------|
| **Janary Victor do Nascimento Júnior** | 1362416604 | Full-Stack / Arquitetura |
| **José Kleivson da Silva Freitas** | 1362411072 | Backend / Banco de Dados |
| **Daniel Obede da Silva** | 1362112473 | Frontend / Testes |
| **Gabriel Jonathas Santos de Oliveira** | 1362317022 | Full-Stack / Integração |
| **Carlos Henrique Cavalcante Moreira** | 1362416272 | Backend / Segurança |

### Informações Acadêmicas

**📚 Instituição:** Faculdade Internacional da Paraíba (FPB) - Campus Tambiá  
**🎓 Curso:** Ciência da Computação  
**📖 Disciplina:** Gestão e Qualidade de Software (A3)  
**👨‍🏫 Orientador:** Prof. Antunes  
**📅 Período:** 2025.2  

---

## 🙏 Agradecimentos

Nossos sinceros agradecimentos a:

- [Flask](https://flask.palletsprojects.com/) - Framework web minimalista e poderoso
- [Bootstrap](https://getbootstrap.com/) - Framework CSS responsivo
- [MySQL](https://www.mysql.com/) - Sistema de banco de dados robusto
- [Chart.js](https://www.chartjs.org/) - Biblioteca de gráficos
- [Font Awesome](https://fontawesome.com/) - Ícones de alta qualidade
- **Prof. Antunes** - Orientação técnica e acadêmica
- **FPB** - Infraestrutura e recursos disponibilizados

---

## 📞 Contato

- 📧 **Email:** kleivsonfreitas@gmail.com
- 🐙 **GitHub:** [@KleivsonFreitas](https://github.com/KleivsonFreitas)
- 💼 **LinkedIn:** [Adicione seu LinkedIn aqui]

---

## 📄 Licença

Este projeto foi desenvolvido exclusivamente para fins **acadêmicos** na disciplina de Gestão e Qualidade de Software da FPB.

**Uso Educacional** - Não destinado a uso comercial.

---

<div align="center">

### ⭐ Se este projeto foi útil para você, considere deixar uma estrela no GitHub!

**Made with ❤️ by Team FPB - A3 2025.2**

[⬆️ Voltar ao topo](#-sistema-de-gestão-financeira---simplifica-finanças)

</div>