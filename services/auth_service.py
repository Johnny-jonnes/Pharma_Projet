"""
Service d'authentification et gestion des sessions.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, Dict
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from database.user_repository import UserRepository
from utils.hash_utils import HashUtils
from config import AUTH_CONFIG, UserRole


class AuthService:
    """
    Service gérant l'authentification des utilisateurs.
    
    Responsabilités:
    - Validation des credentials
    - Gestion des tentatives de connexion
    - Hashage et vérification des mots de passe
    - Gestion de la session utilisateur courante
    """
    
    # Utilisateur actuellement connecté (session)
    _current_user: Optional[User] = None
    
    # Compteur de tentatives par username
    _login_attempts: Dict[str, Tuple[int, datetime]] = {}
    
    def __init__(self):
        """Initialise le service avec le repository."""
        self._user_repository = UserRepository()
    
    @classmethod
    def get_current_user(cls) -> Optional[User]:
        """
        Retourne l'utilisateur actuellement connecté.
        
        Returns:
            Optional[User]: Utilisateur connecté ou None
        """
        return cls._current_user
    
    @classmethod
    def is_logged_in(cls) -> bool:
        """Vérifie si un utilisateur est connecté."""
        return cls._current_user is not None
    
    @classmethod
    def logout(cls) -> None:
        """Déconnecte l'utilisateur courant."""
        cls._current_user = None
    
    def login(
        self, 
        username: str, 
        password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Authentifie un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair
            
        Returns:
            Tuple[bool, str, Optional[User]]: 
                (succès, message, utilisateur)
        """
        # Validation des entrées
        if not username or not password:
            return False, "Identifiant et mot de passe obligatoires", None
        
        username = username.strip().lower()
        
        # Vérifier le blocage
        if self._is_locked_out(username):
            remaining = self._get_lockout_remaining(username)
            return False, f"Compte bloqué. Réessayez dans {remaining} minutes", None
        
        # Récupérer l'utilisateur
        user = self._user_repository.get_by_username(username)
        
        if user is None:
            self._record_failed_attempt(username)
            return False, "Identifiant ou mot de passe incorrect", None
        
        # Vérifier si le compte est actif
        if not user.is_active:
            return False, "Ce compte est désactivé", None
        
        # Vérifier le mot de passe
        if not HashUtils.verify_password(password, user.password_hash):
            self._record_failed_attempt(username)
            attempts = self._get_remaining_attempts(username)
            return False, f"Identifiant ou mot de passe incorrect. {attempts} tentative(s) restante(s)", None
        
        # Connexion réussie
        self._clear_attempts(username)
        AuthService._current_user = user
        
        return True, f"Bienvenue, {user.full_name}", user
    
    def _is_locked_out(self, username: str) -> bool:
        """Vérifie si un compte est bloqué."""
        if username not in self._login_attempts:
            return False
        
        attempts, last_attempt = self._login_attempts[username]
        max_attempts = AUTH_CONFIG.get("max_login_attempts", 3)
        lockout_minutes = AUTH_CONFIG.get("lockout_duration_minutes", 15)
        
        if attempts >= max_attempts:
            lockout_until = last_attempt + timedelta(minutes=lockout_minutes)
            if datetime.now() < lockout_until:
                return True
            else:
                # Blocage expiré, réinitialiser
                self._clear_attempts(username)
                return False
        
        return False
    
    def _get_lockout_remaining(self, username: str) -> int:
        """Retourne le temps de blocage restant en minutes."""
        if username not in self._login_attempts:
            return 0
        
        _, last_attempt = self._login_attempts[username]
        lockout_minutes = AUTH_CONFIG.get("lockout_duration_minutes", 15)
        lockout_until = last_attempt + timedelta(minutes=lockout_minutes)
        remaining = (lockout_until - datetime.now()).total_seconds() / 60
        
        return max(0, int(remaining) + 1)
    
    def _record_failed_attempt(self, username: str) -> None:
        """Enregistre une tentative échouée."""
        if username in self._login_attempts:
            attempts, _ = self._login_attempts[username]
            self._login_attempts[username] = (attempts + 1, datetime.now())
        else:
            self._login_attempts[username] = (1, datetime.now())
    
    def _get_remaining_attempts(self, username: str) -> int:
        """Retourne le nombre de tentatives restantes."""
        max_attempts = AUTH_CONFIG.get("max_login_attempts", 3)
        
        if username not in self._login_attempts:
            return max_attempts
        
        attempts, _ = self._login_attempts[username]
        return max(0, max_attempts - attempts)
    
    def _clear_attempts(self, username: str) -> None:
        """Réinitialise le compteur de tentatives."""
        if username in self._login_attempts:
            del self._login_attempts[username]
    
    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        full_name: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Crée un nouvel utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            role: Rôle (admin, pharmacien, vendeur)
            full_name: Nom complet
            
        Returns:
            Tuple[bool, str, Optional[User]]: (succès, message, utilisateur)
        """
        # Validation
        if not username or not password or not full_name:
            return False, "Tous les champs sont obligatoires", None
        
        username = username.strip().lower()
        
        # Vérifier l'unicité du username
        if self._user_repository.username_exists(username):
            return False, "Ce nom d'utilisateur existe déjà", None
        
        # Valider le rôle
        if not UserRole.is_valid(role):
            return False, f"Rôle invalide. Valeurs autorisées: {', '.join(UserRole.all_roles())}", None
        
        # Valider la force du mot de passe
        is_valid, msg = HashUtils.validate_password_strength(password)
        if not is_valid:
            return False, msg, None
        
        # Créer l'utilisateur
        try:
            user = User(
                username=username,
                password_hash=HashUtils.hash_password(password),
                role=role,
                full_name=full_name.strip()
            )
            
            created_user = self._user_repository.create(user)
            return True, "Utilisateur créé avec succès", created_user
            
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def update_user(
        self,
        user_id: int,
        username: str,
        role: str,
        full_name: str,
        is_active: bool
    ) -> Tuple[bool, str]:
        """
        Met à jour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            username: Nouveau nom d'utilisateur
            role: Nouveau rôle
            full_name: Nouveau nom complet
            is_active: Statut actif
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            return False, "Utilisateur non trouvé"
        
        # Vérifier l'unicité si username modifié
        if username != user.username:
            if self._user_repository.username_exists(username, exclude_id=user_id):
                return False, "Ce nom d'utilisateur existe déjà"
        
        # Valider le rôle
        if not UserRole.is_valid(role):
            return False, "Rôle invalide"
        
        # Mettre à jour
        user.username = username.strip().lower()
        user.role = role
        user.full_name = full_name.strip()
        user.is_active = is_active
        
        success = self._user_repository.update(user)
        
        if success:
            return True, "Utilisateur mis à jour avec succès"
        else:
            return False, "Erreur lors de la mise à jour"
    
    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change le mot de passe d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            return False, "Utilisateur non trouvé"
        
        # Vérifier le mot de passe actuel
        if not HashUtils.verify_password(current_password, user.password_hash):
            return False, "Mot de passe actuel incorrect"
        
        # Valider le nouveau mot de passe
        is_valid, msg = HashUtils.validate_password_strength(new_password)
        if not is_valid:
            return False, msg
        
        # Mettre à jour
        new_hash = HashUtils.hash_password(new_password)
        success = self._user_repository.update_password(user_id, new_hash)
        
        if success:
            return True, "Mot de passe modifié avec succès"
        else:
            return False, "Erreur lors de la modification"
    
    def reset_password(
        self,
        user_id: int,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Réinitialise le mot de passe (admin seulement).
        
        Args:
            user_id: ID de l'utilisateur
            new_password: Nouveau mot de passe
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Vérifier les permissions
        current = self.get_current_user()
        if current is None or not current.is_admin():
            return False, "Action non autorisée"
        
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            return False, "Utilisateur non trouvé"
        
        # Valider le nouveau mot de passe
        is_valid, msg = HashUtils.validate_password_strength(new_password)
        if not is_valid:
            return False, msg
        
        # Mettre à jour
        new_hash = HashUtils.hash_password(new_password)
        success = self._user_repository.update_password(user_id, new_hash)
        
        if success:
            return True, "Mot de passe réinitialisé avec succès"
        else:
            return False, "Erreur lors de la réinitialisation"
    
    def get_all_users(self) -> list:
        """Retourne tous les utilisateurs."""
        return self._user_repository.get_all_including_inactive()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retourne un utilisateur par son ID."""
        return self._user_repository.get_by_id(user_id)
    
    def deactivate_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Désactive un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Vérifier les permissions
        current = self.get_current_user()
        if current is None or not current.is_admin():
            return False, "Action non autorisée"
        
        # Ne pas pouvoir se désactiver soi-même
        if current.id == user_id:
            return False, "Impossible de désactiver votre propre compte"
        
        success = self._user_repository.delete(user_id)
        
        if success:
            return True, "Utilisateur désactivé avec succès"
        else:
            return False, "Erreur lors de la désactivation"