"""
Gestionnaire de connexion à la base de données SQLite.
Implémente le pattern Singleton pour garantir une connexion unique.

Auteur: Alsény Camara
Version: 1.0
"""

import sqlite3
import os
import threading
from typing import Optional, List, Dict, Any, Tuple

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH, SCHEMA_PATH, DATABASE_CONFIG


class DatabaseManager:
    """
    Gestionnaire singleton de la connexion SQLite.
    
    Responsabilités:
    - Maintenir une connexion unique à la base de données
    - Fournir des méthodes d'exécution de requêtes sécurisées
    - Gérer les transactions
    - Initialiser le schéma si nécessaire
    
    Usage:
        db = DatabaseManager()
        results = db.fetch_all("SELECT * FROM users")
    """
    
    # Instance unique (Singleton)
    _instance: Optional['DatabaseManager'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls) -> 'DatabaseManager':
        """
        Implémentation du pattern Singleton thread-safe.
        
        Returns:
            DatabaseManager: Instance unique du gestionnaire
        """
        if cls._instance is None:
            with cls._lock:
                # Double vérification pour thread-safety
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        Initialise la connexion à la base de données.
        Ne s'exécute qu'une seule fois grâce au flag _initialized.
        """
        if self._initialized:
            return
            
        self._connection: Optional[sqlite3.Connection] = None
        self._initialized = True
        self._connect()
    
    def _connect(self) -> None:
        """
        Établit la connexion à la base de données SQLite.
        Crée le répertoire et le fichier si nécessaires.
        
        Raises:
            sqlite3.Error: En cas d'erreur de connexion
        """
        try:
            # Créer le répertoire database si inexistant
            db_dir = os.path.dirname(DATABASE_PATH)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # Établir la connexion
            self._connection = sqlite3.connect(
                DATABASE_PATH,
                timeout=DATABASE_CONFIG["timeout"],
                check_same_thread=DATABASE_CONFIG["check_same_thread"]
            )
            
            # Activer les clés étrangères
            self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Configurer pour retourner des dictionnaires
            self._connection.row_factory = sqlite3.Row
            
            # Initialiser le schéma si base vide
            self._initialize_schema()
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Erreur de connexion à la base de données: {e}")
    
    def _initialize_schema(self) -> None:
        """
        Initialise le schéma de la base de données si les tables n'existent pas.
        Lit et exécute le fichier schema.sql.
        """
        # Vérifier si les tables existent déjà
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        
        if cursor.fetchone() is None:
            # Tables non existantes, exécuter le schéma
            if os.path.exists(SCHEMA_PATH):
                with open(SCHEMA_PATH, 'r', encoding='utf-8') as schema_file:
                    schema_sql = schema_file.read()
                    self._connection.executescript(schema_sql)
                    self._connection.commit()
    
    @property
    def connection(self) -> sqlite3.Connection:
        """
        Retourne la connexion active.
        
        Returns:
            sqlite3.Connection: Connexion SQLite active
        """
        if self._connection is None:
            self._connect()
        return self._connection
    
    def execute(
        self, 
        query: str, 
        parameters: Tuple = ()
    ) -> sqlite3.Cursor:
        """
        Exécute une requête SQL (INSERT, UPDATE, DELETE).
        
        Args:
            query: Requête SQL paramétrée
            parameters: Tuple des paramètres
            
        Returns:
            sqlite3.Cursor: Curseur après exécution
            
        Raises:
            sqlite3.Error: En cas d'erreur d'exécution
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Erreur d'exécution de la requête: {e}")
    
    def execute_many(
        self, 
        query: str, 
        parameters_list: List[Tuple]
    ) -> sqlite3.Cursor:
        """
        Exécute une requête SQL pour plusieurs jeux de paramètres.
        
        Args:
            query: Requête SQL paramétrée
            parameters_list: Liste de tuples de paramètres
            
        Returns:
            sqlite3.Cursor: Curseur après exécution
            
        Raises:
            sqlite3.Error: En cas d'erreur d'exécution
        """
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, parameters_list)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            self.connection.rollback()
            raise sqlite3.Error(f"Erreur d'exécution multiple: {e}")
    
    def fetch_one(
        self, 
        query: str, 
        parameters: Tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Exécute une requête SELECT et retourne un seul résultat.
        
        Args:
            query: Requête SQL SELECT paramétrée
            parameters: Tuple des paramètres
            
        Returns:
            Optional[Dict]: Dictionnaire du résultat ou None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            # Convertir Row en dictionnaire
            return dict(row)
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Erreur de lecture: {e}")
    
    def fetch_all(
        self, 
        query: str, 
        parameters: Tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Exécute une requête SELECT et retourne tous les résultats.
        
        Args:
            query: Requête SQL SELECT paramétrée
            parameters: Tuple des paramètres
            
        Returns:
            List[Dict]: Liste de dictionnaires des résultats
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
            
            # Convertir chaque Row en dictionnaire
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Erreur de lecture multiple: {e}")
    
    def get_last_insert_id(self) -> int:
        """
        Retourne l'ID du dernier enregistrement inséré.
        
        Returns:
            int: ID du dernier INSERT
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]
    
    def begin_transaction(self) -> None:
        """
        Démarre une transaction explicite.
        """
        self.connection.execute("BEGIN TRANSACTION")
    
    def commit(self) -> None:
        """
        Valide la transaction en cours.
        """
        self.connection.commit()
    
    def rollback(self) -> None:
        """
        Annule la transaction en cours.
        """
        self.connection.rollback()
    
    def table_exists(self, table_name: str) -> bool:
        """
        Vérifie si une table existe dans la base de données.
        
        Args:
            table_name: Nom de la table à vérifier
            
        Returns:
            bool: True si la table existe
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def close(self) -> None:
        """
        Ferme la connexion à la base de données.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            DatabaseManager._instance = None
            self._initialized = False
    
    def __del__(self):
        """
        Destructeur - ferme la connexion proprement.
        """
        self.close()