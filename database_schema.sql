-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS gestao_financeira 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE gestao_financeira;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    modo_interface ENUM('simples', 'avancado') DEFAULT 'simples',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de transações
CREATE TABLE IF NOT EXISTS transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    tipo ENUM('receita', 'despesa') NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    categoria VARCHAR(50) DEFAULT 'Outros',
    data DATE NOT NULL,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_data (usuario_id, data),
    INDEX idx_tipo (tipo),
    INDEX idx_categoria (categoria)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de metas financeiras (para futuras implementações)
CREATE TABLE IF NOT EXISTS metas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    valor_alvo DECIMAL(10, 2) NOT NULL,
    valor_atual DECIMAL(10, 2) DEFAULT 0,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    status ENUM('ativa', 'concluida', 'cancelada') DEFAULT 'ativa',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_status (usuario_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de categorias personalizadas (para futuras implementações)
CREATE TABLE IF NOT EXISTS categorias_personalizadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome VARCHAR(50) NOT NULL,
    tipo ENUM('receita', 'despesa') NOT NULL,
    cor VARCHAR(7) DEFAULT '#6366F1',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_usuario_categoria (usuario_id, nome),
    INDEX idx_usuario_tipo (usuario_id, tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS metas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor_alvo DECIMAL(10, 2) NOT NULL,
    valor_atual DECIMAL(10, 2) DEFAULT 0,
    categoria VARCHAR(50) DEFAULT 'Outros',
    data_inicio DATE NOT NULL,
    data_limite DATE,
    cor VARCHAR(7) DEFAULT '#6366F1',
    status ENUM('ativa', 'concluida', 'cancelada') DEFAULT 'ativa',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_conclusao TIMESTAMP NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    INDEX idx_usuario_status (usuario_id, status),
    INDEX idx_data_limite (data_limite)
);

-- Inserir categorias padrão (opcional - dados de exemplo)
INSERT INTO usuarios (nome, email, senha, modo_interface) VALUES
('Maria Silva', 'maria@email.com', 'scrypt:32768:8:1$x2KjN9wqZR5YF8nL$d5e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0', 'simples'),
('Carlos Souza', 'carlos@email.com', 'scrypt:32768:8:1$x2KjN9wqZR5YF8nL$d5e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0', 'avancado');

-- Inserir transações de exemplo para Maria
INSERT INTO transacoes (usuario_id, tipo, valor, descricao, categoria, data) VALUES
(1, 'receita', 1500.00, 'Aposentadoria', 'Salário', '2025-11-01'),
(1, 'despesa', 350.00, 'Conta de luz', 'Moradia', '2025-11-02'),
(1, 'despesa', 280.00, 'Supermercado', 'Alimentação', '2025-11-03'),
(1, 'despesa', 120.00, 'Farmácia', 'Saúde', '2025-11-04');

-- Inserir transações de exemplo para Carlos
INSERT INTO transacoes (usuario_id, tipo, valor, descricao, categoria, data) VALUES
(2, 'receita', 3500.00, 'Vendas da semana', 'Vendas', '2025-11-01'),
(2, 'despesa', 800.00, 'Fornecedor', 'Estoque', '2025-11-02'),
(2, 'despesa', 450.00, 'Aluguel da loja', 'Moradia', '2025-11-03'),
(2, 'receita', 2100.00, 'Vendas da semana', 'Vendas', '2025-11-05'),
(2, 'despesa', 180.00, 'Conta de luz', 'Serviços', '2025-11-06');