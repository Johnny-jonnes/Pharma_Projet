"""
Configuration globale de l'application Pharmacie.
Contient toutes les constantes et paramètres configurables.

Auteur: Alsény Camara
Version: 1.0
"""

import os

# ============================================
# CHEMINS DE L'APPLICATION
# ============================================

# Répertoire racine de l'application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin de la base de données
DATABASE_PATH = os.path.join(BASE_DIR, "database", "pharmacy.db")

# Chemin du schéma SQL
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# Répertoire des assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ============================================
# CONFIGURATION BASE DE DONNÉES
# ============================================

DATABASE_CONFIG = {
    "timeout": 30,              # Timeout connexion en secondes
    "check_same_thread": False, # Permettre accès multi-thread
    "isolation_level": None     # Auto-commit désactivé
}

# ============================================
# CONFIGURATION AUTHENTIFICATION
# ============================================

AUTH_CONFIG = {
    "max_login_attempts": 3,        # Tentatives avant blocage
    "lockout_duration_minutes": 15, # Durée blocage
    "password_min_length": 6,       # Longueur minimale mot de passe
    "hash_algorithm": "sha256"      # Algorithme de hashage
}

# ============================================
# CONFIGURATION STOCK
# ============================================

STOCK_CONFIG = {
    "default_threshold": 10,           # Seuil alerte stock par défaut
    "expiry_alert_days": 30,           # Jours avant alerte péremption
    "low_stock_critical_threshold": 5  # Seuil critique
}

# ============================================
# CONFIGURATION FIDÉLITÉ
# ============================================

LOYALTY_CONFIG = {
    "points_per_unit": 10,  # 1 point pour X unités monétaires dépensées
    "points_value": 0.1     # Valeur d'un point en unités monétaires
}

# ============================================
# CONFIGURATION VENTES
# ============================================

SALE_CONFIG = {
    "number_prefix": "VNT",           # Préfixe numéro vente
    "receipt_title": "PHARMACIE",     # Titre ticket
    "currency_symbol": "GNF",           # Symbole monétaire
    "tax_rate": 0.0                   # TVA (0 pour pharmacie)
}

# ============================================
# RÔLES UTILISATEUR
# ============================================

class UserRole:
    """Énumération des rôles utilisateur."""
    ADMIN = "admin"
    PHARMACIEN = "pharmacien"
    VENDEUR = "vendeur"
    
    @classmethod
    def all_roles(cls):
        """Retourne la liste de tous les rôles."""
        return [cls.ADMIN, cls.PHARMACIEN, cls.VENDEUR]
    
    @classmethod
    def is_valid(cls, role):
        """Vérifie si un rôle est valide."""
        return role in cls.all_roles()

# ============================================
# STATUTS
# ============================================

class SaleStatus:
    """Énumération des statuts de vente."""
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MovementType:
    """Énumération des types de mouvement stock."""
    ENTRY = "entry"
    EXIT = "exit"
    ADJUSTMENT = "adjustment"

# ============================================
# CONFIGURATION INTERFACE
# ============================================

UI_CONFIG = {
    "window_title": "Système de Gestion Pharmacie",
    "window_min_width": 1024,
    "window_min_height": 768,
    "primary_color": "#2C3E50",
    "secondary_color": "#3498DB",
    "success_color": "#27AE60",
    "warning_color": "#F39C12",
    "danger_color": "#E74C3C",
    "background_color": "#ECF0F1",
    "font_family": "Helvetica",
    "font_size_normal": 10,
    "font_size_large": 12,
    "font_size_title": 16
}

# ============================================
# MESSAGES D'ERREUR
# ============================================

ERROR_MESSAGES = {
    "db_connection": "Erreur de connexion à la base de données",
    "invalid_credentials": "Identifiant ou mot de passe incorrect",
    "account_locked": "Compte temporairement bloqué",
    "insufficient_stock": "Stock insuffisant",
    "duplicate_entry": "Cette entrée existe déjà",
    "required_field": "Ce champ est obligatoire",
    "invalid_format": "Format invalide"
}

# ============================================
# MESSAGES DE SUCCÈS
# ============================================

SUCCESS_MESSAGES = {
    "save_success": "Enregistrement effectué avec succès",
    "delete_success": "Suppression effectuée avec succès",
    "update_success": "Mise à jour effectuée avec succès",
    "sale_completed": "Vente validée avec succès"
}