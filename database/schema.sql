-- ============================================
-- PHARMACIE MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Version: 1.0
-- Encodage: UTF-8
-- ============================================

-- Activation des clés étrangères SQLite
PRAGMA foreign_keys = ON;

-- ============================================
-- TABLE: users
-- Description: Utilisateurs du système
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'pharmacien', 'vendeur')),
    full_name VARCHAR(100) NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche par username
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================
-- TABLE: medicaments
-- Description: Catalogue des médicaments
-- ============================================
CREATE TABLE IF NOT EXISTS medicaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    purchase_price REAL NOT NULL CHECK (purchase_price >= 0),
    selling_price REAL NOT NULL CHECK (selling_price >= 0),
    quantity_in_stock INTEGER NOT NULL DEFAULT 0 CHECK (quantity_in_stock >= 0),
    stock_threshold INTEGER DEFAULT 10 CHECK (stock_threshold >= 0),
    expiration_date DATE,
    manufacturer VARCHAR(100),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherches fréquentes
CREATE INDEX IF NOT EXISTS idx_medicaments_code ON medicaments(code);
CREATE INDEX IF NOT EXISTS idx_medicaments_name ON medicaments(name);
CREATE INDEX IF NOT EXISTS idx_medicaments_category ON medicaments(category);
CREATE INDEX IF NOT EXISTS idx_medicaments_expiration ON medicaments(expiration_date);
CREATE INDEX IF NOT EXISTS idx_medicaments_stock ON medicaments(quantity_in_stock);

-- ============================================
-- TABLE: clients
-- Description: Fichier clients
-- ============================================
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100),
    address TEXT,
    loyalty_points INTEGER NOT NULL DEFAULT 0 CHECK (loyalty_points >= 0),
    total_spent REAL NOT NULL DEFAULT 0 CHECK (total_spent >= 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherches
CREATE INDEX IF NOT EXISTS idx_clients_code ON clients(code);
CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(last_name, first_name);

-- ============================================
-- TABLE: loyalty_tiers
-- Description: Paliers du programme fidélité
-- ============================================
CREATE TABLE IF NOT EXISTS loyalty_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    min_points INTEGER NOT NULL UNIQUE CHECK (min_points >= 0),
    discount_percentage REAL NOT NULL CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche par points
CREATE INDEX IF NOT EXISTS idx_loyalty_tiers_points ON loyalty_tiers(min_points);

-- ============================================
-- TABLE: sales
-- Description: En-têtes des ventes
-- ============================================
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_number VARCHAR(30) NOT NULL UNIQUE,
    client_id INTEGER,
    user_id INTEGER NOT NULL,
    sale_date DATETIME NOT NULL,
    subtotal REAL NOT NULL CHECK (subtotal >= 0),
    discount_percentage REAL DEFAULT 0 CHECK (discount_percentage >= 0),
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0),
    total REAL NOT NULL CHECK (total >= 0),
    loyalty_points_earned INTEGER DEFAULT 0 CHECK (loyalty_points_earned >= 0),
    loyalty_points_used INTEGER DEFAULT 0 CHECK (loyalty_points_used >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'completed' CHECK (status IN ('completed', 'cancelled')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- Index pour recherches et rapports
CREATE INDEX IF NOT EXISTS idx_sales_number ON sales(sale_number);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_client ON sales(client_id);
CREATE INDEX IF NOT EXISTS idx_sales_user ON sales(user_id);
CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status);

-- ============================================
-- TABLE: sale_lines
-- Description: Lignes détail des ventes
-- ============================================
CREATE TABLE IF NOT EXISTS sale_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    medicament_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    line_total REAL NOT NULL CHECK (line_total >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (medicament_id) REFERENCES medicaments(id) ON DELETE RESTRICT
);

-- Index pour jointures fréquentes
CREATE INDEX IF NOT EXISTS idx_sale_lines_sale ON sale_lines(sale_id);
CREATE INDEX IF NOT EXISTS idx_sale_lines_medicament ON sale_lines(medicament_id);

-- ============================================
-- TABLE: stock_movements
-- Description: Historique des mouvements de stock
-- ============================================
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicament_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('entry', 'exit', 'adjustment')),
    quantity INTEGER NOT NULL,
    reference_id INTEGER,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (medicament_id) REFERENCES medicaments(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
);

-- Index pour historique
CREATE INDEX IF NOT EXISTS idx_stock_movements_medicament ON stock_movements(medicament_id);
CREATE INDEX IF NOT EXISTS idx_stock_movements_date ON stock_movements(created_at);
CREATE INDEX IF NOT EXISTS idx_stock_movements_type ON stock_movements(movement_type);

-- ============================================
-- DONNÉES INITIALES
-- ============================================

-- Paliers de fidélité par défaut
INSERT INTO loyalty_tiers (name, min_points, discount_percentage, description) VALUES
    ('Standard', 0, 0, 'Niveau de base - Aucune remise'),
    ('Bronze', 100, 2, 'Remise de 2% sur tous les achats'),
    ('Argent', 250, 5, 'Remise de 5% sur tous les achats'),
    ('Or', 500, 8, 'Remise de 8% sur tous les achats'),
    ('Platine', 1000, 10, 'Remise de 10% sur tous les achats');

-- Utilisateur admin par défaut (mot de passe: admin123)
-- Hash SHA-256 de 'admin123'
INSERT INTO users (username, password_hash, role, full_name) VALUES
    ('admin', '240be518fabd2724ddb6f04eeb9d44ae18a7c12a9bcb69a9b7a1f4f5d7d8e8b9', 'admin', 'Administrateur Système');

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Mise à jour automatique de updated_at pour users
CREATE TRIGGER IF NOT EXISTS trigger_users_updated_at
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Mise à jour automatique de updated_at pour medicaments
CREATE TRIGGER IF NOT EXISTS trigger_medicaments_updated_at
AFTER UPDATE ON medicaments
FOR EACH ROW
BEGIN
    UPDATE medicaments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger: Mise à jour automatique de updated_at pour clients
CREATE TRIGGER IF NOT EXISTS trigger_clients_updated_at
AFTER UPDATE ON clients
FOR EACH ROW
BEGIN
    UPDATE clients SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- VUES UTILITAIRES
-- ============================================

-- Vue: Médicaments avec stock faible
CREATE VIEW IF NOT EXISTS view_low_stock AS
SELECT 
    id,
    code,
    name,
    quantity_in_stock,
    stock_threshold,
    (stock_threshold - quantity_in_stock) AS quantity_needed
FROM medicaments
WHERE is_active = 1 
    AND quantity_in_stock <= stock_threshold
ORDER BY quantity_in_stock ASC;

-- Vue: Médicaments proches de la péremption (30 jours)
CREATE VIEW IF NOT EXISTS view_expiring_soon AS
SELECT 
    id,
    code,
    name,
    expiration_date,
    quantity_in_stock,
    CAST((julianday(expiration_date) - julianday('now')) AS INTEGER) AS days_until_expiry
FROM medicaments
WHERE is_active = 1 
    AND expiration_date IS NOT NULL
    AND julianday(expiration_date) - julianday('now') <= 30
    AND julianday(expiration_date) - julianday('now') >= 0
ORDER BY expiration_date ASC;

-- Vue: Ventes du jour
CREATE VIEW IF NOT EXISTS view_today_sales AS
SELECT 
    s.id,
    s.sale_number,
    c.first_name || ' ' || c.last_name AS client_name,
    u.full_name AS seller_name,
    s.total,
    s.status,
    s.sale_date
FROM sales s
LEFT JOIN clients c ON s.client_id = c.id
INNER JOIN users u ON s.user_id = u.id
WHERE DATE(s.sale_date) = DATE('now')
ORDER BY s.sale_date DESC;

-- Vue: Palier fidélité des clients
CREATE VIEW IF NOT EXISTS view_client_loyalty AS
SELECT 
    c.id,
    c.code,
    c.first_name,
    c.last_name,
    c.loyalty_points,
    lt.name AS tier_name,
    lt.discount_percentage
FROM clients c
LEFT JOIN loyalty_tiers lt ON lt.min_points = (
    SELECT MAX(min_points) 
    FROM loyalty_tiers 
    WHERE min_points <= c.loyalty_points AND is_active = 1
)
WHERE c.is_active = 1;