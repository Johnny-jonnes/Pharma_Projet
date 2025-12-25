"""
Modèle Client - Représente un client de la pharmacie.

Auteur: Alsény Camara
Version: 1.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Client:
    """
    Entité représentant un client.
    
    Attributes:
        id: Identifiant unique
        code: Code client unique
        first_name: Prénom
        last_name: Nom de famille
        phone: Numéro de téléphone
        email: Adresse email
        address: Adresse postale
        loyalty_points: Points de fidélité actuels
        total_spent: Total dépensé historique
        is_active: Statut actif
        created_at: Date de création
        updated_at: Date de modification
    """
    
    code: str
    first_name: str
    last_name: str
    id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    loyalty_points: int = 0
    total_spent: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation après initialisation."""
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Le code client est obligatoire")
        
        if not self.first_name or len(self.first_name.strip()) == 0:
            raise ValueError("Le prénom est obligatoire")
        
        if not self.last_name or len(self.last_name.strip()) == 0:
            raise ValueError("Le nom de famille est obligatoire")
        
        if self.loyalty_points < 0:
            raise ValueError("Les points de fidélité ne peuvent pas être négatifs")
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            'id': self.id,
            'code': self.code,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'loyalty_points': self.loyalty_points,
            'total_spent': self.total_spent,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """Crée une instance depuis un dictionnaire."""
        return cls(
            id=data.get('id'),
            code=data['code'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            email=data.get('email'),
            address=data.get('address'),
            loyalty_points=int(data.get('loyalty_points', 0)),
            total_spent=float(data.get('total_spent', 0.0)),
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def get_full_name(self) -> str:
        """Retourne le nom complet du client."""
        return f"{self.first_name} {self.last_name}"
    
    def add_points(self, points: int) -> None:
        """
        Ajoute des points de fidélité.
        
        Args:
            points: Nombre de points à ajouter
        """
        if points < 0:
            raise ValueError("Impossible d'ajouter des points négatifs")
        self.loyalty_points += points
    
    def use_points(self, points: int) -> bool:
        """
        Utilise des points de fidélité.
        
        Args:
            points: Nombre de points à utiliser
            
        Returns:
            bool: True si utilisation réussie
        """
        if points < 0:
            raise ValueError("Impossible d'utiliser des points négatifs")
        
        if points > self.loyalty_points:
            return False
        
        self.loyalty_points -= points
        return True
    
    def add_spent(self, amount: float) -> None:
        """
        Ajoute un montant au total dépensé.
        
        Args:
            amount: Montant à ajouter
        """
        if amount < 0:
            raise ValueError("Impossible d'ajouter un montant négatif")
        self.total_spent += amount