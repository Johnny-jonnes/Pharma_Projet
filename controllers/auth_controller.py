"""
Contrôleur d'authentification.

Gère les actions liées à l'authentification des utilisateurs.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import Optional, Tuple, Callable
from models.user import User
from services.auth_service import AuthService


class AuthController:
    """
    Contrôleur pour la gestion de l'authentification.
    
    Responsabilités:
    - Traiter les demandes de connexion/déconnexion
    - Vérifier les permissions
    - Gérer la session utilisateur
    """
    
    def __init__(self):
        """Initialise le contrôleur."""
        self._auth_service = AuthService()
        
        # Callbacks pour notifier l'UI
        self._on_login_success: Optional[Callable[[User], None]] = None
        self._on_login_failure: Optional[Callable[[str], None]] = None
        self._on_logout: Optional[Callable[[], None]] = None
    
    def set_login_success_callback(self, callback: Callable[[User], None]) -> None:
        """Définit le callback appelé après connexion réussie."""
        self._on_login_success = callback
    
    def set_login_failure_callback(self, callback: Callable[[str], None]) -> None:
        """Définit le callback appelé après échec de connexion."""
        self._on_login_failure = callback
    
    def set_logout_callback(self, callback: Callable[[], None]) -> None:
        """Définit le callback appelé après déconnexion."""
        self._on_logout = callback
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Tente de connecter un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        # Validation des entrées
        if not username or not username.strip():
            message = "Le nom d'utilisateur est obligatoire"
            if self._on_login_failure:
                self._on_login_failure(message)
            return False, message
        
        if not password:
            message = "Le mot de passe est obligatoire"
            if self._on_login_failure:
                self._on_login_failure(message)
            return False, message
        
        # Appel au service
        success, message, user = self._auth_service.login(
            username.strip(), 
            password
        )
        
        if success and user:
            if self._on_login_success:
                self._on_login_success(user)
        else:
            if self._on_login_failure:
                self._on_login_failure(message)
        
        return success, message
    
    def logout(self) -> None:
        """Déconnecte l'utilisateur courant."""
        AuthService.logout()
        
        if self._on_logout:
            self._on_logout()
    
    def get_current_user(self) -> Optional[User]:
        """Retourne l'utilisateur connecté."""
        return AuthService.get_current_user()
    
    def is_logged_in(self) -> bool:
        """Vérifie si un utilisateur est connecté."""
        return AuthService.is_logged_in()
    
    def check_permission(self, permission: str) -> bool:
        """
        Vérifie si l'utilisateur courant a une permission.
        
        Args:
            permission: Nom de la permission
            
        Returns:
            bool: True si autorisé
        """
        user = self.get_current_user()
        
        if user is None:
            return False
        
        permissions_map = {
            'manage_users': user.can_manage_users(),
            'manage_medicaments': user.can_manage_medicaments(),
            'view_reports': user.can_view_reports(),
            'make_sales': True,  # Tous les rôles peuvent vendre
            'manage_clients': user.role in ('admin', 'pharmacien'),
            'view_dashboard': user.role in ('admin', 'pharmacien')
        }
        
        return permissions_map.get(permission, False)
    
    def get_user_role(self) -> Optional[str]:
        """Retourne le rôle de l'utilisateur courant."""
        user = self.get_current_user()
        return user.role if user else None
    
    def get_user_display_name(self) -> str:
        """Retourne le nom d'affichage de l'utilisateur courant."""
        user = self.get_current_user()
        return user.full_name if user else "Non connecté"