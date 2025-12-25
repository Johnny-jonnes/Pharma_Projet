"""
Contrôleur de gestion des utilisateurs.

Gère les opérations CRUD sur les utilisateurs.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, List
from models.user import User
from services.auth_service import AuthService
from config import UserRole


class UserController:
    """
    Contrôleur pour la gestion des utilisateurs.
    
    Responsabilités:
    - CRUD des utilisateurs
    - Gestion des mots de passe
    - Validation des permissions
    """
    
    def __init__(self):
        """Initialise le contrôleur."""
        self._auth_service = AuthService()
    
    def _check_admin_permission(self) -> Tuple[bool, str]:
        """Vérifie que l'utilisateur courant est admin."""
        current = self._auth_service.get_current_user()
        
        if current is None:
            return False, "Utilisateur non connecté"
        
        if not current.is_admin():
            return False, "Permission refusée. Accès administrateur requis."
        
        return True, ""
    
    def get_all_users(self) -> Tuple[bool, str, List[User]]:
        """
        Récupère tous les utilisateurs.
        
        Returns:
            Tuple[bool, str, List[User]]: (succès, message, utilisateurs)
        """
        allowed, message = self._check_admin_permission()
        if not allowed:
            return False, message, []
        
        users = self._auth_service.get_all_users()
        return True, f"{len(users)} utilisateur(s) trouvé(s)", users
    
    def get_user(self, user_id: int) -> Tuple[bool, str, Optional[User]]:
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Tuple[bool, str, Optional[User]]: (succès, message, utilisateur)
        """
        allowed, message = self._check_admin_permission()
        if not allowed:
            return False, message, None
        
        user = self._auth_service.get_user_by_id(user_id)
        
        if user is None:
            return False, "Utilisateur non trouvé", None
        
        return True, "", user
    
    def create_user(
        self,
        username: str,
        password: str,
        confirm_password: str,
        role: str,
        full_name: str
    ) -> Tuple[bool, str]:
        """
        Crée un nouvel utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            confirm_password: Confirmation du mot de passe
            role: Rôle
            full_name: Nom complet
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Vérifier les permissions
        allowed, message = self._check_admin_permission()
        if not allowed:
            return False, message
        
        # Validation des champs
        if not username or not username.strip():
            return False, "Le nom d'utilisateur est obligatoire"
        
        if not password:
            return False, "Le mot de passe est obligatoire"
        
        if password != confirm_password:
            return False, "Les mots de passe ne correspondent pas"
        
        if not full_name or not full_name.strip():
            return False, "Le nom complet est obligatoire"
        
        if not UserRole.is_valid(role):
            return False, f"Rôle invalide. Valeurs: {', '.join(UserRole.all_roles())}"
        
        # Créer l'utilisateur
        success, message, _ = self._auth_service.create_user(
            username=username.strip(),
            password=password,
            role=role,
            full_name=full_name.strip()
        )
        
        return success, message
    
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
        # Vérifier les permissions
        allowed, message = self._check_admin_permission()
        if not allowed:
            return False, message
        
        # Validation
        if not username or not username.strip():
            return False, "Le nom d'utilisateur est obligatoire"
        
        if not full_name or not full_name.strip():
            return False, "Le nom complet est obligatoire"
        
        if not UserRole.is_valid(role):
            return False, "Rôle invalide"
        
        return self._auth_service.update_user(
            user_id=user_id,
            username=username.strip(),
            role=role,
            full_name=full_name.strip(),
            is_active=is_active
        )
    
    def change_password(
        self,
        current_password: str,
        new_password: str,
        confirm_password: str
    ) -> Tuple[bool, str]:
        """
        Change le mot de passe de l'utilisateur connecté.
        
        Args:
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe
            confirm_password: Confirmation
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        current_user = self._auth_service.get_current_user()
        
        if current_user is None:
            return False, "Utilisateur non connecté"
        
        if not current_password:
            return False, "Le mot de passe actuel est obligatoire"
        
        if not new_password:
            return False, "Le nouveau mot de passe est obligatoire"
        
        if new_password != confirm_password:
            return False, "Les mots de passe ne correspondent pas"
        
        return self._auth_service.change_password(
            user_id=current_user.id,
            current_password=current_password,
            new_password=new_password
        )
    
    def reset_password(
        self,
        user_id: int,
        new_password: str,
        confirm_password: str
    ) -> Tuple[bool, str]:
        """
        Réinitialise le mot de passe d'un utilisateur (admin).
        
        Args:
            user_id: ID de l'utilisateur
            new_password: Nouveau mot de passe
            confirm_password: Confirmation
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        allowed, message = self._check_admin_permission()
        if not allowed:
            return False, message
        
        if not new_password:
            return False, "Le nouveau mot de passe est obligatoire"
        
        if new_password != confirm_password:
            return False, "Les mots de passe ne correspondent pas"
        
        return self._auth_service.reset_password(
            user_id=user_id,
            new_password=new_password
        )
    
    def deactivate_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Désactive un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        return self._auth_service.deactivate_user(user_id)
    
    def get_available_roles(self) -> List[Tuple[str, str]]:
        """
        Retourne les rôles disponibles pour affichage.
        
        Returns:
            List[Tuple[str, str]]: Liste (valeur, libellé)
        """
        return [
            (UserRole.ADMIN, "Administrateur"),
            (UserRole.PHARMACIEN, "Pharmacien"),
            (UserRole.VENDEUR, "Vendeur")
        ]