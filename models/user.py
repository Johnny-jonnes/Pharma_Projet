"""
Modèle User - Représente un utilisateur du système.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    Entité représentant un utilisateur du système.
    
    Attributes:
        id: Identifiant unique (auto-généré)
        username: Nom d'utilisateur unique
        password_hash: Mot de passe hashé
        role: Rôle (admin, pharmacien, vendeur)
        full_name: Nom complet de l'utilisateur
        is_active: Statut actif/inactif
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    username: str
    password_hash: str
    role: str
    full_name: str
    id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if self.role not in ('admin', 'pharmacien', 'vendeur'):
            raise ValueError(f"Rôle invalide: {self.role}")
        
        if not self.username or len(self.username.strip()) == 0:
            raise ValueError("Le nom d'utilisateur est obligatoire")
        
        if not self.full_name or len(self.full_name.strip()) == 0:
            raise ValueError("Le nom complet est obligatoire")
    
    def to_dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire.
        
        Returns:
            dict: Représentation dictionnaire de l'utilisateur
        """
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Crée une instance User depuis un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données utilisateur
            
        Returns:
            User: Instance créée
        """
        return cls(
            id=data.get('id'),
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            full_name=data['full_name'],
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.role == 'admin'
    
    def is_pharmacien(self) -> bool:
        """Vérifie si l'utilisateur est pharmacien."""
        return self.role == 'pharmacien'
    
    def is_vendeur(self) -> bool:
        """Vérifie si l'utilisateur est vendeur."""
        return self.role == 'vendeur'
    
    def can_manage_users(self) -> bool:
        """Vérifie si l'utilisateur peut gérer les utilisateurs."""
        return self.is_admin()
    
    def can_manage_medicaments(self) -> bool:
        """Vérifie si l'utilisateur peut gérer les médicaments."""
        return self.role in ('admin', 'pharmacien')
    
    def can_view_reports(self) -> bool:
        """Vérifie si l'utilisateur peut voir les rapports."""
        return self.role in ('admin', 'pharmacien')