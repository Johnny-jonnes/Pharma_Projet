"""
Repository pour la gestion des utilisateurs.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, List
from database.base_repository import BaseRepository
from models.user import User


class UserRepository(BaseRepository[User]):
    """
    Repository pour les opérations CRUD sur les utilisateurs.
    
    Gère l'accès aux données de la table 'users'.
    """
    
    def create(self, user: User) -> User:
        """
        Crée un nouvel utilisateur.
        
        Args:
            user: Utilisateur à créer
            
        Returns:
            User: Utilisateur créé avec son ID
        """
        query = """
            INSERT INTO users (username, password_hash, role, full_name, is_active)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            user.username,
            user.password_hash,
            user.role,
            user.full_name,
            1 if user.is_active else 0
        )
        
        self.db.execute(query, params)
        user.id = self.db.get_last_insert_id()
        return user
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Optional[User]: Utilisateur trouvé ou None
        """
        query = "SELECT * FROM users WHERE id = ?"
        result = self.db.fetch_one(query, (user_id,))
        
        if result is None:
            return None
        
        return User.from_dict(result)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            Optional[User]: Utilisateur trouvé ou None
        """
        query = "SELECT * FROM users WHERE username = ?"
        result = self.db.fetch_one(query, (username,))
        
        if result is None:
            return None
        
        return User.from_dict(result)
    
    def get_all(self) -> List[User]:
        """
        Récupère tous les utilisateurs actifs.
        
        Returns:
            List[User]: Liste des utilisateurs
        """
        query = "SELECT * FROM users WHERE is_active = 1 ORDER BY full_name"
        results = self.db.fetch_all(query)
        return [User.from_dict(row) for row in results]
    
    def get_all_including_inactive(self) -> List[User]:
        """
        Récupère tous les utilisateurs (actifs et inactifs).
        
        Returns:
            List[User]: Liste de tous les utilisateurs
        """
        query = "SELECT * FROM users ORDER BY is_active DESC, full_name"
        results = self.db.fetch_all(query)
        return [User.from_dict(row) for row in results]
    
    def get_by_role(self, role: str) -> List[User]:
        """
        Récupère les utilisateurs par rôle.
        
        Args:
            role: Rôle recherché
            
        Returns:
            List[User]: Liste des utilisateurs du rôle
        """
        query = "SELECT * FROM users WHERE role = ? AND is_active = 1 ORDER BY full_name"
        results = self.db.fetch_all(query, (role,))
        return [User.from_dict(row) for row in results]
    
    def update(self, user: User) -> bool:
        """
        Met à jour un utilisateur.
        
        Args:
            user: Utilisateur à mettre à jour
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = """
            UPDATE users 
            SET username = ?, password_hash = ?, role = ?, 
                full_name = ?, is_active = ?
            WHERE id = ?
        """
        params = (
            user.username,
            user.password_hash,
            user.role,
            user.full_name,
            1 if user.is_active else 0,
            user.id
        )
        
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """
        Met à jour le mot de passe d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            password_hash: Nouveau hash du mot de passe
            
        Returns:
            bool: True si mise à jour réussie
        """
        query = "UPDATE users SET password_hash = ? WHERE id = ?"
        cursor = self.db.execute(query, (password_hash, user_id))
        return cursor.rowcount > 0
    
    def delete(self, user_id: int) -> bool:
        """
        Désactive un utilisateur (suppression logique).
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            bool: True si désactivation réussie
        """
        query = "UPDATE users SET is_active = 0 WHERE id = ?"
        cursor = self.db.execute(query, (user_id,))
        return cursor.rowcount > 0
    
    def username_exists(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Vérifie si un nom d'utilisateur existe déjà.
        
        Args:
            username: Nom d'utilisateur à vérifier
            exclude_id: ID à exclure (pour modification)
            
        Returns:
            bool: True si existe déjà
        """
        if exclude_id:
            query = "SELECT id FROM users WHERE username = ? AND id != ?"
            result = self.db.fetch_one(query, (username, exclude_id))
        else:
            query = "SELECT id FROM users WHERE username = ?"
            result = self.db.fetch_one(query, (username,))
        
        return result is not None
    
    def count_active(self) -> int:
        """
        Compte le nombre d'utilisateurs actifs.
        
        Returns:
            int: Nombre d'utilisateurs actifs
        """
        query = "SELECT COUNT(*) as count FROM users WHERE is_active = 1"
        result = self.db.fetch_one(query)
        return result['count'] if result else 0